import asyncio
import logging
from typing import Optional, Callable
from dataclasses import dataclass
import fractions

import numpy as np
import socketio
from aiortc import RTCPeerConnection, RTCConfiguration, RTCIceServer
from aiortc.contrib.media import MediaStreamTrack
from av import VideoFrame

logger = logging.getLogger(__name__)


@dataclass
class ServerConfig:
    url: str
    namespace: str = "/stream"


class CameraVideoTrack(MediaStreamTrack):
    """Custom video track that streams frames from camera."""

    kind = "video"

    def __init__(
        self,
        camera_id: str,
        width: int = 640,
        height: int = 480,
        fps: int = 30,
    ):
        super().__init__()
        self.camera_id = camera_id
        self.width = width
        self.height = height
        self.fps = fps
        self._frame: Optional[np.ndarray] = None
        self._frame_count = 0
        self._time_base = fractions.Fraction(1, fps)

    def update_frame(self, frame: np.ndarray) -> None:
        """Update the current frame to be sent."""
        self._frame = frame

    async def recv(self) -> VideoFrame:
        """Called by aiortc to get the next frame."""
        pts = self._frame_count
        self._frame_count += 1

        if self._frame is not None:
            frame = self._frame
        else:
            # Generate black frame if no camera frame available
            frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)

        video_frame = VideoFrame.from_ndarray(frame, format="rgb24")
        video_frame.pts = pts
        video_frame.time_base = self._time_base

        await asyncio.sleep(1 / self.fps)
        return video_frame


class WebRTCClient:
    """WebRTC client for streaming to NestJS server."""

    def __init__(self, server_config: ServerConfig):
        self.server_config = server_config
        self.sio = socketio.AsyncClient()
        self.peer_connections: dict[str, RTCPeerConnection] = {}
        self.video_tracks: dict[str, CameraVideoTrack] = {}
        self._connected = False
        self._reconnect_delay = 5
        self._on_connected: Optional[Callable] = None
        self._on_disconnected: Optional[Callable] = None

        self._setup_socket_handlers()

    def _setup_socket_handlers(self) -> None:
        """Setup Socket.IO event handlers."""

        @self.sio.event
        async def connect():
            logger.info("Connected to signaling server")
            self._connected = True
            if self._on_connected:
                await self._on_connected()

        @self.sio.event
        async def disconnect():
            logger.warning("Disconnected from signaling server")
            self._connected = False
            if self._on_disconnected:
                await self._on_disconnected()

        @self.sio.on("connected")
        async def on_connected(data):
            logger.info(f"Server acknowledged connection: {data}")

        @self.sio.on("answer")
        async def on_answer(data):
            camera_id = data["cameraId"]
            answer = data["answer"]
            logger.info(f"Received answer for camera {camera_id}")

            pc = self.peer_connections.get(camera_id)
            if pc:
                from aiortc import RTCSessionDescription

                await pc.setRemoteDescription(
                    RTCSessionDescription(sdp=answer["sdp"], type=answer["type"])
                )
                logger.info(f"Set remote description for camera {camera_id}")

        @self.sio.on("error")
        async def on_error(data):
            logger.error(f"Server error: {data}")

    async def connect(self) -> bool:
        """Connect to the signaling server."""
        try:
            await self.sio.connect(
                self.server_config.url,
                namespaces=[self.server_config.namespace],
            )
            return True
        except Exception as e:
            logger.error(f"Failed to connect to server: {e}")
            return False

    async def start_camera_stream(
        self,
        camera_id: str,
        width: int = 640,
        height: int = 480,
        fps: int = 30,
    ) -> bool:
        """Start streaming a camera to the server."""
        if not self._connected:
            logger.error("Not connected to server")
            return False

        try:
            # Create video track
            video_track = CameraVideoTrack(
                camera_id=camera_id,
                width=width,
                height=height,
                fps=fps,
            )
            self.video_tracks[camera_id] = video_track

            # Create peer connection
            config = RTCConfiguration(
                iceServers=[
                    RTCIceServer(urls="stun:stun.l.google.com:19302"),
                    RTCIceServer(urls="stun:stun1.l.google.com:19302"),
                ]
            )
            pc = RTCPeerConnection(configuration=config)
            self.peer_connections[camera_id] = pc

            # Add track to peer connection
            pc.addTrack(video_track)

            # Handle ICE candidates
            @pc.on("icecandidate")
            async def on_icecandidate(candidate):
                if candidate:
                    await self.sio.emit(
                        "ice-candidate",
                        {
                            "cameraId": camera_id,
                            "candidate": {
                                "candidate": candidate.candidate,
                                "sdpMid": candidate.sdpMid,
                                "sdpMLineIndex": candidate.sdpMLineIndex,
                            },
                        },
                        namespace=self.server_config.namespace,
                    )

            @pc.on("connectionstatechange")
            async def on_connectionstatechange():
                logger.info(
                    f"Connection state for {camera_id}: {pc.connectionState}"
                )

            # Create and send offer
            offer = await pc.createOffer()
            await pc.setLocalDescription(offer)

            await self.sio.emit(
                "offer",
                {
                    "cameraId": camera_id,
                    "offer": {
                        "type": offer.type,
                        "sdp": offer.sdp,
                    },
                },
                namespace=self.server_config.namespace,
            )

            logger.info(f"Sent offer for camera {camera_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to start camera stream {camera_id}: {e}")
            return False

    def update_frame(self, camera_id: str, frame: np.ndarray) -> None:
        """Update the frame for a camera track."""
        track = self.video_tracks.get(camera_id)
        if track:
            track.update_frame(frame)

    async def stop_camera_stream(self, camera_id: str) -> None:
        """Stop streaming a specific camera."""
        pc = self.peer_connections.pop(camera_id, None)
        if pc:
            await pc.close()

        self.video_tracks.pop(camera_id, None)

        if self._connected:
            await self.sio.emit(
                "disconnect-camera",
                {"cameraId": camera_id},
                namespace=self.server_config.namespace,
            )

        logger.info(f"Stopped camera stream {camera_id}")

    async def disconnect(self) -> None:
        """Disconnect from server and close all connections."""
        for camera_id in list(self.peer_connections.keys()):
            await self.stop_camera_stream(camera_id)

        if self.sio.connected:
            await self.sio.disconnect()

        self._connected = False
        logger.info("Disconnected from server")

    async def reconnect_loop(self) -> None:
        """Continuously attempt to reconnect if disconnected."""
        while True:
            if not self._connected:
                logger.info("Attempting to reconnect...")
                success = await self.connect()
                if success:
                    # Restart camera streams
                    for camera_id, track in self.video_tracks.items():
                        await self.start_camera_stream(
                            camera_id,
                            track.width,
                            track.height,
                            track.fps,
                        )
            await asyncio.sleep(self._reconnect_delay)

    def on_connected(self, callback: Callable) -> None:
        """Set callback for connection event."""
        self._on_connected = callback

    def on_disconnected(self, callback: Callable) -> None:
        """Set callback for disconnection event."""
        self._on_disconnected = callback

    def get_status(self) -> dict:
        """Get client connection status."""
        return {
            "connected": self._connected,
            "server_url": self.server_config.url,
            "active_streams": list(self.peer_connections.keys()),
            "peer_states": {
                camera_id: pc.connectionState
                for camera_id, pc in self.peer_connections.items()
            },
        }
