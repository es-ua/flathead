# Flathead Camera Mount Assembly

Stereo camera mount with microphones, LED rings, and Raspberry Pi 5.

## Specifications

```
┌──────────────────────────────────────────────────────────────┐
│ [MIC]                                              [MIC]     │
│           ┌─────────┐            ┌─────────┐                 │
│           │ ○ LED ○ │            │ ○ LED ○ │                 │
│           │  [CAM]  │            │  [CAM]  │                 │
│           └─────────┘            └─────────┘                 │
│               ←─── 120mm stereo baseline ───→                │
│                                                              │
│ [MIC]       ┌──────────────────────────────┐         [MIC]  │
│             │      Raspberry Pi 5          │                 │
│             │        ○        ○            │                 │
│             │        ○        ○            │                 │
│             └──────────────────────────────┘                 │
│   ○                                                    ○     │
└──────────────────────────────────────────────────────────────┘
                        160mm × 85mm
```

| Parameter | Value |
|-----------|-------|
| Stereo baseline | 120mm |
| Mic spacing (front) | 140mm |
| Base plate | 160 × 85 × 4mm |
| Camera tilt | 15° down |

---

## Parts List

| Part | Quantity | Description |
|------|----------|-------------|
| `base_plate.stl` | 1 | Main mounting plate with Pi 5 standoffs |
| `camera_holder.stl` | 2 | Camera + LED ring holder |
| `camera_bracket.stl` | 2 | Angled bracket (15° tilt) |
| `mic_holder.stl` | 4 | INMP441 microphone holder |
| `mic_arm_front.stl` | 2 | Front mic extension arm |
| `mic_arm_side.stl` | 2 | Side mic extension arm |
| `led_ring_clip.stl` | 2 | LED ring retention clip (optional) |

**Total print time:** ~6-8 hours
**Total filament:** ~80-100g

---

## Generate STL Files

```bash
# Install CadQuery
pip install cadquery-ocp
# or with conda:
conda install -c conda-forge cadquery

# Generate STL files
cd flathead/cad
python generate_stl.py

# Custom baseline (optional)
python generate_stl.py --baseline 100
```

---

## Print Settings

### Recommended Material
- **PETG** (preferred) - better heat resistance, slight flex
- **PLA+** - easier to print, sufficient for indoor use
- **ASA/ABS** - if outdoor use required

### Slicer Settings

| Setting | Value |
|---------|-------|
| Layer height | 0.2mm |
| Perimeters | 3 |
| Infill | 30% |
| Infill pattern | Gyroid or Grid |
| Top/Bottom layers | 4 |
| Supports | See below |

### Part-Specific Settings

#### base_plate.stl
- **Orientation:** Flat (as exported)
- **Supports:** None needed
- **Brim:** Yes (5mm) - large flat part

#### camera_holder.stl (×2)
- **Orientation:** Standing (opening facing up)
- **Supports:** Yes - for LED ring recess
- **Support type:** Tree supports or normal

#### camera_bracket.stl (×2)
- **Orientation:** L-shape laying flat
- **Supports:** Yes - for overhang

#### mic_holder.stl (×4)
- **Orientation:** PCB slot facing up
- **Supports:** Minimal or none
- **Note:** Small part, print 4 at once

#### mic_arm_front.stl (×2) / mic_arm_side.stl (×2)
- **Orientation:** Flat
- **Supports:** None needed

#### led_ring_clip.stl (×2)
- **Orientation:** Flat
- **Supports:** None
- **Note:** Optional part

---

## Hardware Required

### Fasteners

| Item | Quantity | Purpose |
|------|----------|---------|
| M2 × 6mm screws | 8 | Camera PCB mounting |
| M2 × 8mm screws | 16 | Mic holder mounting |
| M2.5 × 6mm screws | 4 | Pi 5 mounting |
| M2.5 standoffs 8mm | 4 | Pi 5 standoffs (if not printed) |
| M3 × 8mm screws | 8 | Bracket to base |
| M3 × 10mm screws | 8 | Mic arm to base |
| M4 × 12mm screws | 4 | Robot mounting (corners) |
| M3 nuts | 16 | Various |

### Electronics

| Item | Quantity |
|------|----------|
| Pi Camera v3 | 2 |
| INMP441 I2S Microphone | 4 |
| WS2812B 8-LED Ring | 2 |
| Raspberry Pi 5 | 1 |
| Camera ribbon cables | 2 |

---

## Assembly Order

### 1. Prepare Base Plate
```
1. Remove any support material
2. Check all holes are clear (drill if needed)
3. Insert M2.5 heat-set inserts for Pi 5 (optional)
```

### 2. Mount Raspberry Pi 5
```
1. Place Pi 5 on standoffs
2. Secure with M2.5 screws
3. Don't overtighten (plastic standoffs)
```

### 3. Install Camera Brackets
```
1. Attach brackets to base plate with M3 screws
2. Angle should be 15° forward/down
3. Leave slightly loose for adjustment
```

### 4. Prepare Camera Holders
```
1. Insert LED rings into front recess
2. Optionally secure with LED clips
3. Route LED wires through cable slot
```

### 5. Mount Cameras
```
1. Insert Pi Camera v3 PCB into holder slot
2. Secure with M2 screws in corner holes
3. Connect ribbon cable before final mounting
```

### 6. Attach Camera Assemblies
```
1. Mount camera holders to brackets
2. Adjust angle if needed
3. Tighten all bracket screws
```

### 7. Install Microphones
```
1. Mount mic arms to base plate (M3)
2. Insert INMP441 PCBs into holders
3. Attach holders to arm ends (M2)
4. Route mic wires along arms
```

### 8. Final Wiring
```
1. Connect camera ribbons to Pi 5
2. Connect LED rings to GPIO18 (daisy-chain)
3. Connect microphones to I2S pins
4. Secure all cables with zip ties
```

---

## Troubleshooting

### Camera holder doesn't fit LED ring
- Sand the inside of the recess slightly
- Check ring outer diameter (should be 32mm)
- Reprint with 0.1mm larger recess

### Mic PCB too tight/loose
- PCB slot has 0.3mm tolerance
- Sand if too tight
- Add tape if too loose

### Pi 5 holes don't align
- Check Pi 5 version (hole spacing: 58×49mm)
- Drill holes slightly larger (2.8mm)

### Cameras not parallel
- Loosen bracket screws
- Use level/ruler to align
- Retighten carefully

---

## Customization

Edit `camera_mount.py` parameters:

```python
params = CameraMountParams(
    stereo_baseline=120.0,     # Distance between cameras
    mic_front_spacing=140.0,   # Front mic spacing
    tilt_angle=15.0,           # Camera tilt down
    ring_outer_diameter=32.0,  # LED ring size
)
```

Regenerate STL after changes:
```bash
python generate_stl.py
```
