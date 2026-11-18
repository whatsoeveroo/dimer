"""Dimer 2.0: detailed 3D models of every bought part (CadQuery).

Each function returns a cadtree.Node in the part's own frame (origin and axes written in its docstring),
one named, coloured solid per real piece (pins, plates, gears, wires...). Sizes are from the sellers'
drawings and datasheets; the Pololu tracks come from Pololu's own STEP and the power board from KiCad.
Measure the parts you received before you print anything tight.

    python v2/cad/dimer_parts_2_0.py      writes one STEP per part into v2/cad/step/2_0/parts/
"""
import json, math, os, sys
import cadquery as cq

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "lib"))
from cadtree import Node, Leaf, write_step
import step_colors

POLOLU_STEP = os.environ.get("POLOLU_STEP", os.path.join(HERE, "vendor", "pololu_22t_track_set.step"))
BOARD_STEP = os.environ.get("BOARD_STEP", os.path.join(HERE, "vendor", "dimer_v2_power_board_kicad.step"))
BOARD_JSON = os.path.join(HERE, "..", "pcb", "dimer_v2_power_parts.json")

COL = dict(
    black=(0.06, 0.06, 0.07), dark=(0.18, 0.18, 0.2), steel=(0.74, 0.75, 0.77), nickel=(0.82, 0.83, 0.82),
    brass=(0.80, 0.64, 0.30), gold=(0.86, 0.69, 0.25), copper=(0.75, 0.45, 0.25),
    sg90=(0.12, 0.35, 0.80), sg90_label=(0.85, 0.87, 0.9), white=(0.94, 0.94, 0.92), cream=(0.92, 0.88, 0.78),
    pcb_blue=(0.07, 0.22, 0.58), pcb_black=(0.09, 0.09, 0.1), pcb_purple=(0.36, 0.14, 0.5), pcb_green=(0.05, 0.38, 0.2),
    glass=(0.04, 0.05, 0.07), screen=(0.08, 0.6, 0.75), lens=(0.15, 0.2, 0.3), pouch=(0.78, 0.8, 0.82),
    kapton=(0.92, 0.62, 0.1), red=(0.8, 0.1, 0.1), orange=(0.95, 0.5, 0.1), brown=(0.4, 0.22, 0.12),
    green_term=(0.1, 0.55, 0.3), blue_pot=(0.15, 0.35, 0.85), ir_led=(0.35, 0.45, 0.95), rubber=(0.1, 0.1, 0.11),
    paper=(0.12, 0.12, 0.12), magnet=(0.45, 0.47, 0.5), felt=(0.3, 0.3, 0.32), led_red=(0.9, 0.15, 0.1), led_blue=(0.2, 0.5, 1.0),
    chip=(0.1, 0.1, 0.11), cap=(0.72, 0.6, 0.42), res=(0.08, 0.08, 0.08),
)


# ---------------- small helpers ----------------
def B(x, y, z, cx=0, cy=0, z0=0):
    return cq.Workplane("XY").box(x, y, z, centered=(True, True, False)).translate((cx, cy, z0))
def XB(x0, x1, y0, y1, z0, z1):
    return B(abs(x1 - x0), abs(y1 - y0), abs(z1 - z0), cx=(x0 + x1) / 2, cy=(y0 + y1) / 2, z0=min(z0, z1))
def CZ(d, h, cx=0, cy=0, z0=0):
    return cq.Workplane("XY").circle(d / 2).extrude(h).translate((cx, cy, z0))
def CY(d, length, x=0, z=0, y0=0):
    """cylinder along +Y from y0"""
    return cq.Workplane("XZ").circle(d / 2).extrude(-length).translate((x, y0, z))
def CX(d, length, y=0, z=0, x0=0):
    return cq.Workplane("YZ").circle(d / 2).extrude(length).translate((x0, y, z))
def fil(w, sel, r):
    try:
        return w.edges(sel).fillet(r)
    except Exception:
        return w
def cham(w, sel, r):
    try:
        return w.edges(sel).chamfer(r)
    except Exception:
        return w
def star(n, ro, ri, h, plane="XY"):
    """toothed disc (gear or spline) on a plane through the origin, extruded h along the plane normal"""
    pts = []
    for k in range(n):
        a = 2 * math.pi * k / n
        for da, r in ((-0.30, ri), (-0.12, ro), (0.12, ro), (0.30, ri)):
            aa = a + da * 2 * math.pi / n
            pts.append((r * math.cos(aa), r * math.sin(aa)))
    return cq.Workplane(plane).polyline(pts).close().extrude(h)
def wire_path(points, d):
    """round wire along a polyline of 3D points (sharp joints, small balls hide them)"""
    out = None
    for p, q in zip(points, points[1:]):
        v = cq.Vector(*q) - cq.Vector(*p)
        s = cq.Solid.makeCylinder(d / 2, v.Length, cq.Vector(*p), v.normalized())
        out = s if out is None else out.fuse(s)
    for p in points[1:-1]:
        out = out.fuse(cq.Solid.makeSphere(d / 2, cq.Vector(*p), angleDegrees1=-90, angleDegrees2=90))
    return out

def part(name, pieces):
    """pieces: [(label, shape, colour name or rgb)]"""
    n = Node(name)
    for label, shape, col in pieces:
        n.children.append(Leaf(label, shape, COL[col] if isinstance(col, str) else col))
    return n

def header_row(n, pitch=2.54, up=6.0, down=3.0, strip_h=2.5, along="x", tag="header"):
    """straight pin header lying on Z=0 (the board top), strip on top, pins up and through the board. Centred on the origin."""
    L = pitch * n
    strip = B(L, 2.5, strip_h) if along == "x" else B(2.5, L, strip_h)
    for i in range(n):           # the waist between pins, as on real strips
        o = -L / 2 + pitch * (i + 1)
        if i < n - 1:
            notch = B(0.4, 3, 0.6, cx=o, z0=strip_h - 0.6) if along == "x" else B(3, 0.4, 0.6, cy=o, z0=strip_h - 0.6)
            strip = strip.cut(notch)
    pins = None
    for i in range(n):
        o = -L / 2 + pitch / 2 + pitch * i
        p = cham(B(0.64, 0.64, strip_h + up + down, cx=o if along == "x" else 0, cy=0 if along == "x" else o, z0=-down), ">Z or <Z", 0.15)
        pins = p if pins is None else pins.union(p)
    return [(tag + "_strip", strip, "black"), (tag + "_pins", pins, "gold")]

def smd(cx, cy, z0, kind):
    """a few common SMD parts lying on a board top at z0: returns pieces"""
    if kind == "0603r":
        return [("r0603", B(1.6, 0.8, 0.45, cx, cy, z0), "res"), ("r0603_ends", B(0.3, 0.8, 0.45, cx - 0.65, cy, z0).union(B(0.3, 0.8, 0.45, cx + 0.65, cy, z0)), "nickel")]
    if kind == "0603c":
        return [("c0603", B(1.0, 0.8, 0.8, cx, cy, z0), "cap"), ("c0603_ends", B(0.3, 0.8, 0.8, cx - 0.65, cy, z0).union(B(0.3, 0.8, 0.8, cx + 0.65, cy, z0)), "nickel")]
    if kind == "0805c":
        return [("c0805", B(1.4, 1.25, 1.0, cx, cy, z0), "cap"), ("c0805_ends", B(0.3, 1.25, 1.0, cx - 0.85, cy, z0).union(B(0.3, 1.25, 1.0, cx + 0.85, cy, z0)), "nickel")]
    if kind == "led_red" or kind == "led_blue":
        return [("led", B(1.6, 0.8, 0.6, cx, cy, z0), "white"), ("led_lens", B(1.0, 0.7, 0.15, cx, cy, z0 + 0.6), kind)]
    if kind == "sot23":
        legs = None
        for dx, dy in ((-0.95, -1.1), (0.95, -1.1), (0, 1.1)):
            l = B(0.4, 0.6, 0.25, cx + dx, cy + dy, z0)
            legs = l if legs is None else legs.union(l)
        return [("sot23", B(2.9, 1.3, 1.0, cx, cy, z0 + 0.1), "chip"), ("sot23_legs", legs, "nickel")]
    raise ValueError(kind)

def soic(cx, cy, z0, n, body=(4.9, 3.9), pitch=1.27, h=1.5, rot=0):
    """SOIC-n lying on a board top at z0, long axis along X (rot=90: along Y)"""
    bx, by = body
    b = cham(B(bx, by, h - 0.1, z0=0.1), ">Z", 0.15)
    b = b.cut(CZ(0.6, 0.2, cx=-bx / 2 + 0.8, cy=-by / 2 + 0.8, z0=h - 0.1))       # pin-1 dimple
    legs = None
    for s in (-1, 1):
        for i in range(n // 2):
            x = -pitch * (n / 4 - 0.5) + pitch * i
            l = XB(x - 0.2, x + 0.2, s * by / 2, s * (by / 2 + 1.0), 0, 0.2).union(XB(x - 0.2, x + 0.2, s * by / 2, s * (by / 2 + 0.25), 0.2, 0.75))
            legs = l if legs is None else legs.union(l)
    if rot:
        b = b.rotate((0, 0, 0), (0, 0, 1), rot); legs = legs.rotate((0, 0, 0), (0, 0, 1), rot)
    return [("ic_body", b.translate((cx, cy, z0)), "chip"), ("ic_legs", legs.translate((cx, cy, z0)), "nickel")]


# ---------------- GA12-N20 gear motor, 100 RPM, 3 mm D-shaft x 10 mm ----------------
def motor_ga12_n20():
    """GA12-N20 metal gear motor. Origin: shaft axis is +Y; Y=0 is the gearbox front face. Gearbox and motor run toward -Y.
    Gearbox 12 x 10 x 9 mm, two M1.6 tapped holes 9 mm apart on the front face, can 12 mm round with 10 mm flats, 15 mm long."""
    pieces = []
    def plate(y_front, t):
        p = cq.Workplane("XZ").rect(12, 10).extrude(t).translate((0, y_front, 0))
        return cham(p, "|Y", 0.6)
    front = plate(0, 1.0)
    for sx in (-4.5, 4.5):
        front = front.cut(CY(1.6, 3, x=sx, z=0, y0=-1.5))             # M1.6 holes, 9 mm apart
    front = front.cut(CY(3.2, 3, y0=-1.5))
    pieces += [("gearbox_front_plate", front, "nickel"),
               ("gearbox_mid_plate", plate(-4.2, 0.7).cut(CY(1.2, 2, x=2.2, z=1.3, y0=-5)), "nickel"),
               ("gearbox_rear_plate", plate(-8.2, 0.8), "nickel")]
    posts = None
    for sx in (-4.6, 4.6):
        for sz in (-3.6, 3.6):
            if sx > 0 and sz > 0:
                continue                          # one corner holds the idler gear shaft instead
            q = CY(1.3, 7.2, x=sx, z=sz, y0=-8.2)
            posts = q if posts is None else posts.union(q)
    pieces.append(("gearbox_posts", posts, "nickel"))
    # visible gear train between the plates
    g1 = star(18, 4.6, 4.1, 1.2, "XZ").translate((0, -1.0, 0))                          # output gear behind the front plate
    g2 = star(10, 2.4, 2.0, 1.2, "XZ").translate((2.2, -2.4, 1.3)).union(star(22, 3.6, 3.2, 0.9, "XZ").translate((2.2, -3.3, 1.3)))
    g3 = star(10, 2.4, 2.0, 1.2, "XZ").translate((-2.0, -5.4, -1.0)).union(star(22, 3.6, 3.2, 0.9, "XZ").translate((-2.0, -6.3, -1.0)))
    g4 = star(10, 2.4, 2.0, 1.2, "XZ").translate((1.6, -6.6, -0.8)).union(star(22, 3.6, 3.2, 0.9, "XZ").translate((1.6, -7.5, -0.8)))
    pieces += [("gear_output", g1, "brass"), ("gear_stage_2", g2, "steel"), ("gear_stage_3", g3, "brass"), ("gear_stage_4", g4, "steel"),
               ("gear_shafts", CY(1.0, 7.4, x=2.2, z=1.3, y0=-8.0).union(CY(1.0, 7.4, x=-2.0, z=-1.0, y0=-8.0)).union(CY(1.0, 7.4, x=1.6, z=-0.8, y0=-8.0)), "steel")]
    # output shaft: 3 mm with a 0.5 mm flat over the last 8 mm, small bushing in the front plate
    shaft = CY(3.0, 10.0 + 4.0, y0=-4.0).cut(XB(-2, 2, 2.0, 10.1, 1.0, 2.0))
    shaft = cham(shaft, ">Y", 0.2)
    pieces += [("output_shaft_3mm_D", shaft, "steel"), ("shaft_bushing", CY(4.0, 0.6, y0=0.0).cut(CY(3.0, 2, y0=-0.5)), "brass")]
    # motor can: 12 mm round, cut to 10 mm flats top and bottom
    can = CY(12, 15, y0=-24.0).intersect(XB(-7, 7, -24.0, -9.0, -5, 5))
    can = can.cut(CY(10.4, 0.4, y0=-9.6).cut(CY(9.8, 2, y0=-10)))                      # crimp ring next to the gearbox
    for sx in (-1, 1):
        can = can.cut(XB(sx * 5.4, sx * 6.2, -20.0, -17.0, -1.2, 1.2))                 # the two tabs that hold the end cap
    pieces.append(("motor_can", can, "steel"))
    cap = CY(11.6, 1.8, y0=-25.8).intersect(XB(-6, 6, -26, -24, -4.8, 4.8))
    cap = cap.union(CY(4.0, 0.7, y0=-26.5)).union(CY(2.4, 0.4, y0=-26.9))              # rear bearing bump and shaft end
    pieces.append(("end_cap", cap, "black"))
    tabs = None
    for sx in (-3.6, 3.6):
        t = XB(sx - 0.15, sx + 0.15, -28.6, -24.6, -1.2, 1.2).cut(CX(1.0, 1, y=-27.6, z=0, x0=sx - 0.5))
        tabs = t if tabs is None else tabs.union(t)
    pieces += [("terminals", tabs, "brass"), ("terminal_marks", B(0.8, 0.2, 0.8, cx=3.6, cy=-25.85, z0=2.6).union(CZ(0.9, 0.2, cx=-3.6, cy=-25.9, z0=2.6)), "red")]
    return part("GA12-N20_motor_100rpm", pieces)


# ---------------- SG90 micro servo ----------------
def servo_sg90(horn=None, lead=38.0):
    """TowerPro-style SG90, 180 degrees. Origin: output shaft axis is +Z through (0,0); Z=0 is the underside of the mounting ears.
    Body runs toward -X; cable leaves the -X end at the bottom. horn: None, "single", "double" or "cross"."""
    cx = -5.9                                    # body centre: shaft is 5.5 mm from the front end
    lower = fil(B(22.4, 11.8, 2.4, cx=cx, z0=-15.9), "|Z", 0.6)
    mid = fil(B(22.4, 11.8, 15.9 - 2.4 - 0.25 + 0.0, cx=cx, z0=-13.5 + 0.0), "|Z", 0.6)
    ears = fil(B(32.4, 11.8, 2.5, cx=cx, z0=0.0), "|Z", 1.0)
    for dx in (-13.75, 13.75):
        ears = ears.cut(CZ(2.0, 4, cx=cx + dx, z0=-1)).cut(B(3.0, 1.0, 4, cx=cx + dx + (1.5 if dx > 0 else -1.5), z0=-1))
    upper = fil(B(22.4, 11.8, 4.1, cx=cx, z0=2.5), "|Z", 0.6)
    body = mid.union(ears).union(upper)
    body = body.cut(XB(cx - 11.3, cx + 11.3, -6.0, -5.8, -12.5, -3.0))                 # label recess on the -Y face
    tower = CZ(11.8, 4.3, z0=6.6).union(CZ(5.4, 4.3, cx=-6.4, z0=6.6)).union(XB(-6.4, 0, -2.7, 2.7, 6.6, 10.9))
    tower = fil(tower, ">Z", 0.4)
    spline = star(21, 2.45, 2.2, 3.2).translate((0, 0, 10.9)).union(CZ(3.2, 0.6, z0=10.6))
    spline = spline.cut(CZ(1.6, 3.0, z0=11.4))                                          # horn screw hole
    screws = None
    for sx in (cx - 9.0, cx + 9.0):
        for sy in (-4.0, 4.0):
            s = CZ(1.8, 0.4, cx=sx, cy=sy, z0=-16.3)
            s = s.cut(XB(sx - 0.7, sx + 0.7, sy - 0.12, sy + 0.12, -16.5, -16.0)).cut(XB(sx - 0.12, sx + 0.12, sy - 0.7, sy + 0.7, -16.5, -16.0))
            screws = s if screws is None else screws.union(s)
    label = XB(cx - 11.0, cx + 11.0, -6.0, -5.85, -12.2, -3.3)
    pieces = [("case_bottom", lower, "sg90"), ("case_middle_and_ears", body, "sg90"), ("gear_tower", tower, "sg90"),
              ("output_spline_21T", spline, "white"), ("bottom_screws", screws, "steel"), ("label", label, "sg90_label")]
    # cable: three wires leave the bottom of the -X end, bend down and stop after 25 mm (the real lead is 25 cm)
    x0 = cx - 11.2
    for i, col in enumerate(("brown", "red", "orange")):
        y = -1.0 + 1.0 * i
        pieces.append(("wire_" + col, wire_path([(x0 + 0.5, y, -14.6), (x0 - 4, y, -14.6), (x0 - 8, y, -19.0), (x0 - 8, y, -lead)], 0.95), col))
    pieces.append(("cable_grommet", XB(x0 - 0.8, x0 + 0.6, -2.0, 2.0, -15.4, -13.8), "sg90"))
    if horn:
        h = CZ(7.0, 3.6, z0=11.0)
        if horn in ("single", "double", "cross"):
            arms = [0] if horn == "single" else ([0, 180] if horn == "double" else [0, 90, 180, 270])
            for a in arms:
                arm = (cq.Workplane("XY").polyline([(0, -3.0), (15.5 if horn == "single" else 14, -1.9), (15.5 if horn == "single" else 14, 1.9), (0, 3.0)]).close()
                       .extrude(1.5).translate((0, 0, 13.1)).union(CZ(3.8, 1.5, cx=15.5 if horn == "single" else 14, z0=13.1)))
                for k in range(6):
                    arm = arm.cut(CZ(0.9, 4, cx=4.5 + 2.0 * k, z0=12))
                h = h.union(arm.rotate((0, 0, 0), (0, 0, 1), a))
        h = h.cut(star(21, 2.5, 2.25, 3.0).translate((0, 0, 10.9))).cut(CZ(2.2, 6, z0=12))
        pieces += [("horn_" + horn, h, "white"), ("horn_screw", CZ(3.6, 1.0, z0=14.6).union(CZ(1.8, 3.4, z0=11.4)), "steel")]
    return part("SG90_servo", pieces)


# ---------------- Seeed XIAO ESP32S3 Sense (brain, OV2640 camera, microphone, SD slot) ----------------
def xiao_esp32s3_sense():
    """Origin: tip of the camera lens, looking toward +X. Both boards stand upright (21 mm along Y, 17.8 mm along Z);
    the XIAO's USB-C is at the +Y end, its shield and the 2 x 7 header pins point back (-X)."""
    W, H = 21.0, 17.8
    def board(x0, t, col):
        b = fil(XB(x0 - t, x0, -W / 2, W / 2, -H / 2, H / 2), "|X", 0.8)
        return b, col
    pieces = []
    # camera: lens barrel, holder, sensor module on its small board, folded FPC down to the expansion board
    pieces += [("camera_lens_glass", CX(3.6, 0.3, x0=-0.3), "lens"),
               ("camera_lens_barrel", CX(6.2, 1.6, x0=-1.6).cut(CX(3.6, 2, x0=-1.7)).union(CX(7.0, 0.6, x0=-2.0)), "black"),
               ("camera_holder", fil(XB(-4.6, -2.0, -4.25, 4.25, -4.25, 4.25), "|X", 0.6), "black"),
               ("camera_module_board", XB(-5.1, -4.6, -4.25, 4.25, -4.25, 6.2), "pcb_black"),
               ("camera_fpc", XB(-5.4, -5.1, -3.0, 3.0, 4.0, 7.6), "kapton")]
    eb, c = board(-6.0, 1.0, "pcb_black"); pieces.append(("sense_expansion_board", eb, c))
    # FPC socket, SD card slot and microphone sit on the expansion board's camera side (x = -6.0 .. -4.6)
    pieces += [("fpc_connector", XB(-5.6, -5.0, -3.8, 3.8, 6.2, 8.4), "white"),
               ("sd_card_slot", XB(-6.0, -4.6, -7.5, 1.5, -8.6, -1.6), "steel"),
               ("microphone_MSM261", XB(-6.0, -5.0, 6.0, 9.5, -1.4, 1.4), "steel"),
               ("mic_port", CX(0.6, 0.15, y=7.75, z=0, x0=-5.05), "black")]
    pieces.append(("board_to_board_connector", XB(-10.2, -7.0, -6.0, 6.0, -1.4, 1.4), "white"))
    xb, c = board(-10.2, 1.0, "pcb_black")
    for zz in (-7.62, 7.62):                      # castellated half-holes along both long edges
        for i in range(7):
            yy = -7.62 + 2.54 * i
            xb = xb.cut(CX(1.0, 3, y=yy, z=zz, x0=-12))
    pieces.append(("xiao_esp32s3_board", xb, c))
    pads = None
    for zz in (-7.62, 7.62):
        for i in range(7):
            p = CX(1.6, 1.04, y=-7.62 + 2.54 * i, z=zz, x0=-11.22).cut(CX(1.0, 3, y=-7.62 + 2.54 * i, z=zz, x0=-12))
            pads = p if pads is None else pads.union(p)
    pieces.append(("castellation_pads", pads, "gold"))
    top = -10.2 - 1.0                              # XIAO top face (components point toward -X from here)
    pieces += [("rf_shield_can", fil(XB(top - 2.2, top, -6.6, 5.6, -5.4, 5.4), "|X", 0.3), "nickel"),
               ("usb_c_receptacle", fil(XB(top - 3.2, top, 6.8, 10.9, -4.47, 4.47), "|Y", 1.2), "nickel"),
               ("usb_c_mouth", XB(top - 2.6, top - 0.6, 10.5, 10.95, -3.6, 3.6), "black"),
               ("u_fl_antenna_connector", CX(2.0, 1.25, y=-8.6, z=-2.5, x0=top - 1.25).union(XB(top - 0.5, top, -9.6, -7.6, -3.5, -1.5)), "gold"),
               ("boot_button", XB(top - 1.4, top, -9.8, -7.8, 3.0, 5.0).union(XB(top - 1.9, top - 1.4, -9.1, -8.5, 3.6, 4.4)), "nickel"),
               ("reset_button", XB(top - 1.4, top, -9.8, -7.8, 5.6, 7.6 - 0.6).union(XB(top - 1.9, top - 1.4, -9.1, -8.5, 6.0, 6.6)), "nickel"),
               ("charge_led", XB(top - 0.6, top, 4.6, 5.4, 5.8, 6.6), "led_red"),
               ("user_led", XB(top - 0.6, top, 4.6, 5.4, -6.6, -5.8), "orange")]
    for zz, nm in ((-7.62, "header_bottom_row"), (7.62, "header_top_row")):
        strip = XB(top - 2.5, top, -8.89, 8.89, zz - 1.25, zz + 1.25)
        pins = None
        for i in range(7):
            yy = -7.62 + 2.54 * i
            q = XB(top - 8.5, -10.2 + 0.0, yy - 0.32, yy + 0.32, zz - 0.32, zz + 0.32)
            pins = q if pins is None else pins.union(q)
        pieces += [(nm + "_strip", strip, "black"), (nm + "_pins", pins, "gold")]
    return part("XIAO_ESP32S3_Sense", pieces)


# ---------------- 0.96 inch IPS display, ST7735, 80 x 160, 8-pin SPI module ----------------
def display_st7735_096():
    """Origin: centre of the glass front face, the screen looks toward +X. Module 30 x 24 mm used landscape,
    8-pin header on the right-hand edge (as seen from the front) with pins pointing back."""
    pcb = XB(-4.6, -3.0, -15.0, 15.0, -12.0, 12.0)
    for sy in (-1, 1):
        for sz in (-1, 1):
            pcb = pcb.cut(CX(2.0, 3, y=sy * 12.5, z=sz * 9.5, x0=-5))
    pcb = fil(pcb, "|X", 0.8)
    panel = XB(-3.0, -1.5, -13.98, 13.98, -6.75, 6.75)
    glass = XB(-1.5, -0.0, -13.98, 13.98, -6.75, 6.75)
    active = XB(-0.02, 0.0, -10.85 - 0.5, 10.85 - 0.5, -5.4, 5.4)
    bezel = glass.cut(XB(-0.5, 0.1, -10.85 - 0.5, 10.85 - 0.5, -5.4, 5.4))
    pieces = [("module_pcb", pcb, "pcb_blue"), ("lcd_panel_back", panel, "steel"), ("cover_glass", bezel, "glass"),
              ("active_area_80x160", active, "screen"),
              ("panel_fpc", XB(-4.6, -1.5, 13.98, 14.6, -4.0, 4.0).union(XB(-4.8, -4.6, 10.0, 14.6, -4.0, 4.0)), "kapton"),
              ("backlight_tape", XB(-3.1, -3.0, -13.0, 12.0, -6.0, 6.0), "white")]
    # parts on the back: 3.3 V regulator, two caps, a resistor
    for nm, (y, z, w, h, t, col) in {"ldo_sot23": (-6, -8, 2.9, 1.6, 1.1, "chip"), "cap_1": (-1, -8.5, 2.0, 1.25, 1.0, "cap"),
                                    "cap_2": (2, -8.5, 2.0, 1.25, 1.0, "cap"), "res_bl": (6, -8.5, 1.6, 0.8, 0.45, "res")}.items():
        pieces.append((nm, XB(-4.6 - t, -4.6, y - w / 2, y + w / 2, z - h / 2, z + h / 2), col))
    strip = XB(-7.1, -4.6, 12.7 - 1.25, 12.7 + 1.25, -10.16, 10.16)
    pins = None
    for i in range(8):
        z = -8.89 + 2.54 * i
        q = XB(-13.1, -1.8, 12.7 - 0.32, 12.7 + 0.32, z - 0.32, z + 0.32)
        pins = q if pins is None else pins.union(q)
    pieces += [("header_strip_8", strip, "black"), ("header_pins_8", pins, "gold")]
    return part("ST7735_0.96in_IPS_display", pieces)


# ---------------- MAX98357A I2S amplifier breakout ----------------
def amp_max98357a():
    """Origin: board centre, Z=0 underside. Speaker terminal block at +Y, 7-pin header along the -Y edge, pins up."""
    pcb = fil(B(17.8, 19.3, 1.6), "|Z", 0.8)
    pcb = pcb.cut(CZ(2.5, 4, cx=-6.4, cy=6.4, z0=-1)).cut(CZ(2.5, 4, cx=6.4, cy=6.4, z0=-1))
    t = 1.6
    tb = fil(XB(-3.5, 3.5, 3.0, 10.2, t, t + 8.5), "|Z", 0.3)
    tb = tb.cut(XB(-3.0, -0.4, 9.5, 10.6, t + 1.0, t + 4.0)).cut(XB(0.4, 3.0, 9.5, 10.6, t + 1.0, t + 4.0))
    screws = None
    for x in (-1.75, 1.75):
        s = CZ(2.6, 0.6, cx=x, cy=6.0, z0=t + 8.5 - 0.6).cut(XB(x - 1.4, x + 1.4, 5.85, 6.15, t + 7.6, t + 9))
        screws = s if screws is None else screws.union(s)
    pieces = [("pcb", pcb, "pcb_purple"), ("terminal_block_3.5mm", tb.cut(CZ(2.8, 1, cx=-1.75, cy=6.0, z0=t + 7.9)).cut(CZ(2.8, 1, cx=1.75, cy=6.0, z0=t + 7.9)), "green_term"),
              ("terminal_screws", screws, "nickel"),
              ("max98357a_qfn", cham(B(3.0, 3.0, 0.8, cx=0, cy=-1.5, z0=t), ">Z", 0.1), "chip")]
    for i, (x, y, k) in enumerate(((-4.5, -1.5, "0805c"), (-4.5, 1.0, "0805c"), (4.5, -1.5, "0603c"), (4.5, 0.5, "0603r"), (4.5, 2.2, "0603r"), (-2.0, 2.0, "0603c"))):
        pieces += [("%s_%d" % (n, i), s, c) for n, s, c in smd(x, y, t, k)]
    for n, s, c in header_row(7, up=6.0, down=3.0, tag="header_7"):
        pieces.append((n, s.translate((0, -7.8, t)), c))
    return part("MAX98357A_amplifier", pieces)


# ---------------- TCRT5000 reflective sensor module ----------------
def tcrt5000_module():
    """Origin: centre of the sensor head on the PCB underside plane (Z=0); the sensor looks toward -Z. Board runs toward -Y,
    M3 hole at Y=-10, 4-pin header at the far end with pins up (VCC, GND, DO, AO)."""
    pcb = fil(B(14.0, 32.0, 1.6, cy=-11.0), "|Z", 0.6).cut(CZ(3.2, 4, cy=-10.0, z0=-1))
    t = 1.6
    housing = fil(B(10.2, 5.8, 6.3, z0=-6.3), "|Z", 0.5)
    housing = housing.cut(CZ(3.1, 6.5, cx=-2.54, z0=-6.8)).cut(CZ(3.1, 6.5, cx=2.54, z0=-6.8)).cut(B(0.6, 6.2, 4.0, z0=-6.8))
    pieces = [("pcb", pcb, "pcb_blue"), ("tcrt5000_housing", housing, "black"),
              ("ir_led_lens", CZ(3.0, 6.0, cx=-2.54, z0=-6.6).union(cq.Workplane("XY").sphere(1.5).translate((-2.54, 0, -6.6))), "ir_led"),
              ("phototransistor_lens", CZ(3.0, 6.0, cx=2.54, z0=-6.6).union(cq.Workplane("XY").sphere(1.5).translate((2.54, 0, -6.6))), "black")]
    legs = None
    for x in (-3.8, -1.3, 1.3, 3.8):
        l = B(0.5, 0.5, 2.2, cx=x, cy=0, z0=t - 0.4)
        legs = l if legs is None else legs.union(l)
    pieces.append(("sensor_leg_tails", legs, "nickel"))
    pieces += soic(0, -4.6, t, 8, rot=90)
    pot = fil(B(6.6, 6.6, 4.6, cy=-17.0, z0=t), "|Z", 0.4)
    pot = pot.union(CZ(3.0, 0.8, cy=-17.0, z0=t + 4.6))
    pieces += [("trim_pot", pot.cut(XB(-1.3, 1.3, -17.15, -16.85, t + 4.9, t + 5.6)), "blue_pot")]
    for i, (x, y, k) in enumerate(((-4.6, -3.5, "0603r"), (-4.6, -9.0, "0603r"), (4.6, -3.5, "0603r"), (4.6, -9.0, "0603c"), (4.6, -11.5, "0603r"))):
        pieces += [("%s_%d" % (n, i), s, c) for n, s, c in smd(x, y, t, k)]
    pieces += [("%s_power" % n, s, c) for n, s, c in smd(-4.5, -21.5, t, "led_red")]
    pieces += [("%s_signal" % n, s, c) for n, s, c in smd(4.5, -21.5, t, "led_red")]
    for n, s, c in header_row(4, up=6.0, down=2.5, tag="header_4"):
        pieces.append((n, s.translate((0, -25.5, t)), c))
    return part("TCRT5000_edge_sensor", pieces)


# ---------------- 1S LiPo 803040, 1000 mAh, with protection board and JST PH plug ----------------
def lipo_803040():
    """Origin: centre of the footprint, Z=0 underside. 40 x 30 x 8 mm pouch; the sealed end with the folded protection
    board is at -X and the leads leave from there; the JST PH 2.0 plug sits 15 mm behind the cell."""
    L, W, T = 40.0, 30.0, 8.0
    cell = fil(XB(-L / 2 + 4.0, L / 2, -W / 2, W / 2, 0, T), "|X", 1.6)
    cell = fil(cell, ">X", 0.8)
    seal_flaps = XB(-L / 2 + 4.0, L / 2 - 1.0, W / 2 - 0.1, W / 2 + 0.0, 1.0, T - 1.0)
    pcm = XB(-L / 2 + 0.4, -L / 2 + 4.0, -W / 2 + 1.5, W / 2 - 1.5, 1.4, T - 1.4)
    tape = XB(-L / 2, -L / 2 + 4.2, -W / 2 + 1.0, W / 2 - 1.0, 1.0, T - 1.0).cut(XB(-L / 2 + 0.3, -L / 2 + 4.3, -W / 2 + 1.4, W / 2 - 1.4, 1.3, T - 1.3))
    label = XB(-L / 2 + 6.0, L / 2 - 2.0, -W / 2 + 2.0, W / 2 - 2.0, T, T + 0.05)
    x0 = -L / 2
    red = wire_path([(x0 + 0.2, 1.2, T / 2), (x0 - 6, 1.2, T / 2), (x0 - 12, 1.0, 4.0)], 1.1)
    blk = wire_path([(x0 + 0.2, -1.2, T / 2), (x0 - 6, -1.2, T / 2), (x0 - 12, -1.0, 4.0)], 1.1)
    plug = fil(XB(x0 - 16.5, x0 - 12.0, -3.0, 3.0, 1.6, 6.4), "|X", 0.3).cut(XB(x0 - 17, x0 - 15.0, -2.4, 2.4, 2.4, 5.6))
    return part("LiPo_803040_1000mAh", [("pouch_cell", cell, "pouch"), ("pouch_seal", seal_flaps, "pouch"), ("protection_board", pcm, "pcb_green"),
                                         ("kapton_wrap", tape, "kapton"), ("label", label, "white"), ("lead_red", red, "red"), ("lead_black", blk, "black"),
                                         ("jst_ph2_plug", plug, "white")])


# ---------------- 20 mm 8 ohm 1 W speaker with leads ----------------
def speaker_20mm():
    """Origin: centre of the front rim, sound comes out toward -X. 20 mm across, 4.8 mm deep."""
    frame = CX(20.0, 0.6, x0=0).cut(CX(17.2, 2, x0=-0.5))
    surround = cq.Workplane("YZ").circle(8.6).circle(7.4).extrude(0.6).translate((0.25, 0, 0))
    cone = cq.Workplane("YZ").circle(7.6).workplane(offset=2.0).circle(3.2).loft().translate((0.4, 0, 0))
    cone = cone.cut(cq.Workplane("YZ").circle(7.3).workplane(offset=2.0).circle(2.9).loft().translate((0.2, 0, 0)))
    dome = cq.Workplane("XY").sphere(3.6).intersect(CX(8, 3, x0=-3.6)).translate((4.2, 0, 0)).intersect(CX(7.2, 2, x0=0.6))
    basket = CX(17.6, 1.6, x0=0.6).cut(CX(16.4, 2, x0=0.5)).union(CX(14.0, 0.5, x0=2.0))
    magnet = CX(11.0, 1.6, x0=2.4).union(CX(9.0, 0.6, x0=4.0)).cut(CX(1.6, 4, x0=1))
    pads = XB(2.3, 2.9, 7.6, 10.4, -2.6, -0.8).union(XB(2.3, 2.9, 7.6, 10.4, 0.8, 2.6))
    red = wire_path([(2.9, 9.6, 1.7), (6.0, 9.6, 1.7), (9.0, 11.0, 1.7)], 0.9)
    blk = wire_path([(2.9, 9.6, -1.7), (6.0, 9.6, -1.7), (9.0, 11.0, -1.7)], 0.9)
    return part("speaker_20mm_8ohm_1W", [("frame_rim", frame, "steel"), ("surround", surround, "rubber"), ("cone", cone, "paper"), ("dust_cap", dome, "dark"),
                                          ("basket", basket, "steel"), ("magnet", magnet, "magnet"), ("solder_tabs", pads, "pcb_green"),
                                          ("lead_red", red, "red"), ("lead_black", blk, "black")])


# ---------------- HRO TYPE-C-31-M-12 USB-C receptacle (the power board's charge socket; KiCad has no model) ----------------
def usb_c_hro_31_m_12():
    """Origin: centre of the mouth on the board top plane; the plug goes in from -X, the body runs toward +X, Z=0 is the board top.
    Shell 8.94 x 3.26 mm, 7.35 mm deep."""
    W, Hh, D = 8.94, 3.26, 7.35
    shell = cq.Workplane("YZ").slot2D(W, Hh).extrude(D).translate((0, 0, Hh / 2))
    shell = shell.cut(cq.Workplane("YZ").slot2D(W - 0.5, Hh - 0.5).extrude(D - 0.6).translate((-0.1, 0, Hh / 2)))
    tongue = XB(0.9, D - 0.6, -3.3, 3.3, Hh / 2 - 0.35, Hh / 2 + 0.35)
    contacts = None
    for i in range(12):
        y = -2.75 + 0.5 * i
        c = XB(1.2, D - 1.0, y - 0.12, y + 0.12, Hh / 2 + 0.35, Hh / 2 + 0.4).union(XB(1.2, D - 1.0, y - 0.12, y + 0.12, Hh / 2 - 0.4, Hh / 2 - 0.35))
        contacts = c if contacts is None else contacts.union(c)
    legs = None
    for y in (-4.32, 4.32):
        for x, depth in ((1.6, 1.6), (5.8, 1.6)):
            l = XB(x - 0.3, x + 0.3, y - 0.3, y + 0.3, -depth, 0.5)
            legs = l if legs is None else legs.union(l)
    smt = None
    for i in range(12):
        y = -2.75 + 0.5 * i
        s = XB(D - 0.2, D + 0.6, y - 0.12, y + 0.12, 0, 0.12)
        smt = s if smt is None else smt.union(s)
    return part("USB-C_HRO_TYPE-C-31-M-12", [("shell", shell, "nickel"), ("tongue", tongue, "black"), ("contacts", contacts, "gold"),
                                             ("shell_legs", legs, "nickel"), ("smt_leads", smt, "gold")])


# ---------------- Pololu 22T track set (Pololu's own STEP) and its idler axle screw ----------------
_pololu_cache = []
def pololu_track_22t():
    """Pololu 22T track set, one side: track, drive sprocket (3 mm D bore, at the origin) and idler sprocket (48 mm along +X).
    Origin: drive sprocket axis; the axles run along Z, the hub side of the drive sprocket (toward the robot) is +Z.
    Track 14.6 mm wide, 39 mm tall, 87 mm long."""
    if not _pololu_cache:
        _pololu_cache.append(cq.importers.importStep(POLOLU_STEP).val())
    return part("Pololu_22T_track_set", [("track_and_sprockets", _pololu_cache[0], "rubber")])

def m3_axle_screw(length=12.0):
    """M3 pan-head screw used as the idler axle. Origin: under the head on the axis, shank along +Z."""
    head = CZ(5.5, 2.0, z0=-2.0).cut(XB(-1.8, 1.8, -0.3, 0.3, -2.6, -1.2)).cut(XB(-0.3, 0.3, -1.8, 1.8, -2.6, -1.2))
    return part("M3x%d_idler_axle" % length, [("head", fil(head, "<Z", 0.5), "steel"), ("shank", CZ(3.0, length), "steel")])


# ---------------- power board, from the KiCad 3D export ----------------
def power_board():
    """Dimer V2 power board exactly as laid out in KiCad (official KiCad 3D models for every part, the USB-C added here).
    Origin and axes: KiCad's (X right, Y up = -KiCad Y, Z up from the board underside); the board spans X 0..39.5, Y -33..0."""
    parts_json = json.load(open(BOARD_JSON))
    refs = []
    for p in parts_json["parts"]:
        refs.append((p["ref"], p.get("value", ""), (p["x0"] + p["x1"]) / 2, -(p["y0"] + p["y1"]) / 2))
    n = Node("Dimer_V2_power_board")
    used = {}
    for name, shape, rgb, faces in step_colors.load(BOARD_STEP):
        bb = shape.BoundingBox()
        if "PCB" in name:
            n.children.append(Leaf("pcb_1.6mm", shape, (0.08, 0.2, 0.14), faces)); continue
        cx, cy = (bb.xmin + bb.xmax) / 2, (bb.ymin + bb.ymax) / 2
        ref = min(refs, key=lambda r: (r[2] - cx) ** 2 + (r[3] - cy) ** 2)
        k = ref[0]; used[k] = used.get(k, 0) + 1
        label = "%s_%s" % (k, name) if used[k] == 1 else "%s_%s_%d" % (k, name, used[k])
        n.children.append(Leaf(label, shape, rgb, faces))
    j1 = next(p for p in parts_json["parts"] if p["ref"] == "J1")
    usb = usb_c_hro_31_m_12()
    loc = cq.Location(cq.Vector(min(j1["x0"], j1["x1"]), -(j1["y0"] + j1["y1"]) / 2, parts_json["thickness"]))
    for leaf in usb.children:
        n.children.append(Leaf("J1_USB-C_" + leaf.name, leaf.shape.moved(loc), leaf.rgb))
    return n


ALL = {"motor": motor_ga12_n20, "servo": lambda: servo_sg90(horn="single"), "brain": xiao_esp32s3_sense, "display": display_st7735_096,
       "amp": amp_max98357a, "edge_sensor": tcrt5000_module, "battery": lipo_803040, "speaker": speaker_20mm, "usb_c": usb_c_hro_31_m_12,
       "track": pololu_track_22t, "idler_screw": lambda: m3_axle_screw(20), "power_board": power_board}

if __name__ == "__main__":
    out = os.path.join(HERE, "step", "2_0", "parts"); os.makedirs(out, exist_ok=True)
    for key, fn in ALL.items():
        node = fn()
        path = os.path.join(out, node.name + ".step")
        write_step(node, path)
        nf = sum(len(l.shape.Faces()) for l in node.children)
        print("%-40s %3d solids %6d faces %7.0f kB" % (node.name, len(node.children), nf, os.path.getsize(path) / 1024))
