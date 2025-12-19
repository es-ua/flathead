#!/usr/bin/env python3
"""
Generate STL files for camera mount assembly.

Requirements:
    pip install cadquery-ocp
    # or with conda:
    conda install -c conda-forge cadquery

Usage:
    python generate_stl.py
    python generate_stl.py --output ./my_stl_folder
    python generate_stl.py --baseline 100  # custom baseline
"""

import argparse
import os
import sys

def main():
    parser = argparse.ArgumentParser(description='Generate STL files for Flathead camera mount')
    parser.add_argument('--output', '-o', default='stl', help='Output directory (default: stl)')
    parser.add_argument('--baseline', '-b', type=float, help='Override stereo baseline (mm)')
    parser.add_argument('--step', action='store_true', help='Also export STEP files')
    args = parser.parse_args()

    try:
        from camera_mount import CameraMountParams, export_all
    except ImportError as e:
        print(f"Error: {e}")
        print("\nPlease install CadQuery first:")
        print("  pip install cadquery-ocp")
        print("  # or with conda:")
        print("  conda install -c conda-forge cadquery")
        sys.exit(1)

    # Create params with optional override
    params = CameraMountParams()
    if args.baseline:
        params.stereo_baseline = args.baseline
        # Adjust base width for new baseline
        params.base_width = args.baseline + 40  # camera holders + margin
        print(f"Using custom baseline: {args.baseline}mm")

    print(f"Generating STL files to: {args.output}/")
    print(f"  Stereo baseline: {params.stereo_baseline}mm")
    print(f"  Base plate: {params.base_width}x{params.base_depth}mm")
    print(f"  Mic spacing: {params.mic_front_spacing}mm")
    print()

    export_all(args.output, params)

    # List generated files
    print("\nGenerated files:")
    for f in sorted(os.listdir(args.output)):
        if f.endswith('.stl') or (args.step and f.endswith('.step')):
            path = os.path.join(args.output, f)
            size = os.path.getsize(path) / 1024
            print(f"  {f} ({size:.1f} KB)")

    print("\n✓ Done! Files ready for 3D printing.")
    print("\nPrint quantities:")
    print("  base_plate.stl      x1")
    print("  camera_holder.stl   x2")
    print("  camera_bracket.stl  x2")
    print("  mic_holder.stl      x4")
    print("  mic_arm_front.stl   x2")
    print("  mic_arm_side.stl    x2")
    print("  led_ring_clip.stl   x2 (optional)")


if __name__ == '__main__':
    main()
