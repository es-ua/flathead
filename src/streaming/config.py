"""
FLATHEAD Streaming Service - Configuration
"""

from dataclasses import dataclass, field
from typing import Optional
import os


@dataclass
class AudioConfig:
    """Audio streaming configuration"""
    enabled: bool = True
    sample_rate: int = 48000
    channels: int = 2
    chunk_size: int = 1024
    dtype: str = "int32"

    # I2S devices
    device_front: str = "hw:0"  # Mics 1,2 (front stereo)
    device_side: str = "hw:1"   # Mics 3,4 (side stereo)

    # Streaming
    format: str = "raw"  # raw, opus, mp3


@dataclass
class VideoConfig:
    """Video streaming configuration"""
    enabled: bool = True
    width: int = 640
    height: int = 480
    fps: int = 30

    # Pi Camera devices
    camera_left: int = 0   # /dev/video0
    camera_right: int = 1  # /dev/video1

    # Encoding
    codec: str = "h264"
    bitrate: int = 2_000_000  # 2 Mbps

    # Streaming format
    format: str = "mjpeg"  # mjpeg, h264, raw


@dataclass
class ServerConfig:
    """Server connection configuration"""
    # WebSocket server
    ws_url: str = "ws://192.168.1.100:8765"

    # Or HTTP endpoint
    http_url: str = "http://192.168.1.100:5000"

    # Protocol: websocket, http, rtsp, webrtc
    protocol: str = "websocket"

    # Reconnection
    reconnect_delay: float = 2.0
    max_reconnect_attempts: int = 10

    # Authentication (optional)
    api_key: Optional[str] = None


@dataclass
class StreamingConfig:
    """Main configuration"""
    audio: AudioConfig = field(default_factory=AudioConfig)
    video: VideoConfig = field(default_factory=VideoConfig)
    server: ServerConfig = field(default_factory=ServerConfig)

    # Service settings
    robot_id: str = "flathead-01"
    log_level: str = "INFO"

    @classmethod
    def from_env(cls) -> "StreamingConfig":
        """Load configuration from environment variables"""

        config = cls()

        # Server
        config.server.ws_url = os.getenv(
            "STREAM_WS_URL", config.server.ws_url
        )
        config.server.http_url = os.getenv(
            "STREAM_HTTP_URL", config.server.http_url
        )
        config.server.protocol = os.getenv(
            "STREAM_PROTOCOL", config.server.protocol
        )
        config.server.api_key = os.getenv("STREAM_API_KEY")

        # Audio
        config.audio.enabled = os.getenv(
            "AUDIO_ENABLED", "true"
        ).lower() == "true"
        config.audio.sample_rate = int(os.getenv(
            "AUDIO_SAMPLE_RATE", config.audio.sample_rate
        ))

        # Video
        config.video.enabled = os.getenv(
            "VIDEO_ENABLED", "true"
        ).lower() == "true"
        config.video.width = int(os.getenv(
            "VIDEO_WIDTH", config.video.width
        ))
        config.video.height = int(os.getenv(
            "VIDEO_HEIGHT", config.video.height
        ))
        config.video.fps = int(os.getenv(
            "VIDEO_FPS", config.video.fps
        ))

        # Robot
        config.robot_id = os.getenv("ROBOT_ID", config.robot_id)
        config.log_level = os.getenv("LOG_LEVEL", config.log_level)

        return config
