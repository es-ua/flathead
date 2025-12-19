"""
FLATHEAD LED Status Controller

WS2812B / NeoPixel LED control for status indication.

Hardware:
    - WS2812B LED strip/ring connected to GPIO18 (PWM)
    - 5V power supply for LEDs
    - Level shifter recommended (3.3V -> 5V) but often works without

Statuses:
    - OFF: System idle
    - CONNECTING: Orange pulse - connecting to server
    - STREAMING: Green solid - actively streaming
    - ERROR: Red blink - connection error
    - AUDIO_ACTIVE: Blue pulse overlay - sound detected
    - DIRECTION: Gradient showing sound direction
"""

import asyncio
import logging
import math
import time
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

# Try to import NeoPixel library
try:
    import board
    import neopixel
    NEOPIXEL_AVAILABLE = True
except ImportError:
    NEOPIXEL_AVAILABLE = False
    logger.warning("NeoPixel library not available - LED control disabled")


class LedStatus(Enum):
    """LED status states"""
    OFF = "off"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    STREAMING = "streaming"
    ERROR = "error"
    AUDIO_ACTIVE = "audio_active"


@dataclass
class LedConfig:
    """LED configuration"""
    enabled: bool = True
    pin: int = 18  # GPIO18 (PWM)
    num_leds: int = 16  # Ring or strip size
    brightness: float = 0.3  # 0.0 - 1.0

    # Colors (RGB)
    color_off: Tuple[int, int, int] = (0, 0, 0)
    color_connecting: Tuple[int, int, int] = (255, 165, 0)  # Orange
    color_connected: Tuple[int, int, int] = (0, 100, 255)   # Blue
    color_streaming: Tuple[int, int, int] = (0, 255, 0)     # Green
    color_error: Tuple[int, int, int] = (255, 0, 0)         # Red
    color_audio: Tuple[int, int, int] = (0, 100, 255)       # Blue

    @classmethod
    def from_env(cls) -> "LedConfig":
        """Load config from environment"""
        import os
        return cls(
            enabled=os.getenv("LED_ENABLED", "true").lower() == "true",
            pin=int(os.getenv("LED_PIN", "18")),
            num_leds=int(os.getenv("LED_NUM", "16")),
            brightness=float(os.getenv("LED_BRIGHTNESS", "0.3")),
        )


class LedController:
    """
    WS2812B LED controller for status indication

    Usage:
        led = LedController(config)
        await led.start()

        led.set_status(LedStatus.CONNECTING)
        led.set_status(LedStatus.STREAMING)
        led.show_sound_direction(angle=-30)  # Sound from left

        await led.stop()
    """

    def __init__(self, config: Optional[LedConfig] = None):
        self.config = config or LedConfig()
        self.pixels = None
        self.running = False
        self._status = LedStatus.OFF
        self._sound_direction: Optional[float] = None
        self._sound_intensity: float = 0.0
        self._animation_task: Optional[asyncio.Task] = None

    async def start(self):
        """Initialize LED strip"""
        if not self.config.enabled:
            logger.info("LED controller disabled")
            return

        if not NEOPIXEL_AVAILABLE:
            logger.warning("NeoPixel not available - running in simulation mode")
            self.running = True
            self._animation_task = asyncio.create_task(self._animation_loop())
            return

        try:
            # Initialize NeoPixel
            pin = getattr(board, f"D{self.config.pin}")
            self.pixels = neopixel.NeoPixel(
                pin,
                self.config.num_leds,
                brightness=self.config.brightness,
                auto_write=False
            )
            self.pixels.fill((0, 0, 0))
            self.pixels.show()

            self.running = True
            self._animation_task = asyncio.create_task(self._animation_loop())

            logger.info(f"LED controller started: {self.config.num_leds} LEDs on GPIO{self.config.pin}")

        except Exception as e:
            logger.error(f"Failed to initialize LEDs: {e}")

    async def stop(self):
        """Stop LED controller"""
        self.running = False

        if self._animation_task:
            self._animation_task.cancel()
            try:
                await self._animation_task
            except asyncio.CancelledError:
                pass

        if self.pixels:
            self.pixels.fill((0, 0, 0))
            self.pixels.show()

        logger.info("LED controller stopped")

    def set_status(self, status: LedStatus):
        """Set current status"""
        self._status = status
        logger.debug(f"LED status: {status.value}")

    def show_sound_direction(self, angle: float, intensity: float = 1.0):
        """
        Show sound direction on LED ring

        Args:
            angle: Direction in degrees (-180 to 180, 0 = front)
            intensity: Sound intensity 0.0 - 1.0
        """
        self._sound_direction = angle
        self._sound_intensity = intensity

    def clear_sound_direction(self):
        """Clear sound direction indicator"""
        self._sound_direction = None
        self._sound_intensity = 0.0

    async def _animation_loop(self):
        """Main animation loop"""
        frame = 0

        while self.running:
            try:
                await self._render_frame(frame)
                frame += 1
                await asyncio.sleep(0.033)  # ~30 FPS

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Animation error: {e}")
                await asyncio.sleep(0.1)

    async def _render_frame(self, frame: int):
        """Render single animation frame"""

        if not self.config.enabled:
            return

        num_leds = self.config.num_leds
        colors = [(0, 0, 0)] * num_leds

        # Base status animation
        if self._status == LedStatus.OFF:
            pass  # All off

        elif self._status == LedStatus.CONNECTING:
            # Orange breathing/pulse
            brightness = (math.sin(frame * 0.1) + 1) / 2
            color = self._scale_color(self.config.color_connecting, brightness)
            colors = [color] * num_leds

        elif self._status == LedStatus.CONNECTED:
            # Blue solid
            colors = [self.config.color_connected] * num_leds

        elif self._status == LedStatus.STREAMING:
            # Green with subtle pulse
            brightness = 0.7 + 0.3 * (math.sin(frame * 0.05) + 1) / 2
            color = self._scale_color(self.config.color_streaming, brightness)
            colors = [color] * num_leds

        elif self._status == LedStatus.ERROR:
            # Red blink
            on = (frame // 15) % 2 == 0
            if on:
                colors = [self.config.color_error] * num_leds

        elif self._status == LedStatus.AUDIO_ACTIVE:
            # Blue pulse
            brightness = (math.sin(frame * 0.2) + 1) / 2
            color = self._scale_color(self.config.color_audio, brightness)
            colors = [color] * num_leds

        # Overlay sound direction if available
        if self._sound_direction is not None and self._sound_intensity > 0.1:
            colors = self._overlay_direction(colors, frame)

        # Apply to LEDs
        if self.pixels:
            for i, color in enumerate(colors):
                self.pixels[i] = color
            self.pixels.show()
        else:
            # Simulation mode - log occasionally
            if frame % 30 == 0:
                logger.debug(f"LED sim: status={self._status.value}, color={colors[0]}")

    def _overlay_direction(
        self,
        base_colors: list,
        frame: int
    ) -> list:
        """Overlay sound direction on base colors"""

        num_leds = self.config.num_leds
        colors = list(base_colors)

        # Convert angle to LED position
        # 0° = front (top of ring), -90° = left, 90° = right
        angle = self._sound_direction

        # Map angle to LED index (assuming ring layout)
        # LED 0 = front, increases clockwise
        led_pos = (angle / 360.0 * num_leds + num_leds / 2) % num_leds

        # Create gradient around target position
        for i in range(num_leds):
            # Distance from target LED
            dist = min(
                abs(i - led_pos),
                num_leds - abs(i - led_pos)
            )

            # Intensity falls off with distance
            intensity = max(0, 1 - dist / (num_leds / 4))
            intensity *= self._sound_intensity

            # Pulse effect
            pulse = 0.7 + 0.3 * math.sin(frame * 0.15)
            intensity *= pulse

            if intensity > 0:
                # Blend with audio color
                audio_color = self._scale_color(
                    self.config.color_audio,
                    intensity
                )
                colors[i] = self._blend_colors(colors[i], audio_color, intensity)

        return colors

    def _scale_color(
        self,
        color: Tuple[int, int, int],
        factor: float
    ) -> Tuple[int, int, int]:
        """Scale color brightness"""
        return tuple(int(c * factor) for c in color)

    def _blend_colors(
        self,
        color1: Tuple[int, int, int],
        color2: Tuple[int, int, int],
        factor: float
    ) -> Tuple[int, int, int]:
        """Blend two colors"""
        return tuple(
            int(c1 * (1 - factor) + c2 * factor)
            for c1, c2 in zip(color1, color2)
        )


# Convenience functions for quick status updates
_controller: Optional[LedController] = None

def get_controller() -> Optional[LedController]:
    """Get global LED controller instance"""
    return _controller

def set_controller(controller: LedController):
    """Set global LED controller instance"""
    global _controller
    _controller = controller

def status(s: LedStatus):
    """Quick status update"""
    if _controller:
        _controller.set_status(s)

def sound_direction(angle: float, intensity: float = 1.0):
    """Quick sound direction update"""
    if _controller:
        _controller.show_sound_direction(angle, intensity)
