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
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dimer_components as dc

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "step")
os.makedirs(OUT, exist_ok=True)

# ---------------- parameters (edit me) ----------------
TUB_L, TUB_W_IN, WALL = 150.0, 74.0, 3.0      # chassis tub
FLOOR_Z, FLOOR_T, WALL_TOP = 8.0, 3.0, 44.0   # ground clearance 8 mm
TUB_W = TUB_W_IN + 2 * WALL                   # 80
AXLE_Z, WHEELBASE = 17.0, 110.0               # drive sprocket rear, idler front
WHEEL_D, TRACK_W, TRACK_T, TRACK_GAP = 28.0, 22.0, 3.0, 3.0
TRACK_Y = TUB_W / 2 + TRACK_GAP + TRACK_W / 2
PCB_L, PCB_W, PCB_Z = 100.0, 70.0, 46.0        # main board, underside height
PCB_X = -12.0                                  # board centre
PCB_HOLE_DX, PCB_HOLE_DY = 92.0, 62.0          # M3 hole pattern (matches the PCB)
BAT = (77.0, 41.0, 21.0)                       # 2x18650 holder
BAT_X = -6.5
PAN_X = 58.0                                   # head rotation axis
SERVO_BODY = (22.8, 12.2, 22.5)                # MG90S
SERVO_CUT = (23.4, 12.8)
HEAD = (46.0, 72.0, 62.0)                      # head frame envelope (x, y, z)
HEAD_Z = 64.0
EDGE_X, EDGE_Y = 82.0, 48.0                    # table-edge sensor positions (in front of / behind each track)
SHOVEL_PIVOT = (65.0, 37.8)                    # x, z of shovel axis (left wall)
BLADE_H, BLADE_X = 26.0, 92.0
SWITCH_HOLE, JACK_HOLE = 20.2, 8.2             # round rocker switch and DC charging socket (measure yours)
TOF_Z = 13.0                                   # sensor centre height above the head floor
TOF_HOLES = (17.0, 13.0)                       # distance sensor mounting hole spacing (measure yours)

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
    tub = tub.cut(box(SERVO_CUT[0], WALL + 2, SERVO_CUT[1], cx=SHOVEL_PIVOT[0] - (SERVO_BODY[0] / 2 - 6), cy=TUB_W / 2 - WALL / 2, z0=SHOVEL_PIVOT[1] - SERVO_CUT[1] / 2))
    # rear wall: speaker grille, round power switch hole, charging socket hole
    for gy in (-8, -4, 0, 4, 8):
        for gz in (20, 24, 28, 32, 36):
            if abs(gy) + abs(gz - 28) <= 12:
                tub = tub.cut(cq.Workplane('YZ').circle(1.2).extrude(WALL + 2).translate((-TUB_L / 2 - 1, gy, gz)))
    tub = tub.cut(cq.Workplane('YZ').circle(SWITCH_HOLE / 2).extrude(WALL + 2).translate((-TUB_L / 2 - 1, -25, 31)))
    tub = tub.cut(cq.Workplane('YZ').circle(JACK_HOLE / 2).extrude(WALL + 2).translate((-TUB_L / 2 - 1, 26, 31)))
    tub = tub.cut(ycyl(3.2, WALL + 2, SHOVEL_PIVOT[0], SHOVEL_PIVOT[1], -TUB_W / 2 - 1))
    # cable pass-throughs in the floor and battery strap slots
    for x in (-30, 20):
        tub = tub.cut(box(3, 30, FLOOR_T + 2, cx=x + BAT_X, z0=FLOOR_Z - 1))
    # edge-sensor tabs (TCRT5000 module, M3 hole) at the four corners, looking down
    for sx in (-1, 1):
        for sy in (-1, 1):
            tab = box(14, 16, FLOOR_T, cx=sx * (TUB_L / 2 + 7), cy=sy * 37, z0=FLOOR_Z)
            tab = tab.cut(cq.Workplane("XY").circle(1.6).extrude(10).translate((sx * EDGE_X, sy * 38, FLOOR_Z - 1)))
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
    shell = shell.cut(box(8, 42, 32, cx=PAN_X + hx / 2 - 1.5, z0=HEAD_Z + 25))
    # servo horn screw + cable hole in the floor
    shell = shell.cut(cq.Workplane("XY").circle(3.5).extrude(6).translate((PAN_X, 0, HEAD_Z - 1)))
    shell = shell.cut(box(10, 14, 6, cx=PAN_X - 14, z0=HEAD_Z - 1))
    # distance-sensor window below the display, with four M2 screw holes around it
    shell = shell.cut(box(8, 13, 11, cx=PAN_X + hx / 2 - 1.5, z0=HEAD_Z + TOF_Z - 5.5))
    for sy in (-1, 1):
        for sz in (-1, 1):
            shell = shell.cut(cq.Workplane('YZ').circle(0.9).extrude(8).translate((PAN_X + hx / 2 - 5, -2 + sy * TOF_HOLES[0] / 2, HEAD_Z + TOF_Z + sz * TOF_HOLES[1] / 2)))
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

# ---------------- bought parts, placed in the robot ----------------
STEP_PCB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pcb", "dimer_main_3d.step")
L = cq.Location
def T(x, y, z): return L(cq.Vector(x, y, z))
def R(axis, deg): return L(cq.Vector(0, 0, 0), cq.Vector(*axis), deg)
RX, RY, RZ = (1, 0, 0), (0, 1, 0), (0, 0, 1)

def load_colored_step(path, name):
    """Read a STEP file (the KiCad board export) keeping its per-face colours, as a cq.Assembly."""
    from OCP.STEPCAFControl import STEPCAFControl_Reader
    from OCP.TDocStd import TDocStd_Document
    from OCP.TCollection import TCollection_ExtendedString
    from OCP.XCAFDoc import XCAFDoc_DocumentTool, XCAFDoc_ColorSurf, XCAFDoc_ColorGen
    from OCP.TDF import TDF_LabelSequence, TDF_Label
    from OCP.Quantity import Quantity_Color
    from OCP.TopAbs import TopAbs_SOLID
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopLoc import TopLoc_Location
    from OCP.TopoDS import TopoDS
    doc = TDocStd_Document(TCollection_ExtendedString("x"))
    rd = STEPCAFControl_Reader(); rd.SetColorMode(True); rd.SetNameMode(True); rd.ReadFile(path); rd.Transfer(doc)
    st = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main()); ct = XCAFDoc_DocumentTool.ColorTool_s(doc.Main())
    def colour(lab):
        c = Quantity_Color()
        for t in (XCAFDoc_ColorSurf, XCAFDoc_ColorGen):
            if ct.GetColor_s(lab, t, c): return (round(c.Red(), 3), round(c.Green(), 3), round(c.Blue(), 3))
        return None
    facecol = []                                   # (unlocated face, colour) for every coloured face in the file
    def collect(lab):
        subs = TDF_LabelSequence(); st.GetSubShapes_s(lab, subs)
        for i in range(subs.Length()):
            c = colour(subs.Value(i + 1))
            if c: facecol.append((st.GetShape_s(subs.Value(i + 1)), c))
        comps = TDF_LabelSequence(); st.GetComponents_s(lab, comps)
        for i in range(comps.Length()): collect(comps.Value(i + 1))
        ref = TDF_Label()
        if st.GetReferredShape_s(lab, ref): collect(ref)
    free = TDF_LabelSequence(); st.GetFreeShapes(free)
    out = cq.Assembly(name=name); done = {}
    for i in range(free.Length()):
        collect(free.Value(i + 1))
    idx = {}
    for f, c in facecol: idx.setdefault(hash(cq.Shape.cast(f)), []).append((f, c))
    k = 0
    for i in range(free.Length()):
        ex = TopExp_Explorer(st.GetShape_s(free.Value(i + 1)), TopAbs_SOLID)
        while ex.More():
            sol = TopoDS.Solid_s(ex.Current()); loc = sol.Location()
            base = cq.Solid(sol.Located(TopLoc_Location()))
            area = {}; fc = []
            for f in base.Faces():
                c = None
                for g, cc in idx.get(hash(f), []):
                    if f.wrapped.IsSame(g): c = cc; break
                c = c or (0.05, 0.35, 0.2)
                area[c] = area.get(c, 0) + f.Area(); fc.append((f, c))
            main = max(area, key=area.get)
            child = cq.Assembly(base, name="%s_%02d" % (name, k), color=cq.Color(*main)); k += 1
            for f, c in fc:
                if c != main:
                    try: child.addSubshape(f, color=cq.Color(*c))
                    except Exception: pass
            out.add(child, loc=cq.Location(loc))
            ex.Next()
    return out

placed = []   # (name, assembly, location)
def put(name, a, loc):
    placed.append((name, a, loc))

for sy, tag in ((1, "left"), (-1, "right")):
    put("track_" + tag, dc.track_set(WHEELBASE, WHEEL_D, TRACK_W, TRACK_T), T(0, sy * TRACK_Y, AXLE_Z))
put("motor_left", dc.motor_n20(), T(-WHEELBASE / 2, TUB_W_IN / 2, AXLE_Z))
put("motor_right", dc.motor_n20(), T(-WHEELBASE / 2, -TUB_W_IN / 2, AXLE_Z) * R(RZ, 180))
BAT_TOP = FLOOR_Z + FLOOR_T + 20.6
put("battery", dc.battery_2x18650(), T(BAT_X, 0, FLOOR_Z + FLOOR_T))
if os.path.exists(STEP_PCB):        # the routed board exported from KiCad
    put("main_pcb", load_colored_step(STEP_PCB, "main_pcb"), T(PCB_X - PCB_L / 2, PCB_W / 2, PCB_Z))
    put("pcb_screw_terminals", dc.screw_terminals_v02(), T(PCB_X - PCB_L / 2, PCB_W / 2, PCB_Z))
else:                               # simplified stand-in
    put("main_pcb", dc.main_board_v02(), T(PCB_X - PCB_L / 2, PCB_W / 2, PCB_Z))
put("esp32_s3_devkit", dc.esp32_s3_devkit(), T(PCB_X - PCB_L / 2 + 44.45, PCB_W / 2 - 34.29, PCB_Z + 1.6 + 8.5))
put("servo_pan", dc.servo_mg90s(), T(PAN_X, 0, WALL_TOP + 4))
put("servo_shovel", dc.servo_mg90s(), T(SHOVEL_PIVOT[0], TUB_W_IN / 2 - 2.5, SHOVEL_PIVOT[1]) * R(RX, -90))
put("face_display", dc.lcd_2in(), T(PAN_X + HEAD[0] / 2 - 3, 3, HEAD_Z + 41))
put("distance_sensor", dc.tof200f(), T(PAN_X + HEAD[0] / 2 - 3 - 1.2, -2, HEAD_Z + TOF_Z) * R(RY, 90) * R(RZ, 90))
put("speaker", dc.speaker_28mm(), T(-TUB_L / 2 + WALL + 0.1, 0, 28))
put("power_switch", dc.rocker_round(), T(-TUB_L / 2, -25, 31))
put("charging_socket", dc.dc_jack_panel(), T(-TUB_L / 2, 26, 31))
for sx, fx in ((1, "front"), (-1, "rear")):
    put("edge_sensor_%s_left" % fx, dc.tcrt5000_module(), T(sx * EDGE_X, EDGE_Y, FLOOR_Z + FLOOR_T))
    put("edge_sensor_%s_right" % fx, dc.tcrt5000_module(), T(sx * EDGE_X, -EDGE_Y, FLOOR_Z + FLOOR_T) * R(RZ, 180))

parts = {
    "frame_chassis": (chassis(), (0.62, 0.72, 0.74)),
    "frame_neck_bridge": (neck_bridge(), (0.52, 0.64, 0.68)),
    "frame_head": (head_frame(), (0.72, 0.82, 0.84)),
    "frame_shovel": (shovel(), (0.85, 0.45, 0.38)),
}

assy = cq.Assembly(name="dimer_guideline")
fa = cq.Assembly(name="dimer_frame_only")
for name, (shape, col) in parts.items():
    assy.add(shape, name=name, color=cq.Color(*col)); fa.add(shape, name=name, color=cq.Color(*col))
    cq.exporters.export(shape, os.path.join(OUT, name + ".step"))
for name, a, loc in placed:
    assy.add(a, name=name, loc=loc)
assy.save(os.path.join(OUT, "dimer_guideline_assembly.step"))
fa.save(os.path.join(OUT, "dimer_frame_only.step"))

COMP = os.path.join(OUT, "components"); os.makedirs(COMP, exist_ok=True)
seen = set()
for name, a, loc in placed:
    if a.name not in seen and name != "main_pcb":
        seen.add(a.name); a.save(os.path.join(COMP, a.name + ".step"))

def leaves(a, loc):
    """yield (shape in world coordinates, colour) for every solid in an assembly tree"""
    here = loc * a.loc if a.loc is not None else loc
    col = a.color
    for o in (a.shapes if hasattr(a, "shapes") else []):
        yield o.moved(here), col
    for ch in a.children:
        if ch.color is None and col is not None: ch.color = col
        yield from leaves(ch, here)

if len(sys.argv) > 1:   # optional: mesh dump for the web preview
    mesh = []
    def dump(name, shape, col, tol):
        v, t = shape.tessellate(tol, 0.5)
        if not t: return
        mesh.append({"name": name, "color": [round(c, 3) for c in col], "v": [round(c, 1) for p in v for c in p.toTuple()], "t": [i for tri in t for i in tri]})
    for name, (shape, col) in parts.items():
        dump(name, shape.val(), col, 0.15)
    for name, a, loc in placed:
        for shp, col in leaves(a, loc):
            c = col.toTuple()[:3] if col is not None else (0.5, 0.5, 0.5)
            dump("part_" + name.replace("pcb_screw_terminals", "main_pcb"), shp, c, 0.4 if name == "main_pcb" else 0.25)
    json.dump(mesh, open(sys.argv[1], "w"), separators=(",", ":"))

bb = assy.toCompound().BoundingBox()
print("overall L x W x H: %.0f x %.0f x %.0f mm" % (bb.xlen, bb.ylen, bb.zmax))
print("placed components:", len(placed))
for name, (shape, _) in parts.items():
    b = shape.val().BoundingBox(); print(name, "valid" if shape.val().isValid() else "INVALID", "%.0fx%.0fx%.0f" % (b.xlen, b.ylen, b.zlen), "solids", shape.solids().size())
