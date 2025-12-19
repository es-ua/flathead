#!/usr/bin/env python3
"""
FLATHEAD - Streaming Server
Receives audio/video streams from robot

Run on your PC/server:
    python server.py

Or with Docker:
    docker-compose --profile test up test-server
"""

import asyncio
import json
import logging
import struct
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

try:
    import websockets
    from websockets.server import serve
except ImportError:
    print("Install websockets: pip install websockets")
    exit(1)

try:
    import numpy as np
except ImportError:
    np = None

try:
    import cv2
except ImportError:
    cv2 = None

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class StreamingServer:
    """WebSocket server for receiving robot streams"""

    # Message types (must match client)
    MSG_AUDIO = 0x01
    MSG_VIDEO = 0x02
    MSG_STEREO = 0x03
    MSG_CONTROL = 0xFF

    def __init__(self, host: str = "0.0.0.0", port: int = 8765):
        self.host = host
        self.port = port
        self.clients: Dict[str, dict] = {}

        # Recording
        self.recording = False
        self.record_dir = Path("recordings")
        self.record_dir.mkdir(exist_ok=True)

        # Stats
        self.stats = {
            "audio_frames": 0,
            "video_frames": 0,
            "bytes_received": 0,
            "start_time": time.time()
        }

        # Display window (if OpenCV available)
        self.show_video = cv2 is not None

    def _unpack_header(self, data: bytes) -> tuple:
        """Unpack message header"""
        # Header: msg_type (1) + source_id (1) + timestamp (8) + length (4) = 14 bytes
        if len(data) < 14:
            return None, None, None, None

        header = struct.unpack('>BBdI', data[:14])
        msg_type, source_id, timestamp, length = header

        return msg_type, source_id, timestamp, data[14:14+length]

    async def handle_client(self, websocket):
        """Handle a connected client"""

        client_addr = websocket.remote_address
        client_id = f"{client_addr[0]}:{client_addr[1]}"

        logger.info(f"Client connected: {client_id}")

        self.clients[client_id] = {
            "websocket": websocket,
            "connected_at": time.time(),
            "robot_id": None
        }

        try:
            async for message in websocket:
                await self._process_message(client_id, message)

        except websockets.ConnectionClosed:
            logger.info(f"Client disconnected: {client_id}")
        except Exception as e:
            logger.error(f"Error handling client {client_id}: {e}")
        finally:
            del self.clients[client_id]

    async def _process_message(self, client_id: str, message):
        """Process incoming message"""

        # Check if JSON (control message)
        if isinstance(message, str):
            try:
                data = json.loads(message)
                await self._handle_control(client_id, data)
                return
            except json.JSONDecodeError:
                pass

        # Binary message - unpack header
        msg_type, source_id, timestamp, payload = self._unpack_header(message)

        if msg_type is None:
            logger.warning(f"Invalid message from {client_id}")
            return

        self.stats["bytes_received"] += len(message)

        if msg_type == self.MSG_AUDIO:
            await self._handle_audio(client_id, source_id, timestamp, payload)
        elif msg_type == self.MSG_VIDEO:
            await self._handle_video(client_id, source_id, timestamp, payload)
        elif msg_type == self.MSG_CONTROL:
            pass  # Already handled above

    async def _handle_control(self, client_id: str, data: dict):
        """Handle control message"""

        msg_type = data.get("type")

        if msg_type == "hello":
            robot_id = data.get("robot_id", "unknown")
            self.clients[client_id]["robot_id"] = robot_id
            logger.info(f"Robot {robot_id} connected from {client_id}")
            logger.info(f"Capabilities: {data.get('capabilities', {})}")

    async def _handle_audio(
        self,
        client_id: str,
        source_id: int,
        timestamp: float,
        payload: bytes
    ):
        """Handle audio frame"""

        self.stats["audio_frames"] += 1
        source_name = "front" if source_id == 0 else "side"

        # Log occasionally
        if self.stats["audio_frames"] % 100 == 0:
            logger.debug(f"Audio {source_name}: {len(payload)} bytes")

        # Save if recording
        if self.recording:
            self._save_audio(source_name, timestamp, payload)

    async def _handle_video(
        self,
        client_id: str,
        source_id: int,
        timestamp: float,
        payload: bytes
    ):
        """Handle video frame"""

        self.stats["video_frames"] += 1
        camera_name = "left" if source_id == 0 else "right"

        # Display if OpenCV available
        if self.show_video and cv2 is not None:
            try:
                # Decode JPEG
                img_array = np.frombuffer(payload, dtype=np.uint8)
                frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

                if frame is not None:
                    # Show in window
                    window_name = f"Flathead - {camera_name}"
                    cv2.imshow(window_name, frame)
                    cv2.waitKey(1)

            except Exception as e:
                logger.error(f"Video decode error: {e}")

        # Save if recording
        if self.recording:
            self._save_video(camera_name, timestamp, payload)

    def _save_audio(self, source: str, timestamp: float, data: bytes):
        """Save audio frame to file"""
        # Implementation for audio saving
        pass

    def _save_video(self, camera: str, timestamp: float, data: bytes):
        """Save video frame to file"""
        filename = self.record_dir / f"{camera}_{int(timestamp*1000)}.jpg"
        with open(filename, 'wb') as f:
            f.write(data)

    async def _stats_loop(self):
        """Print stats periodically"""

        while True:
            await asyncio.sleep(10)

            elapsed = time.time() - self.stats["start_time"]
            audio_fps = self.stats["audio_frames"] / elapsed
            video_fps = self.stats["video_frames"] / elapsed
            bandwidth = self.stats["bytes_received"] / elapsed / 1024

            logger.info(
                f"Stats: clients={len(self.clients)}, "
                f"audio={audio_fps:.1f}fps, video={video_fps:.1f}fps, "
                f"bandwidth={bandwidth:.1f}KB/s"
            )

    async def run(self):
        """Run the server"""

        logger.info(f"Starting Flathead Streaming Server on {self.host}:{self.port}")

        # Start stats loop
        asyncio.create_task(self._stats_loop())

        # Start WebSocket server
        async with serve(self.handle_client, self.host, self.port):
            logger.info(f"Server running on ws://{self.host}:{self.port}")
            await asyncio.Future()  # Run forever


async def main():
    import argparse

    parser = argparse.ArgumentParser(description="Flathead Streaming Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8765, help="Port to listen on")
    parser.add_argument("--no-video", action="store_true", help="Disable video display")
    args = parser.parse_args()

    server = StreamingServer(host=args.host, port=args.port)

    if args.no_video:
        server.show_video = False

    try:
        await server.run()
    except KeyboardInterrupt:
        logger.info("Server stopped")


if __name__ == "__main__":
    asyncio.run(main())
