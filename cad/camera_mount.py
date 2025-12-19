#!/usr/bin/env python3
"""
FLATHEAD Robot - Stereo Camera Mount with LED Rings

Parametric CadQuery design for:
- 2x Pi Camera v3 holders
- 2x WS2812B 8-LED ring mounts
- Raspberry Pi 5 mounting plate
- Adjustable stereo baseline

Print settings:
- Material: PETG or PLA+
- Layer height: 0.2mm
- Infill: 30%
- Supports: Yes (for camera holders)

Author: Flathead Project
"""

import cadquery as cq
from dataclasses import dataclass
from typing import Tuple


@dataclass
class CameraMountParams:
    """Parameters for stereo camera mount with microphones"""

    # Stereo baseline (distance between camera centers)
    stereo_baseline: float = 120.0  # mm (12cm for better depth at 2-10m)

    # Pi Camera v3 dimensions
    camera_pcb_width: float = 25.0   # mm
    camera_pcb_height: float = 24.0  # mm
    camera_pcb_thickness: float = 1.0  # mm
    camera_lens_diameter: float = 8.0  # mm
    camera_lens_height: float = 5.0   # mm
    camera_hole_spacing_x: float = 21.0  # mm (M2 holes)
    camera_hole_spacing_y: float = 12.5  # mm
    camera_hole_diameter: float = 2.2   # mm for M2

    # LED ring dimensions (8-LED WS2812B)
    ring_outer_diameter: float = 32.0  # mm
    ring_inner_diameter: float = 12.0  # mm (lens passthrough)
    ring_thickness: float = 3.0        # mm
    ring_mount_depth: float = 2.0      # mm recess

    # INMP441 Microphone dimensions
    mic_pcb_width: float = 14.0   # mm
    mic_pcb_height: float = 9.5   # mm
    mic_pcb_thickness: float = 1.6  # mm
    mic_hole_diameter: float = 2.0  # mm (sound port)
    mic_mount_hole: float = 1.8    # mm for M1.6 or friction fit

    # Microphone array spacing (for TDOA localization)
    mic_front_spacing: float = 140.0  # mm between front L/R mics (wider than cameras)
    mic_side_offset: float = 70.0     # mm from center to side mics

    # Mount body
    mount_thickness: float = 4.0      # mm
    mount_wall: float = 3.0           # mm
    mount_height: float = 45.0        # mm (camera holder height)

    # Raspberry Pi 5 dimensions
    pi_width: float = 85.0    # mm
    pi_height: float = 56.0   # mm
    pi_hole_spacing_x: float = 58.0  # mm
    pi_hole_spacing_y: float = 49.0  # mm
    pi_hole_diameter: float = 2.7    # mm for M2.5
    pi_standoff_height: float = 8.0  # mm

    # Base plate (sized for 120mm baseline + mics)
    base_width: float = 160.0   # mm (120mm baseline + camera holders)
    base_depth: float = 85.0    # mm
    base_thickness: float = 4.0 # mm

    # Tilt adjustment
    tilt_angle: float = 15.0    # degrees downward

    # Mounting holes for robot attachment
    robot_hole_diameter: float = 4.0  # mm for M4
    robot_hole_inset: float = 8.0     # mm from edge


def create_camera_holder(params: CameraMountParams) -> cq.Workplane:
    """
    Create a single camera holder with LED ring mount

    Features:
    - Camera PCB slot
    - LED ring recess (front)
    - Cable routing channel
    - Lens clearance hole
    """

    p = params

    # Outer dimensions
    holder_width = p.ring_outer_diameter + p.mount_wall * 2
    holder_height = p.mount_height
    holder_depth = p.mount_thickness + p.ring_mount_depth + p.camera_pcb_thickness + 2

    # Main body
    holder = (
        cq.Workplane("XY")
        .box(holder_width, holder_depth, holder_height)
    )

    # Front: LED ring recess (circular)
    holder = (
        holder
        .faces(">Y")
        .workplane()
        .circle(p.ring_outer_diameter / 2)
        .cutBlind(-p.ring_mount_depth)
    )

    # Center hole for lens (through the ring area)
    holder = (
        holder
        .faces(">Y")
        .workplane()
        .circle(p.ring_inner_diameter / 2)
        .cutThrough()
    )

    # Camera PCB slot (from back)
    holder = (
        holder
        .faces("<Y")
        .workplane()
        .rect(p.camera_pcb_width + 0.5, p.camera_pcb_height + 0.5)
        .cutBlind(-p.camera_pcb_thickness - 1)
    )

    # Camera mounting holes (M2)
    hole_positions = [
        (p.camera_hole_spacing_x / 2, p.camera_hole_spacing_y / 2),
        (-p.camera_hole_spacing_x / 2, p.camera_hole_spacing_y / 2),
        (p.camera_hole_spacing_x / 2, -p.camera_hole_spacing_y / 2),
        (-p.camera_hole_spacing_x / 2, -p.camera_hole_spacing_y / 2),
    ]

    holder = (
        holder
        .faces("<Y")
        .workplane()
        .pushPoints(hole_positions)
        .hole(p.camera_hole_diameter, depth=holder_depth)
    )

    # Cable routing slot (bottom)
    cable_slot_width = 15.0
    cable_slot_height = 5.0
    holder = (
        holder
        .faces("<Z")
        .workplane()
        .center(0, 0)
        .rect(cable_slot_width, holder_depth)
        .cutBlind(-cable_slot_height)
    )

    return holder


def create_base_plate(params: CameraMountParams) -> cq.Workplane:
    """
    Create the base plate that holds both cameras and Pi 5

    Layout:
    ┌──────────────────────────────────┐
    │  [CAM L]            [CAM R]      │
    │     ○                  ○         │
    │                                  │
    │  ┌────────────────────────┐      │
    │  │    Raspberry Pi 5      │      │
    │  │         ○   ○          │      │
    │  │         ○   ○          │      │
    │  └────────────────────────┘      │
    │  ○                          ○    │  <- robot mount holes
    └──────────────────────────────────┘
    """

    p = params

    # Main base plate
    base = (
        cq.Workplane("XY")
        .box(p.base_width, p.base_depth, p.base_thickness)
    )

    # Camera mount positions
    cam_y_offset = p.base_depth / 2 - 15  # Near front edge
    cam_left_x = -p.stereo_baseline / 2
    cam_right_x = p.stereo_baseline / 2

    # Camera mount holes (for attaching holders)
    cam_mount_holes = [
        (cam_left_x - 10, cam_y_offset),
        (cam_left_x + 10, cam_y_offset),
        (cam_right_x - 10, cam_y_offset),
        (cam_right_x + 10, cam_y_offset),
    ]

    base = (
        base
        .faces(">Z")
        .workplane()
        .pushPoints(cam_mount_holes)
        .hole(3.2, depth=p.base_thickness)  # M3 clearance
    )

    # Pi 5 standoff positions
    pi_center_y = -p.base_depth / 2 + p.pi_height / 2 + 10
    pi_holes = [
        (p.pi_hole_spacing_x / 2, pi_center_y + p.pi_hole_spacing_y / 2),
        (-p.pi_hole_spacing_x / 2, pi_center_y + p.pi_hole_spacing_y / 2),
        (p.pi_hole_spacing_x / 2, pi_center_y - p.pi_hole_spacing_y / 2),
        (-p.pi_hole_spacing_x / 2, pi_center_y - p.pi_hole_spacing_y / 2),
    ]

    # Pi 5 standoffs
    for pos in pi_holes:
        standoff = (
            cq.Workplane("XY")
            .center(pos[0], pos[1])
            .circle(5)  # Standoff outer diameter
            .extrude(p.base_thickness + p.pi_standoff_height)
        )
        # Hole in standoff for M2.5
        standoff = (
            standoff
            .faces(">Z")
            .workplane()
            .hole(p.pi_hole_diameter, depth=p.pi_standoff_height + 2)
        )
        base = base.union(standoff.translate((0, 0, -p.base_thickness / 2)))

    # Robot mounting holes (corners)
    robot_holes = [
        (-p.base_width / 2 + p.robot_hole_inset, -p.base_depth / 2 + p.robot_hole_inset),
        (p.base_width / 2 - p.robot_hole_inset, -p.base_depth / 2 + p.robot_hole_inset),
        (-p.base_width / 2 + p.robot_hole_inset, p.base_depth / 2 - p.robot_hole_inset),
        (p.base_width / 2 - p.robot_hole_inset, p.base_depth / 2 - p.robot_hole_inset),
    ]

    base = (
        base
        .faces(">Z")
        .workplane()
        .pushPoints(robot_holes)
        .hole(p.robot_hole_diameter, depth=p.base_thickness)
    )

    # Microphone arm mounting holes (M3)
    # 4 mics: Front-Left, Front-Right, Side-Left, Side-Right
    mic_arm_holes = [
        # Front mics (near cameras, facing forward)
        (-p.mic_front_spacing / 2, p.base_depth / 2 - 8),
        (p.mic_front_spacing / 2, p.base_depth / 2 - 8),
        # Side mics (for lateral sound)
        (-p.base_width / 2 + 12, 0),
        (p.base_width / 2 - 12, 0),
    ]

    base = (
        base
        .faces(">Z")
        .workplane()
        .pushPoints(mic_arm_holes)
        .hole(3.2, depth=p.base_thickness)  # M3 clearance
    )

    return base


def create_camera_bracket(params: CameraMountParams) -> cq.Workplane:
    """
    Create angled bracket to mount camera holder to base plate

    Allows tilting cameras downward for better ground view
    """

    p = params

    bracket_width = 25.0
    bracket_height = 30.0
    bracket_depth = 20.0

    # L-shaped bracket
    bracket = (
        cq.Workplane("XY")
        # Horizontal part (attaches to base)
        .box(bracket_width, bracket_depth, p.mount_thickness)
        .faces(">Z")
        .workplane()
        # Vertical part (attaches to camera holder)
        .center(0, bracket_depth / 2 - p.mount_thickness / 2)
        .box(bracket_width, p.mount_thickness, bracket_height, centered=(True, True, False))
    )

    # Mounting holes for base plate (M3)
    bracket = (
        bracket
        .faces("<Z")
        .workplane()
        .pushPoints([(-8, 0), (8, 0)])
        .hole(3.2, depth=p.mount_thickness)
    )

    # Mounting holes for camera holder (M3)
    bracket = (
        bracket
        .faces(">Y")
        .workplane()
        .pushPoints([(-8, bracket_height / 2), (8, bracket_height / 2)])
        .hole(3.2, depth=p.mount_thickness)
    )

    return bracket


def create_led_ring_clip(params: CameraMountParams) -> cq.Workplane:
    """
    Optional: Clip to secure LED ring in the camera holder

    Snaps over the ring to hold it in place
    """

    p = params

    clip_thickness = 2.0
    clip_width = 8.0

    # Ring clip (quarter circle with tabs)
    clip = (
        cq.Workplane("XY")
        .circle(p.ring_outer_diameter / 2 + clip_thickness)
        .circle(p.ring_outer_diameter / 2 - 1)
        .extrude(clip_width)
    )

    # Cut to make it a C-clip (open on one side)
    clip = (
        clip
        .faces(">Z")
        .workplane()
        .center(p.ring_outer_diameter / 2, 0)
        .rect(20, 15)
        .cutThrough()
    )

    return clip


def create_mic_holder(params: CameraMountParams) -> cq.Workplane:
    """
    Create holder for INMP441 I2S microphone

    Features:
    - PCB slot with friction fit
    - Sound port hole aligned with mic
    - Cable exit slot
    - M2 mounting holes for attachment to base
    """

    p = params

    # Holder dimensions
    holder_width = p.mic_pcb_width + 4  # 18mm
    holder_height = p.mic_pcb_height + 6  # 15.5mm
    holder_depth = 8.0  # mm

    # Main body
    holder = (
        cq.Workplane("XY")
        .box(holder_width, holder_depth, holder_height)
    )

    # PCB slot (from back)
    holder = (
        holder
        .faces("<Y")
        .workplane()
        .rect(p.mic_pcb_width + 0.3, p.mic_pcb_height + 0.3)
        .cutBlind(-p.mic_pcb_thickness - 0.5)
    )

    # Sound port hole (front, aligned with mic MEMS)
    # INMP441 sound port is offset from center
    holder = (
        holder
        .faces(">Y")
        .workplane()
        .center(3, 0)  # Offset to align with mic port
        .hole(p.mic_hole_diameter + 1, depth=holder_depth)
    )

    # Mounting holes (M2)
    mount_hole_positions = [
        (-holder_width / 2 + 3, -holder_height / 2 + 3),
        (holder_width / 2 - 3, -holder_height / 2 + 3),
    ]

    holder = (
        holder
        .faces("<Z")
        .workplane()
        .pushPoints(mount_hole_positions)
        .hole(2.2, depth=5)  # M2 clearance
    )

    # Cable exit slot (bottom)
    holder = (
        holder
        .faces("<Z")
        .workplane()
        .center(0, 0)
        .rect(8, holder_depth)
        .cutBlind(-4)
    )

    return holder


def create_mic_arm(params: CameraMountParams, length: float = 30.0) -> cq.Workplane:
    """
    Create arm to extend microphone from base plate

    Allows positioning mics at optimal locations for sound localization
    """

    p = params

    arm_width = 12.0
    arm_thickness = 4.0

    # Main arm
    arm = (
        cq.Workplane("XY")
        .box(arm_width, length, arm_thickness)
    )

    # Base mounting holes (M3)
    arm = (
        arm
        .faces("<Y")
        .workplane()
        .center(0, 0)
        .pushPoints([(-4, 0), (4, 0)])
        .hole(3.2, depth=arm_thickness)
    )

    # Mic holder mounting holes (M2)
    arm = (
        arm
        .faces(">Y")
        .workplane()
        .center(0, 0)
        .pushPoints([(-4, 0), (4, 0)])
        .hole(2.2, depth=arm_thickness)
    )

    return arm


def create_full_assembly(params: CameraMountParams = None) -> dict:
    """
    Create all parts for the camera mount assembly

    Parts list:
    - 1x base_plate (with Pi 5 standoffs and mic arm mounts)
    - 2x camera_holder (with LED ring recess)
    - 2x camera_bracket (angled mount)
    - 2x led_ring_clip (optional)
    - 4x mic_holder (INMP441)
    - 4x mic_arm (extension from base)

    Layout:
    ┌────────────────────────────────────────┐
    │  [MIC]                        [MIC]    │  <- Front L/R mics
    │      [CAM+LED]    [CAM+LED]            │
    │                                        │
    │ [MIC]  ┌──────────────────┐    [MIC]  │  <- Side mics
    │        │  Raspberry Pi 5  │            │
    │        └──────────────────┘            │
    │   ○                              ○     │
    └────────────────────────────────────────┘
    """

    if params is None:
        params = CameraMountParams()

    parts = {}

    # Base plate
    parts["base_plate"] = create_base_plate(params)

    # Camera holders (need 2)
    parts["camera_holder"] = create_camera_holder(params)

    # Brackets (need 2)
    parts["camera_bracket"] = create_camera_bracket(params)

    # Optional LED ring clips (need 2)
    parts["led_ring_clip"] = create_led_ring_clip(params)

    # Microphone holders (need 4)
    parts["mic_holder"] = create_mic_holder(params)

    # Microphone arms - front (need 2, shorter)
    parts["mic_arm_front"] = create_mic_arm(params, length=25.0)

    # Microphone arms - side (need 2, longer)
    parts["mic_arm_side"] = create_mic_arm(params, length=35.0)

    return parts


def export_all(output_dir: str = ".", params: CameraMountParams = None):
    """Export all parts as STL and STEP files"""

    import os

    parts = create_full_assembly(params)

    os.makedirs(output_dir, exist_ok=True)

    for name, part in parts.items():
        # STL for printing
        stl_path = os.path.join(output_dir, f"{name}.stl")
        cq.exporters.export(part, stl_path)
        print(f"Exported: {stl_path}")

        # STEP for CAD editing
        step_path = os.path.join(output_dir, f"{name}.step")
        cq.exporters.export(part, step_path)
        print(f"Exported: {step_path}")


# Assembly visualization (for CQ-editor)
if __name__ == "__cq_workplane__" or __name__ == "__main__":
    params = CameraMountParams()

    # Create parts
    base = create_base_plate(params)
    holder = create_camera_holder(params)
    bracket = create_camera_bracket(params)

    # Position for display
    # Left camera assembly
    left_holder = (
        holder
        .rotate((0, 0, 0), (1, 0, 0), params.tilt_angle)
        .translate((-params.stereo_baseline / 2, params.base_depth / 2 - 15, 35))
    )

    # Right camera assembly
    right_holder = (
        holder
        .rotate((0, 0, 0), (1, 0, 0), params.tilt_angle)
        .translate((params.stereo_baseline / 2, params.base_depth / 2 - 15, 35))
    )

    # Full assembly
    assembly = base.union(left_holder).union(right_holder)

    # Show result (works in CQ-editor)
    show_object(base, name="base_plate", options={"color": "gray"})
    show_object(left_holder, name="left_camera", options={"color": "blue"})
    show_object(right_holder, name="right_camera", options={"color": "blue"})
