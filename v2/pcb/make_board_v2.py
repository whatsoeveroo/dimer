"""Dimer V2 power board generator (KiCad 7 pcbnew scripting + freerouting).

Run:  FREEROUTING=/path/to/freerouting-1.9.0.jar python3 v2/pcb/make_board_v2.py
      (needs KiCad 7, java and xvfb-run; --place-only stops before routing)
Writes v2/pcb/dimer_v2_power.kicad_pcb, a DRC report, Gerbers and the JLCPCB
assembly files (BOM + CPL), so JLCPCB solders every part on the board.

The board lies flat in the electronics bay at z = 20.2 mm, on two ledges of
the side walls, above the battery and the left motor.  It carries everything
that is not in the head:
  USB-C charging (TP4056, 580 mA) with red / green lights you can see through
  the rear wall, the power switch (it switches a P-MOSFET, so the small switch
  never carries motor current), the 5 V boost (MT3608) for servo, brain,
  amplifier, the 3.3 V regulator (AP2112K) for the expander and edge sensors,
  the DRV8833 motor driver and the PCA9534 I2C expander.
The XIAO in the head reaches it over 8 jumper wires (5V, GND, SDA, SCL,
PWM L, PWM R, SERVO, GND).

Board coordinates: X = robot x + 36, Y = 16.5 - robot y (robot left is +y).
Rear edge (X = 0) faces the rear wall: USB-C, switch, lights.
Parts above Y < 18 sit under the tilt servo, so only flat parts go there.
Through-hole pins stay out of X < 14, Y < 27.7, which is over the left motor.
"""
import sys, os, math, zipfile, glob, shutil, subprocess, re, csv
sys.path.insert(0, "/usr/lib/python3/dist-packages")
import pcbnew
from pcbnew import FromMM, ToMM, VECTOR2I

HERE = os.path.dirname(os.path.abspath(__file__))
LIB = "/usr/share/kicad/footprints/"
W, H = 39.5, 33.0
NOTCH = (3.0, 28.0)              # rear-right corner cut away: the battery wire comes up here
VIA_D, VIA_DRILL = 0.6, 0.3
LCSC = {}                        # ref -> (LCSC part number or "", comment)
HDR = "Connector_PinHeader_2.54mm.pretty"

board = pcbnew.BOARD()
nets = {}
def net(name):
    if name is None: return None
    if name not in nets:
        n = pcbnew.NETINFO_ITEM(board, name); board.Add(n); nets[name] = n
    return nets[name]

def P(x, y): return VECTOR2I(FromMM(x), FromMM(y))

def text(s, x, y, size=0.8, angle=0, layer=pcbnew.F_SilkS, thick=0.13):
    t = pcbnew.PCB_TEXT(board); t.SetText(s); t.SetPosition(P(x, y)); t.SetLayer(layer)
    t.SetTextSize(VECTOR2I(FromMM(size), FromMM(size))); t.SetTextThickness(FromMM(thick))
    t.SetTextAngleDegrees(angle)
    if layer == pcbnew.B_SilkS: t.SetMirrored(True)
    board.Add(t); return t

def load(lib, name):
    return pcbnew.FootprintLoad(LIB + lib, name)

def finish(fp, ref, value, padnets, lcsc):
    fp.SetReference(ref); fp.SetValue(value)
    fp.Reference().SetVisible(False); fp.Value().SetVisible(False)
    board.Add(fp)
    for p in fp.Pads():
        n = padnets.get(p.GetNumber())
        if n: p.SetNet(net(n))
    if lcsc is not None: LCSC[ref] = (lcsc, value)
    return fp

def smd(lib, name, ref, value, x, y, rot, padnets, lcsc):
    """Part centred at x, y, turned rot degrees."""
    fp = load(lib, name); fp.SetPosition(P(x, y)); fp.SetOrientationDegrees(rot)
    return finish(fp, ref, value, padnets, lcsc)

def facing(lib, name, ref, value, x, y, pad, padnets, lcsc):
    """Part centred at x, y, turned so `pad` lies on its +X side: its front faces the rear edge (-X)."""
    for rot in (0, 90, 180, 270):
        fp = load(lib, name); fp.SetPosition(P(x, y)); fp.SetOrientationDegrees(rot)
        q = [p for p in fp.Pads() if p.GetNumber() == pad][0].GetPosition()
        if ToMM(q.x) - x > 1.0 and abs(ToMM(q.y) - y) < abs(ToMM(q.x) - x): break
    return finish(fp, ref, value, padnets, lcsc)

R0603 = ("Resistor_SMD.pretty", "R_0603_1608Metric")
C0603 = ("Capacitor_SMD.pretty", "C_0603_1608Metric")
C0805 = ("Capacitor_SMD.pretty", "C_0805_2012Metric")
def res(ref, val, x, y, rot, a, b, lcsc): return smd(*R0603, ref, val, x, y, rot, {"1": a, "2": b}, lcsc)
def cap(ref, val, x, y, rot, a, b, lcsc="C14663", big=False): return smd(*(C0805 if big else C0603), ref, val, x, y, rot, {"1": a, "2": b}, lcsc)
def c10u(ref, x, y, rot, a, b): return cap(ref, "10uF 25V", x, y, rot, a, b, lcsc="C15850", big=True)

# ---------------- outline, battery-wire notch, mounting hole ----------------
r = 2.0
def edge_line(a, b):
    s = pcbnew.PCB_SHAPE(board); s.SetShape(pcbnew.SHAPE_T_SEGMENT); s.SetStart(P(*a)); s.SetEnd(P(*b))
    s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(FromMM(0.1)); board.Add(s)
def edge_arc(start, mid, end):
    s = pcbnew.PCB_SHAPE(board); s.SetShape(pcbnew.SHAPE_T_ARC); s.SetArcGeometry(P(*start), P(*mid), P(*end))
    s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(FromMM(0.1)); board.Add(s)
k = r * (1 - math.sqrt(0.5)); nx, ny = NOTCH
edge_line((r, 0), (W - r, 0)); edge_arc((W - r, 0), (W - k, k), (W, r))
edge_line((W, r), (W, H - r)); edge_arc((W, H - r), (W - k, H - k), (W - r, H))
edge_line((W - r, H), (nx, H)); edge_line((nx, H), (nx, ny)); edge_line((nx, ny), (0, ny))
edge_line((0, ny), (0, r)); edge_arc((0, r), (k, k), (r, 0))
HOLE = (5.0, 30.8)                                           # M2 x 6 self-tapping screw into the boss on the right wall
smd("MountingHole.pretty", "MountingHole_2.2mm_M2", "H1", "M2", *HOLE, 0, {}, None)

# ---------------- USB-C charging input (rear edge) ----------------
facing("Connector_USB.pretty", "USB_C_Receptacle_HRO_TYPE-C-31-M-12", "J1", "USB-C 16P TYPE-C-31-M-12", 3.15, 7.5, "A1",
       {"A1": "GND", "B12": "GND", "A12": "GND", "B1": "GND", "A4": "VBUS", "B9": "VBUS", "A9": "VBUS", "B4": "VBUS",
        "A5": "CC1", "B5": "CC2", "S1": "GND"}, "C165948")
res("R1", "5.1k", 9.3, 4.6, 90, "CC1", "GND", "C23186")      # CC pull-downs: any USB-C charger gives 5 V
res("R2", "5.1k", 9.3, 10.4, 90, "CC2", "GND", "C23186")

# ---------------- 1S charger TP4056 (580 mA) and its two lights ----------------
smd("Package_SO.pretty", "SOIC-8-1EP_3.9x4.9mm_P1.27mm_EP2.29x3mm", "U1", "TP4056 ESOP-8", 13.3, 7.0, 90,
    {"1": "GND", "2": "PROG", "3": "GND", "4": "VBUS", "5": "VBAT", "6": "STDBY", "7": "CHRG", "8": "VBUS", "9": "GND"}, "C16581")
c10u("C1", 17.2, 3.4, 90, "VBUS", "GND")
c10u("C2", 13.3, 12.4, 0, "VBAT", "GND")
res("R3", "3k", 17.2, 7.6, 90, "PROG", "GND", "C4211")      # 1200 V / 3 k = 0.4 A: cooler chip, gentle on a 1000 mAh cell
LED = ("LED_SMD.pretty", "LED_0603_1608Metric")
smd(*LED, "D1", "LED red 0603", 2.9, 0.95, 0, {"1": "CHRG", "2": "LED_R"}, "C2286")
smd(*LED, "D2", "LED green 0603", 9.0, 0.95, 0, {"1": "STDBY", "2": "LED_G"}, "C72043")
res("R4", "1k", 5.95, 0.95, 0, "LED_R", "VBUS", "C21190")
res("R5", "1k", 12.05, 0.95, 0, "LED_G", "VBUS", "C21190")

# ---------------- power switch: slide switch drives a P-MOSFET ----------------
facing("Button_Switch_SMD.pretty", "SW_SPDT_PCM12", "SW1", "Slide switch SPDT PCM12SMTR", 2.25, 17.5, "2",
       {"1": "GND", "2": "GATE"}, "")
smd("Package_TO_SOT_SMD.pretty", "SOT-23", "Q1", "AO3401A P-MOSFET", 6.7, 14.9, 0, {"1": "GATE", "2": "VBAT", "3": "VSYS"}, "C15127")
res("R6", "100k", 9.7, 14.9, 90, "GATE", "VBAT", "C25803")

# ---------------- battery plug (JST PH 2.0) ----------------
smd("Connector_JST.pretty", "JST_PH_B2B-PH-K_1x02_P2.00mm_Vertical", "J2", "JST PH 2P vertical B2B-PH-K-S", 12.8, 30.8, 180,
    {"1": "VBAT", "2": "GND"}, "")

# ---------------- 5 V boost MT3608 (servo, brain, amplifier) ----------------
smd("Package_TO_SOT_SMD.pretty", "SOT-23-6", "U2", "MT3608", 20.6, 3.0, 0,
    {"1": "BST_SW", "2": "GND", "3": "BST_FB", "4": "VSYS", "5": "VSYS"}, "C84817")
smd("Inductor_SMD.pretty", "L_Changjiang_FNR5040S", "L1", "4.7-10uH 5040 Isat 3A+ (FNR5040S)", 20.75, 9.2, 0, {"1": "VSYS", "2": "BST_SW"}, "")
smd("Diode_SMD.pretty", "D_SMA", "D3", "SS34", 26.6, 2.4, 0, {"1": "5V", "2": "BST_SW"}, "C8678")
c10u("C3", 20.4, 13.4, 0, "VSYS", "GND")
c10u("C4", 16.8, 13.4, 0, "VSYS", "GND")
def c22u(ref, x, y, rot, a, b): return cap(ref, "22uF 10V", x, y, rot, a, b, lcsc="C45783", big=True)
c22u("C5", 25.4, 5.8, 0, "5V", "GND")   # servo and Wi-Fi bursts
c22u("C6", 25.4, 8.2, 0, "5V", "GND")
c22u("C7", 25.4, 10.6, 0, "5V", "GND")
res("R7", "75k", 23.8, 13.0, 0, "5V", "BST_FB", "C23242")    # 0.6 V x (1 + 75 / 10) = 5.1 V
res("R8", "10k", 23.8, 14.6, 0, "BST_FB", "GND", "C25804")

# ---------------- 3.3 V regulator AP2112K (expander, edge sensors) ----------------
smd("Package_TO_SOT_SMD.pretty", "SOT-23-5", "U3", "AP2112K-3.3", 36.3, 2.6, 0, {"1": "5V", "2": "GND", "3": "5V", "5": "3V3"}, "C51118")
# head 5 V through a Schottky: a USB cable in the XIAO cannot push its 5 V back into this board
smd("Diode_SMD.pretty", "D_SOD-123", "D4", "B5819W", 32.0, 5.6, 0, {"1": "HEAD_5V", "2": "5V"}, "C8598")
# motor driver stays asleep until the firmware wakes it: expander pins start as inputs, these hold the lines low
res("R11", "10k", 36.2, 5.4, 0, "DRV_SLEEP", "GND", "C25804")
res("R12", "10k", 36.2, 7.0, 0, "DIR_L", "GND", "C25804")
res("R13", "10k", 36.2, 8.6, 0, "DIR_R", "GND", "C25804")
c10u("C8", 29.4, 8.8, 0, "5V", "GND")
c10u("C9", 33.0, 8.8, 0, "3V3", "GND")
c10u("C10", 26.3, 17.3, 0, "3V3", "GND")

# ---------------- motor driver DRV8833 (on the switched battery) ----------------
smd("Package_SO.pretty", "HTSSOP-16-1EP_4.4x5mm_P0.65mm_EP3.4x5mm_Mask2.46x2.31mm", "U4", "DRV8833PWP", 31.5, 12.6, 0,
    {"1": "DRV_SLEEP", "2": "MOTL_A", "3": "GND", "4": "MOTL_B", "5": "MOTR_B", "6": "GND", "7": "MOTR_A", "9": "PWM_R", "10": "DIR_R",
     "11": "DRV_VCP", "12": "VSYS", "13": "GND", "14": "DRV_VINT", "15": "DIR_L", "16": "PWM_L", "17": "GND"}, "C50506")
c10u("C11", 38.2, 11.4, 90, "VSYS", "GND")
cap("C12", "10nF", 38.3, 18.1, 90, "DRV_VCP", "VSYS", lcsc="C57112")
cap("C13", "2.2uF 10V", 38.3, 14.9, 90, "DRV_VINT", "GND", lcsc="C23630")

# ---------------- I2C expander PCA9534 (motor direction and sleep, edge sensors) ----------------
# Same pins and address (0x20) as the PCF8574T, but its pins start as inputs at power-up, so the motors cannot start on their own.
smd("Package_SO.pretty", "SOIC-16W_7.5x10.3mm_P1.27mm", "U5", "PCA9534DWR SO-16 wide", 11.1, 22.0, 0,
    {"1": "GND", "2": "GND", "3": "GND", "4": "DIR_L", "5": "DIR_R", "6": "EDGE_L", "7": "EDGE_R", "8": "GND", "9": "DRV_SLEEP",
     "14": "SCL", "15": "SDA", "16": "3V3"}, "")
cap("C14", "100nF", 16.8, 15.6, 0, "3V3", "GND")
res("R9", "4.7k", 20.0, 17.3, 0, "SDA", "3V3", "C23162")
res("R10", "4.7k", 23.0, 17.3, 0, "SCL", "3V3", "C23162")

# ---------------- plugs: 2.54 mm pin headers for jumper wires ----------------
HLCSC = {2: "C124375", 3: "C49257", 4: "C124378"}
X0, DX = 19.0, 2.54
def header(ref, k, y, names, signals, title=None, title_dy=-1.9):
    n = len(names); x = X0 + DX * k
    fp = load(HDR, "PinHeader_1x%02d_P2.54mm_Vertical" % n)
    for rot in (0, 90, 180, 270):            # pin 1 at (x, y), the row running along +X
        fp = load(HDR, "PinHeader_1x%02d_P2.54mm_Vertical" % n); fp.SetOrientationDegrees(rot); fp.SetPosition(P(0, 0))
        p1 = [p for p in fp.Pads() if p.GetNumber() == "1"][0].GetPosition()
        pn = [p for p in fp.Pads() if p.GetNumber() == str(n)][0].GetPosition()
        if n == 1 or (ToMM(pn.x) - ToMM(p1.x) > 1 and abs(ToMM(pn.y) - ToMM(p1.y)) < 0.1): break
    fp.SetPosition(VECTOR2I(FromMM(x) - p1.x, FromMM(y) - p1.y))
    finish(fp, ref, "Pin header 1x%d 2.54mm" % n, {str(i + 1): s for i, s in enumerate(signals)}, HLCSC[n])
    for i, nm in enumerate(names):
        if nm: text(nm, x + DX * i, y + 1.75, size=0.6, thick=0.1)
    if title: text(title, x + DX * (n - 1) / 2, y + title_dy, size=0.7, thick=0.12)
    return fp
header("J3", 0, 20.5, ["V", "G", "S"], ["3V3", "GND", "EDGE_L"], "EDGE L")
header("J4", 4, 20.5, ["V", "G", "S"], ["3V3", "GND", "EDGE_R"], "EDGE R")
header("J5", 0, 25.0, ["G", "5V", "S"], ["GND", "5V", "SERVO"], None)
header("J6", 4, 25.0, ["", ""], ["MOTL_A", "MOTL_B"], None)
header("J7", 6, 25.0, ["", ""], ["MOTR_A", "MOTR_B"], None)
text("TILT", X0 + DX, 23.15, size=0.6, thick=0.1); text("MOT L", X0 + DX * 4.5, 23.15, size=0.6, thick=0.1); text("MOT R", X0 + DX * 6.5, 23.15, size=0.6, thick=0.1)
header("J8", 0, 28.6, ["", "", "", ""], ["HEAD_5V", "GND", "SDA", "SCL"], None)
header("J9", 0, 31.14, ["", "", "", ""], ["SERVO", "GND", "3V3", "GND"], None)
header("J11", 5, 31.14, ["", ""], ["PWM_L", "PWM_R"], None)
for name, x, y in [("HEAD: 5V G DA CL", X0 + DX * 1.5, 26.95)]:
    text(name, x, y, size=0.55, thick=0.1)
text("SV G 3V G", X0 + DX * 1.5, 32.55, size=0.5, thick=0.09); text("PL PR", X0 + DX * 5.5, 32.55, size=0.5, thick=0.09)
text("+", 12.8, 28.6, size=0.8); text("-", 10.8, 28.6, size=0.8); text("BAT", 15.7, 30.8, size=0.6, thick=0.1, angle=90)
text("ON", 4.6, 21.6, size=0.6, thick=0.1)
text("DIMER V2 POWER r1", 23.5, 0.9 + 11.5, size=0.6, thick=0.1, layer=pcbnew.B_SilkS)
text("1S LiPo 3.0-4.2 V - USB-C charge - assembled by JLCPCB", 20, 16, size=0.8, layer=pcbnew.B_SilkS, thick=0.13)


# ---------------- hand-placed copper: thin escapes from fine-pitch power pins, vias under the heat pads ----------------
def pad_at(ref, num):
    return [p for p in board.FindFootprintByReference(ref).Pads() if p.GetNumber() == num][0].GetPosition()
def track(a, b, w, netname, layer=pcbnew.F_Cu):
    t = pcbnew.PCB_TRACK(board); t.SetStart(a); t.SetEnd(b); t.SetWidth(FromMM(w)); t.SetLayer(layer); t.SetNet(net(netname)); board.Add(t)
def via(x, y, netname):
    v = pcbnew.PCB_VIA(board); v.SetPosition(P(x, y)); v.SetDrill(FromMM(VIA_DRILL)); v.SetWidth(FromMM(VIA_D))
    v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); v.SetNet(net(netname)); board.Add(v)
pd = pad_at("U4", "12")                      # motor supply pin: the wide VSYS track joins the end of this stub
track(pd, P(ToMM(pd.x) + 1.3, ToMM(pd.y)), 0.35, "VSYS")
for ref, dy in (("U4", (-1.2, 0, 1.2)), ("U1", (-0.75, 0.75))):   # heat pads down to the bottom ground pour
    c = board.FindFootprintByReference(ref).GetPosition()
    for d in dy:
        via(ToMM(c.x), ToMM(c.y) + d, "GND") if ref == "U4" else via(ToMM(c.x) + d, ToMM(c.y), "GND")

# USB-C: join its two VBUS pad pairs underneath (too tight between the fine pads for the router)
a, b = pad_at("J1", "B9"), pad_at("J1", "A9")
vx = 8.3
track(a, P(vx, ToMM(a.y)), 0.4, "VBUS"); via(vx, ToMM(a.y), "VBUS")
track(P(vx, ToMM(a.y)), P(vx, ToMM(b.y)), 0.4, "VBUS", pcbnew.B_Cu); via(vx, ToMM(b.y), "VBUS")
track(P(vx, ToMM(b.y)), b, 0.4, "VBUS")
# U3 VIN (1) to EN (3): go round the GND pin on the outside
a, b = pad_at("U3", "1"), pad_at("U3", "3"); ux = ToMM(a.x) - 1.25
track(a, P(ux, ToMM(a.y)), 0.4, "5V"); track(P(ux, ToMM(a.y)), P(ux, ToMM(b.y)), 0.4, "5V"); track(P(ux, ToMM(b.y)), b, 0.4, "5V")
# keep tracks and vias 0.35 mm from the board edge (the router does not know the edge rule)
def keepout(pts):
    z = pcbnew.ZONE(board); z.SetIsRuleArea(True); z.SetDoNotAllowTracks(True); z.SetDoNotAllowVias(True)
    z.SetDoNotAllowCopperPour(False); z.SetDoNotAllowPads(False); z.SetDoNotAllowFootprints(False)
    ls = pcbnew.LSET(); ls.AddLayer(pcbnew.F_Cu); ls.AddLayer(pcbnew.B_Cu); z.SetLayerSet(ls)
    o = z.Outline(); o.NewOutline()
    for x, y in pts: o.Append(FromMM(x), FromMM(y))
    board.Add(z)
e = 0.35
for x0, y0, x1, y1 in ((0, 0, W, e), (0, H - e, W, H), (0, 0, e, NOTCH[1]), (W - e, 0, W, H),
                       (NOTCH[0] - e, NOTCH[1], NOTCH[0] + e, H), (0, NOTCH[1] - e, NOTCH[0] + e, NOTCH[1] + e)):
    keepout(((x0, y0), (x1, y0), (x1, y1), (x0, y1)))
c = 1.75                                     # rounded corners: cut off along a chord 0.4 mm inside the arc
keepout(((0, 0), (c, 0), (0, c))); keepout(((W, 0), (W, c), (W - c, 0))); keepout(((W, H), (W - c, H), (W, H - c)))

# ---------------- design rules ----------------
ds = board.GetDesignSettings()
ds.m_MinResolvedSpokes = 1; ds.m_MinClearance = FromMM(0.15); ds.m_TrackMinWidth = FromMM(0.2); ds.m_ViasMinSize = FromMM(0.5)
ds.m_MinThroughDrill = FromMM(0.3); ds.m_CopperEdgeClearance = FromMM(0.3); ds.m_HoleClearance = FromMM(0.25)
ds.m_HoleToHoleMin = FromMM(0.45); ds.m_ViasMinAnnularWidth = FromMM(0.13)
ds.m_NetSettings.m_DefaultNetClass.SetClearance(FromMM(0.15))   # JLCPCB minimum is 0.1 mm
ds.m_NetSettings.m_DefaultNetClass.SetTrackWidth(FromMM(0.25))
ds.m_NetSettings.m_DefaultNetClass.SetViaDiameter(FromMM(VIA_D)); ds.m_NetSettings.m_DefaultNetClass.SetViaDrill(FromMM(VIA_DRILL))
out = os.path.join(HERE, "dimer_v2_power.kicad_pcb")
pcbnew.SaveBoard(out, board)
if "--place-only" in sys.argv:
    print("placed", len(board.GetFootprints()), "footprints, not routed"); sys.exit(0)

# ---------------- autoroute with freerouting ----------------
WORK = os.environ.get("DIMER_WORK", "/tmp/dimer_v2_route"); os.makedirs(WORK, exist_ok=True)
dsn, ses = os.path.join(WORK, "dimer_v2.dsn"), os.path.join(WORK, "dimer_v2.ses")
board = pcbnew.LoadBoard(out)
pcbnew.ExportSpecctraDSN(board, dsn)
WIDTHS = {"HEAD_5V": 0.5, "VBUS": 0.4, "VBAT": 0.6, "VSYS": 0.5, "BST_SW": 0.6, "5V": 0.5, "GND": 0.4, "3V3": 0.3,
          "MOTL_A": 0.4, "MOTL_B": 0.4, "MOTR_A": 0.4, "MOTR_B": 0.4}
txt = open(dsn).read()
m = re.search(r'\(class kicad_default "" (.*?)\n\s*\(circuit', txt, flags=re.S)
allnets = m.group(1).split()
strip = lambda n: n.strip('"')
via = re.search(r'\(use_via "?([^")]+)', txt).group(1)
i0 = txt.index('(class kicad_default')
depth = 0
for j in range(i0, len(txt)):
    if txt[j] == '(': depth += 1
    elif txt[j] == ')':
        depth -= 1
        if depth == 0: break
rest = [n for n in allnets if strip(n) not in WIDTHS]
classes = '(class kicad_default "" %s\n      (circuit (use_via "%s"))\n      (rule (width 250) (clearance 150.1)))' % (" ".join(rest), via)
for w in sorted(set(WIDTHS.values())):
    ns = [n for n in allnets if WIDTHS.get(strip(n)) == w]
    if ns: classes += '\n    (class w%d %s\n      (circuit (use_via "%s"))\n      (rule (width %d) (clearance 180.1)))' % (w * 1000, " ".join(ns), via, w * 1000)
txt = txt[:i0] + classes + txt[j + 1:]
open(dsn, "w").write(txt)
if "--dsn-only" in sys.argv:            # write the router input and stop
    print("wrote", dsn); sys.exit(0)
if "--use-ses" not in sys.argv:         # --use-ses: reuse a session file routed in an earlier run
    if os.path.exists(ses): os.remove(ses)
    jar = os.environ.get("FREEROUTING", "freerouting-1.9.0.jar")
    subprocess.run(["xvfb-run", "-a", "java", "-jar", jar, "-de", dsn, "-do", ses, "-mp", "100"], check=False, timeout=1500,
                   stdout=open(os.path.join(WORK, "fr.log"), "w"), stderr=subprocess.STDOUT)
assert os.path.exists(ses), "freerouting produced no session file"
# read the routed session back in (tracks and vias per net)
stxt = open(ses).read()
SCALE = 1.0 / (1000.0 * int(re.search(r"\(resolution um (\d+)\)", stxt).group(1)))
body = stxt[stxt.index("(network_out"):]
ntracks = nvias = 0
for blk in re.split(r"\(net ", body)[1:]:
    name = re.match(r'"([^"]+)"|(\S+)', blk); name = name.group(1) or name.group(2)
    ni = board.FindNet(name); assert ni is not None, name
    for layer, width, pts in re.findall(r"\(path (\S+) (\d+)((?:\s+-?\d+\s+-?\d+)+)", blk):
        c = [int(v) * SCALE for v in pts.split()]
        xy = list(zip(c[0::2], c[1::2]))
        for (x1, y1), (x2, y2) in zip(xy, xy[1:]):
            t = pcbnew.PCB_TRACK(board); t.SetStart(P(x1, -y1)); t.SetEnd(P(x2, -y2)); t.SetWidth(FromMM(int(width) * SCALE))
            t.SetLayer(pcbnew.F_Cu if layer == "F.Cu" else pcbnew.B_Cu); t.SetNet(ni); board.Add(t); ntracks += 1
    for x, y in re.findall(r'\(via \S+ (-?\d+) (-?\d+)', blk):
        if any(tv.GetClass() == "PCB_VIA" and tv.GetPosition() == P(int(x) * SCALE, -int(y) * SCALE) for tv in board.GetTracks()): continue   # already placed by hand
        v = pcbnew.PCB_VIA(board); v.SetPosition(P(int(x) * SCALE, -int(y) * SCALE)); v.SetDrill(FromMM(VIA_DRILL)); v.SetWidth(FromMM(VIA_D))
        v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); v.SetNet(ni); board.Add(v); nvias += 1
seen = set()                            # drop a via the router put exactly on top of a hand-placed one
for tv in list(board.GetTracks()):
    if tv.GetClass() == "PCB_VIA":
        k = (round(ToMM(tv.GetPosition().x), 2), round(ToMM(tv.GetPosition().y), 2))
        if k in seen: board.Remove(tv); nvias -= 1
        seen.add(k)
print("routed: %d track segments, %d vias" % (ntracks, nvias))

# ---------------- ground stitching vias (tie the top and bottom ground pours together) ----------------
def _seg_d(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay; L2 = dx * dx + dy * dy
    u = 0 if L2 == 0 else max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / L2))
    return math.hypot(px - ax - u * dx, py - ay - u * dy)
_tr = [(ToMM(t.GetStart().x), ToMM(t.GetStart().y), ToMM(t.GetEnd().x), ToMM(t.GetEnd().y), ToMM(t.GetWidth()) / 2) for t in board.GetTracks()]
_pads = []
for fp in board.GetFootprints():
    for p in fp.Pads():
        bb = p.GetBoundingBox(); _pads.append((ToMM(bb.GetLeft()), ToMM(bb.GetTop()), ToMM(bb.GetRight()), ToMM(bb.GetBottom())))
_crt = []
for fp in board.GetFootprints():                # keep stitching vias out from under chips and connectors
    if fp.GetReference()[0] in "UJLDQS":
        c = fp.GetCourtyard(pcbnew.F_CrtYd).BBox(); _crt.append((ToMM(c.GetLeft()), ToMM(c.GetTop()), ToMM(c.GetRight()), ToMM(c.GetBottom())))
nst = 0
gy = 1.5
while gy < H - 1.2:
    gx = 1.5
    while gx < W - 1.2:
        ok = all(_seg_d(gx, gy, a, b, c, d) > w + VIA_D / 2 + 0.3 for a, b, c, d, w in _tr)
        ok = ok and all(not (l - 0.9 < gx < r + 0.9 and tp - 0.9 < gy < bt + 0.9) for l, tp, r, bt in _pads)
        ok = ok and math.hypot(gx - HOLE[0], gy - HOLE[1]) > 3.0 and not (gx < NOTCH[0] + 1.2 and gy > NOTCH[1] - 1.2)
        ok = ok and all(not (l - 0.3 < gx < r_ + 0.3 and tp - 0.3 < gy < bt + 0.3) for l, tp, r_, bt in _crt)
        if ok:
            v = pcbnew.PCB_VIA(board); v.SetPosition(P(gx, gy)); v.SetDrill(FromMM(VIA_DRILL)); v.SetWidth(FromMM(VIA_D))
            v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); v.SetNet(board.FindNet("GND")); board.Add(v); nst += 1
        gx += 2.5
    gy += 2.5
print("ground stitching vias:", nst)

# ---------------- ground pours ----------------
F, B = pcbnew.F_Cu, pcbnew.B_Cu
for layer in (F, B):
    z = pcbnew.ZONE(board); z.SetLayer(layer); z.SetNet(board.FindNet("GND")); z.SetZoneName("GND_" + ("F" if layer == F else "B"))
    o = z.Outline(); o.NewOutline()
    for x, y in ((0, 0), (W, 0), (W, H), (NOTCH[0], H), NOTCH, (0, NOTCH[1])): o.Append(FromMM(x), FromMM(y))
    z.SetLocalClearance(FromMM(0.3)); z.SetMinThickness(FromMM(0.25)); z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
    z.SetThermalReliefGap(FromMM(0.3)); z.SetThermalReliefSpokeWidth(FromMM(0.4))
    z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    board.Add(z)
pcbnew.SaveBoard(out, board)
board = pcbnew.LoadBoard(out)          # fill on a reloaded board (filling the in-memory one crashes KiCad 7)
pcbnew.ZONE_FILLER(board).Fill(board.Zones())
pcbnew.SaveBoard(out, board)
# a stitching via that landed in a pour island ties nothing together: find those with the DRC and take them out
tmp = os.path.join(WORK, "drc_tmp.txt"); pcbnew.WriteDRCReport(board, tmp, pcbnew.EDA_UNITS_MILLIMETRES, True)
bad = set()
for blk in re.split(r"\n(?=\[)", open(tmp).read()):
    if blk.startswith("[via_dangling]") or blk.startswith("[unconnected_items]"):
        for x, y in re.findall(r"@\((-?[\d.]+) mm, (-?[\d.]+) mm\): Via \[GND\]", blk): bad.add((round(float(x), 2), round(float(y), 2)))
drop = [v for v in board.GetTracks() if v.GetClass() == "PCB_VIA" and v.GetNetname() == "GND"
        and (round(ToMM(v.GetPosition().x), 2), round(ToMM(v.GetPosition().y), 2)) in bad]
for v in drop: board.Remove(v)
print("removed island stitching vias:", len(drop))
pcbnew.SaveBoard(out, board)
board = pcbnew.LoadBoard(out); pcbnew.ZONE_FILLER(board).Fill(board.Zones()); pcbnew.SaveBoard(out, board)
board = pcbnew.LoadBoard(out)
pcbnew.WriteDRCReport(board, os.path.join(HERE, "drc_report.txt"), pcbnew.EDA_UNITS_MILLIMETRES, True)

# ---------------- JLCPCB Gerbers + drill ----------------
gdir = os.path.join(HERE, "gerbers"); shutil.rmtree(gdir, ignore_errors=True); os.makedirs(gdir)
pc = pcbnew.PLOT_CONTROLLER(board); po = pc.GetPlotOptions()
po.SetOutputDirectory(gdir); po.SetPlotFrameRef(False); po.SetUseGerberProtelExtensions(True)
po.SetSubtractMaskFromSilk(True); po.SetPlotReference(True); po.SetPlotValue(True); po.SetUseAuxOrigin(False)
po.SetCreateGerberJobFile(False); po.SetUseGerberX2format(False); po.SetIncludeGerberNetlistInfo(False)
for name, lid in [("F_Cu", pcbnew.F_Cu), ("B_Cu", pcbnew.B_Cu), ("F_Paste", pcbnew.F_Paste), ("B_Paste", pcbnew.B_Paste),
                  ("F_Silkscreen", pcbnew.F_SilkS), ("B_Silkscreen", pcbnew.B_SilkS), ("F_Mask", pcbnew.F_Mask), ("B_Mask", pcbnew.B_Mask),
                  ("Edge_Cuts", pcbnew.Edge_Cuts)]:
    pc.SetLayer(lid); pc.OpenPlotfile(name, pcbnew.PLOT_FORMAT_GERBER, name); pc.PlotLayer()
pc.ClosePlot()
dw = pcbnew.EXCELLON_WRITER(board); dw.SetOptions(False, False, VECTOR2I(0, 0), False); dw.SetFormat(True, pcbnew.EXCELLON_WRITER.DECIMAL_FORMAT, 3, 3)
dw.SetRouteModeForOvalHoles(False)
dw.CreateDrillandMapFilesSet(gdir, True, False)
zp = os.path.join(HERE, "dimer_v2_power_gerbers_JLCPCB.zip")
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as zf:
    for f in sorted(glob.glob(os.path.join(gdir, "*"))): zf.write(f, os.path.basename(f))

# ---------------- JLCPCB assembly files: BOM + CPL ----------------
# JLCPCB's part library is rotated against KiCad's for some packages; these are the usual corrections.
# the SOT-23 rule also matches SOT-23-6 and SOT-223 (both 180 at JLCPCB); JLCPCB shows a placement preview to confirm.
ROT_FIX = [(r"^HTSSOP-", 270), (r"^TQFN-", 270), (r"^QFN-", 270), (r"^SOT-23", 180), (r"^SOIC-", 270), (r"^CP_Elec_", 180)]
groups, cpl = {}, []
for fp in board.GetFootprints():
    ref = fp.GetReference()
    if ref not in LCSC: continue
    part, comment = LCSC[ref]; name = str(fp.GetFPID().GetLibItemName())
    groups.setdefault((comment, name, part), []).append(ref)
    smdpads = [p for p in fp.Pads() if p.GetAttribute() == pcbnew.PAD_ATTRIB_SMD]
    if smdpads: c = fp.GetPosition(); cx, cy = ToMM(c.x), ToMM(c.y)
    else:                                   # through-hole parts: centre of the pins
        ps = [p.GetPosition() for p in fp.Pads()]; cx = sum(ToMM(p.x) for p in ps) / len(ps); cy = sum(ToMM(p.y) for p in ps) / len(ps)
    rot = fp.GetOrientationDegrees()
    for pat, d in ROT_FIX:
        if re.match(pat, name): rot += d
    cpl.append((ref, "%.3fmm" % cx, "%.3fmm" % -cy, "Top", "%d" % (round(rot) % 360)))
key = lambda r: (re.sub(r"\d+.*", "", r), int(re.search(r"\d+", r).group()), r)
with open(os.path.join(HERE, "dimer_v2_power_BOM_JLCPCB.csv"), "w", newline="") as f:
    w = csv.writer(f); w.writerow(["Comment", "Designator", "Footprint", "LCSC Part #"])
    for (comment, name, part), refs in sorted(groups.items(), key=lambda kv: key(sorted(kv[1], key=key)[0])):
        w.writerow([comment, ",".join(sorted(refs, key=key)), name, part])
with open(os.path.join(HERE, "dimer_v2_power_CPL_JLCPCB.csv"), "w", newline="") as f:
    w = csv.writer(f); w.writerow(["Designator", "Mid X", "Mid Y", "Layer", "Rotation"])
    for row in sorted(cpl, key=lambda r: key(r[0])): w.writerow(row)
print("tracks", len(board.GetTracks()), "parts placed by JLCPCB", len(cpl), "BOM lines", len(groups), "gerber files", len(os.listdir(gdir)))
