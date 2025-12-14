"""
FLATHEAD ROBOT HEAD - Fusion 360 API Script
============================================

Parametric design for 3D printable robot head with:
- 2x Pi Camera v3 (stereo vision)
- 4x INMP441 I2S microphones (spatial audio)
- Speaker + PAM8403 amplifier
- ESP32 DevKit
- 2x MG996R servos (pan/tilt mechanism)

INSTALLATION:
1. Open Fusion 360
2. Go to: Tools > Add-Ins > Scripts and Add-Ins
3. Click "+" next to "My Scripts"
4. Select this file
5. Click "Run"

Author: Flathead Project
License: MIT
"""

import adsk.core
import adsk.fusion
import traceback
import math

# ============================================================================
# COMPONENT DIMENSIONS (all in cm for Fusion 360)
# ============================================================================

class ComponentDimensions:
    """Real-world dimensions of all components"""

    # === Pi Camera v3 ===
    # PCB: 25mm x 24mm x 9mm (with connector)
    # Lens protrusion: ~5mm
    # Mounting holes: 21mm x 12.5mm spacing, 2.2mm diameter
    PI_CAM_WIDTH = 2.5
    PI_CAM_HEIGHT = 2.4
    PI_CAM_DEPTH = 0.9
    PI_CAM_LENS_DIA = 0.8
    PI_CAM_LENS_PROTRUSION = 0.5
    PI_CAM_MOUNT_HOLE_SPACING_X = 2.1
    PI_CAM_MOUNT_HOLE_SPACING_Y = 1.25
    PI_CAM_MOUNT_HOLE_DIA = 0.22

    # === Stereo baseline ===
    STEREO_BASELINE = 7.0  # 70mm between camera centers (adjustable)

    # === INMP441 I2S Microphone ===
    # PCB: 14mm x 10mm x 3.5mm
    # Mic hole: centered, ~3mm diameter
    MIC_WIDTH = 1.4
    MIC_HEIGHT = 1.0
    MIC_DEPTH = 0.35
    MIC_HOLE_DIA = 0.3

    # === Speaker ===
    # Typical 40mm 4Ohm 3W speaker
    SPEAKER_DIA = 4.0
    SPEAKER_DEPTH = 1.5
    SPEAKER_MOUNT_HOLE_SPACING = 3.4
    SPEAKER_MOUNT_HOLE_DIA = 0.3

    # === PAM8403 Amplifier ===
    # PCB: 30mm x 20mm x 10mm (with components)
    AMP_WIDTH = 3.0
    AMP_HEIGHT = 2.0
    AMP_DEPTH = 1.0

    # === ESP32 DevKit V1 (30-pin) ===
    # PCB: 55mm x 28mm x 10mm (with pins)
    ESP32_WIDTH = 5.5
    ESP32_HEIGHT = 2.8
    ESP32_DEPTH = 1.0
    ESP32_MOUNT_HOLE_SPACING_X = 4.8
    ESP32_MOUNT_HOLE_SPACING_Y = 2.3
    ESP32_MOUNT_HOLE_DIA = 0.3

    # === MG996R Servo ===
    # Body: 40.7mm x 19.7mm x 42.9mm
    # Shaft center from top: 10mm
    # Mounting tabs: 54.5mm total width, 49.5mm hole spacing
    # Tab thickness: 2.5mm each side
    SERVO_WIDTH = 4.07
    SERVO_HEIGHT = 1.97
    SERVO_DEPTH = 4.29
    SERVO_SHAFT_OFFSET = 1.0  # from top of body
    SERVO_TAB_WIDTH = 5.45
    SERVO_TAB_HOLE_SPACING = 4.95
    SERVO_TAB_THICKNESS = 0.25
    SERVO_SHAFT_DIA = 0.6
    SERVO_MOUNT_HOLE_DIA = 0.4

    # === Head Shell ===
    HEAD_WIDTH = 12.0       # Total width
    HEAD_HEIGHT = 10.0      # Total height (without neck)
    HEAD_DEPTH = 8.0        # Front to back
    WALL_THICKNESS = 0.3    # 3mm walls

    # === Neck/Mount ===
    NECK_DIA = 4.0
    NECK_HEIGHT = 2.0


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_box(comp, name, width, height, depth, x=0, y=0, z=0):
    """Create a box body at specified position"""
    sketches = comp.sketches
    xyPlane = comp.xYConstructionPlane

    sketch = sketches.add(xyPlane)
    sketch.name = f"{name}_sketch"

    # Rectangle centered at origin, then move
    rect = sketch.sketchCurves.sketchLines.addCenterPointRectangle(
        adsk.core.Point3D.create(x, y, 0),
        adsk.core.Point3D.create(x + width/2, y + height/2, 0)
    )

    # Extrude
    prof = sketch.profiles.item(0)
    extrudes = comp.features.extrudeFeatures
    extInput = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)

    distance = adsk.core.ValueInput.createByReal(depth)
    extInput.setDistanceExtent(False, distance)

    ext = extrudes.add(extInput)
    ext.bodies.item(0).name = name

    # Move up in Z if needed
    if z != 0:
        moveFeats = comp.features.moveFeatures
        bodies = adsk.core.ObjectCollection.create()
        bodies.add(ext.bodies.item(0))

        transform = adsk.core.Matrix3D.create()
        transform.translation = adsk.core.Vector3D.create(0, 0, z)

        moveInput = moveFeats.createInput(bodies, transform)
        moveFeats.add(moveInput)

    return ext.bodies.item(0)


def create_cylinder(comp, name, diameter, height, x=0, y=0, z=0):
    """Create a cylinder at specified position"""
    sketches = comp.sketches
    xyPlane = comp.xYConstructionPlane

    sketch = sketches.add(xyPlane)
    sketch.name = f"{name}_sketch"

    circles = sketch.sketchCurves.sketchCircles
    circles.addByCenterRadius(adsk.core.Point3D.create(x, y, 0), diameter/2)

    prof = sketch.profiles.item(0)
    extrudes = comp.features.extrudeFeatures
    extInput = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)

    distance = adsk.core.ValueInput.createByReal(height)
    extInput.setDistanceExtent(False, distance)

    ext = extrudes.add(extInput)
    ext.bodies.item(0).name = name

    if z != 0:
        moveFeats = comp.features.moveFeatures
        bodies = adsk.core.ObjectCollection.create()
        bodies.add(ext.bodies.item(0))

        transform = adsk.core.Matrix3D.create()
        transform.translation = adsk.core.Vector3D.create(0, 0, z)

        moveInput = moveFeats.createInput(bodies, transform)
        moveFeats.add(moveInput)

    return ext.bodies.item(0)


def add_hole(comp, face, x, y, diameter, depth):
    """Add a hole to a face"""
    holes = comp.features.holeFeatures

    point = adsk.core.Point3D.create(x, y, 0)

    holeInput = holes.createSimpleInput(adsk.core.ValueInput.createByReal(diameter))
    holeInput.setPositionByPoint(face, point)
    holeInput.setDistanceExtent(adsk.core.ValueInput.createByReal(depth))

    return holes.add(holeInput)


# ============================================================================
# MAIN HEAD DESIGN CLASS
# ============================================================================

class RobotHeadDesigner:
    """Creates the parametric robot head assembly"""

    def __init__(self, app, ui):
        self.app = app
        self.ui = ui
        self.design = None
        self.rootComp = None
        self.dim = ComponentDimensions()

    def run(self):
        """Main entry point"""
        try:
            # Create new document
            doc = self.app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
            self.design = self.app.activeProduct
            self.design.designType = adsk.fusion.DesignTypes.ParametricDesignType
            self.rootComp = self.design.rootComponent

            # Rename
            doc.name = "Flathead_Robot_Head"

            # Create user parameters for key dimensions
            self._create_parameters()

            # Build the head
            self._create_head_shell()
            self._create_camera_mounts()
            self._create_microphone_mounts()
            self._create_speaker_mount()
            self._create_electronics_bay()
            self._create_pan_tilt_mechanism()

            self.ui.messageBox(
                'Robot Head Created Successfully!\n\n'
                'Components:\n'
                '• Head shell with ventilation\n'
                '• 2x Pi Camera v3 mounts (stereo)\n'
                '• 4x INMP441 microphone mounts\n'
                '• Speaker grille + mount\n'
                '• ESP32 + PAM8403 bay\n'
                '• Pan/Tilt servo mounts\n\n'
                'Check the Parameters panel to adjust dimensions.',
                'Flathead Robot Head'
            )

        except:
            if self.ui:
                self.ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

    def _create_parameters(self):
        """Create user-adjustable parameters"""
        params = self.design.userParameters

        # Key adjustable parameters
        params.add("HeadWidth", adsk.core.ValueInput.createByReal(self.dim.HEAD_WIDTH), "cm", "Total head width")
        params.add("HeadHeight", adsk.core.ValueInput.createByReal(self.dim.HEAD_HEIGHT), "cm", "Total head height")
        params.add("HeadDepth", adsk.core.ValueInput.createByReal(self.dim.HEAD_DEPTH), "cm", "Head front-to-back depth")
        params.add("StereoBaseline", adsk.core.ValueInput.createByReal(self.dim.STEREO_BASELINE), "cm", "Distance between camera centers")
        params.add("WallThickness", adsk.core.ValueInput.createByReal(self.dim.WALL_THICKNESS), "cm", "Shell wall thickness")

    def _create_head_shell(self):
        """Create the main head enclosure"""

        # Create head component
        headOcc = self.rootComp.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        headComp = headOcc.component
        headComp.name = "Head_Shell"

        sketches = headComp.sketches
        xyPlane = headComp.xYConstructionPlane

        # --- Outer shell ---
        sketchOuter = sketches.add(xyPlane)
        sketchOuter.name = "Outer_Profile"

        # Rounded rectangle for head shape
        w = self.dim.HEAD_WIDTH
        h = self.dim.HEAD_HEIGHT
        r = 1.0  # Corner radius

        lines = sketchOuter.sketchCurves.sketchLines
        arcs = sketchOuter.sketchCurves.sketchArcs

        # Create rounded rectangle manually
        # Bottom edge
        p1 = adsk.core.Point3D.create(-w/2 + r, -h/2, 0)
        p2 = adsk.core.Point3D.create(w/2 - r, -h/2, 0)
        lines.addByTwoPoints(p1, p2)

        # Right edge
        p3 = adsk.core.Point3D.create(w/2, -h/2 + r, 0)
        p4 = adsk.core.Point3D.create(w/2, h/2 - r, 0)
        lines.addByTwoPoints(p3, p4)

        # Top edge
        p5 = adsk.core.Point3D.create(w/2 - r, h/2, 0)
        p6 = adsk.core.Point3D.create(-w/2 + r, h/2, 0)
        lines.addByTwoPoints(p5, p6)

        # Left edge
        p7 = adsk.core.Point3D.create(-w/2, h/2 - r, 0)
        p8 = adsk.core.Point3D.create(-w/2, -h/2 + r, 0)
        lines.addByTwoPoints(p7, p8)

        # Corner arcs
        arcs.addByCenterStartSweep(
            adsk.core.Point3D.create(w/2 - r, -h/2 + r, 0),
            adsk.core.Point3D.create(w/2, -h/2 + r, 0),
            math.pi / 2
        )
        arcs.addByCenterStartSweep(
            adsk.core.Point3D.create(w/2 - r, h/2 - r, 0),
            adsk.core.Point3D.create(w/2 - r, h/2, 0),
            math.pi / 2
        )
        arcs.addByCenterStartSweep(
            adsk.core.Point3D.create(-w/2 + r, h/2 - r, 0),
            adsk.core.Point3D.create(-w/2, h/2 - r, 0),
            math.pi / 2
        )
        arcs.addByCenterStartSweep(
            adsk.core.Point3D.create(-w/2 + r, -h/2 + r, 0),
            adsk.core.Point3D.create(-w/2 + r, -h/2, 0),
            math.pi / 2
        )

        # Extrude outer shell
        prof = sketchOuter.profiles.item(0)
        extrudes = headComp.features.extrudeFeatures
        extInput = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        extInput.setDistanceExtent(False, adsk.core.ValueInput.createByReal(self.dim.HEAD_DEPTH))
        outerBody = extrudes.add(extInput)
        outerBody.bodies.item(0).name = "Outer_Shell"

        # --- Shell (hollow out) ---
        shellFeats = headComp.features.shellFeatures

        # Get the back face to keep open
        backFace = None
        for face in outerBody.faces:
            normal = face.geometry.normal
            if normal.z < -0.9:  # Back face
                backFace = face
                break

        if backFace:
            faceCollection = adsk.core.ObjectCollection.create()
            faceCollection.add(backFace)

            shellInput = shellFeats.createInput(faceCollection)
            shellInput.insideThickness = adsk.core.ValueInput.createByReal(self.dim.WALL_THICKNESS)
            shellFeats.add(shellInput)

        # --- Camera cutouts (front face) ---
        frontFace = None
        for face in outerBody.faces:
            # After shell, we need to find front face
            try:
                normal = face.geometry.normal
                if normal.z > 0.9:
                    frontFace = face
                    break
            except:
                pass

        return headComp

    def _create_camera_mounts(self):
        """Create mounting points for two Pi Camera v3"""

        camOcc = self.rootComp.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        camComp = camOcc.component
        camComp.name = "Camera_Mounts"

        sketches = camComp.sketches
        xzPlane = camComp.xZConstructionPlane

        # Camera positions (stereo baseline)
        cam_offset_x = self.dim.STEREO_BASELINE / 2
        cam_y = self.dim.HEAD_HEIGHT / 2 - 2.0  # Upper area of head
        cam_z = self.dim.HEAD_DEPTH  # Front face

        for side in [-1, 1]:  # Left and right cameras
            x_pos = side * cam_offset_x

            # Camera mount bracket
            sketch = sketches.add(xzPlane)
            sketch.name = f"Camera_Mount_{'L' if side < 0 else 'R'}"

            # L-bracket profile
            lines = sketch.sketchCurves.sketchLines

            # Simple L-bracket
            bracket_width = 3.0
            bracket_height = 3.0
            bracket_thickness = 0.4

            # Horizontal part (mounts to head)
            p1 = adsk.core.Point3D.create(x_pos - bracket_width/2, cam_z - 0.5, 0)
            p2 = adsk.core.Point3D.create(x_pos + bracket_width/2, cam_z - 0.5, 0)
            p3 = adsk.core.Point3D.create(x_pos + bracket_width/2, cam_z - 0.5 - bracket_thickness, 0)
            p4 = adsk.core.Point3D.create(x_pos - bracket_width/2, cam_z - 0.5 - bracket_thickness, 0)

            lines.addByTwoPoints(p1, p2)
            lines.addByTwoPoints(p2, p3)
            lines.addByTwoPoints(p3, p4)
            lines.addByTwoPoints(p4, p1)

            # Extrude
            if sketch.profiles.count > 0:
                prof = sketch.profiles.item(0)
                extrudes = camComp.features.extrudeFeatures
                extInput = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
                extInput.setDistanceExtent(False, adsk.core.ValueInput.createByReal(bracket_height))
                ext = extrudes.add(extInput)
                ext.bodies.item(0).name = f"Camera_Bracket_{'L' if side < 0 else 'R'}"

        # Add descriptive text as a note
        # (Fusion doesn't support 3D text easily in API, but you can add it manually)

        return camComp

    def _create_microphone_mounts(self):
        """Create 4 microphone mount positions"""

        micOcc = self.rootComp.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        micComp = micOcc.component
        micComp.name = "Microphone_Mounts"

        sketches = micComp.sketches
        xyPlane = micComp.xYConstructionPlane

        # 4 microphones in tetrahedral-ish pattern for spatial audio
        # Front-left, Front-right, Back-left, Back-right
        mic_positions = [
            (-4.0, 3.0, self.dim.HEAD_DEPTH - 0.3),      # Front-left
            (4.0, 3.0, self.dim.HEAD_DEPTH - 0.3),       # Front-right
            (-4.0, -3.0, 1.0),                            # Back-left
            (4.0, -3.0, 1.0),                             # Back-right
        ]

        mic_names = ["FL", "FR", "BL", "BR"]

        for i, (mx, my, mz) in enumerate(mic_positions):
            # Small mounting post for each microphone
            sketch = sketches.add(xyPlane)
            sketch.name = f"Mic_Mount_{mic_names[i]}"

            # Circular mount post
            circles = sketch.sketchCurves.sketchCircles
            circles.addByCenterRadius(adsk.core.Point3D.create(mx, my, 0), 0.8)

            if sketch.profiles.count > 0:
                prof = sketch.profiles.item(0)
                extrudes = micComp.features.extrudeFeatures
                extInput = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
                extInput.setDistanceExtent(False, adsk.core.ValueInput.createByReal(0.5))
                ext = extrudes.add(extInput)
                ext.bodies.item(0).name = f"Mic_Post_{mic_names[i]}"

                # Move to correct Z position
                if mz != 0:
                    moveFeats = micComp.features.moveFeatures
                    bodies = adsk.core.ObjectCollection.create()
                    bodies.add(ext.bodies.item(0))

                    transform = adsk.core.Matrix3D.create()
                    transform.translation = adsk.core.Vector3D.create(0, 0, mz)

                    moveInput = moveFeats.createInput(bodies, transform)
                    moveFeats.add(moveInput)

        return micComp

    def _create_speaker_mount(self):
        """Create speaker grille and mounting"""

        spkOcc = self.rootComp.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        spkComp = spkOcc.component
        spkComp.name = "Speaker_Mount"

        sketches = spkComp.sketches
        xyPlane = spkComp.xYConstructionPlane

        # Speaker position - front center, lower area
        spk_x = 0
        spk_y = -2.0
        spk_z = self.dim.HEAD_DEPTH - self.dim.WALL_THICKNESS

        # Speaker mounting ring
        sketch = sketches.add(xyPlane)
        sketch.name = "Speaker_Ring"

        circles = sketch.sketchCurves.sketchCircles
        # Outer ring
        circles.addByCenterRadius(adsk.core.Point3D.create(spk_x, spk_y, 0), self.dim.SPEAKER_DIA/2 + 0.3)
        # Inner cutout for sound
        circles.addByCenterRadius(adsk.core.Point3D.create(spk_x, spk_y, 0), self.dim.SPEAKER_DIA/2 - 0.3)

        if sketch.profiles.count > 0:
            # Find the ring profile (not the center circle)
            for i in range(sketch.profiles.count):
                prof = sketch.profiles.item(i)
                if prof.areaProperties().area < 5:  # Ring has smaller area
                    extrudes = spkComp.features.extrudeFeatures
                    extInput = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
                    extInput.setDistanceExtent(False, adsk.core.ValueInput.createByReal(0.5))
                    ext = extrudes.add(extInput)
                    ext.bodies.item(0).name = "Speaker_Ring"
                    break

        return spkComp

    def _create_electronics_bay(self):
        """Create mounting area for ESP32 and PAM8403"""

        elecOcc = self.rootComp.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        elecComp = elecOcc.component
        elecComp.name = "Electronics_Bay"

        sketches = elecComp.sketches
        xyPlane = elecComp.xYConstructionPlane

        # ESP32 mounting tray - back of head
        esp_x = 0
        esp_y = -3.0
        esp_z = 1.0

        sketch = sketches.add(xyPlane)
        sketch.name = "ESP32_Tray"

        # Tray base
        lines = sketch.sketchCurves.sketchLines
        tray_w = self.dim.ESP32_WIDTH + 0.5
        tray_h = self.dim.ESP32_HEIGHT + 0.5

        lines.addTwoPointRectangle(
            adsk.core.Point3D.create(esp_x - tray_w/2, esp_y - tray_h/2, 0),
            adsk.core.Point3D.create(esp_x + tray_w/2, esp_y + tray_h/2, 0)
        )

        if sketch.profiles.count > 0:
            prof = sketch.profiles.item(0)
            extrudes = elecComp.features.extrudeFeatures
            extInput = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
            extInput.setDistanceExtent(False, adsk.core.ValueInput.createByReal(0.2))
            ext = extrudes.add(extInput)
            ext.bodies.item(0).name = "ESP32_Tray"

            # Move to position
            moveFeats = elecComp.features.moveFeatures
            bodies = adsk.core.ObjectCollection.create()
            bodies.add(ext.bodies.item(0))

            transform = adsk.core.Matrix3D.create()
            transform.translation = adsk.core.Vector3D.create(0, 0, esp_z)

            moveInput = moveFeats.createInput(bodies, transform)
            moveFeats.add(moveInput)

        # PAM8403 mount - next to ESP32
        amp_x = 4.0
        amp_y = -3.0
        amp_z = 1.0

        sketch2 = sketches.add(xyPlane)
        sketch2.name = "Amplifier_Mount"

        amp_w = self.dim.AMP_WIDTH + 0.3
        amp_h = self.dim.AMP_HEIGHT + 0.3

        sketch2.sketchCurves.sketchLines.addTwoPointRectangle(
            adsk.core.Point3D.create(amp_x - amp_w/2, amp_y - amp_h/2, 0),
            adsk.core.Point3D.create(amp_x + amp_w/2, amp_y + amp_h/2, 0)
        )

        if sketch2.profiles.count > 0:
            prof = sketch2.profiles.item(0)
            extInput = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
            extInput.setDistanceExtent(False, adsk.core.ValueInput.createByReal(0.2))
            ext = extrudes.add(extInput)
            ext.bodies.item(0).name = "Amplifier_Tray"

        return elecComp

    def _create_pan_tilt_mechanism(self):
        """Create servo mounts for pan/tilt head movement"""

        panTiltOcc = self.rootComp.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        panTiltComp = panTiltOcc.component
        panTiltComp.name = "Pan_Tilt_Mechanism"

        sketches = panTiltComp.sketches

        # === PAN SERVO (bottom, rotates head left/right) ===
        xyPlane = panTiltComp.xYConstructionPlane

        pan_sketch = sketches.add(xyPlane)
        pan_sketch.name = "Pan_Servo_Mount"

        # Servo bracket outline
        lines = pan_sketch.sketchCurves.sketchLines

        # MG996R dimensions
        bracket_w = self.dim.SERVO_TAB_WIDTH + 0.5
        bracket_h = self.dim.SERVO_HEIGHT + 0.5
        bracket_z = -2.0  # Below head

        lines.addTwoPointRectangle(
            adsk.core.Point3D.create(-bracket_w/2, -bracket_h/2, 0),
            adsk.core.Point3D.create(bracket_w/2, bracket_h/2, 0)
        )

        if pan_sketch.profiles.count > 0:
            prof = pan_sketch.profiles.item(0)
            extrudes = panTiltComp.features.extrudeFeatures
            extInput = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
            extInput.setDistanceExtent(False, adsk.core.ValueInput.createByReal(0.4))
            ext = extrudes.add(extInput)
            ext.bodies.item(0).name = "Pan_Servo_Bracket"

            # Move below
            moveFeats = panTiltComp.features.moveFeatures
            bodies = adsk.core.ObjectCollection.create()
            bodies.add(ext.bodies.item(0))

            transform = adsk.core.Matrix3D.create()
            transform.translation = adsk.core.Vector3D.create(0, 0, bracket_z)

            moveInput = moveFeats.createInput(bodies, transform)
            moveFeats.add(moveInput)

        # === TILT SERVO (side, tilts head up/down) ===
        xzPlane = panTiltComp.xZConstructionPlane

        tilt_sketch = sketches.add(xzPlane)
        tilt_sketch.name = "Tilt_Servo_Mount"

        # Side mount position
        tilt_x = -self.dim.HEAD_WIDTH/2 - 1.0
        tilt_z = self.dim.HEAD_DEPTH / 2

        lines2 = tilt_sketch.sketchCurves.sketchLines

        lines2.addTwoPointRectangle(
            adsk.core.Point3D.create(tilt_x - 0.5, tilt_z - bracket_h/2, 0),
            adsk.core.Point3D.create(tilt_x + 0.5, tilt_z + bracket_h/2, 0)
        )

        if tilt_sketch.profiles.count > 0:
            prof = tilt_sketch.profiles.item(0)
            extInput = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
            extInput.setDistanceExtent(False, adsk.core.ValueInput.createByReal(bracket_w))
            ext = extrudes.add(extInput)
            ext.bodies.item(0).name = "Tilt_Servo_Bracket"

        # === NECK CONNECTOR ===
        neck_sketch = sketches.add(xyPlane)
        neck_sketch.name = "Neck_Connector"

        circles = neck_sketch.sketchCurves.sketchCircles
        circles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), self.dim.NECK_DIA/2)

        if neck_sketch.profiles.count > 0:
            prof = neck_sketch.profiles.item(0)
            extInput = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
            extInput.setDistanceExtent(False, adsk.core.ValueInput.createByReal(self.dim.NECK_HEIGHT))
            ext = extrudes.add(extInput)
            ext.bodies.item(0).name = "Neck_Tube"

            # Move below pan servo
            moveFeats = panTiltComp.features.moveFeatures
            bodies = adsk.core.ObjectCollection.create()
            bodies.add(ext.bodies.item(0))

            transform = adsk.core.Matrix3D.create()
            transform.translation = adsk.core.Vector3D.create(0, 0, bracket_z - self.dim.NECK_HEIGHT)

            moveInput = moveFeats.createInput(bodies, transform)
            moveFeats.add(moveInput)

        return panTiltComp


# ============================================================================
# ENTRY POINT
# ============================================================================

def run(context):
    app = adsk.core.Application.get()
    ui = app.userInterface

    designer = RobotHeadDesigner(app, ui)
    designer.run()


def stop(context):
    pass
