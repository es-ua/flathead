# FLATHEAD ROBOT - 3D Printed Chassis

## Generated Files

**6 files ready for use:**

### STL Files (for 3D printing):
- `flathead_base_plate.stl` (384 KB) - Layer 1: Base with motor mounts
- `flathead_electronics_deck.stl` (371 KB) - Layer 2: Electronics platform
- `flathead_sensor_ring.stl` (524 KB) - Layer 3: Top ring with LiDAR

### STEP Files (for CAD editing):
- `flathead_base_plate.step` - Open in Fusion 360, FreeCAD, etc.
- `flathead_electronics_deck.step`
- `flathead_sensor_ring.step`

---

## Technical Specifications

```
╔════════════════════════════════════════════════════╗
║  CHASSIS DIMENSIONS                                ║
╠════════════════════════════════════════════════════╣
║  Overall diameter:        180 mm                   ║
║  Overall height:          ~95 mm                   ║
║  Base thickness:          15 mm                    ║
║  Layer spacing:           25 mm                    ║
║  Motor mount spacing:     130 mm                   ║
║  LiDAR center height:     ~100 mm from ground     ║
║  Weight (without electronics): ~300-400g (PETG)   ║
╚════════════════════════════════════════════════════╝
```

### Mounting holes:
- **M3 screws**: Main fasteners between layers
- **M2.5 screws**: Raspberry Pi 5 mounting
- **M3 threaded inserts**: Recommended for durability

---

## 3D PRINTING GUIDE

### Recommended settings:

#### **Material: PETG** (best choice!)
```
Nozzle Temperature:     235-245°C
Bed Temperature:        75-85°C
Print Speed:            40-50 mm/s
First Layer Speed:      20-25 mm/s (50%)
Infill:                 25-30%
Wall Lines:             3-4 lines
Layer Height:           0.2 mm (standard)
Supports:               MINIMAL (designed to avoid!)
Cooling Fan:            30-50%
```

#### Alternative: PLA (prototype only)
```
Nozzle Temperature:     200-215°C
Bed Temperature:        50-60°C
Print Speed:            50-60 mm/s
Infill:                 20%
WARNING: Not recommended for final robot (heat sensitive)
```

---

## Print Time Estimates

```
╔════════════════════════════════════════════════════╗
║  PART                  │  TIME     │  MATERIAL     ║
╠════════════════════════════════════════════════════╣
║  Base Plate            │  4-5 hrs  │  ~120g        ║
║  Electronics Deck      │  3-4 hrs  │  ~80g         ║
║  Sensor Ring           │  2-3 hrs  │  ~60g         ║
║  ─────────────────────────────────────────────     ║
║  TOTAL                 │  9-12 hrs │  ~260g PETG   ║
╚════════════════════════════════════════════════════╝

Can be faster with higher speeds or larger nozzle (0.6mm)
```

---

## Design Contents

### Layer 1: Base Plate
```
- Circular base platform (180mm diameter)
- Left & Right motor mounts (TT motors)
- Front caster wheel mount
- 4 mounting posts (M3 threaded insert holes)
- Cable routing channels (cross pattern)
- Optimized weight distribution
```

### Layer 2: Electronics Deck
```
- Raspberry Pi 5 mounting tray
  • 4× M2.5 mounting holes (correct spacing)
  • 8mm standoff height (air circulation)
  • GPIO access cutout
  • Ventilation slots

- Battery compartment (2S LiPo)
  • 100×35mm internal space
  • U-shaped walls (easy access)
  • Velcro strap slots

- Motor driver standoffs (4× M3)
- Mounting holes align with base posts
- Hollow center (airflow)
```

### Layer 3: Sensor Ring
```
- LiDAR mounting platform
  • Central pedestal (raises LiDAR)
  • 4× M3 mounting holes (60mm circle)
  • Cable routing through center

- GPS antenna bracket
  • Side-mounted
  • 4× standoffs for GPS module

- Camera mount (front)
  • Angled 15° down
  • 2× M3 mounting holes

- Structural ring with mounting holes
```

---

## Bill of Materials (Hardware)

Required for assembly:

```
╔════════════════════════════════════════════════════╗
║  HARDWARE                                          ║
╠════════════════════════════════════════════════════╣
║  M3 × 10mm screws:        ~20 pcs  (~€2)           ║
║  M3 × 15mm screws:        ~12 pcs  (~€1.50)        ║
║  M3 threaded inserts:     ~16 pcs  (~€3)           ║
║  M2.5 × 8mm screws:       4 pcs    (~€0.50)        ║
║  Velcro straps:           1-2 pcs  (~€2)           ║
║  ─────────────────────────────────────────────     ║
║  TOTAL:                            ~€9-10          ║
╚════════════════════════════════════════════════════╝

Where to buy in Hamburg:
  • Bauhaus (Nedderfeld)
  • Conrad Electronic (Innenstadt)
  • Amazon.de (delivery)
```

---

## ASSEMBLY INSTRUCTIONS

### Step 1: Prepare Parts

```
1. Print all 3 parts (or order printing)
2. Remove supports if any
3. Clean stringing
4. Sand rough edges (120-grit sandpaper)
5. Check fit of all holes:
   • M3 holes: bolt should pass freely
   • M2.5 holes: test with Pi 5
   • If tight → drill out slightly
```

### Step 2: Install Threaded Inserts

```
1. M3 brass inserts in base posts (4 per post):
   • Heat soldering iron to 200°C
   • Place insert on hole
   • Carefully melt in (slow & straight!)
   • Let cool 1-2 minutes

2. Check threads: M3 bolt should screw in easily
```

### Step 3: Assemble Bottom Layer

```
1. Mount motors in motor mounts:
   • 2× TT motors
   • M3 screws through mounting holes
   • Wire routing through slots

2. Mount caster wheel at front:
   • Small swivel caster (20-30mm)
   • 4× M3 screws

3. Verify wheels don't touch base
```

### Step 4: Electronics Layer

```
1. Mount Electronics Deck on base:
   • Align mounting holes
   • 4× M3×15mm screws through posts
   • Don't overtighten!

2. Mount Raspberry Pi 5 on tray:
   • 4× M2.5×8mm screws
   • GPIO pins should be accessible
   • Check clearance with standoffs

3. Place battery in compartment:
   • 2S LiPo inside U-walls
   • Velcro strap through slots
   • XT60 connector accessible

4. Mount motor driver:
   • On 4 standoffs
   • M3 screws
   • Wire to Pi GPIO
```

### Step 5: Sensor Ring

```
1. Mount Sensor Ring:
   • Align mounting holes
   • 4× M3×10mm screws

2. Mount RPLIDAR A1:
   • On central platform
   • 4× M3 screws (60mm circle pattern)
   • USB cable through center hole

3. Mount GPS module:
   • On side bracket
   • 4× small screws
   • Antenna facing up

4. Mount camera (optional):
   • Front angled mount
   • 2× M3 screws
```

### Step 6: Wiring & Testing

```
1. Route all cables through channels:
   • Power lines: Battery → Buck converters → Pi
   • Motor wires: Motors → Driver → Pi GPIO
   • LiDAR USB → Pi USB port
   • GPS UART → Pi GPIO pins

2. Cable management:
   • Zip ties in clips
   • Avoid crossing power/signal
   • Leave slack for movement

3. Power-on test:
   • Check voltages
   • Test motor rotation
   • Verify LiDAR spin
   • GPS LED should blink
```

---

## Assembly Checklist

```
□ All parts printed successfully
□ Support material removed
□ Holes checked & drilled if needed
□ Threaded inserts installed (16×)
□ Motors mounted (2×)
□ Caster wheel mounted (1×)
□ Electronics deck attached
□ Pi 5 mounted with standoffs
□ Battery secured with velcro
□ Motor driver installed
□ Sensor ring attached
□ LiDAR mounted & centered
□ GPS module installed
□ Camera mounted (optional)
□ All cables routed
□ Cable ties applied
□ Power-on test PASSED
□ Motors tested (forward/backward)
□ LiDAR spinning
□ GPS acquiring satellites
```

---

## MODIFICATIONS & CUSTOMIZATION

### Easy to change in `chassis_design.py`:

```python
# Parameters at the beginning of file:

class ChassisParams:
    base_diameter = 180          # ← Increase/decrease
    base_height = 15             # ← Base thickness
    motor_mount_spacing = 130    # ← Wider/narrower stance
    battery_length = 100         # ← Bigger battery?
    lidar_center_height = 100    # ← Raise/lower LiDAR
    # ... etc.

# Change parameter → run script → new STL!
```

### Ideas for improvements:

```
- Add LED strip mounts
- Bumper sensor brackets
- Bigger battery compartment
- Second camera mount (rear)
- IMU mounting bracket
- More cable clips
- Status display mount (OLED)
- RGB underglow mounts
```

---

## Where to Print in Hamburg

### Option A: Self-Print
```
FabLab Hamburg:
  Location: Lerchenstrasse 14a
  Cost: ~€20-30 for all parts
  Time: 2-3 visits (long prints)
  Bonus: Learn 3D printing!
```

### Option B: Print Service
```
Treatstock.de:
  1. Upload these STL files
  2. Choose PETG material
  3. Select Hamburg local printer
  4. Order → delivered in ~7 days
  Cost: ~€60-80
```

### Option C: Buy Printer
```
Ender 3 V3 SE:
  Cost: ~€200-250
  Source: Amazon.de
  Benefit: Great learning experience
  Bonus: Print anytime!
```

---

## Total Cost Breakdown

```
╔════════════════════════════════════════════════════╗
║  CHASSIS COMPLETE COST                             ║
╠════════════════════════════════════════════════════╣
║  3D Printing (PETG):      €60-80   (Treatstock)    ║
║  OR Print yourself:       €20-30   (FabLab)        ║
║  Hardware (screws, etc):  €9-10                    ║
║  ─────────────────────────────────────────────     ║
║  TOTAL:                   €69-90                   ║
╚════════════════════════════════════════════════════╝

Add to previous BOM €994:
  → Total project: €1,063-1,084
```

---

## Design Features

### Optimized for 3D printing:
```
- Minimal overhangs (<45°)
- No support in most areas
- Flat surfaces for bed adhesion
- Proper wall thickness (3mm)
- Mounting holes slightly oversized
```

### Smart engineering:
```
- Modular 3-layer design
- Easy component access
- Cable management built-in
- Airflow for Pi cooling
- Low center of gravity (battery low)
- Balanced weight distribution
```

### Future-proof:
```
- Parametric design (easy to change)
- Extra mounting points
- Expandable structure
- Standard M3 hardware
- Compatible with common components
```

---

## Next Steps

```
1. Review STL files (upload to online viewer)
2. Decide: Print yourself or order?
3. Order hardware (screws, inserts)
4. Wait for prints (1 week)
5. Assemble chassis (2-3 hours)
6. Install electronics
7. First power-on test!
8. Start ROS 2 development!
```

---

## Visualization

STL files can be viewed in:
- **Online**: viewstl.com (drag & drop)
- **Windows**: 3D Builder (built-in)
- **Mac**: Preview (open STL)
- **Linux**: MeshLab, FreeCAD
- **Browser**: Three.js viewers

---

## Ready to Build!

**You now have:**
- Complete 3D printable chassis
- All mounting points for components
- Optimized design for robotics
- Professional quality CAD files
- Full documentation

**Next: ORDER YOUR PRINT!**

---

*Generated by FLATHEAD ROBOT Chassis Designer*
*Parametric CAD with CadQuery*
*Hamburg, Germany | 2024*
