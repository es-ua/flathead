"""
FLATHEAD LED Status Controller

Dual WS2812B rings for stereo camera status indication.

Hardware:
    - 2x WS2812B 8-LED rings (one per camera)
    - Left ring: GPIO18 (PWM0)
    - Right ring: GPIO12 (PWM0 alt) or GPIO13 (PWM1)
    - Daisy-chain option: both rings on GPIO18

Statuses:
    - OFF: System idle
    - CONNECTING: Orange pulse - connecting to server
    - STREAMING: Green solid - actively streaming
    - ERROR: Red blink - connection error
    - AUDIO_ACTIVE: Blue pulse overlay - sound detected
"""

import asyncio
import logging
import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Tuple, List

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


class CameraStatus(Enum):
    """Individual camera status"""
    OFF = "off"
    ACTIVE = "active"
    ERROR = "error"


@dataclass
class DualRingConfig:
    """Configuration for dual LED rings"""
    enabled: bool = True

    # Ring configuration
    # Option 1: Daisy-chained (both on one pin)
    # Option 2: Separate pins (independent control)
    daisy_chain: bool = True  # True = one pin, False = two pins

    # GPIO pins (PWM capable)
    pin_left: int = 18   # GPIO18 - PWM0
    pin_right: int = 12  # GPIO12 - PWM0 (alt) or 13 for PWM1

    # LEDs per ring
    leds_per_ring: int = 8

    # Brightness
    brightness: float = 0.3

    # Colors (RGB)
    color_off: Tuple[int, int, int] = (0, 0, 0)
    color_connecting: Tuple[int, int, int] = (255, 165, 0)   # Orange
    color_connected: Tuple[int, int, int] = (0, 100, 255)    # Blue
    color_streaming: Tuple[int, int, int] = (0, 255, 0)      # Green
    color_error: Tuple[int, int, int] = (255, 0, 0)          # Red
    color_audio: Tuple[int, int, int] = (0, 150, 255)        # Cyan-blue
    color_camera_active: Tuple[int, int, int] = (255, 255, 255)  # White accent

    @classmethod
    def from_env(cls) -> "DualRingConfig":
        """Load config from environment"""
        import os
        return cls(
            enabled=os.getenv("LED_ENABLED", "true").lower() == "true",
            daisy_chain=os.getenv("LED_DAISY_CHAIN", "true").lower() == "true",
            pin_left=int(os.getenv("LED_PIN_LEFT", "18")),
            pin_right=int(os.getenv("LED_PIN_RIGHT", "12")),
            leds_per_ring=int(os.getenv("LED_PER_RING", "8")),
            brightness=float(os.getenv("LED_BRIGHTNESS", "0.3")),
        )


# Keep old config for backwards compatibility
LedConfig = DualRingConfig


class DualRingController:
    """
    Dual WS2812B LED ring controller for stereo cameras

    Layout (daisy-chained):
        Ring 0 (Left camera):  LEDs 0-7
        Ring 1 (Right camera): LEDs 8-15

    Usage:
        led = DualRingController(config)
        await led.start()

        led.set_status(LedStatus.STREAMING)
        led.set_camera_status("left", CameraStatus.ACTIVE)
        led.show_sound_direction(angle=-30)  # Sound from left

        await led.stop()
    """

    def __init__(self, config: Optional[DualRingConfig] = None):
        self.config = config or DualRingConfig()
        self.pixels_left = None
        self.pixels_right = None
        self.pixels_combined = None  # For daisy-chain mode
        self.running = False

        # Global status
        self._status = LedStatus.OFF

        # Per-camera status
        self._camera_left = CameraStatus.OFF
        self._camera_right = CameraStatus.OFF

        # Sound direction
        self._sound_direction: Optional[float] = None
        self._sound_intensity: float = 0.0

        # Animation
        self._animation_task: Optional[asyncio.Task] = None

    @property
    def num_leds(self) -> int:
        """Total number of LEDs"""
        return self.config.leds_per_ring * 2

    async def start(self):
        """Initialize LED rings"""
        if not self.config.enabled:
            logger.info("LED controller disabled")
            return

        if not NEOPIXEL_AVAILABLE:
            logger.warning("NeoPixel not available - running in simulation mode")
            self.running = True
            self._animation_task = asyncio.create_task(self._animation_loop())
            return

        try:
            if self.config.daisy_chain:
                # Both rings on one pin (daisy-chained)
                pin = getattr(board, f"D{self.config.pin_left}")
                self.pixels_combined = neopixel.NeoPixel(
                    pin,
                    self.num_leds,
                    brightness=self.config.brightness,
                    auto_write=False
                )
                self.pixels_combined.fill((0, 0, 0))
                self.pixels_combined.show()
                logger.info(f"Dual LED rings (daisy-chain): {self.num_leds} LEDs on GPIO{self.config.pin_left}")
            else:
                # Separate pins for each ring
                pin_left = getattr(board, f"D{self.config.pin_left}")
                pin_right = getattr(board, f"D{self.config.pin_right}")

                self.pixels_left = neopixel.NeoPixel(
                    pin_left,
                    self.config.leds_per_ring,
                    brightness=self.config.brightness,
                    auto_write=False
                )
                self.pixels_right = neopixel.NeoPixel(
                    pin_right,
                    self.config.leds_per_ring,
                    brightness=self.config.brightness,
                    auto_write=False
                )

                self.pixels_left.fill((0, 0, 0))
                self.pixels_right.fill((0, 0, 0))
                self.pixels_left.show()
                self.pixels_right.show()

                logger.info(f"Dual LED rings: Left=GPIO{self.config.pin_left}, Right=GPIO{self.config.pin_right}")

            self.running = True
            self._animation_task = asyncio.create_task(self._animation_loop())

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

        # Turn off all LEDs
        if self.pixels_combined:
            self.pixels_combined.fill((0, 0, 0))
            self.pixels_combined.show()
        if self.pixels_left:
            self.pixels_left.fill((0, 0, 0))
            self.pixels_left.show()
        if self.pixels_right:
            self.pixels_right.fill((0, 0, 0))
            self.pixels_right.show()

        logger.info("LED controller stopped")

    def set_status(self, status: LedStatus):
        """Set global status for both rings"""
        self._status = status
        logger.debug(f"LED status: {status.value}")

    def set_camera_status(self, camera: str, status: CameraStatus):
        """Set individual camera status"""
        if camera == "left":
            self._camera_left = status
        elif camera == "right":
            self._camera_right = status
        logger.debug(f"Camera {camera} status: {status.value}")

    def show_sound_direction(self, angle: float, intensity: float = 1.0):
        """
        Show sound direction across both rings

        Args:
            angle: Direction in degrees (-180 to 180, 0 = front)
                   Negative = left, Positive = right
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

        n = self.config.leds_per_ring

        # Generate colors for each ring
        colors_left = self._render_ring(frame, "left")
        colors_right = self._render_ring(frame, "right")

        # Apply sound direction overlay
        if self._sound_direction is not None and self._sound_intensity > 0.1:
            colors_left, colors_right = self._overlay_sound_direction(
                colors_left, colors_right, frame
            )

        # Apply to hardware
        if self.pixels_combined:
            # Daisy-chain mode: left ring first, then right
            for i, color in enumerate(colors_left):
                self.pixels_combined[i] = color
            for i, color in enumerate(colors_right):
                self.pixels_combined[n + i] = color
            self.pixels_combined.show()

        elif self.pixels_left and self.pixels_right:
            # Separate pins mode
            for i, color in enumerate(colors_left):
                self.pixels_left[i] = color
            for i, color in enumerate(colors_right):
                self.pixels_right[i] = color
            self.pixels_left.show()
            self.pixels_right.show()

        else:
            # Simulation mode
            if frame % 30 == 0:
                logger.debug(f"LED sim: status={self._status.value}, L={colors_left[0]}, R={colors_right[0]}")

    def _render_ring(self, frame: int, side: str) -> List[Tuple[int, int, int]]:
        """Render colors for one ring"""
        n = self.config.leds_per_ring
        colors = [(0, 0, 0)] * n

        # Get camera status for this side
        cam_status = self._camera_left if side == "left" else self._camera_right

        # Base color from global status
        if self._status == LedStatus.OFF:
            return colors

        elif self._status == LedStatus.CONNECTING:
            # Orange breathing pulse
            brightness = (math.sin(frame * 0.1) + 1) / 2
            color = self._scale_color(self.config.color_connecting, brightness)
            colors = [color] * n

        elif self._status == LedStatus.CONNECTED:
            # Blue solid
            colors = [self.config.color_connected] * n

        elif self._status == LedStatus.STREAMING:
            # Green with gentle pulse
            brightness = 0.7 + 0.3 * (math.sin(frame * 0.05) + 1) / 2
            color = self._scale_color(self.config.color_streaming, brightness)
            colors = [color] * n

            # Add white accent for active camera
            if cam_status == CameraStatus.ACTIVE:
                # Rotating white dot
                dot_pos = (frame // 4) % n
                colors[dot_pos] = self.config.color_camera_active

        elif self._status == LedStatus.ERROR:
            # Red blink
            on = (frame // 15) % 2 == 0
            if on:
                colors = [self.config.color_error] * n

        elif self._status == LedStatus.AUDIO_ACTIVE:
            # Blue pulse
            brightness = (math.sin(frame * 0.2) + 1) / 2
            color = self._scale_color(self.config.color_audio, brightness)
            colors = [color] * n

        # Camera-specific error override
        if cam_status == CameraStatus.ERROR:
            # Half the ring shows error
            for i in range(n // 2):
                colors[i] = self.config.color_error

        return colors

    def _overlay_sound_direction(
        self,
        colors_left: List[Tuple[int, int, int]],
        colors_right: List[Tuple[int, int, int]],
        frame: int
    ) -> Tuple[List, List]:
        """Overlay sound direction indicator on both rings"""

        angle = self._sound_direction
        intensity = self._sound_intensity
        n = self.config.leds_per_ring

        # Pulse effect
        pulse = 0.6 + 0.4 * math.sin(frame * 0.15)

        # Determine which ring should be brighter based on angle
        # angle < 0 = sound from left
        # angle > 0 = sound from right

        if angle < -30:  # Sound from left
            left_intensity = intensity * pulse
            right_intensity = intensity * pulse * 0.3
        elif angle > 30:  # Sound from right
            left_intensity = intensity * pulse * 0.3
            right_intensity = intensity * pulse
        else:  # Sound from front (both rings equal)
            left_intensity = intensity * pulse * 0.7
            right_intensity = intensity * pulse * 0.7

        # Apply to rings
        audio_color = self.config.color_audio

        for i in range(n):
            if left_intensity > 0:
                colors_left[i] = self._blend_colors(
                    colors_left[i],
                    self._scale_color(audio_color, left_intensity),
                    left_intensity * 0.5
                )
            if right_intensity > 0:
                colors_right[i] = self._blend_colors(
                    colors_right[i],
                    self._scale_color(audio_color, right_intensity),
                    right_intensity * 0.5
                )

        return colors_left, colors_right

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


# Backwards compatibility alias
LedController = DualRingController


# Global controller instance
_controller: Optional[DualRingController] = None


def get_controller() -> Optional[DualRingController]:
    """Get global LED controller instance"""
    return _controller


def set_controller(controller: DualRingController):
    """Set global LED controller instance"""
    global _controller
    _controller = controller


def status(s: LedStatus):
    """Quick status update"""
    if _controller:
        _controller.set_status(s)


def camera_status(camera: str, s: CameraStatus):
    """Quick camera status update"""
    if _controller:
        _controller.set_camera_status(camera, s)


def sound_direction(angle: float, intensity: float = 1.0):
    """Quick sound direction update"""
    if _controller:
        _controller.show_sound_direction(angle, intensity)
