import asyncio
import logging
from dataclasses import dataclass
from typing import Optional, Callable, Any
import numpy as np

try:
    from picamera2 import Picamera2
    from libcamera import controls
    PICAMERA_AVAILABLE = True
except ImportError:
    PICAMERA_AVAILABLE = False
    Picamera2 = None

logger = logging.getLogger(__name__)


@dataclass
class CameraConfig:
    device_id: int
    width: int = 640
    height: int = 480
    fps: int = 30
    format: str = "RGB888"


class CameraManager:
    """Manages dual Pi Camera v3 setup for stereo vision."""

    def __init__(
        self,
        left_config: CameraConfig,
        right_config: CameraConfig,
    ):
        self.left_config = left_config
        self.right_config = right_config
        self.left_camera: Optional[Any] = None
        self.right_camera: Optional[Any] = None
        self._running = False
        self._frame_callbacks: list[Callable] = []

        if not PICAMERA_AVAILABLE:
            logger.warning(
                "picamera2 not available. Using mock camera for testing."
            )

    async def initialize(self) -> bool:
        """Initialize both cameras."""
        try:
            if PICAMERA_AVAILABLE:
                self.left_camera = await self._init_camera(
                    self.left_config, "left"
                )
                self.right_camera = await self._init_camera(
                    self.right_config, "right"
                )
            else:
                logger.info("Using mock cameras for development")
                self.left_camera = MockCamera(self.left_config, "left")
                self.right_camera = MockCamera(self.right_config, "right")

            logger.info("Both cameras initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize cameras: {e}")
            return False

    async def _init_camera(
        self, config: CameraConfig, name: str
    ) -> "Picamera2":
        """Initialize a single Pi Camera."""
        camera = Picamera2(config.device_id)

        camera_config = camera.create_video_configuration(
            main={
                "size": (config.width, config.height),
                "format": config.format,
            },
            controls={
                "FrameRate": config.fps,
            },
        )

        camera.configure(camera_config)
        camera.start()

        logger.info(
            f"Camera {name} (device {config.device_id}) started: "
            f"{config.width}x{config.height}@{config.fps}fps"
        )

        return camera

    def capture_frame(self, camera_id: str) -> Optional[np.ndarray]:
        """Capture a single frame from specified camera."""
        camera = self.left_camera if camera_id == "left" else self.right_camera

        if camera is None:
            return None

        try:
            if PICAMERA_AVAILABLE:
                frame = camera.capture_array()
            else:
                frame = camera.capture_array()

            return frame

        except Exception as e:
            logger.error(f"Failed to capture frame from {camera_id}: {e}")
            return None

    def capture_stereo(self) -> tuple[Optional[np.ndarray], Optional[np.ndarray]]:
        """Capture synchronized frames from both cameras."""
        left_frame = self.capture_frame("left")
        right_frame = self.capture_frame("right")
        return left_frame, right_frame

    def add_frame_callback(self, callback: Callable) -> None:
        """Add callback for frame events."""
        self._frame_callbacks.append(callback)

    async def start_streaming(self) -> None:
        """Start continuous frame capture."""
        self._running = True

        while self._running:
            left_frame, right_frame = self.capture_stereo()

            for callback in self._frame_callbacks:
                try:
                    await callback(left_frame, right_frame)
                except Exception as e:
                    logger.error(f"Frame callback error: {e}")

            await asyncio.sleep(1 / self.left_config.fps)

    def stop_streaming(self) -> None:
        """Stop frame capture."""
        self._running = False

    async def shutdown(self) -> None:
        """Shutdown cameras and release resources."""
        self.stop_streaming()

        if self.left_camera:
            if PICAMERA_AVAILABLE:
                self.left_camera.stop()
                self.left_camera.close()
            self.left_camera = None

        if self.right_camera:
            if PICAMERA_AVAILABLE:
                self.right_camera.stop()
                self.right_camera.close()
            self.right_camera = None

        logger.info("Cameras shut down")

    def get_status(self) -> dict:
        """Get camera status information."""
        return {
            "left": {
                "initialized": self.left_camera is not None,
                "config": {
                    "device_id": self.left_config.device_id,
                    "resolution": f"{self.left_config.width}x{self.left_config.height}",
                    "fps": self.left_config.fps,
                },
            },
            "right": {
                "initialized": self.right_camera is not None,
                "config": {
                    "device_id": self.right_config.device_id,
                    "resolution": f"{self.right_config.width}x{self.right_config.height}",
                    "fps": self.right_config.fps,
                },
            },
            "streaming": self._running,
        }


class MockCamera:
    """Mock camera for development/testing without hardware."""

    def __init__(self, config: CameraConfig, name: str):
        self.config = config
        self.name = name
        self._frame_count = 0

    def capture_array(self) -> np.ndarray:
        """Generate a test pattern frame."""
        frame = np.zeros(
            (self.config.height, self.config.width, 3), dtype=np.uint8
        )

        # Create gradient based on camera side
        if self.name == "left":
            frame[:, :, 2] = np.linspace(0, 255, self.config.width, dtype=np.uint8)
        else:
            frame[:, :, 0] = np.linspace(0, 255, self.config.width, dtype=np.uint8)

        # Add frame counter
        self._frame_count += 1

        return frame
