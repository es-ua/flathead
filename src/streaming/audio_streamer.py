"""
FLATHEAD - Audio Streaming Module
4x INMP441 I2S microphones
"""

import asyncio
import numpy as np
import logging
from typing import Optional, Callable, AsyncGenerator
from dataclasses import dataclass

try:
    import sounddevice as sd
except ImportError:
    sd = None
    logging.warning("sounddevice not available - audio disabled")

from config import AudioConfig

logger = logging.getLogger(__name__)


@dataclass
class AudioFrame:
    """Audio frame with metadata"""
    data: bytes
    timestamp: float
    channels: int
    sample_rate: int
    source: str  # "front" or "side"


class AudioStreamer:
    """
    Handles 4-microphone array (2x stereo I2S buses)

    Mic layout:
        Mic 1 (FL) -------- Mic 2 (FR)   <- Front stereo (I2S bus 0)
             |                  |
             |     [ROBOT]      |
             |                  |
        Mic 3 (L)          Mic 4 (R)     <- Side stereo (I2S bus 1)
    """

    def __init__(self, config: AudioConfig):
        self.config = config
        self.running = False
        self._streams = {}
        self._queues = {
            "front": asyncio.Queue(maxsize=50),
            "side": asyncio.Queue(maxsize=50)
        }

    def _check_available(self) -> bool:
        """Check if audio is available"""
        if sd is None:
            logger.error("sounddevice not installed")
            return False
        return True

    def list_devices(self) -> list:
        """List available audio devices"""
        if not self._check_available():
            return []
        return sd.query_devices()

    def _create_callback(self, source: str) -> Callable:
        """Create audio callback for a source"""

        def callback(indata, frames, time_info, status):
            if status:
                logger.warning(f"Audio {source} status: {status}")

            # Create frame
            frame = AudioFrame(
                data=indata.tobytes(),
                timestamp=time_info.inputBufferAdcTime,
                channels=self.config.channels,
                sample_rate=self.config.sample_rate,
                source=source
            )

            # Non-blocking put
            try:
                self._queues[source].put_nowait(frame)
            except asyncio.QueueFull:
                pass  # Drop frame if queue full

        return callback

    async def start(self):
        """Start audio capture from all microphones"""

        if not self._check_available():
            return

        self.running = True
        logger.info("Starting audio capture...")

        # Start front microphones (I2S bus 0)
        try:
            self._streams["front"] = sd.InputStream(
                device=self.config.device_front,
                samplerate=self.config.sample_rate,
                channels=self.config.channels,
                dtype=self.config.dtype,
                blocksize=self.config.chunk_size,
                callback=self._create_callback("front")
            )
            self._streams["front"].start()
            logger.info(f"Front mics started on {self.config.device_front}")
        except Exception as e:
            logger.error(f"Failed to start front mics: {e}")

        # Start side microphones (I2S bus 1)
        try:
            self._streams["side"] = sd.InputStream(
                device=self.config.device_side,
                samplerate=self.config.sample_rate,
                channels=self.config.channels,
                dtype=self.config.dtype,
                blocksize=self.config.chunk_size,
                callback=self._create_callback("side")
            )
            self._streams["side"].start()
            logger.info(f"Side mics started on {self.config.device_side}")
        except Exception as e:
            logger.warning(f"Side mics not available: {e}")

    async def stop(self):
        """Stop audio capture"""
        self.running = False

        for name, stream in self._streams.items():
            try:
                stream.stop()
                stream.close()
                logger.info(f"Stopped {name} audio stream")
            except Exception as e:
                logger.error(f"Error stopping {name}: {e}")

        self._streams.clear()

    async def get_frame(self, source: str = "front") -> Optional[AudioFrame]:
        """Get next audio frame from specified source"""
        try:
            return await asyncio.wait_for(
                self._queues[source].get(),
                timeout=1.0
            )
        except asyncio.TimeoutError:
            return None

    async def stream_frames(self, source: str = "front") -> AsyncGenerator[AudioFrame, None]:
        """Async generator for audio frames"""
        while self.running:
            frame = await self.get_frame(source)
            if frame:
                yield frame

    async def get_combined_frame(self) -> Optional[dict]:
        """Get frames from both sources combined"""

        front_frame = None
        side_frame = None

        try:
            front_frame = self._queues["front"].get_nowait()
        except asyncio.QueueEmpty:
            pass

        try:
            side_frame = self._queues["side"].get_nowait()
        except asyncio.QueueEmpty:
            pass

        if front_frame or side_frame:
            return {
                "front": front_frame,
                "side": side_frame,
                "timestamp": front_frame.timestamp if front_frame else side_frame.timestamp
            }
        return None


class SoundLocalizer:
    """Calculate sound direction from microphone array"""

    def __init__(self, mic_distance_cm: float = 30.0):
        self.mic_distance = mic_distance_cm
        self.speed_of_sound = 34300  # cm/s at 20°C

    def calculate_direction(
        self,
        left_audio: np.ndarray,
        right_audio: np.ndarray,
        sample_rate: int
    ) -> tuple[float, float]:
        """
        Calculate sound direction using cross-correlation

        Returns: (angle_degrees, confidence)
            angle: -90 (left) to +90 (right)
            confidence: 0.0 to 1.0
        """

        # Flatten if needed
        left = left_audio.flatten().astype(np.float32)
        right = right_audio.flatten().astype(np.float32)

        # Normalize
        left = left / (np.max(np.abs(left)) + 1e-10)
        right = right / (np.max(np.abs(right)) + 1e-10)

        # Cross-correlation
        correlation = np.correlate(left, right, mode='full')
        center = len(correlation) // 2

        # Find peak
        peak_idx = np.argmax(correlation)
        delay_samples = peak_idx - center

        # Convert to time delay
        delay_seconds = delay_samples / sample_rate

        # Convert to angle
        # sin(angle) = delay * speed_of_sound / mic_distance
        sin_angle = np.clip(
            (delay_seconds * self.speed_of_sound) / self.mic_distance,
            -1.0, 1.0
        )
        angle_rad = np.arcsin(sin_angle)
        angle_deg = np.degrees(angle_rad)

        # Calculate confidence from correlation peak
        peak_value = correlation[peak_idx]
        baseline = np.mean(np.abs(correlation))
        confidence = min(1.0, peak_value / (baseline * 10 + 1e-10))

        return angle_deg, confidence

    def localize_2d(
        self,
        front_left: np.ndarray,
        front_right: np.ndarray,
        side_left: np.ndarray,
        side_right: np.ndarray,
        sample_rate: int
    ) -> tuple[float, float, float]:
        """
        2D sound localization using all 4 microphones

        Returns: (azimuth_deg, elevation_deg, confidence)
        """

        # Front pair gives left-right
        azimuth_front, conf_front = self.calculate_direction(
            front_left, front_right, sample_rate
        )

        # Side pair gives additional left-right
        azimuth_side, conf_side = self.calculate_direction(
            side_left, side_right, sample_rate
        )

        # Combine estimates (weighted average)
        total_conf = conf_front + conf_side + 1e-10
        azimuth = (
            azimuth_front * conf_front +
            azimuth_side * conf_side
        ) / total_conf

        # For elevation, we'd need front-back comparison
        # Simplified: use intensity difference
        front_energy = np.mean(front_left**2 + front_right**2)
        side_energy = np.mean(side_left**2 + side_right**2)
        elevation = 0.0  # Placeholder

        confidence = (conf_front + conf_side) / 2

        return azimuth, elevation, confidence
