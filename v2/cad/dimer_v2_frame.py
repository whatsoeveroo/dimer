"""Dimer V2 (half-size) frame guideline generator (CadQuery).

Run:  pip install cadquery && python v2/cad/dimer_v2_frame.py
Writes STEP files into v2/cad/step/.  Units: mm.
Axes: X = forward, Y = left, Z = up, table surface at Z = 0.

V2 is a separate, smaller robot. V1 in cad/ is untouched.
Differences from V1: about half the size, the head is fixed (no neck servo),
the shovel is fixed (no shovel servo), one flat 1S battery, no custom board.

This is a ROUGH GUIDELINE, not a design: it fixes where the parts sit and
where the mounting holes go.  Change the numbers below after measuring the
parts you actually bought, then run again.
"""
import json, os, sys
import cadquery as cq
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "cad"))
import dimer_components as dc
from dimer_components import B, CZ, CY, CX, asm, small_board, header

OUT = os.path.join(HERE, "step")
os.makedirs(OUT, exist_ok=True)

# ---------------- parameters (edit me) ----------------
TUB_L, TUB_W_IN, WALL = 76.0, 34.0, 2.0        # chassis tub
FLOOR_Z, FLOOR_T, WALL_TOP = 2.5, 1.5, 36.0    # ground clearance 2.5 mm
TUB_W = TUB_W_IN + 2 * WALL                    # 38
XI = TUB_L / 2 - WALL                          # inner face of front / rear wall (36)
AXLE_Z, WHEELBASE = 9.0, 58.0
WHEEL_D, TRACK_W, TRACK_T, TRACK_GAP = 15.0, 11.0, 1.5, 1.5
TRACK_Y = TUB_W / 2 + TRACK_GAP + TRACK_W / 2  # 26
BAT = (40.0, 30.0, 10.0)                       # flat 1S LiPo, largest size that fits
DECK_Z = 16.0                                  # modules sit on top of battery and motors (foam tape)
LID_T = 2.0
HEAD_X0, HEAD_L, HEAD_W, HEAD_H = 10.0, 28.0, 40.0, 26.0   # fixed head on the lid
HEAD_Z = WALL_TOP + LID_T                      # 38
LCD_Z = HEAD_Z + 12.0                          # display centre height
EDGE_X, EDGE_Y, EDGE_Z = 47.2, 27.0, 10.0      # table-edge sensors, in front of each track
BLADE_X, BLADE_H, BLADE_W = 55.0, 13.0, 66.0   # fixed shovel blade
TOF_Y, TOF_Z = 0.0, 30.5                      # distance sensor window in the front wall

def box(x, y, z, cx=0, cy=0, z0=0):
    return cq.Workplane("XY").box(x, y, z, centered=(True, True, False)).translate((cx, cy, z0))
def xcyl(d, length, y, z, x0):
    return cq.Workplane("YZ").circle(d / 2).extrude(length).translate((x0, y, z))
def ycyl(d, length, x, z, y0):
    return cq.Workplane("XZ").circle(d / 2).extrude(-length).translate((x, y0, z))
def zcyl(d, h, x, y, z0):
    return cq.Workplane("XY").circle(d / 2).extrude(h).translate((x, y, z0))

# Left motor drives the rear wheel, right motor drives the front wheel.
# Two N20 motors are too long to sit on one axle in a 34 mm wide body.
MOTORS = ((-WHEELBASE / 2, 1), (WHEELBASE / 2, -1))     # (x, side of the driven wheel)

# ---------------- chassis tub ----------------
def chassis():
    tub = box(TUB_L, TUB_W, WALL_TOP - FLOOR_Z, z0=FLOOR_Z).cut(box(TUB_L - 2 * WALL, TUB_W_IN, WALL_TOP, z0=FLOOR_Z + FLOOR_T))
    for mx, sy in MOTORS:
        # motor shaft hole on the driven side, M3 idler-axle pilot hole on the other side
        tub = tub.cut(ycyl(4.6, WALL + 2, mx, AXLE_Z, TUB_W_IN / 2 - 1 if sy > 0 else -TUB_W / 2 - 1))
        tub = tub.cut(ycyl(2.5, WALL + 2, mx, AXLE_Z, TUB_W_IN / 2 - 1 if sy < 0 else -TUB_W / 2 - 1))
        # rib between motor gearbox and battery: holds the motor square and stops the battery sliding
        rx = mx - 7.4 if mx > 0 else mx + 7.4
        tub = tub.union(box(2.0, 10, 9, cx=rx, cy=sy * (TUB_W_IN / 2 - 5), z0=FLOOR_Z + FLOOR_T - 0.1))
    # lid screw bosses at the rear corners (M2 self-tap, 1.6 mm pilot)
    for sy in (-1, 1):
        tub = tub.union(box(3, 4, 10, cx=-XI + 1.5, cy=sy * (TUB_W_IN / 2 - 2), z0=WALL_TOP - 10))
        tub = tub.cut(zcyl(1.6, 9, -XI + 1.5, sy * (TUB_W_IN / 2 - 2), WALL_TOP - 8))
    # front wall: lid tab screws (M2), shovel screws (M2), distance-sensor window, cable notch
    for sy in (-1, 1):
        tub = tub.cut(xcyl(2.2, WALL + 2, sy * 15, WALL_TOP - 4, XI - 1))
    for y in (-12, 8):
        tub = tub.cut(xcyl(1.6, WALL + 2, y, 14, XI - 1))
    tub = tub.cut(box(WALL + 2, 8, 5, cx=XI + WALL / 2, cy=TOF_Y, z0=TOF_Z - 2.5))
    tub = tub.cut(box(WALL + 2, 9, 5, cx=XI + WALL / 2, cy=-8, z0=18.5))
    # rear wall: USB-C charging slot
    tub = tub.cut(box(WALL + 2, 10, 4.4, cx=-XI - WALL / 2, cy=8.5, z0=DECK_Z + 1.0))
    # battery strap slots in the floor
    for x in (-10, 10):
        tub = tub.cut(box(2, 24, FLOOR_T + 2, cx=x, z0=FLOOR_Z - 1))
    # shell attachment ears on the wall tops (M2) - bolt your shell here
    for x in (-20, 0):
        for sy in (-1, 1):
            ear = box(7, 5, 3, cx=x, cy=sy * (TUB_W / 2 + 2.5), z0=WALL_TOP - 3)
            tub = tub.union(ear.cut(zcyl(1.6, 5, x, sy * (TUB_W / 2 + 2.8), WALL_TOP - 4)))
    return tub

# ---------------- top: lid with the fixed head ----------------
def top():
    hx = HEAD_X0 + HEAD_L / 2
    lid = box(TUB_L, TUB_W, LID_T, z0=WALL_TOP)
    head = box(HEAD_L, HEAD_W, HEAD_H, cx=hx, z0=HEAD_Z).cut(box(HEAD_L - 4, HEAD_W - 4, HEAD_H - 1.9, cx=hx, z0=HEAD_Z - 0.1))
    t = lid.union(head)
    # wire opening from the body up into the head
    t = t.cut(box(18, 26, LID_T + 2, cx=hx - 2, z0=WALL_TOP - 1))
    # display window (0.96 inch, 21.7 x 10.8 mm active, landscape)
    t = t.cut(box(6, 23, 12, cx=HEAD_X0 + HEAD_L - 1, z0=LCD_Z - 6))
    # speaker grille in the back of the head, microphone hole in the top
    for gy in (-6, -3, 0, 3, 6):
        for gz in (-6, -3, 0, 3, 6):
            if abs(gy) + abs(gz) <= 9:
                t = t.cut(xcyl(1.6, 6, gy, LCD_Z + gz, HEAD_X0 - 2))
    t = t.cut(zcyl(1.5, 6, hx + 0.7, 0, HEAD_Z + HEAD_H - 4))
    t = t.cut(box(4.8, 9, LID_T + 2, cx=-22, cy=8.5, z0=WALL_TOP - 1))          # slide switch, lever up
    # rear lid screws (M2 clearance)
    for sy in (-1, 1):
        t = t.cut(zcyl(2.2, LID_T + 2, -XI + 1.5, sy * (TUB_W_IN / 2 - 2), WALL_TOP - 1))
    # front tabs that drop behind the tub front wall, screwed from the front
    for sy in (-1, 1):
        tab = box(3, 4, 8, cx=XI - 1.6, cy=sy * 15, z0=WALL_TOP - 8)
        t = t.union(tab.cut(xcyl(1.6, 5, sy * 15, WALL_TOP - 4, XI - 4)))
    return t

# ---------------- fixed shovel (also carries the two edge sensors) ----------------
def shovel():
    x0 = TUB_L / 2
    flange = box(2, 30, 9.5, cx=x0 + 1, cy=-2, z0=7.5)
    for y in (-12, 8):
        flange = flange.cut(xcyl(2.2, 4, y, 14, x0 - 1))
    shelf = box(BLADE_X - x0 - 2, BLADE_W, 2.5, cx=(x0 + 2 + BLADE_X) / 2, z0=7.5)
    for sy in (-1, 1):
        shelf = shelf.cut(box(12, 8, 6, cx=EDGE_X, cy=sy * EDGE_Y, z0=6))          # sensor looks down through here
        shelf = shelf.cut(zcyl(2.5, 6, EDGE_X, sy * (EDGE_Y - 10), 6))             # sensor board screw (M3 self-tap)
    shelf = shelf.cut(box(12, 8, 6, cx=EDGE_X, cy=0, z0=6))                          # room for the pin stubs under the two boards
    blade = (cq.Workplane("XZ").polyline([(BLADE_X, 2), (BLADE_X + 7, 1), (BLADE_X + 8, 1), (BLADE_X + 1.5, 2 + BLADE_H), (BLADE_X, 2 + BLADE_H)]).close()
             .extrude(-BLADE_W).translate((0, -BLADE_W / 2, 0)))
    return flange.union(shelf).union(blade)

# ---------------- small bought parts that V1 does not have ----------------
def track_v2():
    """Printed drive wheel and idler with a rubber band or printed TPU belt. Origin: midway between axles, on the axle line."""
    parts = []
    for x in (-WHEELBASE / 2, WHEELBASE / 2):
        for s, col in dc.wheel(WHEEL_D, TRACK_W - 4):
            parts.append((s.translate((x, 0, 0)), "white" if col == "steel" else col))
    belt = (cq.Workplane("XZ").slot2D(WHEELBASE + WHEEL_D + 2 * TRACK_T, WHEEL_D + 2 * TRACK_T).extrude(-TRACK_W)
            .cut(cq.Workplane("XZ").slot2D(WHEELBASE + WHEEL_D, WHEEL_D).extrude(-TRACK_W - 2).translate((0, 1, 0))).translate((0, -TRACK_W / 2, 0)))
    parts.append((belt, "rubber"))
    return asm("track_v2", parts)

def lipo_1s():
    """Origin: centre of footprint, Z=0 underside. Wires leave toward -X."""
    cell = B(BAT[0] - 4, BAT[1], BAT[2], cx=2).edges("|X").fillet(2.0)
    cap = B(4, BAT[1] - 2, BAT[2] - 3, cx=-BAT[0] / 2 + 2, z0=1.5)
    return asm("battery_lipo_1s", [(cell, "steel"), (cap, "yellow")])

def esp32_s3_supermini():
    parts = [(B(22.5, 18, 1.2), "pcb_black"), (B(8.9, 7.4, 3.2, cx=-8.5, z0=1.2), "steel"), (B(7, 7, 0.9, cx=3, z0=1.2), "black"), (B(5, 2, 1.2, cx=9.5, z0=1.2), "white")]
    for sy in (-1, 1):
        for s, col in header(8, along="x"):
            parts.append((s.translate((0, sy * 7.62, 1.2)), col))
    return asm("esp32_s3_supermini", parts)

def lcd_096():
    """Origin: centre of the glass front face, the screen looks toward +X. 30 x 24 mm module used landscape."""
    pcb = B(1.6, 30, 24, cx=-3.0, z0=-12)
    glass = B(2.2, 26, 15, cx=-1.1, z0=-7.5)
    scr = B(0.1, 21.7, 10.8, cx=0.05, z0=-5.4)
    parts = [(pcb, "pcb_blue"), (glass, "glass"), (scr, "screen")]
    strip = B(2.5, 2.5, 20.3, cx=-5.05, cy=13.2, z0=-10.15)
    pins = None
    for i in range(8):
        p = B(11.5, 0.64, 0.64, cx=-6.5, cy=13.2, z0=-8.89 + 2.54 * i - 0.32)
        pins = p if pins is None else pins.union(p)
    return asm("lcd_0in96_st7735", parts + [(strip, "black"), (pins, "gold")])

def speaker_20mm():
    """Origin: centre of the front rim, sound comes out toward -X."""
    rim = CX(20, 1.0, x0=0).cut(CX(17, 3, x0=-1))
    cone = cq.Workplane("YZ").circle(8.5).workplane(offset=2.5).circle(4).loft().translate((0.5, 0, 0))
    return asm("speaker_20mm", [(rim, "steel"), (cone, "dark"), (CX(14, 1.6, x0=1.0), "steel"), (CX(10, 2.2, x0=2.6), "grey")])

def slide_switch():
    """Origin: centre of the panel face. Lever sticks out toward -X, body toward +X."""
    return asm("slide_switch", [(B(4.4, 8.6, 4.4, cx=2.2, z0=-2.2), "steel"), (B(3.5, 2.5, 2.5, cx=-1.75, cy=1.5, z0=-1.25), "black"), (B(3, 5.5, 0.6, cx=5.9, z0=-0.3), "gold")])

def charger_boost_1s():
    return small_board("charger_boost_1s_usb_c", 26, 17, "pcb_blue", [(7.4, 8.9, 3.2, -9.6, 0, "steel"), (6, 6, 3, 2, 0, "dark"), (3, 3, 1, 9, 4, "black"), (1.2, 1.2, 0.8, 9, -5, "white")])

# ---------------- bought parts, placed in the robot ----------------
L = cq.Location
def T(x, y, z): return L(cq.Vector(x, y, z))
def R(axis, deg): return L(cq.Vector(0, 0, 0), cq.Vector(*axis), deg)
RX, RY, RZ = (1, 0, 0), (0, 1, 0), (0, 0, 1)

placed = []
def put(name, a, loc): placed.append((name, a, loc))
# groups in the assembly tree, so a CAD program shows folders instead of one long flat list
GROUPS = {"track": "drive", "motor": "drive", "battery": "power", "usb_c": "power", "power_": "power", "esp32": "brain",
          "speaker": "voice", "microphone": "voice", "face_": "face", "distance": "senses", "edge_": "senses"}
def group_of(name):
    return next(g for k, g in GROUPS.items() if name.startswith(k))

for sy, tag in ((1, "left"), (-1, "right")):
    put("track_" + tag, track_v2(), T(0, sy * TRACK_Y, AXLE_Z))
put("motor_left", dc.motor_n20(), T(MOTORS[0][0], TUB_W_IN / 2, AXLE_Z))
put("motor_right", dc.motor_n20(), T(MOTORS[1][0], -TUB_W_IN / 2, AXLE_Z) * R(RZ, 180))
put("battery", lipo_1s(), T(0, 0, FLOOR_Z + FLOOR_T))
put("usb_c_charger", charger_boost_1s(), T(-XI + 13.5, 8.5, DECK_Z))
put("power_switch", slide_switch(), T(-22, 8.5, HEAD_Z) * R(RY, 90))
put("motor_driver", dc.drv8833_driver(), T(-XI + 12.5, -9, DECK_Z))
put("esp32_s3_supermini", esp32_s3_supermini(), T(2, -8, DECK_Z))
put("speaker_amplifier", dc.max98357_amp(), T(23.5, -8, DECK_Z))
put("distance_sensor", dc.vl53l0x_tof(), T(XI - 3, TOF_Y, TOF_Z) * R(RY, 90) * R(RZ, 90))
put("face_display", lcd_096(), T(HEAD_X0 + HEAD_L - 2, 0, LCD_Z))
put("speaker", speaker_20mm(), T(HEAD_X0 + 2.1, 0, LCD_Z))
put("microphone", dc.inmp441_mic(), T(HEAD_X0 + HEAD_L / 2 + 0.7, 0, HEAD_Z + HEAD_H - 5.4))
put("edge_sensor_front_left", dc.tcrt5000_module(), T(EDGE_X, EDGE_Y, EDGE_Z))
put("edge_sensor_front_right", dc.tcrt5000_module(), T(EDGE_X, -EDGE_Y, EDGE_Z) * R(RZ, 180))

# .clean() merges faces that lie on the same plane or cylinder, so each wall is one face to push or pull
parts = {
    "v2_frame_chassis": (chassis().clean(), (0.62, 0.72, 0.74)),
    "v2_frame_top": (top().clean(), (0.72, 0.82, 0.84)),
    "v2_frame_shovel": (shovel().clean(), (0.85, 0.45, 0.38)),
}

assy = cq.Assembly(name="dimer_v2_guideline")
fa = cq.Assembly(name="dimer_v2_frame_only")
sub = {g: cq.Assembly(name=g) for g in ["printed_frame"] + list(dict.fromkeys(GROUPS.values()))}
for name, (shape, col) in parts.items():
    sub["printed_frame"].add(shape, name=name, color=cq.Color(*col)); fa.add(shape, name=name, color=cq.Color(*col))
    cq.exporters.export(shape, os.path.join(OUT, name + ".step"))
for name, a, loc in placed:
    sub[group_of(name)].add(a, name=name, loc=loc)
for g, a in sub.items():
    assy.add(a, name=g)
assy.save(os.path.join(OUT, "dimer_v2_guideline_assembly.step"))
fa.save(os.path.join(OUT, "dimer_v2_frame_only.step"))

COMP = os.path.join(OUT, "components"); os.makedirs(COMP, exist_ok=True)
V1_COMP = os.path.join(HERE, "..", "..", "cad", "step", "components")
seen = set()
for name, a, loc in placed:          # only the parts V1 does not already have a STEP for
    if a.name not in seen and not os.path.exists(os.path.join(V1_COMP, a.name + ".step")):
        seen.add(a.name); a.save(os.path.join(COMP, a.name + ".step"))

def leaves(a, loc):
    here = loc * a.loc if a.loc is not None else loc
    col = a.color
    for o in (a.shapes if hasattr(a, "shapes") else []):
        yield o.moved(here), col
    for ch in a.children:
        if ch.color is None and col is not None: ch.color = col
        yield from leaves(ch, here)

solids = [(n, s.val(), c) for n, (s, c) in parts.items()]
for name, a, loc in placed:
    for shp, col in leaves(a, loc):
        solids.append(("part_" + name, shp, col.toTuple()[:3] if col is not None else (0.5, 0.5, 0.5)))

if len(sys.argv) > 1:   # optional: mesh dump for a preview
    mesh = []
    for name, shape, col in solids:
        v, t = shape.tessellate(0.1, 0.4)
        if t: mesh.append({"name": name, "color": [round(c, 3) for c in col], "v": [round(c, 2) for p in v for c in p.toTuple()], "t": [i for tri in t for i in tri]})
    json.dump(mesh, open(sys.argv[1], "w"), separators=(",", ":"))

bb = assy.toCompound().BoundingBox()
print("overall L x W x H: %.0f x %.0f x %.0f mm" % (bb.xlen, bb.ylen, bb.zmax))
print("placed components:", len(placed))
for name, (shape, _) in parts.items():
    b = shape.val().BoundingBox(); print(name, "valid" if shape.val().isValid() else "INVALID", "%.0fx%.0fx%.0f" % (b.xlen, b.ylen, b.zlen), "solids", shape.solids().size())

# clash check: every bought part against the frame and against each other (by part name)
groups = {}
for n, s, _ in solids: groups.setdefault(n, []).append(s)
comp = {n: cq.Compound.makeCompound(v) for n, v in groups.items()}
names = list(comp); bad = 0
for i in range(len(names)):
    for j in range(i + 1, len(names)):
        a, b = comp[names[i]], comp[names[j]]
        ba, bb2 = a.BoundingBox(), b.BoundingBox()
        if ba.xmin > bb2.xmax or bb2.xmin > ba.xmax or ba.ymin > bb2.ymax or bb2.ymin > ba.ymax or ba.zmin > bb2.zmax or bb2.zmin > ba.zmax: continue
        try: vol = a.intersect(b).Volume()
        except Exception: vol = 0
        if {names[i][5:8], names[j][5:8]} == {"tra", "mot"}: continue      # motor shaft is a press fit in the wheel hub
        if vol > 0.5: bad += 1; print("CLASH %s x %s: %.1f mm3" % (names[i], names[j], vol))
print("clashes over 0.5 mm3:", bad)
