#!/usr/bin/env python3
"""
FLATHEAD ROBOT - Parametric Chassis Design
Created with CadQuery - fully customizable 3D printable robot chassis

Design Philosophy:
- Modular 3-layer design (base, electronics, sensors)
- Optimized for 3D printing (no supports where possible)
- Easy assembly with M3 screws
- Cable management built-in
- Designed for: Pi 5, RPLIDAR A1, 2S LiPo, TT motors
"""

import cadquery as cq
from typing import Dict, Tuple
import math

# ============================================================================
# DESIGN PARAMETERS - Легко менять все размеры!
# ============================================================================

class ChassisParams:
    """All dimensions in millimeters"""

    # === MAIN CHASSIS ===
    base_diameter = 180          # Main body diameter
    base_height = 15             # Bottom plate thickness
    wall_thickness = 3           # Structural walls

    # === RASPBERRY PI 5 ===
    pi5_length = 85.6
    pi5_width = 56
    pi5_height = 17
    pi5_mount_hole_spacing_length = 58  # Between mounting holes
    pi5_mount_hole_spacing_width = 49
    pi5_mount_hole_diameter = 2.5       # M2.5 screws
    pi5_standoff_height = 8             # Clearance below Pi

    # === MOTORS & WHEELS ===
    motor_length = 70            # TT Motor
    motor_diameter = 25
    motor_mount_spacing = 130    # Distance between left/right motors
    wheel_diameter = 65
    wheel_thickness = 27

    # === BATTERY ===
    battery_length = 100         # 2S LiPo typical
    battery_width = 35
    battery_height = 20
    battery_clearance = 2        # Extra space

    # === LIDAR ===
    lidar_diameter = 76          # RPLIDAR A1
    lidar_height = 40
    lidar_mount_holes = 4        # Mounting holes
    lidar_mount_hole_diameter = 3
    lidar_mount_circle_diameter = 60
    lidar_center_height = 100    # Height from ground

    # === GPS ===
    gps_module_length = 25
    gps_module_width = 25
    gps_module_height = 8

    # === GENERAL ===
    m3_hole_diameter = 3.2       # M3 screws (slightly larger for ease)
    m3_insert_diameter = 4.2     # Brass threaded inserts
    layer_spacing = 25           # Vertical space between layers
    corner_radius = 5            # Rounded corners

    @classmethod
    def get_layer_heights(cls) -> Dict[str, float]:
        """Calculate Z positions for each layer"""
        return {
            'base': 0,
            'electronics': cls.base_height + cls.layer_spacing,
            'sensors': cls.base_height + 2 * cls.layer_spacing
        }


class ChassisDesigner:
    """Main chassis design generator"""

    def __init__(self, params: ChassisParams = None):
        self.p = params or ChassisParams()
        self.layers = self.p.get_layer_heights()

    def create_base_plate(self) -> cq.Workplane:
        """
        Layer 1: Bottom chassis plate
        - Circular main body
        - Motor mounts (left/right)
        - Mounting holes for upper layers
        - Cable routing channels
        """

        print("🔨 Creating base plate...")

        # Main circular base
        base = (cq.Workplane("XY")
                .circle(self.p.base_diameter / 2)
                .extrude(self.p.base_height)
        )

        # Add mounting posts for upper layers (4 corners in square pattern)
        post_positions = self._get_mounting_post_positions()
        for x, y in post_positions:
            post = (cq.Workplane("XY")
                    .workplane(offset=self.p.base_height)
                    .circle(6)  # 12mm diameter posts
                    .extrude(self.p.layer_spacing - 2)
                    .faces(">Z").workplane()
                    .hole(self.p.m3_insert_diameter, depth=15)  # Threaded insert hole
            )
            base = base.union(post.translate((x, y, 0)))

        # Motor mounting brackets (left and right)
        motor_y = -self.p.base_diameter / 2 + 20  # Near the back edge

        for side in [-1, 1]:  # Left and right
            motor_x = side * self.p.motor_mount_spacing / 2
            motor_mount = self._create_motor_mount()
            base = base.union(motor_mount.translate((motor_x, motor_y, 0)))

        # Front caster mount
        caster_mount = self._create_caster_mount()
        caster_y = self.p.base_diameter / 2 - 15
        base = base.union(caster_mount.translate((0, caster_y, 0)))

        # Cable routing channels
        base = self._add_cable_channels(base)

        print("✅ Base plate complete")
        return base

    def create_electronics_deck(self) -> cq.Workplane:
        """
        Layer 2: Electronics mounting deck
        - Raspberry Pi 5 mounting tray
        - Motor driver mounting
        - Battery compartment
        - Power distribution area
        """

        print("🔨 Creating electronics deck...")

        # Main deck plate (ring shape - hollow center for airflow)
        outer_r = self.p.base_diameter / 2 - 5
        inner_r = 30  # Hollow center

        deck = (cq.Workplane("XY")
                .workplane(offset=self.layers['electronics'])
                .circle(outer_r)
                .circle(inner_r)
                .extrude(3)  # 3mm deck thickness
        )

        # Add mounting holes to align with base posts
        post_positions = self._get_mounting_post_positions()
        for x, y in post_positions:
            deck = (deck.faces(">Z").workplane()
                    .pushPoints([(x, y)])
                    .hole(self.p.m3_hole_diameter)
            )

        # Pi 5 mounting tray (removable)
        pi_tray = self._create_pi5_tray()
        pi_x, pi_y = 0, -20  # Slightly towards back
        deck = deck.union(pi_tray.translate((pi_x, pi_y, self.layers['electronics'])))

        # Battery compartment walls
        battery_walls = self._create_battery_compartment()
        battery_x, battery_y = 0, 40  # Front area
        deck = deck.union(battery_walls.translate((battery_x, battery_y, self.layers['electronics'])))

        # Standoffs for motor driver (small board)
        driver_positions = [(30, 0), (30, 20), (50, 0), (50, 20)]
        for x, y in driver_positions:
            standoff = (cq.Workplane("XY")
                       .workplane(offset=self.layers['electronics'] + 3)
                       .circle(3)
                       .extrude(5)
                       .faces(">Z").workplane()
                       .hole(self.p.m3_hole_diameter)
            )
            deck = deck.union(standoff.translate((x, y, 0)))

        print("✅ Electronics deck complete")
        return deck

    def create_sensor_ring(self) -> cq.Workplane:
        """
        Layer 3: Top sensor mounting ring
        - LiDAR mounting plate
        - GPS antenna mount
        - Camera mounts
        - Status LED windows
        """

        print("🔨 Creating sensor ring...")

        # Top ring (thinner, just structural)
        ring = (cq.Workplane("XY")
                .workplane(offset=self.layers['sensors'])
                .circle(self.p.base_diameter / 2 - 5)
                .circle(self.p.lidar_diameter / 2 + 10)  # Large center hole for LiDAR
                .extrude(3)
        )

        # Add mounting holes to align with base posts
        post_positions = self._get_mounting_post_positions()
        for x, y in post_positions:
            ring = (ring.faces(">Z").workplane()
                   .pushPoints([(x, y)])
                   .hole(self.p.m3_hole_diameter)
            )

        # Central LiDAR mounting platform
        lidar_mount = self._create_lidar_mount()
        ring = ring.union(lidar_mount.translate((0, 0, self.layers['sensors'])))

        # GPS antenna bracket (to the side)
        gps_bracket = self._create_gps_bracket()
        gps_x = self.p.base_diameter / 2 - 30
        ring = ring.union(gps_bracket.translate((gps_x, 0, self.layers['sensors'] + 3)))

        # Camera mounts (front, angled down slightly)
        camera_mount = self._create_camera_mount()
        camera_y = self.p.base_diameter / 2 - 20
        ring = ring.union(camera_mount.translate((0, camera_y, self.layers['sensors'])))

        print("✅ Sensor ring complete")
        return ring

    # ========================================================================
    # HELPER METHODS - Component mounting details
    # ========================================================================

    def _get_mounting_post_positions(self) -> list:
        """Returns positions for 4 structural mounting posts in square pattern"""
        offset = 60  # Distance from center
        return [
            (offset, offset),
            (-offset, offset),
            (-offset, -offset),
            (offset, -offset)
        ]

    def _create_motor_mount(self) -> cq.Workplane:
        """Create L-bracket for TT motor mounting"""

        bracket = (cq.Workplane("XZ")
                  .rect(30, 25)
                  .extrude(self.p.wall_thickness)
        )

        # Mounting holes for motor
        hole_spacing = 20
        bracket = (bracket.faces(">Y").workplane()
                  .pushPoints([
                      (0, 10),
                      (-hole_spacing/2, 10),
                      (hole_spacing/2, 10)
                  ])
                  .hole(self.p.m3_hole_diameter)
        )

        # Wire routing slot
        bracket = (bracket.faces(">Y").workplane()
                  .rect(8, 5)
                  .cutThruAll()
        )

        return bracket

    def _create_caster_mount(self) -> cq.Workplane:
        """Create front caster wheel mount"""

        mount = (cq.Workplane("XY")
                .rect(30, 20)
                .extrude(self.p.base_height)
        )

        # Mounting holes for caster
        mount = (mount.faces(">Z").workplane()
                .pushPoints([
                    (-10, -7),
                    (10, -7),
                    (-10, 7),
                    (10, 7)
                ])
                .hole(self.p.m3_hole_diameter)
        )

        return mount

    def _add_cable_channels(self, base: cq.Workplane) -> cq.Workplane:
        """Add grooves for cable routing in base plate"""

        # Simple cross-pattern channels
        channel_width = 5
        channel_depth = 2

        # X-axis channel
        channel_x = (cq.Workplane("XY")
                    .rect(self.p.base_diameter - 20, channel_width)
                    .extrude(channel_depth)
        )
        base = base.cut(channel_x)

        # Y-axis channel
        channel_y = (cq.Workplane("XY")
                    .rect(channel_width, self.p.base_diameter - 20)
                    .extrude(channel_depth)
        )
        base = base.cut(channel_y)

        return base

    def _create_pi5_tray(self) -> cq.Workplane:
        """Create removable Raspberry Pi 5 mounting tray"""

        tray_margin = 3
        tray_length = self.p.pi5_length + 2 * tray_margin
        tray_width = self.p.pi5_width + 2 * tray_margin

        # Base tray
        tray = (cq.Workplane("XY")
               .rect(tray_length, tray_width)
               .extrude(2)
        )

        # Standoffs for Pi 5 (4 corners)
        standoff_positions = [
            (-self.p.pi5_mount_hole_spacing_length/2, -self.p.pi5_mount_hole_spacing_width/2),
            (self.p.pi5_mount_hole_spacing_length/2, -self.p.pi5_mount_hole_spacing_width/2),
            (-self.p.pi5_mount_hole_spacing_length/2, self.p.pi5_mount_hole_spacing_width/2),
            (self.p.pi5_mount_hole_spacing_length/2, self.p.pi5_mount_hole_spacing_width/2),
        ]

        for x, y in standoff_positions:
            standoff = (cq.Workplane("XY")
                       .workplane(offset=2)
                       .circle(4)
                       .extrude(self.p.pi5_standoff_height)
                       .faces(">Z").workplane()
                       .hole(self.p.pi5_mount_hole_diameter)
            )
            tray = tray.union(standoff.translate((x, y, 0)))

        # GPIO access cutout
        gpio_cutout = (cq.Workplane("XY")
                      .workplane(offset=2)
                      .rect(55, tray_width + 2)
                      .extrude(self.p.pi5_standoff_height + 2)
                      .translate((tray_length/2 - 15, 0, 0))
        )
        tray = tray.cut(gpio_cutout)

        # Ventilation slots - simplified approach
        for i in range(-2, 3):
            slot_y = i * 10
            if abs(slot_y) > 5:  # Skip center area with standoffs
                vent_cut = (cq.Workplane("XY")
                           .workplane(offset=1)
                           .rect(tray_length - 25, 3)
                           .extrude(2)
                           .translate((0, slot_y, 0))
                )
                tray = tray.cut(vent_cut)

        return tray

    def _create_battery_compartment(self) -> cq.Workplane:
        """Create walls for battery bay"""

        length = self.p.battery_length + self.p.battery_clearance * 2
        width = self.p.battery_width + self.p.battery_clearance * 2
        wall_h = self.p.battery_height + 5
        wall_t = 2

        # U-shaped walls (open at front for easy access)
        walls = (cq.Workplane("XY")
                .rect(length, width)
                .rect(length - 2*wall_t, width - 2*wall_t)
                .extrude(wall_h)
        )

        # Remove front wall for access
        front_cut = (cq.Workplane("XY")
                    .rect(length + 2, wall_t + 2)
                    .extrude(wall_h + 2)
                    .translate((0, width/2, -1))
        )
        walls = walls.cut(front_cut)

        # Velcro strap slots (top edges)
        strap_slot = (cq.Workplane("XY")
                     .workplane(offset=wall_h - 3)
                     .rect(length - 10, 2)
                     .extrude(3)
        )
        walls = walls.cut(strap_slot)

        return walls.translate((0, 0, 3))

    def _create_lidar_mount(self) -> cq.Workplane:
        """Create central mounting platform for RPLIDAR A1"""

        # Central pedestal
        pedestal_height = 30
        pedestal = (cq.Workplane("XY")
                   .circle(15)
                   .extrude(pedestal_height)
        )

        # Top mounting plate
        plate = (cq.Workplane("XY")
                .workplane(offset=pedestal_height)
                .circle(self.p.lidar_diameter / 2 + 5)
                .extrude(4)
        )

        # RPLIDAR mounting holes (4x M3 in circle pattern)
        angle_step = 360 / self.p.lidar_mount_holes
        for i in range(self.p.lidar_mount_holes):
            angle = math.radians(i * angle_step)
            x = (self.p.lidar_mount_circle_diameter / 2) * math.cos(angle)
            y = (self.p.lidar_mount_circle_diameter / 2) * math.sin(angle)

            plate = (plate.faces(">Z").workplane()
                    .pushPoints([(x, y)])
                    .hole(self.p.lidar_mount_hole_diameter)
            )

        # Cable routing hole through center
        plate = (plate.faces(">Z").workplane()
                .circle(8)
                .cutThruAll()
        )

        return pedestal.union(plate)

    def _create_gps_bracket(self) -> cq.Workplane:
        """Create small bracket for GPS module"""

        bracket = (cq.Workplane("XY")
                  .rect(self.p.gps_module_length + 4, self.p.gps_module_width + 4)
                  .extrude(2)
        )

        # Standoffs
        standoff_positions = [(-8, -8), (8, -8), (-8, 8), (8, 8)]
        for x, y in standoff_positions:
            standoff = (cq.Workplane("XY")
                       .workplane(offset=2)
                       .circle(2)
                       .extrude(5)
                       .faces(">Z").workplane()
                       .hole(2)
            )
            bracket = bracket.union(standoff.translate((x, y, 0)))

        return bracket

    def _create_camera_mount(self) -> cq.Workplane:
        """Create bracket for camera (Pi Camera or USB cam)"""

        # Simple angled bracket
        mount = (cq.Workplane("XZ")
                .rect(40, 25)
                .extrude(3)
        )

        # Mounting holes
        mount = (mount.faces(">Y").workplane()
                .pushPoints([(-12, 10), (12, 10)])
                .hole(3)
        )

        # Rotate slightly down (15 degrees)
        mount = mount.rotate((0, 0, 0), (1, 0, 0), -15)

        return mount

    # ========================================================================
    # EXPORT METHODS
    # ========================================================================

    def generate_all_parts(self) -> Dict[str, cq.Workplane]:
        """Generate all chassis parts"""

        print("\n" + "="*60)
        print("🤖 GENERATING FLATHEAD ROBOT CHASSIS")
        print("="*60 + "\n")

        parts = {
            'base_plate': self.create_base_plate(),
            'electronics_deck': self.create_electronics_deck(),
            'sensor_ring': self.create_sensor_ring(),
        }

        print("\n" + "="*60)
        print("✅ ALL PARTS GENERATED SUCCESSFULLY!")
        print("="*60 + "\n")

        return parts

    def export_stl(self, parts: Dict[str, cq.Workplane], output_dir: str = "."):
        """Export all parts to STL files"""

        print(f"\n📦 Exporting STL files to {output_dir}/...")

        for name, part in parts.items():
            filename = f"{output_dir}/flathead_{name}.stl"
            cq.exporters.export(part, filename)
            print(f"  ✅ {filename}")

        print("\n🎉 Export complete!")

    def export_step(self, parts: Dict[str, cq.Workplane], output_dir: str = "."):
        """Export all parts to STEP files (for CAD software)"""

        print(f"\n📦 Exporting STEP files to {output_dir}/...")

        for name, part in parts.items():
            filename = f"{output_dir}/flathead_{name}.step"
            cq.exporters.export(part, filename)
            print(f"  ✅ {filename}")

        print("\n🎉 Export complete!")

    def print_specifications(self):
        """Print design specifications"""

        print("\n" + "="*60)
        print("📐 CHASSIS SPECIFICATIONS")
        print("="*60)
        print(f"  Overall diameter:        {self.p.base_diameter}mm")
        print(f"  Total height:            ~{self.p.base_height + 2*self.p.layer_spacing + 30}mm")
        print(f"  Base plate thickness:    {self.p.base_height}mm")
        print(f"  Layer spacing:           {self.p.layer_spacing}mm")
        print(f"  Motor mount spacing:     {self.p.motor_mount_spacing}mm")
        print(f"  LiDAR center height:     ~{self.layers['sensors'] + 35}mm")
        print(f"  Estimated print time:    8-12 hours (all parts)")
        print(f"  Estimated material:      ~250-300g PETG")
        print("="*60 + "\n")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    # Create designer
    designer = ChassisDesigner()

    # Generate all parts
    parts = designer.generate_all_parts()

    # Export to STL (ready for 3D printing)
    designer.export_stl(parts, "./output")

    # Also export STEP (can open in Fusion 360, FreeCAD, etc.)
    designer.export_step(parts, "./output")

    # Print specifications
    designer.print_specifications()

    print("\n🎨 DESIGN COMPLETE!")
    print("📁 Files ready in ./output/")
    print("🖨️ Ready for 3D printing or further modifications!")
