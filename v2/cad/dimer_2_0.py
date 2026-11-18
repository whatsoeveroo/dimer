"""Dimer 2.0: Pololu tracks, every bought part in detail, and Shell 2.0 around them (CadQuery).

    python v2/cad/dimer_2_0.py [mesh.json]
writes into v2/cad/step/2_0/
    dimer_2_0_full_assembly.step   Shell 2.0 + every bought part in detail + screws, in folders
    dimer_2_0_parts_only.step      the bought parts and screws, no shell (model your own shell over this)
    dimer_2_0_shell_only.step      the five printed Shell 2.0 pieces
    shell/<piece>.step             each printed piece on its own
    parts/<part>.step              each bought part on its own, in its own frame (run dimer_parts_2_0.py)
Axes: X forward, Y left, Z up, table at Z = 0, mm. Same as V2.

What changed from V2 (dimer_v2_frame.py):
- Pololu 22T tracks: axles 19.5 mm up (was 13.6), 48 mm apart (was 58), 14.6 mm wide (was 11).
  The GA12-N20 3 mm D-shaft pushes into the drive sprocket's D bore; the gearbox front plate sits in a 1 mm pocket
  in the wall so 6.2 mm of the 10 mm shaft is inside the sprocket.
- The idler sprockets turn on M3 x 20 screws through a spacer boss on the wall, nut inside.
- The power board deck goes up to 27 mm (was 20.2) to clear the higher motors; the bay is 52 mm tall (was 42).
- The tilt axis goes up to 45.5 mm so the head arms pass over the taller tracks.
- Battery is the 8 mm thick 803040 you bought (was a 10 mm placeholder).
- Shell 2.0 adds a back cover for the head and a rounded bay lid.
"""
import json, os, sys
import cadquery as cq

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "lib"))
sys.path.insert(0, HERE)
from cadtree import Node, Leaf, write_step, flatten, mesh as tree_mesh
import dimer_parts_2_0 as P

OUT = os.path.join(HERE, "step", "2_0")
os.makedirs(os.path.join(OUT, "shell"), exist_ok=True)

# ---------------- parameters ----------------
TUB_L, TUB_W_IN, WALL = 78.0, 34.0, 2.0
TUB_W = TUB_W_IN + 2 * WALL                    # 38
XI = TUB_L / 2 - WALL                          # 37
FLOOR_Z, FLOOR_T = 3.0, 1.5                    # floor top at 4.5; the Pololu track lifts the body 3 mm off the table
FLOOR_TOP = FLOOR_Z + FLOOR_T
AXLE_Z, WHEELBASE = 19.5, 48.0                 # Pololu 22T: 39 mm tall loop, sprockets 48 mm apart
TRACK_W, TRACK_GAP = 14.6, 1.0
TRACK_IN = TUB_W / 2 + TRACK_GAP               # 20: inner face of each track
TRACK_Y = TRACK_IN + TRACK_W / 2               # 27.3
TRACK_TOP = 2 * AXLE_Z                         # 39
GEARBOX_Y = TUB_W / 2 - 1.0                    # gearbox front face, 1 mm into the wall
MOTORS = ((-WHEELBASE / 2, 1), (WHEELBASE / 2, -1))   # left motor drives the rear sprocket, right motor the front one
XS = 5.0                                       # the bay is behind x = XS, the low step in front of it
STEP_TOP = 26.0                                # step plate clears the front motor (top at 24.5)
DECK_Z = 27.0                                  # power board underside; its battery socket pins clear the rear motor
BAY_TOP = 53.0                                 # room for the jumper plugs and the tilt servo
LID_T = 2.0
BOARD_X0, BOARD_Y0 = -36.0, 16.5               # robot position of the board's KiCad origin
PX, PZ = XS - 11.5, TRACK_TOP + 7.5            # head tilt axis: the servo case and the head arms stay 1.5 mm above the tracks
HEAD_W, HEAD_L = 38.0, 38.0                    # fits between the tracks with 1 mm each side
HEAD_Z = STEP_TOP + LID_T + 2.0                # 30
HEAD_X0 = XS + WALL + 5.5                      # 2.5 mm further forward than V2 so the back cover clears the lid at full tilt
HEAD_X1 = HEAD_X0 + HEAD_L
LCD_Z = HEAD_Z + 2.8 + 12.0
CAM_Z = LCD_Z + 12.0 + 5.0
SPK_Z = HEAD_Z + 14.5                          # speaker centre, in the left cheek
AMP_X, AMP_Y, AMP_Z = HEAD_X0 + 13.5, -HEAD_W / 2 + 12.5, HEAD_Z + 3.4   # amplifier board centre and underside
HEAD_H = CAM_Z + 9.5 + 2.0 - HEAD_Z
EDGE_X, EDGE_Y, EDGE_Z = HEAD_X1 + 7.4, TRACK_Y, 10.0
BLADE_X, BLADE_H = EDGE_X + 7.8, 15.0
BLADE_W = 2 * (TRACK_Y + TRACK_W / 2) + 1.0    # 70: a little wider than the tracks
ARM_L_Y = TUB_W_IN / 2 - 2.5 + 14.6 + 0.1           # left head arm, just outside the servo horn
IDLER_HUB = TRACK_IN + 4.45                     # the idler's hub face (from the Pololu STEP)
TILT = float(os.environ.get("DIMER_TILT", "0"))
if TILT:                                       # tilt check only: write the files somewhere else
    import tempfile; OUT = tempfile.mkdtemp(); os.makedirs(os.path.join(OUT, "shell"), exist_ok=True)

BOARD = json.load(open(os.path.join(HERE, "..", "pcb", "dimer_v2_power_parts.json")))
PB = {p["ref"]: p for p in BOARD["parts"]}
def board_to_robot(X, Y): return X + BOARD_X0, BOARD_Y0 - Y
def _centre(ref): p = PB[ref]; return (p["x0"] + p["x1"]) / 2, (p["y0"] + p["y1"]) / 2
USB_C_XY, SWITCH_XY, LEDS_XY = _centre("J1"), PB["SW1"]["lever"], [_centre("D1"), _centre("D2")]

box, xbox, zcyl = P.B, P.XB, P.CZ
def ycyl(d, length, x, z, y0): return P.CY(d, length, x=x, z=z, y0=y0)
def xcyl(d, length, y, z, x0): return P.CX(d, length, y=y, z=z, x0=x0)
soft = P.fil


# ================= Shell 2.0 =================
def chassis():
    outer = soft(box(TUB_L, TUB_W, BAY_TOP - FLOOR_Z, z0=FLOOR_Z), "|Z", 4.0)
    outer = soft(outer, "<Z", 1.2)
    outer = outer.cut(xbox(XS, TUB_L, -TUB_W, TUB_W, STEP_TOP, BAY_TOP + 1))
    tub = outer.cut(soft(box(TUB_L - 2 * WALL, TUB_W_IN, BAY_TOP, z0=FLOOR_TOP), "|Z", 2.0))
    for mx, sy in MOTORS:
        wall_in, wall_out = sy * TUB_W_IN / 2, sy * TUB_W / 2
        # gearbox pocket (12 x 10, 1 mm deep, from the inside) and the shaft hole through the rest of the wall
        tub = tub.cut(xbox(mx - 6.2, mx + 6.2, wall_in - sy * 0.5, sy * GEARBOX_Y, AXLE_Z - 5.2, AXLE_Z + 5.2))
        tub = tub.cut(ycyl(5.0, WALL + 2, mx, AXLE_Z, min(wall_in, wall_out) - 1))
        # saddle under the motor can, kept clear of the battery (|x| < 20.5)
        sx = 1 if mx > 0 else -1
        ys = sorted((sy * GEARBOX_Y, sy * 4.0))          # stops short of the middle: the battery lead runs under the motors
        tub = tub.union(xbox(sx * 20.8, sx * 30.0, ys[0], ys[1], FLOOR_TOP - 0.1, AXLE_Z - 5.0))
        # idler on the other side: spacer boss outside, M3 hole through the boss and wall, nut trap inside
        iy_in, iy_out = -sy * TUB_W_IN / 2, -sy * TUB_W / 2
        boss = ycyl(7.0, IDLER_HUB - 0.3 - TUB_W / 2 + 0.5, mx, AXLE_Z, TUB_W / 2 - 0.5)
        if sy > 0: boss = boss.mirror("XZ")
        tub = tub.union(boss)
        nut = xbox(mx - 4.0, mx + 4.0, iy_in, iy_in + sy * 3.0, AXLE_Z - 4.5, AXLE_Z + 4.5)
        tub = tub.union(nut)
        ya, yb = -sy * 13.0, -sy * (IDLER_HUB + 1.0)
        tub = tub.cut(ycyl(3.2, abs(yb - ya), mx, AXLE_Z, min(ya, yb)))
        tub = tub.cut(cq.Workplane("XZ").polygon(6, 6.4).extrude(2.6).translate((mx, max(iy_in + sy * 0.3, iy_in + sy * 2.9), AXLE_Z)))
    # tilt servo drops into a notch in the left wall; pivot boss for the other head arm on the right wall
    tub = tub.cut(box(23.4, WALL + 2, BAY_TOP - (PZ - 6.4) + 1, cx=PX - 5.9, cy=TUB_W / 2 - WALL / 2, z0=PZ - 6.4))
    for ex in (-13.75, 13.75):                                                                           # M2 pilots for the servo ears
        tub = tub.cut(ycyl(1.6, WALL + 2, PX - 5.9 + ex, PZ, TUB_W_IN / 2 - 1))
    boss = ycyl(9, 6.6, PX, PZ, -TUB_W / 2 - 6.3).cut(ycyl(2.5, 12, PX, PZ, -TUB_W / 2 - 8))
    tub = tub.union(boss)
    # front wall: lid tab screws (M2), shovel screws (M2)
    for sy in (-1, 1):
        tub = tub.cut(xcyl(2.2, WALL + 2, sy * 12, STEP_TOP - 4, XI - 1))
    for y in (-5, 5):
        tub = tub.cut(xcyl(1.6, WALL + 2, y, 12, XI - 1))
    # power board: ledges on both side walls, a screw pillar at the rear right (M2 x 6)
    for sy in (-1, 1):
        tub = tub.union(xbox(-XI + 0.5, XS - 1.5, sy * (TUB_W_IN / 2 - 1.5), sy * TUB_W_IN / 2, DECK_Z - 1.2, DECK_Z))
    hx, hy = board_to_robot(*BOARD["holes"][0])
    tub = tub.union(xbox(hx - 2.2, hx + 2.6, -TUB_W_IN / 2 - 0.5, hy + 2.2, FLOOR_TOP - 0.1, DECK_Z).cut(zcyl(1.6, 9, hx, hy, DECK_Z - 8)))
    # rear wall: USB-C plug opening, power switch slot in a thin pocket, lid tab screw (M2)
    ux, uy = board_to_robot(*USB_C_XY); sx_, sy_ = board_to_robot(*SWITCH_XY)
    tub = tub.cut(soft(box(WALL + 2, 12.5, 7.0, cx=-XI - WALL / 2, cy=uy, z0=DECK_Z + 1.6 + 1.63 - 3.5), "|X", 2.0))
    tub = tub.cut(xbox(-XI - WALL - 1, -XI - 1.0, sy_ - 5.5, sy_ + 5.5, DECK_Z - 0.5, DECK_Z + 6))
    tub = tub.cut(box(WALL + 2, 6.5, 3.4, cx=-XI - WALL / 2, cy=sy_, z0=DECK_Z + 1.6 - 0.2))
    tub = tub.cut(xcyl(2.2, WALL + 2, 4, BAY_TOP - 4, -XI - WALL - 1))
    # battery strap slots in the floor, and a window under the battery to push it out
    for x in (-12, 12):
        tub = tub.cut(box(2, 24, FLOOR_T + 2, cx=x, z0=FLOOR_Z - 1))
    tub = tub.cut(soft(box(14, 14, FLOOR_T + 2, cx=0, z0=FLOOR_Z - 1), "|Z", 3))
    return tub


def bay_lid():
    """Shell 2.0 bay lid: rounded top over the bay, riser and step plate in one piece."""
    lid = soft(box(TUB_L / 2 + XS, TUB_W, LID_T + 1.0, cx=(XS - TUB_L / 2) / 2, z0=BAY_TOP), "|Z", 4.0)
    lid = soft(lid, ">Z", 1.5)
    riser = xbox(XS, XS + WALL, -TUB_W / 2, TUB_W / 2, STEP_TOP, BAY_TOP + LID_T)
    step = soft(xbox(XS, TUB_L / 2, -TUB_W / 2, TUB_W / 2, STEP_TOP, STEP_TOP + LID_T), "|Z", 4.0)
    t = lid.union(riser).union(step)
    t = t.cut(soft(box(WALL + 2, 16, 9, cx=XS + WALL / 2, z0=STEP_TOP + LID_T + 3), "|X", 2))     # cable slot to the head
    for led in LEDS_XY:                                                                            # light pipes over the charge lights
        lx, ly = board_to_robot(*led); t = t.cut(zcyl(2.5, LID_T + 4, lx, ly, BAY_TOP - 1))
    for y0, y1 in ((-15.0, -1.0), (11.0, 15.5)):                                                  # lips that hold the board's front edge down
        t = t.union(xbox(XS - 2.5, XS, y0, y1, DECK_Z + 1.6 + 0.05, DECK_Z + 1.6 + 1.6))
    tab = xbox(-XI, -XI + 2.5, 2, 6, BAY_TOP - 8, BAY_TOP).cut(xcyl(1.6, 5, 4, BAY_TOP - 4, -XI - 1))
    t = t.union(tab)
    for sy in (-1, 1):
        tab = xbox(XI - 2.0, XI, sy * 12 - 2, sy * 12 + 2, STEP_TOP - 8, STEP_TOP).cut(xcyl(1.6, 5, sy * 12, STEP_TOP - 4, XI - 3))
        t = t.union(tab)
    for gx in range(5):                                                                             # vent slots over the boost converter
        t = t.cut(soft(box(1.6, 12, LID_T + 4, cx=-26 + 3.2 * gx, cy=-6, z0=BAY_TOP - 1), "|Z", 0.7))
    return t


def head():
    hx = (HEAD_X0 + HEAD_X1) / 2
    shell = soft(box(HEAD_L, HEAD_W, HEAD_H, cx=hx, z0=HEAD_Z), "|X", 6.0)
    shell = soft(shell, ">X", 2.5)
    inner = soft(xbox(HEAD_X0 - 1, HEAD_X1 - 2, -HEAD_W / 2 + 2, HEAD_W / 2 - 2, HEAD_Z + 2, HEAD_Z + HEAD_H - 2), "|X", 3.0)
    h = shell.cut(inner)
    h = h.cut(soft(box(6, 23, 12, cx=HEAD_X1 - 1, cy=-0.5, z0=LCD_Z - 6), "|X", 1.0))      # display window
    h = h.cut(xcyl(8.0, 6, 0, CAM_Z, HEAD_X1 - 4))                                         # camera window
    h = h.cut(xcyl(1.5, 6, 7.75, CAM_Z, HEAD_X1 - 4))                                      # microphone hole
    for gx in (-6, -3, 0, 3, 6):                                                           # speaker grille in the left cheek
        for gz in (-6, -3, 0, 3, 6):
            if abs(gx) + abs(gz) <= 9:
                h = h.cut(ycyl(1.6, 6, HEAD_X0 + 13 + gx, SPK_Z + gz, HEAD_W / 2 - 4))
    # speaker cup and amplifier standoffs
    h = h.union(ycyl(22.4, 1.6, HEAD_X0 + 13, SPK_Z, HEAD_W / 2 - 2 - 1.6).cut(ycyl(20.5, 3, HEAD_X0 + 13, SPK_Z, HEAD_W / 2 - 4)))
    for sx in (-6.4, 6.4):
        h = h.union(zcyl(4.0, AMP_Z - HEAD_Z - 1.9, AMP_X + sx, AMP_Y + 6.4, HEAD_Z + 1.9).cut(zcyl(1.6, 3, AMP_X + sx, AMP_Y + 6.4, HEAD_Z + 1.5)))
    # display and camera rails
    for sy in (-1, 1):
        h = h.union(xbox(HEAD_X1 - 7.8, HEAD_X1 - 6.6, sy * 14.2, sy * (HEAD_W / 2 - 1.5), LCD_Z - 12, LCD_Z + 6))
    # two arms reach back to the tilt axis: the left one takes the servo horn, the right one turns on an M3 screw
    # the left arm sits on the outside of the servo's single-arm horn (two M2 screws through the horn holes),
    # the right arm turns on an M3 screw in the boss on the right wall
    for sy, y0, bore in ((1, ARM_L_Y, 4.2), (-1, -28.6, 3.2)):
        arm = ycyl(11, 3, PX, PZ, y0).union(xbox(PX, HEAD_X0 + 8, y0, y0 + 3, PZ - 5, PZ + 5))
        yo = y0 + 3 if sy > 0 else y0
        web = xbox(HEAD_X0 + 1, HEAD_X0 + 8, sy * (HEAD_W / 2 - 1), yo, PZ - 5, PZ + 5)
        h = h.union(arm).union(web).cut(ycyl(bore, 5, PX, PZ, y0 - 1))
        if sy > 0:
            for hx in (6.5, 10.5):
                h = h.cut(ycyl(1.6, 5, PX + hx, PZ, y0 - 1))
    # back cover screw bosses
    for sy in (-1, 1):
        for zz in (HEAD_Z + 6, HEAD_Z + HEAD_H - 6):
            h = h.union(xcyl(5, 4, sy * (HEAD_W / 2 - 4.5), zz, HEAD_X0).cut(xcyl(1.6, 6, sy * (HEAD_W / 2 - 4.5), zz, HEAD_X0 - 1)))
    return h


def head_back():
    """Shell 2.0: back cover of the head, with a slot for the cable bundle and a rounded rim."""
    c = soft(xbox(HEAD_X0 - 2.0, HEAD_X0, -HEAD_W / 2, HEAD_W / 2, HEAD_Z, HEAD_Z + HEAD_H), "|X", 6.0)
    c = c.cut(soft(xbox(HEAD_X0 - 3, HEAD_X0 + 1, -6, 6, HEAD_Z - 1, HEAD_Z + 6), "|X", 2.0))
    c = c.union(soft(xbox(HEAD_X0, HEAD_X0 + 1.5, -HEAD_W / 2 + 2.2, HEAD_W / 2 - 2.2, HEAD_Z + 2.2, HEAD_Z + HEAD_H - 2.2), "|X", 3.8)
                .cut(soft(xbox(HEAD_X0 - 1, HEAD_X0 + 2, -HEAD_W / 2 + 3.4, HEAD_W / 2 - 3.4, HEAD_Z + 3.4, HEAD_Z + HEAD_H - 3.4), "|X", 2.6)))
    c = c.cut(soft(xbox(HEAD_X0 - 3, HEAD_X0 + 3, -6, 6, HEAD_Z - 1, HEAD_Z + 6), "|X", 2.0))
    for sy in (-1, 1):
        for zz in (HEAD_Z + 6, HEAD_Z + HEAD_H - 6):
            c = c.cut(xcyl(2.2, 6, sy * (HEAD_W / 2 - 4.5), zz, HEAD_X0 - 3)).cut(xcyl(4.2, 1.0, sy * (HEAD_W / 2 - 4.5), zz, HEAD_X0 - 2.5))
            c = c.cut(xbox(HEAD_X0 - 0.1, HEAD_X0 + 2, sy * (HEAD_W / 2 - 4.5) - 2.8, sy * (HEAD_W / 2 - 4.5) + 2.8, zz - 2.8, zz + 2.8))
    for k in range(4):                                     # vent slots for the XIAO
        c = c.cut(soft(xbox(HEAD_X0 - 3, HEAD_X0 + 1, -7 + 4.7 * k - 0.8, -7 + 4.7 * k + 0.8, CAM_Z - 6, CAM_Z + 6), "|X", 0.7))
    return c


def shovel():
    x0 = TUB_L / 2
    flange = soft(box(2, 30, 9.5, cx=x0 + 1, cy=-2, z0=7.0), "|X", 1.5)
    for y in (-5, 5):
        flange = flange.cut(xcyl(2.2, 4, y, 12, x0 - 1))
    for y in (-12, 12):
        flange = flange.cut(xcyl(4.6, 4, y, STEP_TOP - 4, x0 - 1))
    shelf = xbox(x0 + 2, BLADE_X, -TUB_W / 2, TUB_W / 2, 7.5, 10).union(xbox(EDGE_X - 8.5, BLADE_X, -BLADE_W / 2, BLADE_W / 2, 7.5, 10))
    shelf = soft(shelf, "|Z", 1.0)
    for sy in (-1, 1):
        shelf = shelf.cut(box(12, 8, 6, cx=EDGE_X, cy=sy * EDGE_Y, z0=6))
        shelf = shelf.cut(zcyl(2.5, 6, EDGE_X, sy * (EDGE_Y - 10), 6))
    shelf = shelf.cut(box(12, 8, 6, cx=EDGE_X, cy=0, z0=6))
    blade = (cq.Workplane("XZ").polyline([(BLADE_X, 2), (BLADE_X + 7, 1), (BLADE_X + 8, 1), (BLADE_X + 1.5, 2 + BLADE_H), (BLADE_X, 2 + BLADE_H)]).close()
             .extrude(-BLADE_W).translate((0, -BLADE_W / 2, 0)))
    blade = soft(blade, "|X", 1.0)
    return flange.union(shelf).union(blade)


# ================= bought parts, placed =================
L = cq.Location
def T(x, y, z): return L(cq.Vector(x, y, z))
def R(axis, deg): return L(cq.Vector(0, 0, 0), cq.Vector(*axis), deg)
RX, RY, RZ = (1, 0, 0), (0, 1, 0), (0, 0, 1)
HEAD_TILT = T(PX, 0, PZ) * R(RY, -TILT) * T(-PX, 0, -PZ)

GROUPS = [("drive", "Tracks and motors"), ("power", "Battery and power board"), ("head_tilt", "Tilt servo"), ("face", "Display"),
          ("brain_and_camera", "XIAO ESP32S3 Sense"), ("voice", "Speaker and amplifier"), ("senses", "Edge sensors"), ("screws", "Screws and nuts")]
groups = {g: Node(g) for g, _ in GROUPS}
LABELS = {}
def put(group, name, node, loc, label):
    node.name = name
    groups[group].add(node, loc)
    LABELS[name] = label

put("drive", "track_left", P.pololu_track_22t(), T(MOTORS[0][0], TRACK_Y, AXLE_Z) * R(RX, 90), "Pololu 22T track, left (driven at the rear)")
put("drive", "track_right", P.pololu_track_22t(), T(MOTORS[1][0], -TRACK_Y, AXLE_Z) * R(RZ, 180) * R(RX, 90), "Pololu 22T track, right (driven at the front)")
put("drive", "motor_left", P.motor_ga12_n20(), T(MOTORS[0][0], GEARBOX_Y, AXLE_Z), "GA12-N20 motor, left (rear)")
put("drive", "motor_right", P.motor_ga12_n20(), T(MOTORS[1][0], -GEARBOX_Y, AXLE_Z) * R(RZ, 180), "GA12-N20 motor, right (front)")
put("power", "battery", P.lipo_803040(), T(0, 0, FLOOR_TOP), "LiPo 803040, 1000 mAh")
put("power", "power_board", P.power_board(), T(BOARD_X0, BOARD_Y0, DECK_Z), "Power board (KiCad 3D)")
put("head_tilt", "servo_tilt", P.servo_sg90(horn="single", lead=26.0), T(PX, TUB_W_IN / 2 - 2.5, PZ) * R(RX, -90), "SG90 tilt servo")
put("face", "face_display", P.display_st7735_096(), HEAD_TILT * T(HEAD_X1 - 2, 0, LCD_Z), "0.96 in IPS display")
put("brain_and_camera", "brain_camera", P.xiao_esp32s3_sense(), HEAD_TILT * T(HEAD_X1 - 2.2, 0, CAM_Z), "XIAO ESP32S3 Sense")
put("voice", "speaker", P.speaker_20mm(), HEAD_TILT * T(HEAD_X0 + 13, HEAD_W / 2 - 2.4, SPK_Z) * R(RZ, -90), "20 mm speaker")
put("voice", "speaker_amplifier", P.amp_max98357a(), HEAD_TILT * T(AMP_X, AMP_Y, AMP_Z), "MAX98357A amplifier")
put("senses", "edge_sensor_left", P.tcrt5000_module(), T(EDGE_X, EDGE_Y, EDGE_Z), "TCRT5000 edge sensor, left")
put("senses", "edge_sensor_right", P.tcrt5000_module(), T(EDGE_X, -EDGE_Y, EDGE_Z) * R(RZ, 180), "TCRT5000 edge sensor, right")

# ---------------- screws ----------------
def screw(d, length, hd, hh, name):
    """pan head with a cross; origin under the head, shank along +Z"""
    head_ = zcyl(hd, hh, z0=-hh).cut(xbox(-hd * 0.33, hd * 0.33, -0.25, 0.25, -hh - 1, -hh * 0.4)).cut(xbox(-0.25, 0.25, -hd * 0.33, hd * 0.33, -hh - 1, -hh * 0.4))
    n = Node(name)
    n.children += [Leaf("head", soft(head_, "<Z", hh * 0.35), P.COL["steel"]), Leaf("shank", zcyl(d, length), P.COL["steel"])]
    return n
M2, M3 = (2.0, 3.8, 1.4), (3.0, 5.5, 1.8)
DIR = {"+x": R(RY, 90), "-x": R(RY, -90), "+y": R(RX, -90), "-y": R(RX, 90), "-z": R(RX, 180), "+z": L()}
def sc(size, length, at, v, name):
    d, hd, hh = size
    put("screws", name, screw(d, length, hd, hh, "M%d x %d" % (d, length)), T(*at) * DIR[v], "M%d x %d screw" % (d, length))
hx_, hy_ = board_to_robot(*BOARD["holes"][0])
sc(M2, 6, (-TUB_L / 2, 4, BAY_TOP - 4), "+x", "screw_lid_rear")
for i, y in enumerate((-12, 12)): sc(M2, 4, (TUB_L / 2, y, STEP_TOP - 4), "-x", "screw_lid_front_%d" % i)
for i, y in enumerate((-5, 5)): sc(M2, 6, (TUB_L / 2 + 2, y, 12), "-x", "screw_shovel_%d" % i)
sc(M2, 6, (hx_, hy_, DECK_Z + 1.6), "-z", "screw_board")
sc(M3, 20, (MOTORS[1][0], TRACK_Y + TRACK_W / 2 - 1.8, AXLE_Z), "-y", "screw_idler_left")
sc(M3, 20, (MOTORS[0][0], -(TRACK_Y + TRACK_W / 2 - 1.8), AXLE_Z), "+y", "screw_idler_right")
sc(M3, 10, (PX, -28.6, PZ), "+y", "screw_head_pivot")
for i, sy in enumerate((-1, 1)): sc(M3, 6, (EDGE_X, sy * (EDGE_Y - 10), EDGE_Z + 1.6), "-z", "screw_edge_sensor_%d" % i)
for i, sy in enumerate((-1, 1)):
    for j, zz in enumerate((HEAD_Z + 6, HEAD_Z + HEAD_H - 6)):
        put("screws", "screw_head_back_%d%d" % (i, j), screw(2.0, 6, 3.8, 1.4, "M2 x 6"), HEAD_TILT * T(HEAD_X0 - 1.5, sy * (HEAD_W / 2 - 4.5), zz) * DIR["+x"], "M2 x 6 screw")
for i, ex in enumerate((-13.75, 13.75)):
    sc(M2, 6, (PX - 5.9 + ex, TUB_W_IN / 2 - 2.5, PZ), "+y", "screw_servo_ear_%d" % i)
for i, hx in enumerate((6.5, 10.5)):
    put("screws", "screw_horn_%d" % i, screw(2.0, 5, 3.8, 1.4, "M2 x 5"), HEAD_TILT * T(PX + hx, ARM_L_Y + 3, PZ) * DIR["-y"], "M2 x 5 screw")
for i, (mx, sy) in enumerate(MOTORS):
    nut = Node("M3 nut"); nut.children.append(Leaf("nut", cq.Workplane("XZ").polygon(6, 6.2).extrude(2.4).cut(P.CY(3.0, 4, y0=-3)), P.COL["steel"]))
    put("screws", "nut_idler_%d" % i, nut, T(mx, -sy * (TUB_W_IN / 2 - 0.2), AXLE_Z) * (R(RZ, 180) if sy > 0 else L()), "M3 nut")

# ---------------- Shell 2.0 pieces ----------------
SHELL = {
    "shell_2_0_chassis": (chassis, (0.62, 0.72, 0.74), "Chassis tub"),
    "shell_2_0_bay_lid": (bay_lid, (0.52, 0.64, 0.68), "Bay lid, riser and step"),
    "shell_2_0_head": (lambda: head().rotate((PX, 0, PZ), (PX, 1, PZ), -TILT), (0.74, 0.84, 0.86), "Head"),
    "shell_2_0_head_back": (lambda: head_back().rotate((PX, 0, PZ), (PX, 1, PZ), -TILT), (0.66, 0.76, 0.78), "Head back cover"),
    "shell_2_0_shovel": (shovel, (0.85, 0.45, 0.38), "Shovel and sensor shelf"),
}
shell = Node("shell_2_0")
shell_solids = {}
for name, (fn, col, label) in SHELL.items():
    s = fn().clean().val()
    shell_solids[name] = s
    shell.children.append(Leaf(name, s, col))
    LABELS[name] = label

parts_root = Node("bought_parts", [groups[g] for g, _ in GROUPS])
full = Node("dimer_2_0", [shell, parts_root])

if __name__ == "__main__":
    write_step(full, os.path.join(OUT, "dimer_2_0_full_assembly.step"))
    write_step(Node("dimer_2_0_parts_only", [groups[g] for g, _ in GROUPS]), os.path.join(OUT, "dimer_2_0_parts_only.step"))
    write_step(shell, os.path.join(OUT, "dimer_2_0_shell_only.step"))
    for name, s in shell_solids.items():
        write_step(Node(name, [Leaf(name, s, SHELL[name][1])]), os.path.join(OUT, "shell", name + ".step"))
    for f in sorted(os.listdir(OUT)):
        if f.endswith(".step"): print("%-36s %6.0f kB" % (f, os.path.getsize(os.path.join(OUT, f)) / 1024))
    for name, s in shell_solids.items():
        b = s.BoundingBox(); print("%-24s %s %3.0f x %3.0f x %3.0f mm" % (name, "valid" if s.isValid() else "INVALID", b.xlen, b.ylen, b.zlen))

    # ---------------- clash check: each placed part against the shell and against each other ----------------
    if not os.environ.get("DIMER_NO_CHECK"):
        bodies = {n: s for n, s in shell_solids.items()}
        for g in groups.values():
            for ch in g.children:
                bodies[ch.name] = cq.Compound.makeCompound([s for _, s, _, _ in flatten(ch)])
        allowed = [("track_left", "motor_left"), ("track_right", "motor_right"),          # D-shaft inside the drive sprocket
                   ("screw_idler_left", "track_left"), ("screw_idler_right", "track_right"),   # the idler turns on its screw
                   ("screw_board", "power_board"),
                   ("servo_tilt", "screw_horn_0"), ("servo_tilt", "screw_horn_1")]    # M2 screws bite into the horn holes
        names = list(bodies); bad = 0
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                a, b = names[i], names[j]
                if (a, b) in allowed or (b, a) in allowed: continue
                if (a.startswith(("screw", "nut")) and b.startswith("shell")) or (b.startswith(("screw", "nut")) and a.startswith("shell")): continue
                A, Bb = bodies[a], bodies[b]
                ba, bb = A.BoundingBox(), Bb.BoundingBox()
                if ba.xmin > bb.xmax or bb.xmin > ba.xmax or ba.ymin > bb.ymax or bb.ymin > ba.ymax or ba.zmin > bb.zmax or bb.zmin > ba.zmax: continue
                try: inter = A.intersect(Bb); vol = inter.Volume()
                except Exception: vol = 0
                if vol > 0.2:
                    bad += 1; bx = inter.BoundingBox()
                    print("CLASH %s x %s: %.1f mm3 at x %.1f..%.1f y %.1f..%.1f z %.1f..%.1f" % (a, b, vol, bx.xmin, bx.xmax, bx.ymin, bx.ymax, bx.zmin, bx.zmax))
        print("clashes over 0.2 mm3:", bad)

    if len(sys.argv) > 1:
        json.dump({"labels": LABELS}, open(sys.argv[1] + ".labels.json", "w"))
