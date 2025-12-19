# FLATHEAD ROBOT - Wiring Guide

Complete wiring documentation for all components.

---

## Overview

```
+-------------------------------------------------------------------+
|                     FLATHEAD v2.5 WIRING                          |
+-------------------------------------------------------------------+
|                                                                   |
|  RASPBERRY PI 5 INTERFACES:                                       |
|                                                                   |
|    I2C Bus:                                                       |
|      - 3x TCA9548A multiplexers (22x INA219 sensors)              |
|      - 2x PCA9685 PWM drivers (22 servos)                         |
|      - 1x BNO055 IMU                                              |
|                                                                   |
|    I2S Bus:                                                       |
|      - 4x INMP441 microphones (2 per bus)                         |
|                                                                   |
|    UART:                                                          |
|      - 1x u-blox GPS module                                       |
|                                                                   |
|    USB:                                                           |
|      - 1x RPLIDAR A1M8                                            |
|                                                                   |
|    CSI:                                                           |
|      - 2x Pi Camera v3 (stereo on head)                           |
|                                                                   |
|    GPIO:                                                          |
|      - 4x Foot contact switches                                   |
|      - 4x Motor encoder inputs                                    |
|      - Motor driver control signals                               |
|      - Audio amplifier PWM                                        |
|                                                                   |
+-------------------------------------------------------------------+
```

---

## Raspberry Pi 5 GPIO Pinout

```
                    Raspberry Pi 5 GPIO Header
                    ==========================

        3V3  (1)  (2)  5V
      GPIO2  (3)  (4)  5V
      GPIO3  (5)  (6)  GND
      GPIO4  (7)  (8)  GPIO14 (UART TX)
        GND  (9)  (10) GPIO15 (UART RX)
     GPIO17 (11)  (12) GPIO18 (I2S CLK)
     GPIO27 (13)  (14) GND
     GPIO22 (15)  (16) GPIO23
        3V3 (17)  (18) GPIO24
     GPIO10 (19)  (20) GND
      GPIO9 (21)  (22) GPIO25
     GPIO11 (23)  (24) GPIO8
        GND (25)  (26) GPIO7
      GPIO0 (27)  (28) GPIO1
      GPIO5 (29)  (30) GND
      GPIO6 (31)  (32) GPIO12
     GPIO13 (33)  (34) GND
     GPIO19 (35)  (36) GPIO16
     GPIO26 (37)  (38) GPIO20 (I2S DIN)
        GND (39)  (40) GPIO21 (I2S DOUT)


    ACTIVE PINS FOR FLATHEAD:
    =========================

    I2C (Bus 1):
      GPIO2 (SDA) - Pin 3
      GPIO3 (SCL) - Pin 5

    I2S (Bus 0 - Mics 1&2):
      GPIO18 (CLK) - Pin 12
      GPIO19 (FS)  - Pin 35
      GPIO20 (DIN) - Pin 38

    I2S (Bus 1 - Mics 3&4):
      GPIO12 (CLK) - Pin 32
      GPIO13 (FS)  - Pin 33
      GPIO21 (DIN) - Pin 40

    UART (GPS):
      GPIO14 (TX) - Pin 8
      GPIO15 (RX) - Pin 10

    Motor Driver (BTS7960):
      GPIO5  (RPWM_A) - Pin 29  - Motor FL
      GPIO6  (LPWM_A) - Pin 31
      GPIO16 (RPWM_B) - Pin 36  - Motor FR
      GPIO17 (LPWM_B) - Pin 11
      GPIO22 (RPWM_C) - Pin 15  - Motor BL
      GPIO23 (LPWM_C) - Pin 16
      GPIO24 (RPWM_D) - Pin 18  - Motor BR
      GPIO25 (LPWM_D) - Pin 22

    Foot Switches:
      GPIO4  - Pin 7   - FL foot
      GPIO27 - Pin 13  - FR foot
      GPIO10 - Pin 19  - BL foot
      GPIO9  - Pin 21  - BR foot

    Audio Amplifier:
      GPIO26 (PWM) - Pin 37

    Motor Encoders:
      GPIO7  - Pin 26  - FL encoder A
      GPIO8  - Pin 24  - FL encoder B
      GPIO11 - Pin 23  - FR encoder A
      GPIO0  - Pin 27  - FR encoder B
      GPIO1  - Pin 28  - BL encoder A
      (use I2C GPIO expander for remaining)
```

---

## 1. AUDIO SYSTEM - INMP441 Microphones

### Microphone Placement

```
                    FLATHEAD TOP VIEW
                    =================

                      [FRONT]
                         ^
                         |
              +----------+----------+
              |    Mic 1 (FL)       |
              |       o             |
              |                     |
    Mic 3 o   |      [BODY]        |   o Mic 4
    (Left)    |                     |   (Right)
              |                     |
              |       o             |
              |    Mic 2 (FR)       |
              +----------+----------+
                         |
                         v
                      [REAR]


    Purpose:
      - Mic 1 + Mic 2: Front stereo (voice detection)
      - Mic 3 + Mic 4: Side stereo (sound localization)
```

### I2S Bus 0 - Front Microphones (Mic 1 & 2)

```
    INMP441 #1 (Front Left)          Raspberry Pi 5
    =======================          ==============

         VDD ─────────────────────── 3.3V (Pin 17)
         GND ─────────────────────── GND (Pin 14)
         SCK ─────────────────────── GPIO18 (Pin 12)
         WS  ─────────────────────── GPIO19 (Pin 35)
         SD  ─────────────────────── GPIO20 (Pin 38)
         L/R ─────────────────────── GND (Left channel)


    INMP441 #2 (Front Right)         Raspberry Pi 5
    ========================         ==============

         VDD ─────────────────────── 3.3V (Pin 17)
         GND ─────────────────────── GND (Pin 14)
         SCK ─────────────────────── GPIO18 (Pin 12)  [shared]
         WS  ─────────────────────── GPIO19 (Pin 35)  [shared]
         SD  ─────────────────────── GPIO20 (Pin 38)  [shared]
         L/R ─────────────────────── 3.3V (Right channel)
```

### I2S Bus 1 - Side Microphones (Mic 3 & 4)

```
    INMP441 #3 (Left Side)           Raspberry Pi 5
    ======================           ==============

         VDD ─────────────────────── 3.3V (Pin 1)
         GND ─────────────────────── GND (Pin 34)
         SCK ─────────────────────── GPIO12 (Pin 32)
         WS  ─────────────────────── GPIO13 (Pin 33)
         SD  ─────────────────────── GPIO21 (Pin 40)
         L/R ─────────────────────── GND (Left channel)


    INMP441 #4 (Right Side)          Raspberry Pi 5
    =======================          ==============

         VDD ─────────────────────── 3.3V (Pin 1)
         GND ─────────────────────── GND (Pin 34)
         SCK ─────────────────────── GPIO12 (Pin 32)  [shared]
         WS  ─────────────────────── GPIO13 (Pin 33)  [shared]
         SD  ─────────────────────── GPIO21 (Pin 40)  [shared]
         L/R ─────────────────────── 3.3V (Right channel)
```

### Enable Second I2S Bus

Add to `/boot/firmware/config.txt`:
```
# Enable second I2S interface
dtoverlay=i2s-gpio28-31
# Or use software I2S on GPIO 12,13,21
dtoverlay=hifiberry-dac
```

### Audio Output - PAM8403 Amplifier

```
    PAM8403 Amplifier                Raspberry Pi 5
    =================                ==============

         VCC ─────────────────────── 5V (Pin 2)
         GND ─────────────────────── GND (Pin 6)
         INL ─────────────────────── GPIO26 (Pin 37) via RC filter
         INR ─────────────────────── GPIO26 (Pin 37) via RC filter

    RC Filter (for PWM to audio):
         GPIO26 ──┬── 1kΩ ──┬── INL/INR
                  │         │
                 10kΩ      10µF
                  │         │
                 GND       GND


    Speaker Connection:
         OUT L+ ──────── Speaker + (4Ω 3W)
         OUT L- ──────── Speaker -
```

---

## 2. I2C BUS - Sensors & Controllers

### I2C Address Map

```
    I2C Bus 1 (GPIO2/GPIO3)
    =======================

    Address   Device              Notes
    -------   ------              -----
    0x40      PCA9685 #1          Servos 0-15 (Legs FL, FR)
    0x41      PCA9685 #2          Servos 0-15 (Legs BL, BR, Head)
    0x28      BNO055 IMU          9-axis orientation
    0x70      TCA9548A #1         Mux for FL leg sensors
    0x71      TCA9548A #2         Mux for FR leg sensors
    0x72      TCA9548A #3         Mux for BL, BR, Head sensors


    TCA9548A #1 (0x70) - FL Leg
    ---------------------------
    Channel 0: INA219 @ 0x40 - Hip Abduction servo
    Channel 1: INA219 @ 0x40 - Hip Flexion servo
    Channel 2: INA219 @ 0x40 - Knee servo
    Channel 3: INA219 @ 0x40 - Ankle servo
    Channel 4: INA219 @ 0x40 - Swivel servo

    TCA9548A #2 (0x71) - FR Leg
    ---------------------------
    Channel 0: INA219 @ 0x40 - Hip Abduction servo
    Channel 1: INA219 @ 0x40 - Hip Flexion servo
    Channel 2: INA219 @ 0x40 - Knee servo
    Channel 3: INA219 @ 0x40 - Ankle servo
    Channel 4: INA219 @ 0x40 - Swivel servo

    TCA9548A #3 (0x72) - BL, BR, Head
    ---------------------------------
    Channel 0: INA219 @ 0x40 - BL Hip Abduction
    Channel 1: INA219 @ 0x40 - BL Hip Flexion
    Channel 2: INA219 @ 0x40 - BL Knee
    Channel 3: INA219 @ 0x40 - BL Ankle
    Channel 4: INA219 @ 0x40 - BL Swivel
    Channel 5: INA219 @ 0x41 - BR Hip Abduction (alt addr)
    Channel 6: INA219 @ 0x41 - BR remaining + Head Pan
    Channel 7: INA219 @ 0x41 - BR remaining + Head Tilt
```

### I2C Wiring Diagram

```
    Raspberry Pi 5                    I2C Devices
    ==============                    ===========

                                   +-------------+
    GPIO2 (SDA) ──────┬────────────│ PCA9685 #1  │ (0x40)
    GPIO3 (SCL) ──────┼──┬─────────│ SDA    SCL  │
                      │  │         +-------------+
                      │  │
                      │  │         +-------------+
                      ├──┼─────────│ PCA9685 #2  │ (0x41)
                      │  │         │ SDA    SCL  │
                      │  │         +-------------+
                      │  │
                      │  │         +-------------+
                      ├──┼─────────│ BNO055 IMU  │ (0x28)
                      │  │         │ SDA    SCL  │
                      │  │         +-------------+
                      │  │
                      │  │         +-------------+
                      ├──┼─────────│ TCA9548A #1 │ (0x70)
                      │  │         │ SDA    SCL  │──── 5x INA219
                      │  │         +-------------+
                      │  │
                      │  │         +-------------+
                      ├──┼─────────│ TCA9548A #2 │ (0x71)
                      │  │         │ SDA    SCL  │──── 5x INA219
                      │  │         +-------------+
                      │  │
                      │  │         +-------------+
                      └──┴─────────│ TCA9548A #3 │ (0x72)
                                   │ SDA    SCL  │──── 12x INA219
                                   +-------------+

    Pull-up resistors: 4.7kΩ on SDA and SCL lines
    (may already be on Pi or breakout boards)
```

### INA219 Current Sensor Wiring (per servo)

```
    Servo Power Path with INA219
    ============================

    7.4V Rail ───┬─── INA219 VIN+ ────┐
                 │                     │
                 │    INA219 VIN- ─────┼─── Servo V+
                 │         │           │
                 │        GND          │
                 │         │           │
    GND ─────────┴─────────┴───────────┴─── Servo GND


    INA219 Module Connections:
    ==========================

         VCC ──────── 3.3V
         GND ──────── GND
         SDA ──────── TCA9548A channel SDA
         SCL ──────── TCA9548A channel SCL
         VIN+ ─────── Power source (7.4V)
         VIN- ─────── Servo V+ (measurement point)
```

---

## 3. SERVO SYSTEM - PCA9685 PWM Drivers

### PCA9685 #1 - Front Legs (Address 0x40)

```
    PCA9685 #1 Pin Assignments
    ==========================

    Channel   Servo                   Leg
    -------   -----                   ---
    0         Hip Abduction           FL
    1         Hip Flexion             FL
    2         Knee                    FL
    3         Ankle                   FL
    4         Swivel                  FL
    5         Hip Abduction           FR
    6         Hip Flexion             FR
    7         Knee                    FR
    8         Ankle                   FR
    9         Swivel                  FR
    10-15     (unused/spare)


    Wiring:
    =======

         VCC ──────── 3.3V (logic)
         GND ──────── GND
         SDA ──────── GPIO2 (Pin 3)
         SCL ──────── GPIO3 (Pin 5)
         OE  ──────── GND (always enabled)
         V+  ──────── 7.4V (from buck converter)

    Address Selection:
         A0 ──────── GND
         A1 ──────── GND
         A2 ──────── GND
         A3 ──────── GND
         A4 ──────── GND
         = Address 0x40
```

### PCA9685 #2 - Rear Legs + Head (Address 0x41)

```
    PCA9685 #2 Pin Assignments
    ==========================

    Channel   Servo                   Leg/Part
    -------   -----                   --------
    0         Hip Abduction           BL
    1         Hip Flexion             BL
    2         Knee                    BL
    3         Ankle                   BL
    4         Swivel                  BL
    5         Hip Abduction           BR
    6         Hip Flexion             BR
    7         Knee                    BR
    8         Ankle                   BR
    9         Swivel                  BR
    10        Pan servo               Head
    11        Tilt servo              Head
    12-15     (unused/spare)


    Address Selection:
         A0 ──────── 3.3V  (set bit)
         A1 ──────── GND
         A2 ──────── GND
         A3 ──────── GND
         A4 ──────── GND
         = Address 0x41
```

### DS3218 Servo Wiring

```
    DS3218 Servo Cable Colors:
    ==========================

    Brown  ──────── GND
    Red    ──────── V+ (7.4V)
    Orange ──────── PWM Signal (to PCA9685 channel)


    PWM Settings for DS3218:
    ========================

    Frequency: 50Hz (20ms period)
    Pulse width:
      - 500µs  = 0°   (min position)
      - 1500µs = 90°  (center)
      - 2500µs = 180° (max position)
```

---

## 4. MOTOR SYSTEM - BTS7960 Driver

### BTS7960 Wiring (4-Channel Configuration)

```
    BTS7960 Module Connections
    ==========================

    Motor FL (Front Left):
    ----------------------
         RPWM ──────── GPIO5  (Pin 29)
         LPWM ──────── GPIO6  (Pin 31)
         R_EN ──────── 3.3V (always enabled)
         L_EN ──────── 3.3V (always enabled)
         VCC  ──────── 5V
         GND  ──────── GND
         B+   ──────── 12V Battery
         B-   ──────── GND
         M+   ──────── Motor FL +
         M-   ──────── Motor FL -

    Motor FR (Front Right):
    -----------------------
         RPWM ──────── GPIO16 (Pin 36)
         LPWM ──────── GPIO17 (Pin 11)
         (other connections same pattern)
         M+   ──────── Motor FR +
         M-   ──────── Motor FR -

    Motor BL (Back Left):
    ---------------------
         RPWM ──────── GPIO22 (Pin 15)
         LPWM ──────── GPIO23 (Pin 16)
         M+   ──────── Motor BL +
         M-   ──────── Motor BL -

    Motor BR (Back Right):
    ----------------------
         RPWM ──────── GPIO24 (Pin 18)
         LPWM ──────── GPIO25 (Pin 22)
         M+   ──────── Motor BR +
         M-   ──────── Motor BR -


    Control Logic:
    ==============
    Forward:  RPWM=PWM, LPWM=LOW
    Reverse:  RPWM=LOW, LPWM=PWM
    Brake:    RPWM=HIGH, LPWM=HIGH
    Coast:    RPWM=LOW, LPWM=LOW
```

### Motor Encoder Wiring (JGA25-370)

```
    JGA25-370 Encoder Connections
    =============================

    Motor FL:
         Encoder VCC ──────── 3.3V
         Encoder GND ──────── GND
         Encoder A   ──────── GPIO7  (Pin 26)
         Encoder B   ──────── GPIO8  (Pin 24)

    Motor FR:
         Encoder A   ──────── GPIO11 (Pin 23)
         Encoder B   ──────── GPIO0  (Pin 27)

    Motor BL:
         Encoder A   ──────── GPIO1  (Pin 28)
         Encoder B   ──────── (via MCP23017 GPIO expander)

    Motor BR:
         Encoder A   ──────── (via MCP23017 GPIO expander)
         Encoder B   ──────── (via MCP23017 GPIO expander)


    Note: Pi 5 has limited GPIO. Use MCP23017 I2C GPIO
    expander for additional encoder inputs if needed.
```

---

## 5. NAVIGATION SENSORS

### BNO055 IMU

```
    BNO055 Connections
    ==================

         VIN ──────── 3.3V
         GND ──────── GND
         SDA ──────── GPIO2 (Pin 3)
         SCL ──────── GPIO3 (Pin 5)
         RST ──────── 3.3V (not reset)
         INT ──────── (optional) GPIO interrupt

    I2C Address: 0x28 (default)

    Mounting:
      - Center of robot body
      - Aligned with robot axes
      - X forward, Y left, Z up
```

### u-blox SAM-M10Q GPS

```
    GPS Module Connections
    ======================

         VCC ──────── 3.3V
         GND ──────── GND
         TX  ──────── GPIO15 (Pin 10) - Pi RX
         RX  ──────── GPIO14 (Pin 8)  - Pi TX
         PPS ──────── (optional) GPIO for precise timing

    UART Settings:
      - Baud: 9600 (default) or 115200
      - 8N1 format

    Enable UART on Pi:
      Add to /boot/firmware/config.txt:
      enable_uart=1
```

### RPLIDAR A1M8

```
    RPLIDAR Connections
    ===================

         5V   ──────── 5V (USB or direct)
         GND  ──────── GND
         TX   ──────── USB (via included adapter)
         RX   ──────── USB
         MCTL ──────── (motor control, via USB)

    Connection: USB to Pi 5 USB port

    Device: /dev/ttyUSB0 (typically)
```

---

## 6. VISION SYSTEM - Pi Cameras

### Stereo Camera Setup on Head

```
    Camera Connections
    ==================

    Camera Left (CAM0):
         Ribbon cable ──────── Pi 5 CAM0 connector

    Camera Right (CAM1):
         Ribbon cable ──────── Pi 5 CAM1 connector


    Head Servo Mounting:
    ====================

                    +------------------+
                    |    Camera L      |
                    |       [ ]        |
                    +--------+---------+
                             |
              +--------------+--------------+
              |         Pan Servo           |
              |        (MG996R #1)          |
              +--------------+--------------+
                             |
              +--------------+--------------+
              |        Tilt Servo           |
              |        (MG996R #2)          |
              +--------------+--------------+
                             |
                    +--------+---------+
                    |    Camera R      |
                    |       [ ]        |
                    +------------------+


    Stereo baseline: ~6-8cm between cameras
```

---

## 7. STATUS LED RINGS (2× WS2812B 8-LED)

```
    Dual WS2812B 8-LED Rings (one per camera)
    =========================================

    Left camera ring:  8 LEDs
    Right camera ring: 8 LEDs
    Total: 16 LEDs


    OPTION 1: Daisy-Chain (Recommended)
    ===================================

    Both rings connected in series on one GPIO pin:

         Pi 5                Ring 1 (Left)      Ring 2 (Right)
         ====                =============      ==============

         GPIO18 (Pin 12) ──── DIN
                              DOUT ──────────── DIN
                                                DOUT (unused)

         5V     (Pin 4)  ──── VCC ─────────── VCC
         GND    (Pin 6)  ──── GND ─────────── GND


    Wiring Diagram:
    ===============

                    ┌─────────────┐     ┌─────────────┐
         GPIO18 ────┤ DIN    DOUT ├─────┤ DIN    DOUT ├──(nc)
                    │             │     │             │
           5V   ────┤ VCC         │     │ VCC         │
                    │   [LEFT]    │     │   [RIGHT]   │
          GND   ────┤ GND         │     │ GND         │
                    │  CAMERA     │     │  CAMERA     │
                    └─────────────┘     └─────────────┘
                      LEDs 0-7           LEDs 8-15


    OPTION 2: Separate Pins
    =======================

    Each ring on its own GPIO (independent control):

         GPIO18 (Pin 12) ──── DIN (Left ring)
         GPIO12 (Pin 32) ──── DIN (Right ring)
         5V     (Pin 4)  ──── VCC (both)
         GND    (Pin 6)  ──── GND (both)


    Physical Mounting:
    ==================

         ┌─────────────────────────────────────┐
         │           ROBOT HEAD                │
         │                                     │
         │   ┌───────┐           ┌───────┐    │
         │   │○○○○○○○│           │○○○○○○○│    │
         │   │○┌───┐○│           │○┌───┐○│    │
         │   │○│CAM│○│           │○│CAM│○│    │
         │   │○│ L │○│           │○│ R │○│    │
         │   │○└───┘○│           │○└───┘○│    │
         │   │○○○○○○○│           │○○○○○○○│    │
         │   └───────┘           └───────┘    │
         │     LEFT               RIGHT       │
         └─────────────────────────────────────┘


    Status Colors:
    ==============

    OFF          = (0,0,0)       - System idle
    CONNECTING   = (255,165,0)   - Orange pulse (both rings)
    CONNECTED    = (0,100,255)   - Blue solid (both rings)
    STREAMING    = (0,255,0)     - Green + white rotating dot
    ERROR        = (255,0,0)     - Red blink
    AUDIO_LEFT   = Blue glow on left ring  (sound from left)
    AUDIO_RIGHT  = Blue glow on right ring (sound from right)


    Environment Variables:
    ======================

    LED_ENABLED=true          # Enable/disable
    LED_DAISY_CHAIN=true      # true=one pin, false=two pins
    LED_PIN_LEFT=18           # GPIO for left (or both if daisy)
    LED_PIN_RIGHT=12          # GPIO for right (if separate)
    LED_PER_RING=8            # LEDs per ring
    LED_BRIGHTNESS=0.3        # 0.0 - 1.0


    Power Calculation:
    ==================

    Each LED: max 60mA (full white)
    16 LEDs × 60mA = 960mA max

    At 30% brightness: ~300mA
    Safe to power from Pi 5V rail.
```

---

## 8. FOOT CONTACT SWITCHES

```
    Micro Switch Wiring
    ===================

    Each foot has a normally-open micro switch:

         Switch Common ──────── GND
         Switch NO     ──────── GPIOx (with internal pull-up)


    GPIO Assignments:
    =================

         FL foot ──────── GPIO4  (Pin 7)
         FR foot ──────── GPIO27 (Pin 13)
         BL foot ──────── GPIO10 (Pin 19)
         BR foot ──────── GPIO9  (Pin 21)


    Software Configuration:
    =======================

    Enable internal pull-ups in code:
      GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    Logic:
      HIGH = foot not touching (switch open)
      LOW  = foot contact (switch closed)
```

---

## 9. POWER DISTRIBUTION

### Power System Overview

```
    POWER DISTRIBUTION
    ==================

    Battery (3S3P 18650)
    11.1V nominal, 30Ah
           │
           ├────────────────────────────────────────┐
           │                                        │
           ▼                                        ▼
    +-------------+                          +-------------+
    │  BMS 20A    │                          │  XT60 Out   │
    │   3S        │                          │  (Motors)   │
    +------┬------+                          +------┬------+
           │                                        │
           │ 11.1V                                  │ 11.1V
           │                                        │
    +------┴------+                          +------┴------+
    │             │                          │  BTS7960    │
    │             │                          │  Driver     │
    ▼             ▼                          +-------------+
    Buck #1    Buck #2
    12V→5V     12V→7.4V
    (Pi)       (Servos)
       │          │
       │          └──────────────────┐
       │                             │
       ▼                             ▼
    +------+                   +----------+
    │ Pi 5 │                   │ PCA9685  │
    │      │                   │ V+ rail  │
    +------+                   +----------+
       │
       │ 3.3V (from Pi)
       │
       ├─────────────────────────────────────┐
       │                                     │
       ▼                                     ▼
    Sensors                              Microphones
    (IMU, GPS,                          (INMP441 x4)
     INA219, etc)
```

### Buck Converter Settings

```
    LM2596 Buck Converters
    ======================

    Buck #1 (Pi Power):
         Input:  11.1V (battery)
         Output: 5.1V @ 3A
         Load:   Raspberry Pi 5

    Buck #2 (Servo Power):
         Input:  11.1V (battery)
         Output: 7.4V @ 10A (use high-current version)
         Load:   22x servos via PCA9685

    Buck #3 (Sensor Power):
         Input:  11.1V (battery)
         Output: 3.3V @ 1A
         Load:   Low-power sensors (optional, can use Pi 3.3V)


    Adjustment:
         Use multimeter to set exact voltage
         before connecting loads!
```

### Wiring Gauge Recommendations

```
    Wire Gauge Guide
    ================

    Battery to BMS:        14 AWG (high current)
    BMS to Buck converters: 16 AWG
    Buck to Pi:            18 AWG
    Buck to PCA9685 V+:    14 AWG (servo current!)
    Motor power:           16 AWG
    Signal wires:          22-24 AWG
    I2C/SPI:              22 AWG
```

---

## 10. COMPLETE WIRING CHECKLIST

```
    PRE-POWER CHECKLIST
    ===================

    [ ] All GND connections tied together
    [ ] No shorts between power rails
    [ ] Buck converters set to correct voltage
    [ ] Polarity checked on all connections
    [ ] I2C pull-ups present (4.7kΩ)
    [ ] Servo power separate from logic power
    [ ] Motor driver enable pins connected
    [ ] Camera ribbons seated properly
    [ ] USB connections secure

    POWER-ON SEQUENCE
    =================

    1. [ ] Connect battery
    2. [ ] Verify 5V rail (Pi power)
    3. [ ] Verify 7.4V rail (servo power)
    4. [ ] Power on Pi (wait for boot)
    5. [ ] Test I2C: i2cdetect -y 1
    6. [ ] Verify all addresses visible
    7. [ ] Test one servo movement
    8. [ ] Test one motor direction
    9. [ ] Check sensor readings
    10.[ ] Full system test
```

---

## 11. TROUBLESHOOTING

### Common Issues

```
    I2C devices not detected:
    -------------------------
    - Check SDA/SCL connections
    - Verify pull-up resistors
    - Check device power (3.3V)
    - Try lower I2C speed: dtparam=i2c_baudrate=50000

    Servos jittering:
    -----------------
    - Add capacitors on servo power rail (1000µF)
    - Check for voltage drop under load
    - Verify PWM frequency (50Hz for standard servos)
    - Separate servo power from logic power

    Motors not running:
    -------------------
    - Check enable pins (should be HIGH)
    - Verify motor power supply
    - Test with direct battery connection
    - Check PWM signal with oscilloscope

    Microphones not working:
    ------------------------
    - Verify I2S overlay enabled
    - Check L/R pin configuration
    - Test with arecord command
    - Verify clock and data connections

    GPS no fix:
    -----------
    - Move to outdoor/window location
    - Check antenna connection
    - Verify UART settings
    - Wait 1-2 minutes for cold start
```

---

## 12. TEST COMMANDS

```bash
# I2C scan
i2cdetect -y 1

# Test servo (requires adafruit-circuitpython-pca9685)
python3 -c "
from adafruit_pca9685 import PCA9685
import board, busio
i2c = busio.I2C(board.SCL, board.SDA)
pca = PCA9685(i2c)
pca.frequency = 50
pca.channels[0].duty_cycle = 0x7FFF  # center position
"

# Test microphones
arecord -D plughw:0 -f S32_LE -r 48000 -c 2 test.wav

# Test GPS
cat /dev/ttyAMA0

# Test IMU (requires adafruit-circuitpython-bno055)
python3 -c "
import board, adafruit_bno055
i2c = board.I2C()
sensor = adafruit_bno055.BNO055_I2C(i2c)
print(f'Euler: {sensor.euler}')
"

# Test LiDAR
ls /dev/ttyUSB*
# Should show /dev/ttyUSB0
```

---

*FLATHEAD Robot Wiring Guide v1.0*
*December 2024*
