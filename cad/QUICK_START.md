# QUICK START - FLATHEAD CHASSIS

## What you have:

### Ready 3D models:
1. **flathead_base_plate.stl** (384 KB)
2. **flathead_electronics_deck.stl** (371 KB)
3. **flathead_sensor_ring.stl** (524 KB)

### CAD files for editing:
1. **flathead_base_plate.step**
2. **flathead_electronics_deck.step**
3. **flathead_sensor_ring.step**

### Source code:
- **chassis_design.py** - parametric design (modifiable!)

---

## QUICK START

### Option 1: View models (NOW!)

```bash
# Online viewer (easiest):
1. Go to: https://www.viewstl.com
2. Drag & drop STL files
3. Rotate, zoom, inspect!

# Alternative:
https://3dviewer.net
```

### Option 2: Order print (TODAY!)

```bash
# Treatstock.de (recommended):
1. Go to: www.treatstock.de
2. Upload flathead_*.stl files
3. Choose material: PETG
4. Choose color: Black (or any!)
5. Hamburg local printer
6. Get quote (~€60-80)
7. Order → delivered in ~7 days

# Total time from now: 10 minutes!
```

### Option 3: Print yourself (THIS WEEK!)

```bash
# FabLab Hamburg:
1. Visit: fablab-hamburg.org
2. Check hours: Tuesday evening
3. Bring: USB stick with STL files
4. Print time: ~10-12 hours total
5. Cost: ~€20-30
6. Learn 3D printing!
```

---

## Modifications

### Want to change dimensions?

```bash
# Edit chassis_design.py:

class ChassisParams:
    base_diameter = 180      # ← Change this!
    battery_length = 100     # ← Or this!
    motor_mount_spacing = 130
    # ... etc

# Then run:
python3 chassis_design.py

# → New STL files generated!
```

---

## What to buy

### For chassis assembly:

```
Hardware (~€9):
  □ M3×10mm screws (20 pcs)
  □ M3×15mm screws (12 pcs)
  □ M3 threaded inserts (16 pcs)
  □ M2.5×8mm screws (4 pcs)
  □ Velcro straps (1-2 pcs)

Where:
  • Conrad Electronic Hamburg
  • Bauhaus
  • Amazon.de
```

---

## Specifications

```
╔═══════════════════════════════════════╗
║  Diameter:    180mm                   ║
║  Height:      ~95mm                   ║
║  Weight:      ~300-400g (PETG)        ║
║  Print time:  9-12 hours              ║
║  Material:    ~260g PETG              ║
║  Cost:        €60-80 (service)        ║
║              €20-30 (self-print)      ║
╚═══════════════════════════════════════╝
```

---

## What's included in design:

```
Layer 1: Base Plate
  - TT motor mounts (left/right)
  - Caster wheel mount (front)
  - Cable routing channels
  - Structural posts (M3 inserts)

Layer 2: Electronics Deck
  - Raspberry Pi 5 tray (removable)
  - Battery compartment (2S LiPo)
  - Motor driver standoffs
  - Ventilation & GPIO access

Layer 3: Sensor Ring
  - RPLIDAR A1 mount (central)
  - GPS antenna bracket
  - Camera mount (front, angled)
  - Top structural ring
```

---

## Next Actions

```
□ 1. View STL files online (5 min)
     → viewstl.com

□ 2. Decide: Print service or FabLab? (5 min)

□ 3. Order print OR book FabLab visit (10 min)
     → treatstock.de OR fablab-hamburg.org

□ 4. Order hardware screws (10 min)
     → Amazon.de cart ready

□ 5. Wait for delivery (~7 days)
     → Continue with ROS 2 setup!

□ 6. Assemble chassis (2-3 hours)
     → Follow ASSEMBLY.md

□ 7. Install electronics (2 hours)
     → Mount Pi, LiDAR, battery

□ 8. ROBOT READY!
```

---

## Questions?

**About modifications:**
- Edit `chassis_design.py` (all parameters there)
- Re-run script → new STLs!

**About printing:**
- Check ASSEMBLY.md (full guide)
- Settings provided for PETG & PLA

**About assembly:**
- Step-by-step in ASSEMBLY.md
- Hardware list included

---

## Pro Tips

```
- Print in PETG (not PLA) for durability
- Use threaded inserts for easier assembly
- Test component fit before final assembly
- Route cables through channels
- Leave slack in wires for movement
- Check LiDAR rotation clearance
```

---

## Summary

**YOU HAVE:**
- Professional 3D printable robot chassis
- Optimized for your components
- Modular 3-layer design
- Full documentation

**NEXT STEP:**
- Order your print TODAY!
- 10 minutes to order
- 7 days delivery
- Robot ready in 2 weeks!

---

**Let's build FLATHEAD!**
