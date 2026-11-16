"""Dimer frame guideline generator (CadQuery).

Run:  pip install cadquery && python cad/dimer_frame.py
Writes STEP files into cad/step/.  Units: mm.
Axes: X = forward, Y = left, Z = up, table surface at Z = 0.

This is a ROUGH GUIDELINE, not a design: it fixes where the parts sit and
where the mounting holes go.  Change the numbers below after measuring the
parts you actually bought, then run again.
"""
import json, os, sys
import cadquery as cq

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "step")
os.makedirs(OUT, exist_ok=True)

# ---------------- parameters (edit me) ----------------
TUB_L, TUB_W_IN, WALL = 150.0, 74.0, 3.0      # chassis tub
FLOOR_Z, FLOOR_T, WALL_TOP = 8.0, 3.0, 44.0   # ground clearance 8 mm
TUB_W = TUB_W_IN + 2 * WALL                   # 80
AXLE_Z, WHEELBASE = 17.0, 110.0               # drive sprocket rear, idler front
WHEEL_D, TRACK_W, TRACK_T, TRACK_GAP = 30.0, 22.0, 3.0, 3.0
TRACK_Y = TUB_W / 2 + TRACK_GAP + TRACK_W / 2
PCB_L, PCB_W, PCB_Z = 100.0, 70.0, 46.0        # main board, underside height
PCB_X = -12.0                                  # board centre
PCB_HOLE_DX, PCB_HOLE_DY = 92.0, 62.0          # M3 hole pattern (matches the PCB)
BAT = (77.0, 41.0, 21.0)                       # 2x18650 holder
BAT_X = -6.5
PAN_X = 58.0                                   # head rotation axis
SERVO_BODY = (22.8, 12.2, 22.5)                # MG90S
SERVO_CUT = (23.4, 12.8)
HEAD = (46.0, 64.0, 52.0)                      # head frame envelope (x, y, z)
HEAD_Z = 64.0
SHOVEL_PIVOT = (65.0, 36.0)                    # x, z of shovel axis (left wall)
BLADE_H, BLADE_X = 26.0, 88.0

def box(x, y, z, cx=0, cy=0, z0=0):
    return cq.Workplane("XY").box(x, y, z, centered=(True, True, False)).translate((cx, cy, z0))

def ycyl(d, length, x, z, y0):
    """cylinder along +Y starting at y0"""
    return cq.Workplane("XZ").circle(d / 2).extrude(-length).translate((x, y0, z))

# ---------------- chassis tub ----------------
def chassis():
    outer = box(TUB_L, TUB_W, WALL_TOP - FLOOR_Z, z0=FLOOR_Z)
    inner = box(TUB_L - 2 * WALL, TUB_W_IN, WALL_TOP, z0=FLOOR_Z + FLOOR_T)
    tub = outer.cut(inner)
    # PCB standoff posts (M3 self-tap / heat-set insert, 2.5 mm pilot)
    for sx in (-1, 1):
        for sy in (-1, 1):
            px, py = PCB_X + sx * PCB_HOLE_DX / 2, sy * PCB_HOLE_DY / 2
            post = cq.Workplane("XY").circle(3.5).extrude(PCB_Z - FLOOR_Z).translate((px, py, FLOOR_Z))
            web = box(7, TUB_W_IN / 2 - abs(py), PCB_Z - FLOOR_Z - 6, cx=px, cy=sy * (abs(py) + TUB_W_IN / 2) / 2, z0=FLOOR_Z)
            tub = tub.union(post).union(web)
            tub = tub.cut(cq.Workplane("XY").circle(1.25).extrude(14).translate((px, py, PCB_Z - 14)))
    # axle / motor shaft holes through both walls
    for x, d in ((-WHEELBASE / 2, 4.2), (WHEELBASE / 2, 3.2)):
        tub = tub.cut(ycyl(d, TUB_W + 2, x, AXLE_Z, -TUB_W / 2 - 1))
    # N20 motor cradles (12 x 10 gearbox section) at the rear
    for sy in (-1, 1):
        cradle = box(16, 16, AXLE_Z + 2 - FLOOR_Z, cx=-WHEELBASE / 2, cy=sy * (TUB_W_IN / 2 - 8), z0=FLOOR_Z)
        slot = box(12.2, 17, 10.2, cx=-WHEELBASE / 2, cy=sy * (TUB_W_IN / 2 - 8), z0=AXLE_Z - 5.1)
        tub = tub.union(cradle).cut(slot)
    # shovel servo shaft opening in the left wall + pivot pin hole in the right wall
    tub = tub.cut(ycyl(13, WALL + 2, SHOVEL_PIVOT[0], SHOVEL_PIVOT[1], TUB_W_IN / 2 - 1))
    tub = tub.cut(ycyl(3.2, WALL + 2, SHOVEL_PIVOT[0], SHOVEL_PIVOT[1], -TUB_W / 2 - 1))
    # cable pass-throughs in the floor and battery strap slots
    for x in (-30, 20):
        tub = tub.cut(box(3, 30, FLOOR_T + 2, cx=x + BAT_X, z0=FLOOR_Z - 1))
    # edge-sensor tabs (TCRT5000 module, M3 hole) at the four corners, looking down
    for sx in (-1, 1):
        for sy in (-1, 1):
            tab = box(14, 16, FLOOR_T, cx=sx * (TUB_L / 2 + 7), cy=sy * 28, z0=FLOOR_Z)
            tab = tab.cut(cq.Workplane("XY").circle(1.6).extrude(10).translate((sx * (TUB_L / 2 + 8), sy * 28, FLOOR_Z - 1)))
            tub = tub.union(tab)
    # shell attachment ears on the wall tops (M3) - bolt your shell here
    for x in (-60, 20):
        for sy in (-1, 1):
            ear = box(10, 8, 4, cx=x, cy=sy * (TUB_W / 2 + 4), z0=WALL_TOP - 4)
            ear = ear.cut(cq.Workplane("XY").circle(1.6).extrude(6).translate((x, sy * (TUB_W / 2 + 4.5), WALL_TOP - 5)))
            tub = tub.union(ear)
    return tub

# ---------------- neck bridge (holds the pan servo) ----------------
def neck_bridge():
    plate = box(36, TUB_W, 4, cx=PAN_X - 1, z0=WALL_TOP)
    # servo shaft sits 6 mm from one end of the 22.8 mm body
    cut = box(SERVO_CUT[0], SERVO_CUT[1], 10, cx=PAN_X - (SERVO_BODY[0] / 2 - 6), z0=WALL_TOP - 2)
    plate = plate.cut(cut)
    for dx in (-(SERVO_BODY[0] / 2 - 6) - 13.9, -(SERVO_BODY[0] / 2 - 6) + 13.9):  # servo ear screws
        plate = plate.cut(cq.Workplane("XY").circle(1.0).extrude(10).translate((PAN_X + dx, 0, WALL_TOP - 2)))
    for x in (PAN_X - 14, PAN_X + 12):                                              # bolts into the walls
        for sy in (-1, 1):
            plate = plate.cut(cq.Workplane("XY").circle(1.6).extrude(10).translate((x, sy * (TUB_W / 2 - 1.5), WALL_TOP - 2)))
    return plate

# ---------------- head frame (holds the face display) ----------------
def head_frame():
    hx, hy, hz = HEAD
    shell = box(hx, hy, hz, cx=PAN_X, z0=HEAD_Z).cut(box(hx - 6, hy - 6, hz - 3, cx=PAN_X, z0=HEAD_Z + 3))
    # display window in the front face (2.0 inch 240x320 used landscape: 41 x 31 mm active)
    shell = shell.cut(box(8, 42, 32, cx=PAN_X + hx / 2 - 1.5, z0=HEAD_Z + 12))
    # servo horn screw + cable hole in the floor
    shell = shell.cut(cq.Workplane("XY").circle(3.5).extrude(6).translate((PAN_X, 0, HEAD_Z - 1)))
    shell = shell.cut(box(10, 14, 6, cx=PAN_X - 14, z0=HEAD_Z - 1))
    # distance-sensor window under the display, mic hole above it
    shell = shell.cut(box(8, 14, 5, cx=PAN_X + hx / 2 - 1.5, z0=HEAD_Z + 4.5))
    return shell

# ---------------- shovel ----------------
def shovel():
    px, pz = SHOVEL_PIVOT
    arm_y = TRACK_Y + TRACK_W / 2 + 3 + 2
    BLADE_W = 2 * arm_y + 4
    s = None
    for sy in (-1, 1):
        # hub on the wall -> spacer out past the track -> arm forward-down to the blade
        hub = ycyl(12, arm_y - TUB_W / 2 - 1, px, pz, sy * (TUB_W / 2 + 1) if sy > 0 else -arm_y)
        arm = (cq.Workplane("XZ").polyline([(px - 6, pz - 6), (px + 6, pz + 6), (BLADE_X + 2, 22), (BLADE_X + 2, 8)]).close()
               .extrude(-4).translate((0, sy * arm_y - 2, 0)))
        part = hub.union(arm)
        s = part if s is None else s.union(part)
    blade = (cq.Workplane("XZ").polyline([(BLADE_X, 4), (BLADE_X + 14, 2), (BLADE_X + 16, 2), (BLADE_X + 3, 4 + BLADE_H), (BLADE_X, 4 + BLADE_H)]).close()
             .extrude(-BLADE_W).translate((0, -BLADE_W / 2, 0)))
    return s.union(blade)

# ---------------- reference blocks for bought parts (not printed) ----------------
def references():
    refs = {}
    track = None
    for sy in (-1, 1):
        loop = (cq.Workplane("XZ").slot2D(WHEELBASE + WHEEL_D + 2 * TRACK_T, WHEEL_D + 2 * TRACK_T).extrude(-TRACK_W)
                .cut(cq.Workplane("XZ").slot2D(WHEELBASE + WHEEL_D, WHEEL_D).extrude(-TRACK_W))
                .translate((0, sy * TRACK_Y - TRACK_W / 2, AXLE_Z)))
        track = loop if track is None else track.union(loop)
        for x in (-WHEELBASE / 2, WHEELBASE / 2):
            track = track.union(ycyl(WHEEL_D - 1, TRACK_W - 4, x, AXLE_Z, sy * TRACK_Y - TRACK_W / 2 + 2))
    refs["ref_tracks_and_wheels"] = (track, (0.25, 0.25, 0.27))
    m = None
    for sy in (-1, 1):
        y_in = sy * (TUB_W_IN / 2)
        g = box(12, 9, 10, cx=-WHEELBASE / 2, cy=y_in - sy * 4.5, z0=AXLE_Z - 5)
        b = ycyl(12, 15, -WHEELBASE / 2, AXLE_Z, y_in - sy * 9 - (15 if sy > 0 else 0))
        sh = ycyl(3, 12, -WHEELBASE / 2, AXLE_Z, y_in if sy > 0 else y_in - 12)
        mm = g.union(b).union(sh)
        m = mm if m is None else m.union(mm)
    refs["ref_n20_motors"] = (m, (0.75, 0.6, 0.2))
    refs["ref_battery_2x18650"] = (box(*BAT, cx=BAT_X, z0=FLOOR_Z + FLOOR_T), (0.2, 0.55, 0.3))
    pcb = box(PCB_L, PCB_W, 1.6, cx=PCB_X, z0=PCB_Z)
    for sx in (-1, 1):
        for sy in (-1, 1):
            pcb = pcb.cut(cq.Workplane("XY").circle(1.6).extrude(3).translate((PCB_X + sx * PCB_HOLE_DX / 2, sy * PCB_HOLE_DY / 2, PCB_Z - 1)))
    refs["ref_main_pcb"] = (pcb, (0.1, 0.45, 0.25))
    refs["ref_esp32_devkit"] = (box(70, 28, 12, cx=PCB_X - 6, cy=0.5, z0=PCB_Z + 1.6 + 9), (0.15, 0.15, 0.18))
    sx0 = PAN_X - (SERVO_BODY[0] / 2 - 6)
    pan = (box(*SERVO_BODY, cx=sx0, z0=WALL_TOP + 4 - 15.9)
           .union(box(32.3, 12.2, 2.5, cx=sx0, z0=WALL_TOP + 4))
           .union(cq.Workplane("XY").circle(2.4).extrude(15).translate((PAN_X, 0, WALL_TOP + 4))))
    refs["ref_servo_pan_mg90s"] = (pan, (0.2, 0.4, 0.8))
    px, pz = SHOVEL_PIVOT
    sh = (box(SERVO_BODY[0], SERVO_BODY[2], SERVO_BODY[1], cx=px - (SERVO_BODY[0] / 2 - 6), cy=TUB_W_IN / 2 - 4.5 - SERVO_BODY[2] / 2, z0=pz - SERVO_BODY[1] / 2)
          .union(ycyl(4.8, 9, px, pz, TUB_W_IN / 2 - 4.5)))
    refs["ref_servo_shovel_mg90s"] = (sh, (0.2, 0.4, 0.8))
    lcd = box(4, 58, 35, cx=PAN_X + HEAD[0] / 2 - 5, z0=HEAD_Z + 10.5)
    refs["ref_display_2in"] = (lcd, (0.05, 0.75, 0.85))
    refs["ref_speaker_28mm"] = (cq.Workplane("YZ").circle(14).extrude(6).translate((-TUB_L / 2 + WALL + 0.5, 0, 28)), (0.6, 0.3, 0.6))
    return refs

parts = {
    "frame_chassis": (chassis(), (0.62, 0.72, 0.74)),
    "frame_neck_bridge": (neck_bridge(), (0.52, 0.64, 0.68)),
    "frame_head": (head_frame(), (0.72, 0.82, 0.84)),
    "frame_shovel": (shovel(), (0.85, 0.45, 0.38)),
}
refs = references()

assy = cq.Assembly(name="dimer_guideline")
for name, (shape, col) in {**parts, **refs}.items():
    assy.add(shape, name=name, color=cq.Color(*col))
    if name.startswith("frame_"):
        cq.exporters.export(shape, os.path.join(OUT, name + ".step"))
assy.save(os.path.join(OUT, "dimer_guideline_assembly.step"))

fa = cq.Assembly(name="dimer_frame_only")
for name, (shape, col) in parts.items():
    fa.add(shape, name=name, color=cq.Color(*col))
fa.save(os.path.join(OUT, "dimer_frame_only.step"))

if len(sys.argv) > 1:   # optional: mesh dump for the web preview
    mesh = []
    for name, (shape, col) in {**parts, **refs}.items():
        v, t = shape.val().tessellate(0.15, 0.3)
        mesh.append({"name": name, "color": col, "v": [round(c, 2) for p in v for c in p.toTuple()], "t": [i for tri in t for i in tri]})
    json.dump(mesh, open(sys.argv[1], "w"))

bb = assy.toCompound().BoundingBox()
print("overall L x W x H: %.0f x %.0f x %.0f mm" % (bb.xlen, bb.ylen, bb.zmax))
for name, (shape, _) in parts.items():
    b = shape.val().BoundingBox(); print(name, "valid" if shape.val().isValid() else "INVALID", "%.0fx%.0fx%.0f" % (b.xlen, b.ylen, b.zlen), "solids", shape.solids().size())
