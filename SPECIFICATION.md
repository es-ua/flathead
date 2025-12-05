# FLATHEAD ROBOT - Authentic Specification v2.5

**Version:** 2.5 - AUTHENTIC 5-DOF CONFIGURATION
**Date:** December 2024
**Developer:** Esso (Hamburg, Germany)
**Inspiration:** Flathead from Cyberpunk 2077
**Configuration:** TRUE TO ORIGINAL - 5-DOF Legs + Independent Steering + 2-DOF Head

---

## Executive Summary

**FLATHEAD v2.5** - maximum fidelity to the original design with professional capabilities:

### Key Features:
- **5-DOF Legs:** 20 servos for full control (Hip Abduction + Hip Flexion + Knee + Ankle + Swivel)
- **Dynamic Stance:** Legs spread and narrow (12-32cm track width)
- **Independent Steering:** Swivel compensates leg spread + advanced maneuvers
- **2-DOF Head:** Active vision with pan/tilt tracking
- **Complete Feedback:** 22x current sensors + 4x foot switches
- **Multi-LLM Intelligence:** LangGraph orchestration

### Unique Capabilities:
- Dynamic leg spread (narrow <-> wide stance)
- Sideways stepping (native, without wheels!)
- Wheel compensation (swivel corrects direction)
- Ackermann steering (car-like turns)
- Tank turns (pivot in place)
- Crab walk (sideways on wheels)
- Drift turns (controlled slides)
- Active stability (lean into turns, wide stance for rough terrain)
- Narrow space navigation (legs together)

### Total Degrees of Freedom: 22 DOF
- Legs: 20 DOF (5-DOF x 4 legs)
- Head: 2 DOF (pan + tilt)

---

## Complete BOM - EUR 994

```
+---------------------------------------------------+
|  FLATHEAD v2.5 - AUTHENTIC BUILD                  |
+---------------------------------------------------+
|                                                   |
|  COMPUTE & STORAGE                                |
|    Raspberry Pi 5 8GB                   EUR 90    |
|    SanDisk 64GB microSD A2              EUR 12    |
|    -----------------------------------------      |
|    Subtotal:                            EUR 102   |
|                                                   |
|  VISION SYSTEM                                    |
|    2x Pi Camera v3 (stereo)             EUR 60    |
|      - On 2-DOF head                              |
|      - 180 deg x 75 deg coverage                  |
|    -----------------------------------------      |
|    Subtotal:                            EUR 60    |
|                                                   |
|  NAVIGATION & SENSORS                             |
|    RPLIDAR A1M8 (360 deg LiDAR)         EUR 100   |
|    BNO055 IMU (9-axis)                  EUR 25    |
|    u-blox SAM-M10Q GPS                  EUR 20    |
|    -----------------------------------------      |
|    Subtotal:                            EUR 145   |
|                                                   |
|  AUDIO SYSTEM                                     |
|    4x INMP441 I2S microphone            EUR 20    |
|    PAM8403 amplifier                    EUR 5     |
|    Speaker 4 Ohm 3W                     EUR 3     |
|    -----------------------------------------      |
|    Subtotal:                            EUR 28    |
|                                                   |
|  5-DOF HYBRID MOTION SYSTEM                       |
|                                                   |
|    LEG SERVOS (20x DS3218):                       |
|      20x DS3218 servo (25kg/cm @ 7.4V)  EUR 240   |
|                                                   |
|      Per leg (5x servo):                          |
|        - 1x Hip Abduction (spread/narrow)         |
|        - 1x Hip Flexion (forward/back)            |
|        - 1x Knee (up/down)                        |
|        - 1x Ankle (foot angle)                    |
|        - 1x Swivel (wheel steering)               |
|                                                   |
|    WHEEL DRIVE:                                   |
|      4x JGA25-370 motor + encoder       EUR 40    |
|      4x Rubber wheels (100mm)           EUR 20    |
|      BTS7960 motor driver (4-ch)        EUR 15    |
|                                                   |
|    CONTROL:                                       |
|      2x PCA9685 PWM driver (16ch)       EUR 16    |
|        - Board 1: Legs 1-2 (10 servo)             |
|        - Board 2: Legs 3-4 (10 servo)             |
|      Motor mounting brackets            EUR 5     |
|      Swivel mounting hardware           EUR 3     |
|      Hip joint assemblies               EUR 5     |
|      LM2596 Buck 12V->7.4V (servo)      EUR 5     |
|    -----------------------------------------      |
|    Subtotal:                            EUR 349   |
|                                                   |
|  2-DOF HEAD SYSTEM                                |
|    2x MG996R servo (pan/tilt)           EUR 12    |
|    Head mounting brackets               EUR 2     |
|    Thrust bearing (pan axis)            EUR 2     |
|    -----------------------------------------      |
|    Subtotal:                            EUR 16    |
|                                                   |
|  COMPLETE FEEDBACK SYSTEM                         |
|    22x INA219 current sensor            EUR 88    |
|      - 20 leg servos (5-DOF x 4)                  |
|      - 2 head servos                              |
|    3x TCA9548A I2C multiplexer          EUR 15    |
|      - Mux 1: Leg FL (5 sensors)                  |
|      - Mux 2: Leg FR (5 sensors)                  |
|      - Mux 3: Legs BL+BR (10 sensors)             |
|        + Head (2 sensors)                         |
|    4x Micro switch (foot contact)       EUR 4     |
|    Feedback wiring & connectors         EUR 5     |
|    -----------------------------------------      |
|    Subtotal:                            EUR 112   |
|                                                   |
|  POWER SYSTEM                                     |
|    6x Samsung 18650 (3S3P)              EUR 38    |
|      - 30Ah @ 11.1V = 360Wh                       |
|    3S BMS 20A                           EUR 8     |
|    LM2596 Buck 12V->5V (Pi)             EUR 4     |
|    LM2596 Buck 12V->3.3V (sensors)      EUR 3     |
|    TP4056 3S charger                    EUR 12    |
|    XT60 connectors (x5)                 EUR 3     |
|    DC barrel jacks                      EUR 2     |
|    -----------------------------------------      |
|    Subtotal:                            EUR 70    |
|                                                   |
|  ELECTRONICS & WIRING                             |
|    Breadboard + wires + connectors      EUR 20    |
|    Resistors + capacitors               EUR 6     |
|    Heat shrink + screws                 EUR 6     |
|    Extra JST connectors                 EUR 4     |
|    -----------------------------------------      |
|    Subtotal:                            EUR 36    |
|                                                   |
|  STRUCTURE & MECHANICAL                           |
|    PLA filament 1.5kg                   EUR 30    |
|    3D printing service                  EUR 25    |
|    Carbon fiber rods                    EUR 12    |
|    Ball bearings (leg joints)           EUR 10    |
|    Thrust bearings (swivel + head)      EUR 6     |
|    Adhesives                            EUR 6     |
|    Extra structural parts               EUR 10    |
|    Foot pads with switch mounts         EUR 3     |
|    -----------------------------------------      |
|    Subtotal:                            EUR 102   |
|                                                   |
|  MISCELLANEOUS                                    |
|    Anti-static bags + cable ties        EUR 8     |
|    Debugging tools                      EUR 6     |
|    -----------------------------------------      |
|    Subtotal:                            EUR 14    |
|                                                   |
|  ================================================ |
|  GRAND TOTAL:                           EUR 994   |
|  ================================================ |
|                                                   |
|  Evolution from original:                         |
|    Base quadruped (3-DOF):              EUR 644   |
|    +Wheels & hybrid:                    +EUR 113  |
|    +Full feedback:                      +EUR 64   |
|    +Swivel steering:                    +EUR 81   |
|    +Hip abduction (5-DOF):              +EUR 68   |
|    +2-DOF head:                         +EUR 24   |
|    TOTAL:                               EUR 994   |
|                                                   |
+---------------------------------------------------+
```

---

## Complete Actuator Inventory

```
+---------------------------------------------------+
|  ACTUATORS: 26 TOTAL (22 DOF)                     |
+---------------------------------------------------+
|                                                   |
|  SERVOS (22x):                                    |
|                                                   |
|    Legs (20x DS3218 @ 25kg/cm):                   |
|                                                   |
|      Per leg (5x servo):                          |
|        1. Hip Abduction (sideways)                |
|           Range: +/-30 deg (narrow <-> wide)      |
|                                                   |
|        2. Hip Flexion (forward/back)              |
|           Range: +/-60 deg (swing)                |
|                                                   |
|        3. Knee (up/down)                          |
|           Range: 0-120 deg (flexion)              |
|                                                   |
|        4. Ankle (foot angle)                      |
|           Range: +/-30 deg (tilt)                 |
|                                                   |
|        5. Swivel (wheel steering)                 |
|           Range: +/-90 deg (full steering)        |
|           Purpose: Compensate abduction +         |
|                    Advanced maneuvers             |
|                                                   |
|      Total: 4 legs x 5 servo = 20 servo           |
|                                                   |
|    Head (2x MG996R @ 11kg/cm):                    |
|      - 1x Pan (left/right +/-90 deg)              |
|      - 1x Tilt (up/down +45/-30 deg)              |
|                                                   |
|  MOTORS (4x):                                     |
|    - 4x JGA25-370 DC (wheel drive)                |
|      - 200 RPM @ 12V                              |
|      - Hall encoders (odometry)                   |
|      - 100mm wheels                               |
|                                                   |
|  TOTAL DEGREES OF FREEDOM: 22 DOF                 |
|    - Legs: 5-DOF x 4 = 20 DOF                     |
|    - Head: 2-DOF = 2 DOF                          |
|                                                   |
|  AUTHENTIC TO CYBERPUNK ORIGINAL!                 |
|                                                   |
+---------------------------------------------------+
```

---

## 5-DOF Leg Architecture

### Detailed Joint Structure:

```
         [Body Mount]
              |
         +=========+
         |  Servo  |  <- Joint 1: Hip Abduction
         |    1    |     Axis: Vertical (body frame)
         | Abduct  |     Movement: Leg sideways
         +====+====+     Range: +/-30 deg (12-32cm track)
              |
         +====+====+
         |  Servo  |  <- Joint 2: Hip Flexion
         |    2    |     Axis: Lateral (perpendicular to body)
         |  Flex   |     Movement: Leg forward/back
         +====+====+     Range: +/-60 deg (swing arc)
              |
         [Upper Leg]
         8-10cm segment
              |
         +====+====+
         |  Servo  |  <- Joint 3: Knee
         |    3    |     Axis: Lateral
         |  Knee   |     Movement: Leg up/down
         +====+====+     Range: 0-120 deg (flexion)
              |
         [Lower Leg]
         10-12cm segment
              |
         +====+====+
         |  Servo  |  <- Joint 4: Ankle
         |    4    |     Axis: Lateral
         |  Ankle  |     Movement: Foot angle
         +====+====+     Range: +/-30 deg (tilt)
              |
         +====+====+
         |  Servo  |  <- Joint 5: Swivel
         |    5    |     Axis: Vertical (foot frame)
         | Swivel  |     Movement: Wheel direction
         +====+====+     Range: +/-90 deg (steering)
              |            Purpose: Compensate + Steer
         [Motor Mount]
              |
         [JGA25-370]
              |
            [O]  <- 100mm wheel


Weight per leg assembly: ~400g
Total leg reach: ~25cm (extended)
Minimum height: 5cm (crouched)
Maximum height: 30cm (standing)
```

---

## Movement Capabilities - Unique to 5-DOF

### Dynamic Stance Control:

```python
class DynamicStance:
    """5-DOF enables adaptive stance width"""

    STANCE_MODES = {
        'narrow': -20,    # 12cm track (tight spaces)
        'normal': 0,      # 20cm track (default)
        'wide': +20,      # 28cm track (stability)
        'extra_wide': +30 # 32cm track (maximum)
    }

    async def set_stance_width(self, mode):
        """Dynamically adjust leg spread"""

        angle = self.STANCE_MODES[mode]

        # All legs abduct to same angle
        for leg in ['FL', 'FR', 'BL', 'BR']:
            await robot.legs[leg].hip_abduction.set_angle(angle)

        # Swivel compensates to keep wheels forward!
        for leg in ['FL', 'FR', 'BL', 'BR']:
            await robot.legs[leg].swivel.set_angle(-angle)

        # Result: Legs spread, wheels still straight!

        logger.info(f"Stance: {mode} ({12+angle*0.4:.0f}cm track)")
```

---

## Swivel Compensation System

### Why Swivel is Critical for 5-DOF:

```
+---------------------------------------------------+
|  SWIVEL DUAL PURPOSE                              |
+---------------------------------------------------+
|                                                   |
|  Purpose 1: COMPENSATION                          |
|                                                   |
|    When legs abduct, wheels follow:               |
|                                                   |
|      Wide stance (no compensation):               |
|        /Body\                                     |
|       /  |  \                                     |
|      O/    \O  <- Wheels angled! BAD             |
|                                                   |
|      Wide stance (WITH compensation):             |
|        /Body\                                     |
|       /  |  \                                     |
|      O->  <-O  <- Wheels straight! GOOD          |
|      Swivel compensated!                          |
|                                                   |
|    Formula:                                       |
|      swivel_angle = -hip_abduction_angle          |
|                                                   |
|  Purpose 2: ADVANCED STEERING                     |
|                                                   |
|    Independent of leg position:                   |
|      - Ackermann steering                         |
|      - Tank turns                                 |
|      - Crab walk                                  |
|      - Drift turns                                |
|                                                   |
|    Combined compensation + steering:              |
|      total_swivel = -hip_abduct + steering_angle  |
|                                                   |
+---------------------------------------------------+
```

---

## Power Consumption (Updated for 5-DOF)

```
+---------------------------------------------------+
|  POWER ANALYSIS - 22 SERVO + 4 MOTOR              |
+---------------------------------------------------+
|                                                   |
|  MODE POWER CONSUMPTION:                          |
|                                                   |
|  Idle Mode:       6.5W  -> 55h runtime            |
|    - All servo minimal hold                       |
|    - Sensors active                               |
|    - Pi idle                                      |
|                                                   |
|  Wheel Mode:      25W   -> 14.4h runtime          |
|    - Legs: holding position (2W)                  |
|    - Hip abduction: locked (0.4W)                 |
|    - Swivel: compensating (0.6W)                  |
|    - Motors: active (12W)                         |
|    - Pi + sensors: (8W)                           |
|    - Head: tracking (2W)                          |
|                                                   |
|  Leg Mode:        32W   -> 11.3h runtime          |
|    - All leg servo active (24W)                   |
|    - Hip abduction: dynamic (2W)                  |
|    - Swivel: locked (0.2W)                        |
|    - Pi + sensors: (8W)                           |
|    - Head: looking down (1W)                      |
|                                                   |
|  Hybrid Mode:     38W   -> 9.5h runtime           |
|    - Leg servo: adaptive (16W)                    |
|    - Hip abduction: dynamic (2W)                  |
|    - Swivel: compensating + steering (2W)         |
|    - Motors: active (10W)                         |
|    - Pi + sensors: (8W)                           |
|                                                   |
|  Peak (climbing):  68W   -> 5.3h runtime          |
|    - All servo max (36W)                          |
|    - Motors max (18W)                             |
|    - Pi + sensors peak (14W)                      |
|                                                   |
|  Battery: 360Wh (3S3P, 30Ah @ 11.1V)              |
|                                                   |
+---------------------------------------------------+
```

---

## Locomotion Modes

### MODE 1: WHEEL MODE - Speed Champion

```
Configuration:
  - Legs: Fixed height, stance adjustable
  - Hip abduction: Active (stability control)
  - Swivel: Compensating + steering
  - Wheels: 4WD powered
  - Head: Active scanning

Capabilities:
  - Speed: 1.0-1.3 m/s
  - Narrow stance (tight spaces)
  - Wide stance (stability)
  - Ackermann steering
  - Tank turns
  - Crab walk
  - Drift turns
  - Lean into turns

Power: 25W
Runtime: 14.4 hours
Terrain: Flat surfaces
```

### MODE 2: LEG MODE - Terrain Master

```
Configuration:
  - Legs: Full 5-DOF active
  - Hip abduction: Dynamic spreading
  - Swivel: Locked forward
  - Wheels: Freewheel
  - Head: Looking down for obstacles

Capabilities:
  - Speed: 0.6 m/s
  - Stairs: 20cm height
  - Native sidestep (without wheels!)
  - Wide stance on rough terrain
  - Narrow stance on beams
  - Adaptive foot placement
  - Dynamic stability

Power: 32W
Runtime: 11.3 hours
Terrain: Stairs, rocks, obstacles
```

### MODE 3: HYBRID MODE - Versatile

```
Configuration:
  - Legs: Adaptive 5-DOF
  - Hip abduction: Real-time adjust
  - Swivel: Compensation + steering
  - Wheels: Powered (variable)
  - Head: Context-aware

Capabilities:
  - Speed: 0.8-1.0 m/s
  - Best of both worlds
  - Dynamic stance width
  - Terrain adaptation
  - Speed + capability
  - Professional grade

Power: 38W
Runtime: 9.5 hours
Terrain: Mixed surfaces
```

---

## Physical Specifications

```
Dimensions:
  Body: 25cm x 20cm x 15cm
  With legs normal stance: 35cm x 35cm x 30cm
  With legs wide stance: 40cm x 40cm x 30cm
  With legs narrow: 28cm x 28cm x 30cm
  With head: total height 45cm

Weight Distribution:
  Body + electronics: ~850g
  Battery: ~300g
  Legs (4x @ ~450g): ~1800g
  Head assembly: ~400g
  TOTAL: ~3.35kg (+0.65kg vs 4-DOF)

Footprint (adjustable):
  Narrow stance: 28cm x 28cm (12cm track)
  Normal stance: 35cm x 35cm (20cm track)
  Wide stance: 40cm x 40cm (28cm track)
  Extra wide: 42cm x 42cm (32cm track)

Track width variation: 20cm (12-32cm range)
This is 167% variation! Huge flexibility!
```

---

## Advantages of 5-DOF Configuration

```
+---------------------------------------------------+
|  WHY 5-DOF IS WORTH IT                            |
+---------------------------------------------------+
|                                                   |
|  vs 4-DOF (EUR 926):                              |
|    Cost difference: +EUR 68 (only 7% more)        |
|                                                   |
|  Gained capabilities:                             |
|                                                   |
|    1. Dynamic Stance Width                        |
|       - 12-32cm adjustable track                  |
|       - 167% range variation                      |
|       - Real-time adaptation                      |
|                                                   |
|    2. Narrow Space Navigation                     |
|       - Can navigate 14cm corridors               |
|       - 4-DOF minimum: 20cm fixed                 |
|       - 30% space reduction                       |
|                                                   |
|    3. Stability Enhancement                       |
|       - 60% wider stance available                |
|       - Active tilt correction                    |
|       - Asymmetric stance on slopes               |
|       - Much safer on rough terrain               |
|                                                   |
|    4. Native Sideways Stepping                    |
|       - Leg mode sidestep (without wheels!)       |
|       - Natural animal movement                   |
|       - 4-DOF can only crab walk with wheels      |
|                                                   |
|    5. Lean Into Turns                             |
|       - Motorcycle-style cornering                |
|       - Higher safe speed in turns                |
|       - Professional handling                     |
|                                                   |
|    6. Terrain Adaptation                          |
|       - Legs spread on rough ground               |
|       - Legs narrow on smooth ground              |
|       - Dynamic optimization                      |
|                                                   |
|    7. Authentic to Original                       |
|       - True Cyberpunk 2077 design                |
|       - Matches original capabilities             |
|       - Professional appearance                   |
|                                                   |
|  Trade-offs:                                      |
|    - +4 servo (20 vs 16)                          |
|    - +15% complexity                              |
|    - +0.65kg weight                               |
|    - +1 week assembly time                        |
|    - -1h runtime (14.4h vs 15.7h)                 |
|                                                   |
|  Verdict: ABSOLUTELY WORTH IT!                    |
|                                                   |
+---------------------------------------------------+
```

---

## 12-Week Build Plan

```
WEEK 1-2: Parts & Planning
  - Order all components (EUR 994)
  - Design 3D models (5-DOF specific)
  - 3D print all parts (~65 hours)
  - Study servo placement

WEEK 3-4: Mechanical Assembly
  - Assemble hip joints (2-servo per hip)
  - Mount all 20 leg servos
  - Install swivel mechanisms
  - Assemble 2-DOF head
  - Mount motors & wheels

WEEK 5-6: Electronics & Feedback
  - Wire 22 servos to 2x PCA9685
  - Install 22x INA219 sensors
  - Configure 3x I2C multiplexers
  - Install 4x foot switches
  - Power system integration

WEEK 7-8: Core Software
  - Pi 5 setup (Ubuntu 24, Docker)
  - Servo control system
  - 5-DOF kinematics library
  - Swivel compensation algorithm
  - Feedback monitoring system

WEEK 9-10: Intelligence & Navigation
  - LangGraph framework
  - Multi-agent system
  - SLAM implementation
  - Terrain analysis
  - Stance selection agent

WEEK 11: Advanced Features
  - Native sideways stepping
  - Stability correction system
  - Narrow corridor navigation
  - Slope handling
  - All steering modes

WEEK 12: Testing & Polish
  - Stance transformation testing
  - Narrow space validation
  - Slope stability testing
  - Mode transition optimization
  - Documentation & video
```

---

## Success Metrics

```
+---------------------------------------------------+
|  PERFORMANCE TARGETS - 5-DOF SPECIFIC             |
+---------------------------------------------------+
|                                                   |
|  STANCE CONTROL:                                  |
|    - Track width range: 12-32cm (167%)            |
|    - Stance transition: <2 seconds                |
|    - Narrow corridor: 14cm minimum                |
|    - Wide stability: 30% better than 4-DOF        |
|    - Asymmetric stance: slopes up to 25 deg       |
|                                                   |
|  COMPENSATION:                                    |
|    - Wheel alignment: +/-2 deg accuracy           |
|    - Compensation lag: <50ms                      |
|    - Works at all stance widths                   |
|                                                   |
|  LEG MODE:                                        |
|    - Sideways step: 5cm per step                  |
|    - Sidestep speed: 0.2 m/s                      |
|    - Stance-aware gait: smooth                    |
|                                                   |
|  STABILITY:                                       |
|    - Tilt recovery: <1 second                     |
|    - Wind resistance: 40% better (wide)           |
|    - Rough terrain: no falls                      |
|                                                   |
+---------------------------------------------------+
```

---

## Final Summary

```
+---------------------------------------------------+
|  FLATHEAD v2.5 - AUTHENTIC BUILD                  |
+---------------------------------------------------+
|                                                   |
|  TOTAL COST: EUR 994                              |
|                                                   |
|  CONFIGURATION:                                   |
|    - 22 Servos (20 leg + 2 head)                  |
|    - 4 Motors (wheel drive)                       |
|    - 22 DOF (5-DOF legs + 2-DOF head)             |
|    - 26 Actuators total                           |
|                                                   |
|  UNIQUE 5-DOF CAPABILITIES:                       |
|    - Dynamic stance (12-32cm track)               |
|    - Narrow space navigation                      |
|    - Wide stance stability                        |
|    - Native sideways stepping                     |
|    - Asymmetric stance correction                 |
|    - Swivel compensation system                   |
|    - Lean into turns                              |
|    - Professional terrain adaptation              |
|                                                   |
|  AUTHENTIC TO CYBERPUNK ORIGINAL                  |
|                                                   |
|  RUNTIME: 14.4h wheel, 11.3h leg                  |
|                                                   |
|  BUILD TIME: 12 weeks                             |
|                                                   |
|  PROFESSIONAL GRADE CAPABILITIES                  |
|  AT DIY BUDGET                                    |
|                                                   |
+---------------------------------------------------+
```

---

**FLATHEAD v2.5 - The Authentic Cyberpunk Robot**

*"In Night City, you can be anything you want to be."*
*"So build a robot that shouldn't exist... for under EUR 1000."*
