"""
FLATHEAD - Video Streaming Module
2x Pi Camera v3 (stereo on head)
"""

import asyncio
import logging
import time
from typing import Optional, AsyncGenerator
from dataclasses import dataclass

try:
    import cv2
except ImportError:
    cv2 = None
    logging.warning("OpenCV not available - video disabled")

try:
    from picamera2 import Picamera2
    PICAMERA_AVAILABLE = True
except ImportError:
    PICAMERA_AVAILABLE = False
    logging.warning("picamera2 not available - using OpenCV fallback")

from config import VideoConfig

logger = logging.getLogger(__name__)


@dataclass
class VideoFrame:
    """Video frame with metadata"""
    data: bytes
    timestamp: float
    width: int
    height: int
    camera: str  # "left" or "right"
    format: str  # "jpeg", "h264", "raw"


class CameraCapture:
    """Single camera capture handler"""

    def __init__(
        self,
        camera_id: int,
        name: str,
        config: VideoConfig
    ):
        self.camera_id = camera_id
        self.name = name
        self.config = config
        self.capture = None
        self.picam = None
        self.running = False

    async def start(self) -> bool:
        """Initialize and start camera"""

        if PICAMERA_AVAILABLE:
            return await self._start_picamera()
        elif cv2 is not None:
            return await self._start_opencv()
        else:
            logger.error(f"No camera backend available for {self.name}")
            return False

    async def _start_picamera(self) -> bool:
        """Start using picamera2 (preferred for Pi Camera)"""
        try:
            self.picam = Picamera2(self.camera_id)

            # Configure camera
            config = self.picam.create_video_configuration(
                main={"size": (self.config.width, self.config.height)},
                controls={"FrameRate": self.config.fps}
            )
            self.picam.configure(config)
            self.picam.start()

            self.running = True
            logger.info(f"Started {self.name} camera (picamera2)")
            return True

        except Exception as e:
            logger.error(f"Failed to start {self.name} with picamera2: {e}")
            return False

    async def _start_opencv(self) -> bool:
        """Start using OpenCV (fallback)"""
        try:
            self.capture = cv2.VideoCapture(self.camera_id)

            if not self.capture.isOpened():
                logger.error(f"Cannot open camera {self.camera_id}")
                return False

            # Configure
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.width)
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.height)
            self.capture.set(cv2.CAP_PROP_FPS, self.config.fps)

            self.running = True
            logger.info(f"Started {self.name} camera (OpenCV)")
            return True

        except Exception as e:
            logger.error(f"Failed to start {self.name} with OpenCV: {e}")
            return False

    async def capture_frame(self) -> Optional[VideoFrame]:
        """Capture a single frame"""

        if not self.running:
            return None

        try:
            if self.picam:
                return await self._capture_picamera()
            elif self.capture:
                return await self._capture_opencv()
        except Exception as e:
            logger.error(f"Capture error on {self.name}: {e}")
            return None

        return None

    async def _capture_picamera(self) -> Optional[VideoFrame]:
        """Capture frame using picamera2"""

        # Capture as numpy array
        frame = self.picam.capture_array()

        # Encode as JPEG
        if cv2 is not None:
            _, jpeg = cv2.imencode(
                '.jpg', frame,
                [cv2.IMWRITE_JPEG_QUALITY, 85]
            )
            data = jpeg.tobytes()
            fmt = "jpeg"
        else:
            data = frame.tobytes()
            fmt = "raw"

        return VideoFrame(
            data=data,
            timestamp=time.time(),
            width=self.config.width,
            height=self.config.height,
            camera=self.name,
            format=fmt
        )

    async def _capture_opencv(self) -> Optional[VideoFrame]:
        """Capture frame using OpenCV"""

        ret, frame = self.capture.read()

        if not ret:
            return None

        # Encode as JPEG
        _, jpeg = cv2.imencode(
            '.jpg', frame,
            [cv2.IMWRITE_JPEG_QUALITY, 85]
        )

        return VideoFrame(
            data=jpeg.tobytes(),
            timestamp=time.time(),
            width=frame.shape[1],
            height=frame.shape[0],
            camera=self.name,
            format="jpeg"
        )

    async def stop(self):
        """Stop camera capture"""
        self.running = False

        if self.picam:
            try:
                self.picam.stop()
                self.picam.close()
            except Exception as e:
                logger.error(f"Error stopping picamera {self.name}: {e}")
            self.picam = None

        if self.capture:
            try:
                self.capture.release()
            except Exception as e:
                logger.error(f"Error releasing OpenCV {self.name}: {e}")
            self.capture = None

        logger.info(f"Stopped {self.name} camera")


class StereoVideoStreamer:
    """
    Handles stereo camera pair on robot head

    Camera layout:
        +------------------+
        | [Left]  [Right]  |  <- Stereo pair on pan/tilt head
        +--------+---------+
                 |
            [Pan Servo]
                 |
           [Tilt Servo]
    """

    def __init__(self, config: VideoConfig):
        self.config = config
        self.running = False

        self.cameras = {
            "left": CameraCapture(config.camera_left, "left", config),
            "right": CameraCapture(config.camera_right, "right", config)
        }

        self._frame_queues = {
            "left": asyncio.Queue(maxsize=10),
            "right": asyncio.Queue(maxsize=10),
            "stereo": asyncio.Queue(maxsize=10)
        }

    async def start(self):
        """Start both cameras"""
        self.running = True

        for name, camera in self.cameras.items():
            success = await camera.start()
            if not success:
                logger.warning(f"Camera {name} failed to start")

        # Start capture loops
        asyncio.create_task(self._capture_loop("left"))
        asyncio.create_task(self._capture_loop("right"))
        asyncio.create_task(self._stereo_sync_loop())

        logger.info("Stereo video streaming started")

    async def _capture_loop(self, camera_name: str):
        """Continuous capture loop for one camera"""

        camera = self.cameras[camera_name]
        queue = self._frame_queues[camera_name]

        target_interval = 1.0 / self.config.fps

        while self.running and camera.running:
            start_time = time.time()

            frame = await camera.capture_frame()

            if frame:
                try:
                    queue.put_nowait(frame)
                except asyncio.QueueFull:
                    # Drop oldest frame
                    try:
                        queue.get_nowait()
                        queue.put_nowait(frame)
                    except asyncio.QueueEmpty:
                        pass

            # Maintain frame rate
            elapsed = time.time() - start_time
            sleep_time = max(0, target_interval - elapsed)
            await asyncio.sleep(sleep_time)

    async def _stereo_sync_loop(self):
        """Synchronize left and right frames for stereo"""

        while self.running:
            left_frame = None
            right_frame = None

            try:
                left_frame = await asyncio.wait_for(
                    self._frame_queues["left"].get(),
                    timeout=0.1
                )
            except asyncio.TimeoutError:
                pass

            try:
                right_frame = await asyncio.wait_for(
                    self._frame_queues["right"].get(),
                    timeout=0.1
                )
            except asyncio.TimeoutError:
                pass

            if left_frame and right_frame:
                # Check if timestamps are close enough (within 50ms)
                if abs(left_frame.timestamp - right_frame.timestamp) < 0.05:
                    stereo_pair = {
                        "left": left_frame,
                        "right": right_frame,
                        "timestamp": (left_frame.timestamp + right_frame.timestamp) / 2
                    }
                    try:
                        self._frame_queues["stereo"].put_nowait(stereo_pair)
                    except asyncio.QueueFull:
                        pass

            await asyncio.sleep(0.001)

    async def get_frame(self, camera: str = "left") -> Optional[VideoFrame]:
        """Get single camera frame"""
        try:
            return await asyncio.wait_for(
                self._frame_queues[camera].get(),
                timeout=1.0
            )
        except asyncio.TimeoutError:
            return None

    async def get_stereo_frame(self) -> Optional[dict]:
        """Get synchronized stereo frame pair"""
        try:
            return await asyncio.wait_for(
                self._frame_queues["stereo"].get(),
                timeout=1.0
            )
        except asyncio.TimeoutError:
            return None

    async def stream_frames(self, camera: str = "left") -> AsyncGenerator[VideoFrame, None]:
        """Async generator for video frames"""
        while self.running:
            frame = await self.get_frame(camera)
            if frame:
                yield frame

    async def stream_stereo(self) -> AsyncGenerator[dict, None]:
        """Async generator for stereo frame pairs"""
        while self.running:
            stereo = await self.get_stereo_frame()
            if stereo:
                yield stereo

    async def stop(self):
        """Stop all cameras"""
        self.running = False

        for camera in self.cameras.values():
            await camera.stop()

        logger.info("Stereo video streaming stopped")


class DepthEstimator:
    """Estimate depth from stereo camera pair"""

    def __init__(self, baseline_cm: float = 7.0, focal_length_px: float = 500):
        """
        Args:
            baseline_cm: Distance between cameras in cm
            focal_length_px: Focal length in pixels
        """
        self.baseline = baseline_cm
        self.focal_length = focal_length_px

        if cv2 is not None:
            # Create stereo matcher
            self.stereo = cv2.StereoBM_create(numDisparities=64, blockSize=15)
        else:
            self.stereo = None

    def compute_disparity(
        self,
        left_frame: bytes,
        right_frame: bytes
    ) -> Optional[any]:
        """Compute disparity map from stereo pair"""

        if cv2 is None or self.stereo is None:
            return None

        import numpy as np

        # Decode JPEG frames
        left_img = cv2.imdecode(
            np.frombuffer(left_frame, np.uint8),
            cv2.IMREAD_GRAYSCALE
        )
        right_img = cv2.imdecode(
            np.frombuffer(right_frame, np.uint8),
            cv2.IMREAD_GRAYSCALE
        )

        if left_img is None or right_img is None:
            return None

        # Compute disparity
        disparity = self.stereo.compute(left_img, right_img)

        return disparity

    def disparity_to_depth(self, disparity: any) -> any:
        """Convert disparity map to depth map (in cm)"""

        import numpy as np

        # Avoid division by zero
        disparity = np.maximum(disparity, 0.1)

        # depth = baseline * focal_length / disparity
        depth = (self.baseline * self.focal_length) / disparity

        return depth
