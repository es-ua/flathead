# FLATHEAD CHASSIS - COMPLETE PACKAGE

```
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║              🤖 FLATHEAD ROBOT - 3D PRINTED CHASSIS              ║
║                  Professional Parametric Design                   ║
║                   Created with CadQuery (Python)                  ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
```

## PACKAGE CONTENTS

### 3D Print Files (Ready to Print!)

```
STL FILES:

┌─────────────────────────────────────────────────────┐
│  flathead_base_plate.stl             384 KB         │
│  • Bottom layer с motor mounts                      │
│  • Caster wheel mount                               │
│  • Structural posts                                 │
│  • Cable routing channels                           │
│  • Print time: ~4-5 hours                           │
│  • Material: ~120g PETG                             │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│  flathead_electronics_deck.stl       371 KB         │
│  • Middle layer for electronics                     │
│  • Raspberry Pi 5 mounting tray                     │
│  • Battery compartment walls                        │
│  • Motor driver standoffs                           │
│  • Print time: ~3-4 hours                           │
│  • Material: ~80g PETG                              │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│  flathead_sensor_ring.stl            524 KB         │
│  • Top layer for sensors                            │
│  • RPLIDAR A1 central mount                         │
│  • GPS antenna bracket                              │
│  • Camera mount (angled)                            │
│  • Print time: ~2-3 hours                           │
│  • Material: ~60g PETG                              │
└─────────────────────────────────────────────────────┘

TOTAL PRINT TIME: 9-12 hours
TOTAL MATERIAL:   ~260g PETG (~€6-8)
```

---

### CAD Files (For Modifications)

```
STEP FILES (Universal CAD format):

┌─────────────────────────────────────────────────────┐
│  flathead_base_plate.step            237 KB         │
│  flathead_electronics_deck.step      253 KB         │
│  flathead_sensor_ring.step           171 KB         │
│                                                     │
│  Open in:                                           │
│  • Fusion 360 (free personal)                       │
│  • FreeCAD (open source)                            │
│  • SolidWorks                                       │
│  • OnShape (browser-based)                          │
│  • Any CAD software                                 │
│                                                     │
│  Use for:                                           │
│  • Custom modifications                             │
│  • Size adjustments                                 │
│  • Adding features                                  │
│  • Integration with other parts                     │
└─────────────────────────────────────────────────────┘
```

---

### Source Code (Parametric Design)

```
PYTHON FILE:

┌─────────────────────────────────────────────────────┐
│  chassis_design.py                   20 KB          │
│                                                     │
│  Features:                                          │
│  • Full parametric design                           │
│  • Easy size modifications                          │
│  • Component-specific parameters                    │
│  • Regenerate STLs instantly                        │
│  • Well-documented code                             │
│  • CadQuery-based (Python CAD)                      │
│                                                     │
│  Change any dimension:                              │
│    base_diameter = 180  →  200mm                    │
│    Run script → new STL files!                      │
└─────────────────────────────────────────────────────┘
```

---

## TECHNICAL OVERVIEW

```
╔═══════════════════════════════════════════════════════════════╗
║  CHASSIS SPECIFICATIONS                                       ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  Dimensions:                                                  ║
║    Diameter:              180 mm                              ║
║    Total Height:          ~95 mm                              ║
║    Base Thickness:        15 mm                               ║
║    Layer Spacing:         25 mm                               ║
║                                                               ║
║  Components Supported:                                        ║
║    - Raspberry Pi 5       (85.6 × 56 × 17 mm)                ║
║    - RPLIDAR A1          (76mm dia, 40mm height)             ║
║    - TT Motors (2×)       (70mm length, 25mm dia)            ║
║    - 2S LiPo Battery      (100 × 35 × 20 mm)                 ║
║    - Motor Driver         (Standard size)                     ║
║    - GPS Module           (25 × 25 mm)                        ║
║    - Camera              (Pi Camera / USB)                   ║
║                                                               ║
║  Mounting:                                                    ║
║    M3 screws              Primary structure                   ║
║    M2.5 screws            Raspberry Pi                        ║
║    Threaded inserts       16× recommended                     ║
║                                                               ║
║  Weight (empty):          300-400g (PETG)                     ║
║  Print Material:          ~260g PETG                          ║
║  Print Time:              9-12 hours total                    ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```

---

## DESIGN FEATURES

```
SMART ENGINEERING:

┌─────────────────────────────────────────────────────┐
│  3D Print Optimized:                                │
│  - Minimal support material needed                  │
│  - Flat surfaces for bed adhesion                   │
│  - No overhangs >45° (self-supporting)              │
│  - Proper wall thickness (3mm)                      │
│  - Easy removal from print bed                      │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│  Modular Design:                                    │
│  - 3 separate layers (easy access)                  │
│  - Removable Pi tray                                │
│  - Quick battery replacement                        │
│  - Component serviceability                         │
│  - Expandable structure                             │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│  Cable Management:                                  │
│  - Built-in cable routing channels                  │
│  - Separate power/signal paths                      │
│  - Cable clips throughout                           │
│  - Strain relief points                             │
│  - Clean, organized wiring                          │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│  Thermal Management:                                │
│  - Ventilation slots in Pi tray                     │
│  - Hollow center (airflow)                          │
│  - Pi standoffs (8mm clearance)                     │
│  - Open structure                                   │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│  Mechanical Stability:                              │
│  - Low center of gravity (battery low)              │
│  - Wide motor stance (130mm)                        │
│  - Balanced weight distribution                     │
│  - Structural posts (threaded inserts)              │
│  - Rigid construction                               │
└─────────────────────────────────────────────────────┘
```

---

## COST BREAKDOWN

```
╔═══════════════════════════════════════════════════════════════╗
║  TOTAL CHASSIS COST                                           ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  Option A: Print Service (Treatstock.de)                      ║
║    3D Printing (PETG):         €60-80                         ║
║    Hardware (screws, inserts): €9-10                          ║
║    ─────────────────────────────────────                      ║
║    TOTAL:                      €69-90                         ║
║    Time from order:            ~7 days                        ║
║                                                               ║
║  Option B: FabLab Hamburg (Self-Print)                        ║
║    FabLab membership:          €10-15                         ║
║    PETG material:              €10-15                         ║
║    Hardware:                   €9-10                          ║
║    ─────────────────────────────────────                      ║
║    TOTAL:                      €29-40                         ║
║    Time investment:            2-3 visits                     ║
║    Learning value:             HIGH!                          ║
║                                                               ║
║  Option C: Buy Printer (Long-term)                            ║
║    Ender 3 V3 SE:              €200-250                       ║
║    PETG filament:              €25                            ║
║    Hardware:                   €9-10                          ║
║    ─────────────────────────────────────                      ║
║    INITIAL:                    €234-285                       ║
║    Per-print after:            ~€5-10                         ║
║    ROI after:                  3-4 projects                   ║
║    Flexibility:                MAXIMUM!                       ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝

ADD TO PREVIOUS ELECTRONICS BOM: €994

╔═══════════════════════════════════════════════════════════════╗
║  COMPLETE FLATHEAD ROBOT COST                                 ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  Electronics (BOM v2.5):       €994                           ║
║  Chassis (Option A):           €69-90                         ║
║  ─────────────────────────────────────                        ║
║  PROJECT TOTAL:                €1,063-1,084                   ║
║                                                               ║
║  Still under €1,100 budget!                                   ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```

---

## READY TO USE

### Immediate Actions:

```
STEP 1: View Your Models (5 min)
   https://www.viewstl.com
   Drag & drop STL files
   Inspect all 3 layers!

STEP 2: Choose Printing Method (5 min)
   A) Treatstock.de (easy, €60-80)
   B) FabLab Hamburg (cheap, €20-30)
   C) Buy printer (€200, long-term best)

STEP 3: Order Print (10 min)
   Upload STL files
   Choose PETG material
   Select Hamburg location
   → Get quote & order!

STEP 4: Order Hardware (10 min)
   M3 screws & inserts
   Conrad Electronic / Amazon.de
   ~€9-10 total

STEP 5: Wait for Delivery (~7 days)
   Continue with ROS 2 setup
   Plan software architecture
   Prepare workspace

STEP 6: Assemble! (2-3 hours)
   Follow assembly instructions
   Install threaded inserts
   Mount all layers
   Install electronics

STEP 7: ROBOT READY!
   Power on
   Test motors
   Verify sensors
   Start autonomous navigation!
```

---

## CUSTOMIZATION

Want to modify? **EASY!**

```python
# Edit chassis_design.py:

class ChassisParams:
    base_diameter = 180          # ← Make it bigger/smaller
    motor_mount_spacing = 130    # ← Wider/narrower stance
    battery_length = 100         # ← Bigger battery space
    lidar_center_height = 100    # ← Raise/lower LiDAR
    layer_spacing = 25           # ← Taller robot
    # ... dozens of parameters!

# Save file → Run script → New STLs instantly!
```

**Common modifications:**
- Bigger chassis (200mm diameter)
- Taller layers (more clearance)
- Different motor spacing
- Larger battery compartment
- Additional sensor mounts
- Custom cable routing
- Extra mounting points

**All parametric → changes take seconds!**

---

## PRO TIPS

```
Printing:
  • Use PETG (not PLA) for durability
  • 0.2mm layer height (standard quality)
  • 25-30% infill (strong enough)
  • Minimal supports needed
  • Clean bed for adhesion

Assembly:
  • Install threaded inserts first
  • Test-fit components before final assembly
  • Route cables through channels
  • Leave slack in wiring
  • Use Loctite on critical screws

Testing:
  • Power on without motors first
  • Test each component separately
  • Verify LiDAR rotation clearance
  • Check GPIO connections
  • Test motor directions
```

---

## USAGE

```bash
# Install CadQuery
pip install cadquery-ocp

# Generate STL/STEP files
cd cad
mkdir -p output
python chassis_design.py

# Files will be in ./output/
```

---

*Generated by FLATHEAD ROBOT Chassis Designer*
*Parametric 3D CAD Design with Python (CadQuery)*
*Hamburg, Germany | December 2024*
*Ready for Autonomous Navigation & ROS 2*
