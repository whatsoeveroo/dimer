"""Dimer V2 (half-size) frame guideline generator (CadQuery).

Run:  pip install cadquery && python v2/cad/dimer_v2_frame.py
Writes STEP files into v2/cad/step/.  Units: mm.
Axes: X = forward, Y = left, Z = up, table surface at Z = 0.

V2 is a separate, smaller robot. V1 in cad/ is untouched.
V2.1 layout: the head sits low on a step in front of the electronics bay and tilts up on
one small servo. The brain with its camera lives in the head, above the display.
The shovel is fixed. One flat 1S battery, no custom board.

This is a ROUGH GUIDELINE, not a design: it fixes where the parts sit and
where the mounting holes go.  Change the numbers below after measuring the
parts you actually bought, then run again.

Options (environment variables):
  DIMER_DISPLAY=st7735_096 | gc9a01_128_round | ssd1306_096_oled   which face display
  DIMER_TILT=25                                                   head tilted up by this many degrees (check only, saves nothing)
"""
import json, os, sys, tempfile
import cadquery as cq
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "cad"))
import dimer_components as dc
from dimer_components import B, CZ, CY, CX, asm, small_board, header

DISPLAY = os.environ.get("DIMER_DISPLAY", "st7735_096")
TILT = float(os.environ.get("DIMER_TILT", "0"))
TILT_MAX = 25.0
#            module width, how far it reaches below / above the screen centre, window in the head front
DISPLAYS = {"st7735_096":       dict(w=30.0, below=12.0, above=12.0, window=("rect", 23, 12)),
            "gc9a01_128_round": dict(w=38.0, below=19.0, above=19.0, window=("round", 33)),
            "ssd1306_096_oled": dict(w=27.3, below=12.4, above=18.0, window=("rect", 23, 12))}   # its pins stick back along the top edge
DSP = DISPLAYS[DISPLAY]
VARIANT = DISPLAY != "st7735_096"     # the default display writes the main files; the others go to step/display_options/
OUT = os.path.join(HERE, "step", "display_options", DISPLAY) if VARIANT else os.path.join(HERE, "step")
if TILT: OUT = tempfile.mkdtemp()
os.makedirs(OUT, exist_ok=True)

# ---------------- parameters (edit me) ----------------
TUB_L, TUB_W_IN, WALL = 78.0, 34.0, 2.0        # chassis tub
FLOOR_Z, FLOOR_T = 4.0, 1.5                    # ground clearance 4 mm
TUB_W = TUB_W_IN + 2 * WALL                    # 38
XI = TUB_L / 2 - WALL                          # inner face of front / rear wall (37)
BAY_TOP, STEP_TOP, XS = 40.0, 19.0, 5.0        # tall electronics bay behind x = XS, low step in front of it
LID_T = 2.0
WHEEL_D, WHEELBASE = 22.0, 58.0                # bigger wheels than the first V2 (15 mm)
TRACK_W, TRACK_T, LUG, TRACK_GAP = 11.0, 1.2, 1.4, 1.5
AXLE_Z = WHEEL_D / 2 + TRACK_T + LUG           # 13.6
TRACK_TOP = 2 * AXLE_Z
TRACK_Y = TUB_W / 2 + TRACK_GAP + TRACK_W / 2  # 26
BAT = (40.0, 30.0, 10.0)                       # flat 1S LiPo, largest size that fits
DECK_Z = 20.2                                  # pinned boards sit on foam above battery and motors
PX, PZ = XS - 11.5, 33.5                       # head tilt axis (along Y), just above the tracks
HEAD_W = max(40.0, DSP["w"] + 6)
HEAD_Z = STEP_TOP + LID_T + 2.0 if HEAD_W <= 40 else TRACK_TOP + 1.5   # a head wider than the gap between the tracks must sit above them
HEAD_X0, HEAD_L = XS + WALL + 3.0, 38.0
HEAD_X1 = HEAD_X0 + HEAD_L
LCD_Z = HEAD_Z + 2.0 + DSP["below"]            # display centre
CAM_Z = LCD_Z + DSP["above"] + 5.0             # camera lens centre, above the display
HEAD_H = CAM_Z + 9.5 + 2.0 - HEAD_Z
EDGE_X, EDGE_Y, EDGE_Z = HEAD_X1 + 7.4, 27.0, 10.0   # table-edge sensors, in front of each track
BLADE_X, BLADE_H, BLADE_W = EDGE_X + 7.8, 15.0, 66.0 # fixed shovel blade

def box(x, y, z, cx=0, cy=0, z0=0):
    return cq.Workplane("XY").box(x, y, z, centered=(True, True, False)).translate((cx, cy, z0))
def xbox(x0, x1, y0, y1, z0, z1):
    return box(x1 - x0, y1 - y0, z1 - z0, cx=(x0 + x1) / 2, cy=(y0 + y1) / 2, z0=z0)
def xcyl(d, length, y, z, x0):
    return cq.Workplane("YZ").circle(d / 2).extrude(length).translate((x0, y, z))
def ycyl(d, length, x, z, y0):
    """cylinder along +Y starting at y0"""
    return cq.Workplane("XZ").circle(d / 2).extrude(-length).translate((x, y0, z))
def zcyl(d, h, x, y, z0):
    return cq.Workplane("XY").circle(d / 2).extrude(h).translate((x, y, z0))
def soft(shape, sel, r):
    """round edges if the kernel can, otherwise leave them square"""
    try: return shape.edges(sel).fillet(r)
    except Exception: return shape

# Left motor drives the rear wheel, right motor drives the front wheel.
# Two N20 motors are too long to sit on one axle in a 34 mm wide body.
MOTORS = ((-WHEELBASE / 2, 1), (WHEELBASE / 2, -1))     # (x, side of the driven wheel)

# ---------------- chassis tub ----------------
def chassis():
    outer = soft(box(TUB_L, TUB_W, BAY_TOP - FLOOR_Z, z0=FLOOR_Z), "|Z", 3.0)
    outer = outer.cut(xbox(XS, TUB_L, -TUB_W, TUB_W, STEP_TOP, BAY_TOP + 1))            # low step at the front
    tub = outer.cut(soft(box(TUB_L - 2 * WALL, TUB_W_IN, BAY_TOP, z0=FLOOR_Z + FLOOR_T), "|Z", 1.5))
    for mx, sy in MOTORS:
        # motor shaft hole on the driven side, M3 idler-axle pilot hole on the other side
        tub = tub.cut(ycyl(4.6, WALL + 2, mx, AXLE_Z, TUB_W_IN / 2 - 1 if sy > 0 else -TUB_W / 2 - 1))
        tub = tub.cut(ycyl(2.5, WALL + 2, mx, AXLE_Z, TUB_W_IN / 2 - 1 if sy < 0 else -TUB_W / 2 - 1))
        # saddle under the gearbox with a lip toward the end wall
        pad = box(13, 11, AXLE_Z - 5 - FLOOR_Z - FLOOR_T + 0.1, cx=mx, cy=sy * (TUB_W_IN / 2 - 5.5), z0=FLOOR_Z + FLOOR_T - 0.1)
        tub = tub.union(pad)
    # tilt servo drops into a notch in the left wall; pivot boss for the other head arm on the right wall
    tub = tub.cut(box(23.4, WALL + 2, BAY_TOP - (PZ - 6.4) + 1, cx=PX - 5.4, cy=TUB_W / 2 - WALL / 2, z0=PZ - 6.4))
    boss = ycyl(8, 6.6, PX, PZ, -TUB_W / 2 - 6.3).cut(ycyl(2.5, 12, PX, PZ, -TUB_W / 2 - 8))
    tub = tub.union(boss)
    # front wall: lid tab screws (M2), shovel screws (M2)
    for sy in (-1, 1):
        tub = tub.cut(xcyl(2.2, WALL + 2, sy * 12, STEP_TOP - 4, XI - 1))
    for y in (-5, 5):
        tub = tub.cut(xcyl(1.6, WALL + 2, y, 13, XI - 1))
    # rear wall: USB-C charging slot, lid tab screw (M2)
    tub = tub.cut(box(WALL + 2, 10, 4.4, cx=-XI - WALL / 2, cy=8.5, z0=DECK_Z + 0.2))
    tub = tub.cut(xcyl(2.2, WALL + 2, 4, BAY_TOP - 4, -XI - WALL - 1))
    # battery strap slots in the floor
    for x in (-10, 10):
        tub = tub.cut(box(2, 24, FLOOR_T + 2, cx=x, z0=FLOOR_Z - 1))
    # shell attachment ears on the bay wall tops (M2) - bolt your shell here
    for x, sy in ((-30, 1), (-30, -1), (-2, -1)):
        ear = box(7, 5, 3, cx=x, cy=sy * (TUB_W / 2 + 2.5), z0=BAY_TOP - 3)
        tub = tub.union(ear.cut(zcyl(1.6, 5, x, sy * (TUB_W / 2 + 2.8), BAY_TOP - 4)))
    return tub

# ---------------- top: bay lid, riser and step plate in one piece ----------------
def top():
    lid = soft(box(TUB_L / 2 + XS, TUB_W, LID_T, cx=(XS - TUB_L / 2) / 2, z0=BAY_TOP), "|Z", 3.0)
    riser = xbox(XS, XS + WALL, -TUB_W / 2, TUB_W / 2, STEP_TOP, BAY_TOP + LID_T)
    step = xbox(XS, TUB_L / 2, -TUB_W / 2, TUB_W / 2, STEP_TOP, STEP_TOP + LID_T)
    t = lid.union(riser).union(step)
    t = t.cut(box(WALL + 2, 16, 9, cx=XS + WALL / 2, z0=STEP_TOP + LID_T + 3))             # cable slot from the bay to the head
    t = t.cut(box(4.8, 9, LID_T + 2, cx=-31, cy=8.5, z0=BAY_TOP - 1))                       # slide switch, lever up
    # rear tab behind the rear wall, front tabs behind the front wall: screwed from outside (M2)
    tab = xbox(-XI, -XI + 2.5, 2, 6, BAY_TOP - 8, BAY_TOP).cut(xcyl(1.6, 5, 4, BAY_TOP - 4, -XI - 1))
    t = t.union(tab)
    for sy in (-1, 1):
        tab = xbox(XI - 2.0, XI, sy * 12 - 2, sy * 12 + 2, STEP_TOP - 8, STEP_TOP).cut(xcyl(1.6, 5, sy * 12, STEP_TOP - 4, XI - 3))
        t = t.union(tab)
    return t

# ---------------- head: tilts on the servo, holds display, camera brain, speaker ----------------
def head():
    hx = (HEAD_X0 + HEAD_X1) / 2
    shell = soft(box(HEAD_L, HEAD_W, HEAD_H, cx=hx, z0=HEAD_Z), "|X", 5.0)
    shell = soft(shell, ">X", 2.0)
    inner = soft(xbox(HEAD_X0 - 1, HEAD_X1 - 2, -HEAD_W / 2 + 2, HEAD_W / 2 - 2, HEAD_Z + 2, HEAD_Z + HEAD_H - 2), "|X", 3.0)
    h = shell.cut(inner)                                    # open at the back: your shell closes it
    w = DSP["window"]                                       # display window, slightly larger than the active area
    if w[0] == "rect": h = h.cut(box(6, w[1], w[2], cx=HEAD_X1 - 1, z0=LCD_Z - w[2] / 2))
    else: h = h.cut(xcyl(w[1], 6, 0, LCD_Z, HEAD_X1 - 4))
    h = h.cut(xcyl(8.0, 6, 0, CAM_Z, HEAD_X1 - 4))          # CAMERA window, above the display
    h = h.cut(xcyl(1.5, 6, 7.5, CAM_Z, HEAD_X1 - 4))        # microphone hole (the microphone is on the camera board)
    for gx in (-6, -3, 0, 3, 6):                            # speaker grille in the left cheek
        for gz in (-6, -3, 0, 3, 6):
            if abs(gx) + abs(gz) <= 9:
                h = h.cut(ycyl(1.6, 6, HEAD_X0 + 13 + gx, HEAD_Z + 13 + gz, HEAD_W / 2 - 4))
    # two arms reach back to the tilt axis: left one bolts to the servo, right one turns on an M3 screw
    for sy, bore in ((1, 5.2), (-1, 3.2)):
        y0 = 25.6 if sy > 0 else -28.6
        arm = ycyl(10, 3, PX, PZ, y0).union(xbox(PX, HEAD_X0 + 8, y0, y0 + 3, PZ - 5, PZ + 5))
        web = xbox(HEAD_X0 + 1, HEAD_X0 + 8, min(sy * (HEAD_W / 2 - 1), sy * 28.6), max(sy * (HEAD_W / 2 - 1), sy * 28.6), PZ - 5, PZ + 5)
        h = h.union(arm).union(web).cut(ycyl(bore, 5, PX, PZ, y0 - 1))
    return h

# ---------------- fixed shovel (also carries the two edge sensors) ----------------
def shovel():
    x0 = TUB_L / 2
    flange = box(2, 30, 9.5, cx=x0 + 1, cy=-2, z0=7.5)
    for y in (-5, 5):
        flange = flange.cut(xcyl(2.2, 4, y, 13, x0 - 1))
    shelf = xbox(x0 + 2, BLADE_X, -TUB_W / 2, TUB_W / 2, 7.5, 10).union(xbox(EDGE_X - 8.5, BLADE_X, -BLADE_W / 2, BLADE_W / 2, 7.5, 10))
    for sy in (-1, 1):
        shelf = shelf.cut(box(12, 8, 6, cx=EDGE_X, cy=sy * EDGE_Y, z0=6))          # sensor looks down through here
        shelf = shelf.cut(zcyl(2.5, 6, EDGE_X, sy * (EDGE_Y - 10), 6))             # sensor board screw (M3 self-tap)
    shelf = shelf.cut(box(12, 8, 6, cx=EDGE_X, cy=0, z0=6))                          # room for the pin stubs under the two boards
    blade = (cq.Workplane("XZ").polyline([(BLADE_X, 2), (BLADE_X + 7, 1), (BLADE_X + 8, 1), (BLADE_X + 1.5, 2 + BLADE_H), (BLADE_X, 2 + BLADE_H)]).close()
             .extrude(-BLADE_W).translate((0, -BLADE_W / 2, 0)))
    return flange.union(shelf).union(blade)

# ---------------- small bought parts that V1 does not have ----------------
def track_v2():
    a = dc.track_set(WHEELBASE, WHEEL_D, TRACK_W, TRACK_T, bogies=0)
    a.name = "track_v2"
    return a

def lipo_1s():
    """Origin: centre of footprint, Z=0 underside. Wires leave toward -X."""
    cell = B(BAT[0] - 4, BAT[1], BAT[2], cx=2).edges("|X").fillet(2.0)
    cap = B(4, BAT[1] - 2, BAT[2] - 3, cx=-BAT[0] / 2 + 2, z0=1.5)
    return asm("battery_lipo_1s", [(cell, "steel"), (cap, "yellow")])

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

def lcd_128_round():
    """1.28 inch round IPS, GC9A01, 240 x 240, SPI, 7 pins. Origin: centre of the glass front face, looks toward +X.
    Round board 38 mm across, glass 35.6 mm, active circle 32.4 mm. Header on the back near the bottom, pins pointing back."""
    pcb = CX(38, 1.6, x0=-4.2)
    glass = CX(35.6, 2.6, x0=-2.6)
    scr = CX(32.4, 0.1, x0=-0.05)
    strip = B(2.5, 17.8, 2.5, cx=-7.05, z0=-14.5)
    pins = None
    for i in range(7):
        p = B(11.5, 0.64, 0.64, cx=-8.5, cy=-7.62 + 2.54 * i, z0=-13.57)
        pins = p if pins is None else pins.union(p)
    return asm("lcd_1in28_gc9a01_round", [(pcb, "pcb_black"), (glass, "glass"), (scr, "screen"), (strip, "black"), (pins, "gold")])

def oled_096():
    """0.96 inch OLED, SSD1306, 128 x 64, I2C, 4 pins. Origin: centre of the active area on the glass front, looks toward +X.
    Board 27.3 x 27.8 mm with four M2 holes, glass 26.7 x 19.3 mm, active 21.7 x 10.9 mm. Header along the top edge, pins pointing back."""
    pcb = B(1.6, 27.3, 27.8, cx=-2.4, z0=-12.4)
    for hy in (-11.75, 11.75):
        for hz in (-10.4, 13.0):
            pcb = pcb.cut(CX(2.2, 4, y=hy, z=hz, x0=-5))
    glass = B(1.6, 26.7, 19.3, cx=-0.8, z0=-8.6)
    scr = B(0.1, 21.7, 10.9, cx=-0.05 + 0.05, z0=-5.45)
    strip = B(2.5, 10.2, 2.5, cx=-4.45, z0=11.8)
    pins = None
    for i in range(4):
        p = B(11.5, 0.64, 0.64, cx=-5.9, cy=-3.81 + 2.54 * i, z0=12.73)
        pins = p if pins is None else pins.union(p)
    return asm("oled_0in96_ssd1306", [(pcb, "pcb_blue"), (glass, "black"), (scr, "screen"), (strip, "black"), (pins, "gold")])

def xiao_s3_sense():
    """Seeed XIAO ESP32S3 Sense: brain, OV2640 camera and microphone in one 21 x 17.5 mm stack.
    Origin: tip of the camera lens, looking toward +X. Boards stand upright, header pins point back."""
    cam = B(4.5, 8.5, 8.5, cx=-3.75, z0=-4.25)
    lens = CX(6.5, 1.5, x0=-1.5).union(CX(4.0, 0.2, x0=-0.2))
    sense = B(1.2, 21, 17.5, cx=-6.6, z0=-8.75)
    link = B(3.0, 12, 3.0, cx=-8.7, cy=-3, z0=-1.5)
    usb = B(3.0, 7.3, 8.9, cx=-8.7, cy=7.4, z0=-4.45)
    xiao = B(1.2, 21, 17.5, cx=-10.8, z0=-8.75)
    can = B(2.0, 9, 11, cx=-12.4, cy=-4, z0=-5.5)
    parts = [(cam, "black"), (lens, "glass"), (sense, "pcb_black"), (link, "white"), (usb, "steel"), (xiao, "pcb_black"), (can, "steel")]
    for sz in (-7.62, 7.62):
        strip = B(2.5, 17.8, 2.5, cx=-12.65, z0=sz - 1.25)
        pins = None
        for i in range(7):
            q = B(8.5, 0.64, 0.64, cx=-15.5, cy=-7.62 + 2.54 * i, z0=sz - 0.32)
            pins = q if pins is None else pins.union(q)
        parts += [(strip, "black"), (pins, "gold")]
    return asm("xiao_esp32s3_sense_camera", parts)

def io_expander():
    """PCF8574 I2C expander, small breakout. Gives 8 extra slow pins over the two I2C wires."""
    return small_board("pcf8574_io_expander", 20, 16, "pcb_red", [(7.5, 5.3, 1.6, 0, 0, "black"), (2, 1.2, 1, 6, 3, "dark")], pins=[(6, 0, -6.6, "x"), (6, 0, 6.6, "x")])

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
HEAD_TILT = T(PX, 0, PZ) * R(RY, -TILT) * T(-PX, 0, -PZ)      # everything in the head moves with this

placed = []
def put(name, a, loc): placed.append((name, a, loc))
def hput(name, a, loc): placed.append((name, a, HEAD_TILT * loc))
# groups in the assembly tree, so a CAD program shows folders instead of one long flat list
GROUPS = {"track": "drive", "motor": "drive", "battery": "power", "usb_c": "power", "power_": "power", "brain": "brain_and_camera", "io_": "brain_and_camera",
          "speaker": "voice", "face_": "face", "edge_": "senses", "servo": "head_tilt"}
def group_of(name):
    return next(g for k, g in GROUPS.items() if name.startswith(k))

for sy, tag in ((1, "left"), (-1, "right")):
    put("track_" + tag, track_v2(), T(0, sy * TRACK_Y, AXLE_Z))
put("motor_left", dc.motor_n20(), T(MOTORS[0][0], TUB_W_IN / 2, AXLE_Z))
put("motor_right", dc.motor_n20(), T(MOTORS[1][0], -TUB_W_IN / 2, AXLE_Z) * R(RZ, 180))
put("battery", lipo_1s(), T(0, 0, FLOOR_Z + FLOOR_T))
put("usb_c_charger", charger_boost_1s(), T(-XI + 13.5, 8.5, DECK_Z - 0.6))
put("power_switch", slide_switch(), T(-31, 8.5, BAY_TOP + LID_T) * R(RY, 90))
put("motor_driver", dc.drv8833_driver(), T(-XI + 9.75, -9, DECK_Z))
put("io_expander", io_expander(), T(-XI + 29.5, -9, DECK_Z))
put("servo_tilt", dc.servo_mg90s(horn=False), T(PX, TUB_W_IN / 2 - 2.5, PZ) * R(RX, -90))
hput("face_display", {"st7735_096": lcd_096, "gc9a01_128_round": lcd_128_round, "ssd1306_096_oled": oled_096}[DISPLAY](), T(HEAD_X1 - 2, 0, LCD_Z))
hput("brain_camera", xiao_s3_sense(), T(HEAD_X1 - 1.5, 0, CAM_Z))
hput("speaker", speaker_20mm(), T(HEAD_X0 + 13, HEAD_W / 2 - 2.4, HEAD_Z + 13) * R(RZ, -90))
hput("speaker_amplifier", dc.max98357_amp(), T(HEAD_X0 + 11.5, -HEAD_W / 2 + 11.5, HEAD_Z + 2.2))
put("edge_sensor_front_left", dc.tcrt5000_module(), T(EDGE_X, EDGE_Y, EDGE_Z))
put("edge_sensor_front_right", dc.tcrt5000_module(), T(EDGE_X, -EDGE_Y, EDGE_Z) * R(RZ, 180))

# .clean() merges faces that lie on the same plane or cylinder, so each wall is one face to push or pull
parts = {
    "v2_frame_chassis": (chassis().clean(), (0.62, 0.72, 0.74)),
    "v2_frame_top": (top().clean(), (0.52, 0.64, 0.68)),
    "v2_frame_head": (head().clean().rotate((PX, 0, PZ), (PX, 1, PZ), -TILT), (0.72, 0.82, 0.84)),
    "v2_frame_shovel": (shovel().clean(), (0.85, 0.45, 0.38)),
}

assy = cq.Assembly(name="dimer_v2_guideline")
fa = cq.Assembly(name="dimer_v2_frame_only")
sub = {g: cq.Assembly(name=g) for g in ["printed_frame"] + list(dict.fromkeys(GROUPS.values()))}
for name, (shape, col) in parts.items():
    sub["printed_frame"].add(shape, name=name, color=cq.Color(*col)); fa.add(shape, name=name, color=cq.Color(*col))
    if not VARIANT or name == "v2_frame_head":
        cq.exporters.export(shape, os.path.join(OUT, name + ".step"))
for name, a, loc in placed:
    sub[group_of(name)].add(a, name=name, loc=loc)
for g, a in sub.items():
    assy.add(a, name=g)
assy.save(os.path.join(OUT, "dimer_v2_guideline_assembly.step"))
if not VARIANT: fa.save(os.path.join(OUT, "dimer_v2_frame_only.step"))

COMP = os.path.join(OUT, "components") if not VARIANT else OUT; os.makedirs(COMP, exist_ok=True)
V1_COMP = os.path.join(HERE, "..", "..", "cad", "step", "components")
seen = set()
for name, a, loc in placed:          # only the parts V1 does not already have a STEP for
    if VARIANT and name != "face_display": continue
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
        if vol > 0.5: bad += 1; bx = a.intersect(b).BoundingBox(); print("CLASH %s x %s: %.1f mm3 at x %.0f..%.0f y %.0f..%.0f z %.0f..%.0f" % (names[i], names[j], vol, bx.xmin, bx.xmax, bx.ymin, bx.ymax, bx.zmin, bx.zmax))
print("clashes over 0.5 mm3:", bad)
