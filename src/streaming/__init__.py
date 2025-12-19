"""
FLATHEAD Streaming Service

Unified audio/video streaming from robot to server.

Components:
    - AudioStreamer: 4x INMP441 I2S microphones
    - StereoVideoStreamer: 2x Pi Camera v3
    - StreamingService: Combined streaming with WebSocket/HTTP
    - LedController: WS2812B status LEDs
"""

from .config import StreamingConfig, AudioConfig, VideoConfig, ServerConfig
from .audio_streamer import AudioStreamer, AudioFrame, SoundLocalizer
from .video_streamer import StereoVideoStreamer, VideoFrame, DepthEstimator
from .led_controller import LedController, LedConfig, LedStatus

__all__ = [
    "StreamingConfig",
    "AudioConfig",
    "VideoConfig",
    "ServerConfig",
    "AudioStreamer",
    "AudioFrame",
    "SoundLocalizer",
    "StereoVideoStreamer",
    "VideoFrame",
    "DepthEstimator",
    "LedController",
    "LedConfig",
    "LedStatus",
]

__version__ = "1.0.0"
