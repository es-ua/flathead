#!/usr/bin/env python3
"""
Flathead Robot Camera Streaming Client

Streams video from two Pi Camera v3 modules to the server via WebRTC.
"""

import asyncio
import logging
import os
import signal
import sys
from typing import Optional

import yaml

from camera_manager import CameraManager, CameraConfig
from webrtc_client import WebRTCClient, ServerConfig

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("flathead-client")


class FlatheadStreamingClient:
    """Main application class for the streaming client."""

    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.camera_manager: Optional[CameraManager] = None
        self.webrtc_client: Optional[WebRTCClient] = None
        self._shutdown_event = asyncio.Event()

    def _load_config(self, config_path: Optional[str]) -> dict:
        """Load configuration from file or environment."""
        default_config = {
            "server": {
                "url": os.getenv("SERVER_URL", "http://localhost:8080"),
                "namespace": "/stream",
            },
            "cameras": {
                "left": {
                    "device_id": int(os.getenv("LEFT_CAMERA_ID", "0")),
                    "width": 640,
                    "height": 480,
                    "fps": 30,
                },
                "right": {
                    "device_id": int(os.getenv("RIGHT_CAMERA_ID", "1")),
                    "width": 640,
                    "height": 480,
                    "fps": 30,
                },
            },
            "reconnect_delay": 5,
        }

        if config_path and os.path.exists(config_path):
            with open(config_path, "r") as f:
                file_config = yaml.safe_load(f)
                default_config.update(file_config)
                logger.info(f"Loaded config from {config_path}")

        return default_config

    async def initialize(self) -> bool:
        """Initialize camera and WebRTC client."""
        # Initialize cameras
        left_config = CameraConfig(
            device_id=self.config["cameras"]["left"]["device_id"],
            width=self.config["cameras"]["left"]["width"],
            height=self.config["cameras"]["left"]["height"],
            fps=self.config["cameras"]["left"]["fps"],
        )
        right_config = CameraConfig(
            device_id=self.config["cameras"]["right"]["device_id"],
            width=self.config["cameras"]["right"]["width"],
            height=self.config["cameras"]["right"]["height"],
            fps=self.config["cameras"]["right"]["fps"],
        )

        self.camera_manager = CameraManager(left_config, right_config)

        if not await self.camera_manager.initialize():
            logger.error("Failed to initialize cameras")
            return False

        # Initialize WebRTC client
        server_config = ServerConfig(
            url=self.config["server"]["url"],
            namespace=self.config["server"]["namespace"],
        )
        self.webrtc_client = WebRTCClient(server_config)

        self.webrtc_client.on_connected(self._on_server_connected)
        self.webrtc_client.on_disconnected(self._on_server_disconnected)

        return True

    async def _on_server_connected(self) -> None:
        """Called when connected to server."""
        logger.info("Connected to server, starting camera streams...")

        if self.webrtc_client:
            # Start both camera streams
            left_cfg = self.config["cameras"]["left"]
            right_cfg = self.config["cameras"]["right"]

            await self.webrtc_client.start_camera_stream(
                "left",
                width=left_cfg["width"],
                height=left_cfg["height"],
                fps=left_cfg["fps"],
            )

            await self.webrtc_client.start_camera_stream(
                "right",
                width=right_cfg["width"],
                height=right_cfg["height"],
                fps=right_cfg["fps"],
            )

    async def _on_server_disconnected(self) -> None:
        """Called when disconnected from server."""
        logger.warning("Disconnected from server")

    async def _frame_loop(self) -> None:
        """Main loop for capturing and sending frames."""
        if not self.camera_manager or not self.webrtc_client:
            return

        fps = self.config["cameras"]["left"]["fps"]
        frame_interval = 1 / fps

        while not self._shutdown_event.is_set():
            try:
                # Capture frames from both cameras
                left_frame, right_frame = self.camera_manager.capture_stereo()

                # Update WebRTC tracks
                if left_frame is not None:
                    self.webrtc_client.update_frame("left", left_frame)

                if right_frame is not None:
                    self.webrtc_client.update_frame("right", right_frame)

                await asyncio.sleep(frame_interval)

            except Exception as e:
                logger.error(f"Frame loop error: {e}")
                await asyncio.sleep(1)

    async def run(self) -> None:
        """Main run loop."""
        if not await self.initialize():
            logger.error("Initialization failed")
            return

        logger.info("Flathead streaming client starting...")
        logger.info(f"Server URL: {self.config['server']['url']}")

        # Connect to server
        if not await self.webrtc_client.connect():
            logger.error("Failed to connect to server")
            return

        # Start frame capture loop and reconnection loop
        tasks = [
            asyncio.create_task(self._frame_loop()),
            asyncio.create_task(self.webrtc_client.reconnect_loop()),
        ]

        # Wait for shutdown signal
        await self._shutdown_event.wait()

        # Cancel tasks
        for task in tasks:
            task.cancel()

        await asyncio.gather(*tasks, return_exceptions=True)

    async def shutdown(self) -> None:
        """Graceful shutdown."""
        logger.info("Shutting down...")

        self._shutdown_event.set()

        if self.webrtc_client:
            await self.webrtc_client.disconnect()

        if self.camera_manager:
            await self.camera_manager.shutdown()

        logger.info("Shutdown complete")


async def main():
    """Entry point."""
    config_path = os.getenv("CONFIG_PATH", "/app/config.yml")

    client = FlatheadStreamingClient(config_path)

    # Setup signal handlers
    loop = asyncio.get_event_loop()

    def signal_handler():
        asyncio.create_task(client.shutdown())

    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, signal_handler)

    try:
        await client.run()
    except KeyboardInterrupt:
        await client.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
