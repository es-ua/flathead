#!/usr/bin/env python3
"""
FLATHEAD - Unified Streaming Service
Streams audio (4 mics) + video (2 cameras) to server

Usage:
    python main.py
    # or with env vars:
    STREAM_WS_URL=ws://server:8765 python main.py
"""

import asyncio
import json
import logging
import signal
import struct
import time
from typing import Optional

try:
    import websockets
except ImportError:
    websockets = None
    logging.warning("websockets not available")

try:
    import aiohttp
except ImportError:
    aiohttp = None

from config import StreamingConfig
from audio_streamer import AudioStreamer, AudioFrame
from video_streamer import StereoVideoStreamer, VideoFrame
from led_controller import LedController, LedConfig, LedStatus, set_controller

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class StreamingService:
    """
    Unified streaming service for Flathead robot

    Streams:
        - 4x audio channels (front L/R, side L/R)
        - 2x video channels (stereo cameras)

    Protocol:
        Each message is prefixed with header:
        - 1 byte: message type (0x01=audio, 0x02=video, 0x03=stereo, 0xFF=control)
        - 1 byte: source ID (camera/mic index)
        - 8 bytes: timestamp (double)
        - 4 bytes: data length
        - N bytes: data
    """

    # Message types
    MSG_AUDIO = 0x01
    MSG_VIDEO = 0x02
    MSG_STEREO = 0x03
    MSG_CONTROL = 0xFF

    def __init__(self, config: StreamingConfig):
        self.config = config
        self.running = False

        # Streamers
        self.audio = AudioStreamer(config.audio) if config.audio.enabled else None
        self.video = StereoVideoStreamer(config.video) if config.video.enabled else None

        # LED controller
        self.led = LedController(LedConfig.from_env())
        set_controller(self.led)

        # Connection
        self.websocket = None
        self.http_session = None

        # Stats
        self.stats = {
            "audio_frames": 0,
            "video_frames": 0,
            "bytes_sent": 0,
            "errors": 0,
            "start_time": None
        }

    def _pack_message(
        self,
        msg_type: int,
        source_id: int,
        timestamp: float,
        data: bytes
    ) -> bytes:
        """Pack data with header for transmission"""

        header = struct.pack(
            '>BBdI',  # big-endian: byte, byte, double, uint32
            msg_type,
            source_id,
            timestamp,
            len(data)
        )
        return header + data

    async def connect(self) -> bool:
        """Connect to streaming server"""

        self.led.set_status(LedStatus.CONNECTING)
        protocol = self.config.server.protocol

        if protocol == "websocket":
            success = await self._connect_websocket()
        elif protocol == "http":
            success = await self._connect_http()
        else:
            logger.error(f"Unknown protocol: {protocol}")
            self.led.set_status(LedStatus.ERROR)
            return False

        if success:
            self.led.set_status(LedStatus.CONNECTED)
        else:
            self.led.set_status(LedStatus.ERROR)
        return success

    async def _connect_websocket(self) -> bool:
        """Connect via WebSocket"""

        if websockets is None:
            logger.error("websockets library not installed")
            return False

        url = self.config.server.ws_url
        logger.info(f"Connecting to {url}...")

        for attempt in range(self.config.server.max_reconnect_attempts):
            try:
                # Add auth header if API key provided
                headers = {}
                if self.config.server.api_key:
                    headers["Authorization"] = f"Bearer {self.config.server.api_key}"

                self.websocket = await websockets.connect(
                    url,
                    extra_headers=headers,
                    ping_interval=20,
                    ping_timeout=10,
                    max_size=10 * 1024 * 1024  # 10MB max message
                )

                # Send hello message
                hello = json.dumps({
                    "type": "hello",
                    "robot_id": self.config.robot_id,
                    "capabilities": {
                        "audio": self.config.audio.enabled,
                        "video": self.config.video.enabled,
                        "audio_channels": 4,
                        "video_channels": 2
                    }
                })
                await self.websocket.send(hello)

                logger.info(f"Connected to {url}")
                return True

            except Exception as e:
                logger.warning(f"Connection attempt {attempt + 1} failed: {e}")
                await asyncio.sleep(self.config.server.reconnect_delay)

        logger.error("Failed to connect after all attempts")
        return False

    async def _connect_http(self) -> bool:
        """Initialize HTTP session"""

        if aiohttp is None:
            logger.error("aiohttp library not installed")
            return False

        self.http_session = aiohttp.ClientSession()
        logger.info(f"HTTP session ready for {self.config.server.http_url}")
        return True

    async def disconnect(self):
        """Disconnect from server"""

        if self.websocket:
            try:
                await self.websocket.close()
            except Exception as e:
                logger.error(f"Error closing websocket: {e}")
            self.websocket = None

        if self.http_session:
            await self.http_session.close()
            self.http_session = None

    async def send(self, data: bytes) -> bool:
        """Send data to server"""

        try:
            if self.websocket:
                await self.websocket.send(data)
                self.stats["bytes_sent"] += len(data)
                return True

            elif self.http_session:
                async with self.http_session.post(
                    self.config.server.http_url,
                    data=data,
                    headers={"Content-Type": "application/octet-stream"}
                ) as resp:
                    if resp.status == 200:
                        self.stats["bytes_sent"] += len(data)
                        return True
                    else:
                        logger.warning(f"HTTP error: {resp.status}")
                        return False

        except Exception as e:
            logger.error(f"Send error: {e}")
            self.stats["errors"] += 1
            return False

        return False

    async def _stream_audio(self):
        """Audio streaming loop"""

        if not self.audio:
            return

        logger.info("Starting audio streaming...")

        source_ids = {"front": 0, "side": 1}

        while self.running:
            try:
                # Get frames from both sources
                for source in ["front", "side"]:
                    frame = await self.audio.get_frame(source)

                    if frame:
                        message = self._pack_message(
                            self.MSG_AUDIO,
                            source_ids[source],
                            frame.timestamp,
                            frame.data
                        )
                        await self.send(message)
                        self.stats["audio_frames"] += 1

            except Exception as e:
                logger.error(f"Audio streaming error: {e}")
                self.stats["errors"] += 1
                await asyncio.sleep(0.1)

    async def _stream_video(self):
        """Video streaming loop"""

        if not self.video:
            return

        logger.info("Starting video streaming...")

        while self.running:
            try:
                # Get stereo frame pair
                stereo = await self.video.get_stereo_frame()

                if stereo:
                    # Send left frame
                    if stereo["left"]:
                        message = self._pack_message(
                            self.MSG_VIDEO,
                            0,  # left camera
                            stereo["left"].timestamp,
                            stereo["left"].data
                        )
                        await self.send(message)

                    # Send right frame
                    if stereo["right"]:
                        message = self._pack_message(
                            self.MSG_VIDEO,
                            1,  # right camera
                            stereo["right"].timestamp,
                            stereo["right"].data
                        )
                        await self.send(message)

                    self.stats["video_frames"] += 1

            except Exception as e:
                logger.error(f"Video streaming error: {e}")
                self.stats["errors"] += 1
                await asyncio.sleep(0.1)

    async def _stats_loop(self):
        """Print statistics periodically"""

        while self.running:
            await asyncio.sleep(10)

            elapsed = time.time() - self.stats["start_time"]
            audio_fps = self.stats["audio_frames"] / elapsed
            video_fps = self.stats["video_frames"] / elapsed
            bandwidth = self.stats["bytes_sent"] / elapsed / 1024  # KB/s

            logger.info(
                f"Stats: audio={audio_fps:.1f}fps, video={video_fps:.1f}fps, "
                f"bandwidth={bandwidth:.1f}KB/s, errors={self.stats['errors']}"
            )

    async def run(self):
        """Main service loop"""

        self.running = True
        self.stats["start_time"] = time.time()

        # Start LED controller
        await self.led.start()

        # Connect to server
        if not await self.connect():
            logger.error("Failed to connect to server")
            return

        # Start streamers
        if self.audio:
            await self.audio.start()
        if self.video:
            await self.video.start()

        # Set streaming status
        self.led.set_status(LedStatus.STREAMING)

        # Create streaming tasks
        tasks = [
            asyncio.create_task(self._stats_loop())
        ]

        if self.audio:
            tasks.append(asyncio.create_task(self._stream_audio()))
        if self.video:
            tasks.append(asyncio.create_task(self._stream_video()))

        logger.info("Streaming service running...")

        try:
            await asyncio.gather(*tasks)
        except asyncio.CancelledError:
            logger.info("Streaming cancelled")
        finally:
            await self.stop()

    async def stop(self):
        """Stop the service"""

        logger.info("Stopping streaming service...")
        self.running = False

        # LED off
        self.led.set_status(LedStatus.OFF)
        await self.led.stop()

        if self.audio:
            await self.audio.stop()
        if self.video:
            await self.video.stop()

        await self.disconnect()

        # Final stats
        elapsed = time.time() - self.stats["start_time"]
        logger.info(
            f"Final stats: {self.stats['audio_frames']} audio frames, "
            f"{self.stats['video_frames']} video frames, "
            f"{self.stats['bytes_sent'] / 1024 / 1024:.1f}MB sent in {elapsed:.1f}s"
        )


async def main():
    """Entry point"""

    # Load config from environment
    config = StreamingConfig.from_env()

    logger.info(f"Starting Flathead Streaming Service")
    logger.info(f"Robot ID: {config.robot_id}")
    logger.info(f"Server: {config.server.ws_url}")
    logger.info(f"Audio: {config.audio.enabled}, Video: {config.video.enabled}")

    # Create service
    service = StreamingService(config)

    # Handle shutdown
    loop = asyncio.get_event_loop()

    def shutdown():
        logger.info("Shutdown signal received")
        asyncio.create_task(service.stop())

    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, shutdown)

    # Run service
    try:
        await service.run()
    except KeyboardInterrupt:
        logger.info("Interrupted")
    finally:
        await service.stop()


if __name__ == "__main__":
    asyncio.run(main())
