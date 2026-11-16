"""Dimer main board v0.2 generator (KiCad 7 pcbnew scripting + freerouting).

Run:  python3 pcb/make_board.py        (needs KiCad 7, java, xvfb-run and
      freerouting-1.9.0.jar; set FREEROUTING=/path/to/jar)
Writes pcb/dimer_main.kicad_pcb, a DRC report, Gerbers and the JLCPCB
assembly files (BOM + CPL), so JLCPCB solders every part on the board.

v0.2 is the "no soldering" board: the motor driver, speaker amplifier,
5 V converter and microphone are chips on the board, and every connector is
fitted by JLCPCB.  The ESP32-S3 dev board plugs into sockets, everything
else plugs in or goes under a screw terminal.
"""
import sys, os, math, zipfile, glob, shutil, subprocess, re, csv
sys.path.insert(0, "/usr/lib/python3/dist-packages")
import pcbnew
from pcbnew import FromMM, ToMM, VECTOR2I

HERE = os.path.dirname(os.path.abspath(__file__))
LIB = "/usr/share/kicad/footprints/"
W, H = 100.0, 70.0
VIA_D, VIA_DRILL = 0.7, 0.3
LCSC = {}                      # ref -> (LCSC part number, comment)
HDR = "Connector_PinHeader_2.54mm.pretty"
SOCK = "Connector_PinSocket_2.54mm.pretty"

board = pcbnew.BOARD()
nets = {}
def net(name):
    if name is None: return None
    if name not in nets:
        n = pcbnew.NETINFO_ITEM(board, name); board.Add(n); nets[name] = n
    return nets[name]

def P(x, y): return VECTOR2I(FromMM(x), FromMM(y))

def text(s, x, y, size=1.0, angle=0, layer=pcbnew.F_SilkS, thick=0.15):
    t = pcbnew.PCB_TEXT(board); t.SetText(s); t.SetPosition(P(x, y)); t.SetLayer(layer)
    t.SetTextSize(VECTOR2I(FromMM(size), FromMM(size))); t.SetTextThickness(FromMM(thick))
    t.SetTextAngleDegrees(angle)
    if layer == pcbnew.B_SilkS: t.SetMirrored(True)
    board.Add(t); return t

def place(lib, name, ref, value, p1, pN=None, padnets=None):
    """Place a footprint so pad 1 is at p1 and the last pad at pN (tries the 4 rotations)."""
    for ang in (0, 90, 180, 270):
        fp = pcbnew.FootprintLoad(LIB + lib, name)
        fp.SetOrientationDegrees(ang); fp.SetPosition(P(0, 0))
        pads = sorted(fp.Pads(), key=lambda p: int(p.GetNumber()) if p.GetNumber().isdigit() else 0)
        pads = [p for p in pads if p.GetNumber()] or pads
        a = pads[0].GetPosition()
        fp.SetPosition(VECTOR2I(FromMM(p1[0]) - a.x, FromMM(p1[1]) - a.y))
        b = pads[-1].GetPosition()
        if pN is None or (abs(ToMM(b.x) - pN[0]) < 1.5 and abs(ToMM(b.y) - pN[1]) < 1.5):
            break
    else:
        raise RuntimeError("cannot orient " + ref)
    fp.SetReference(ref); fp.SetValue(value)
    fp.Reference().SetVisible(False); fp.Value().SetVisible(False)
    board.Add(fp)
    for p in fp.Pads():
        n = (padnets or {}).get(p.GetNumber())
        if n: p.SetNet(net(n))
    return fp

def header(ref, value, x, y, names, signals, horizontal=True, label_side=1, title=None, socket=False):
    """1xN header.  names = silk label per pin, signals = net per pin."""
    n = len(names)
    pN = (x + 2.54 * (n - 1), y) if horizontal else (x, y + 2.54 * (n - 1))
    fp = place(SOCK if socket else HDR, ("PinSocket" if socket else "PinHeader") + "_1x%02d_P2.54mm_Vertical" % n, ref, value, (x, y), pN if n > 1 else None,
               {str(i + 1): s for i, s in enumerate(signals)})
    for i, nm in enumerate(names):
        if not nm: continue
        if horizontal:
            text(nm, x + 2.54 * i, y + label_side * (1.9 + 0.48 * len(nm)), angle=90)
        else:
            text(nm, x + label_side * (1.9 + 0.45 * len(nm)), y + 2.54 * i)
    if title:
        if horizontal: text(title, x + 1.27 * (n - 1), y - label_side * 2.55)
    return fp

# ---------------- outline + mounting holes ----------------
r = 3.0
def edge_line(a, b):
    s = pcbnew.PCB_SHAPE(board); s.SetShape(pcbnew.SHAPE_T_SEGMENT); s.SetStart(P(*a)); s.SetEnd(P(*b))
    s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(FromMM(0.1)); board.Add(s)
def edge_arc(c, start, mid, end):
    s = pcbnew.PCB_SHAPE(board); s.SetShape(pcbnew.SHAPE_T_ARC); s.SetArcGeometry(P(*start), P(*mid), P(*end))
    s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(FromMM(0.1)); board.Add(s)
edge_line((r, 0), (W - r, 0)); edge_line((W, r), (W, H - r)); edge_line((W - r, H), (r, H)); edge_line((0, H - r), (0, r))
k = r * (1 - math.sqrt(0.5))
edge_arc(None, (W - r, 0), (W - k, k), (W, r)); edge_arc(None, (W, H - r), (W - k, H - k), (W - r, H))
edge_arc(None, (r, H), (k, H - k), (0, H - r)); edge_arc(None, (0, r), (k, k), (r, 0))
HOLES = [(4, 4), (W - 4, 4), (4, H - 4), (W - 4, H - 4)]
for i, (x, y) in enumerate(HOLES):
    place("MountingHole.pretty", "MountingHole_3.2mm_M3", "H%d" % (i + 1), "M3", (x, y))


def smd(lib, name, ref, value, x, y, rot, padnets, lcsc):
    """Surface-mount part centred at x, y."""
    fp = pcbnew.FootprintLoad(LIB + lib, name)
    fp.SetPosition(P(x, y)); fp.SetOrientationDegrees(rot)
    fp.SetReference(ref); fp.SetValue(value)
    fp.Reference().SetVisible(False); fp.Value().SetVisible(False)
    board.Add(fp)
    for p in fp.Pads():
        n = padnets.get(p.GetNumber())
        if n: p.SetNet(net(n))
    LCSC[ref] = (lcsc, value)
    return fp
R0603 = ("Resistor_SMD.pretty", "R_0603_1608Metric")
C0603 = ("Capacitor_SMD.pretty", "C_0603_1608Metric")
C0805 = ("Capacitor_SMD.pretty", "C_0805_2012Metric")
def res(ref, val, x, y, rot, a, b, lcsc): return smd(*R0603, ref, val, x, y, rot, {"1": a, "2": b}, lcsc)
def cap(ref, val, x, y, rot, a, b, lcsc="C14663", big=False): return smd(*(C0805 if big else C0603), ref, val, x, y, rot, {"1": a, "2": b}, lcsc)
C10U = dict(lcsc="C15850", big=True)

# ---------------- ESP32-S3-DevKitC-1 sockets ----------------
J1 = ["3V3", "3V3", "RST", "LCD_CS", "LCD_DC", "LCD_MOSI", "LCD_SCK", "I2S_BCLK", "I2S_WS", "I2S_DOUT", "I2S_DIN",
      "I2C_SDA", None, None, "I2C_SCL", "VBAT_SENSE", "EDGE_FL", "EDGE_FR", "EDGE_RL", "EDGE_RR", "5V", "GND"]
J1_GPIO = ["3V3", "3V3", "RST", "4", "5", "6", "7", "15", "16", "17", "18", "8", "3", "46", "9", "10", "11", "12", "13", "14", "5V", "GND"]
J3 = ["GND", None, None, "BTN", "LED_DATA", "MOT_AIN1", "MOT_AIN2", "MOT_BIN1", "MOT_BIN2", "SERVO_SHOVEL",
      None, None, None, None, None, "SERVO_AUX", "SERVO_PAN", "SERVO_TILT", None, None, "GND", "GND"]
J3_GPIO = ["GND", "43", "44", "1", "2", "42", "41", "40", "39", "38", "37", "36", "35", "0", "45", "48", "47", "21", "20", "19", "GND", "GND"]
X1, YA, YB, YB2 = 71.12, 22.86, 45.72, 48.26     # pin 1 x, J1 row, J3 row (22.86 pitch), J3 row (25.40 pitch)
def devrow(ref, y, sig):
    LCSC[ref] = ("C2886702", "Socket 1x22 2.54mm")
    return place(SOCK, "PinSocket_1x22_P2.54mm_Vertical", ref, "Socket 1x22 2.54mm", (X1, y), (X1 - 2.54 * 21, y), {str(i + 1): s for i, s in enumerate(sig)})
devrow("U1A", YA, J1); devrow("U1B", YB, J3); devrow("U1C", YB2, J3)
for i in range(22):
    x = X1 - 2.54 * i
    text(J1_GPIO[i], x, YA + 1.9 + 0.48 * len(J1_GPIO[i]), angle=90)
    text(J3_GPIO[i], x, YB - 1.9 - 0.48 * len(J3_GPIO[i]), angle=90)
text("ESP32-S3 DEV BOARD: USB END", 31.0, 50.5, size=0.9); text("ANTENNA END", 65.0, 50.5, size=0.9)

HLCSC = {2: "C124375", 3: "C49257", 4: "C124378", 8: "C124381"}
_header = header
def header(ref, value, x, y, names, signals, **kw):
    LCSC[ref] = (HLCSC[len(names)], "Pin header 1x%d 2.54mm" % len(names))
    return _header(ref, "Pin header 1x%d 2.54mm" % len(names), x, y, names, signals, **kw)

# ---------------- top strip: plugs fed from J1 ----------------
ya, yb = 5.08, 13.97
for i, nm in enumerate(["FL", "FR", "RL", "RR"]):
    header("J%d" % (10 + i), "EDGE_" + nm, 10.16 + 10.16 * i, ya, ["3V3", "GND", "DO"], ["3V3", "GND", "EDGE_" + nm], title="EDGE " + nm)
header("J14", "I2C_A", 50.8, ya, ["3V3", "GND", "SCL", "SDA"], ["3V3", "GND", "I2C_SCL", "I2C_SDA"], title="EYE (I2C)")
header("J15", "I2C_B", 63.5, ya, ["3V3", "GND", "SCL", "SDA"], ["3V3", "GND", "I2C_SCL", "I2C_SDA"], title="I2C SPARE")
header("J18", "LCD_ST7789", 55.88, yb, ["GND", "VCC", "SCL", "SDA", "RES", "DC", "CS", "BLK"],
       ["GND", "3V3", "LCD_SCK", "LCD_MOSI", "RST", "LCD_DC", "LCD_CS", "3V3"], title="FACE LCD")

# on-board microphone (I2S, sound hole goes through the board)
smd("Sensor_Audio.pretty", "InvenSense_ICS-43434-6_3.5x2.65mm", "U5", "ICS-43434", 27.0, 14.6, 0,
    {"1": "I2S_WS", "2": "GND", "3": "GND", "4": "I2S_BCLK", "5": "3V3", "6": "I2S_DIN"}, "C5656610")
cap("C9", "100nF", 30.6, 13.4, 90, "3V3", "GND")
text("MIC", 22.6, 14.6, size=0.9)

# ---------------- bottom strip: plugs fed from J3 ----------------
y0 = 63.5
for i, (nm, s) in enumerate([("TILT", "SERVO_TILT"), ("PAN", "SERVO_PAN"), ("AUX", "SERVO_AUX"), ("SHVL", "SERVO_SHOVEL")]):
    x = 10.16 + 2.54 * i
    place(HDR, "PinHeader_1x03_P2.54mm_Vertical", "J%d" % (20 + i), "Pin header 1x3 2.54mm", (x, y0 - 5.08), (x, y0), {"1": s, "2": "5V", "3": "GND"})
    LCSC["J%d" % (20 + i)] = (HLCSC[3], "Pin header 1x3 2.54mm")
    text(nm, x, y0 - 5.08 - 1.9 - 0.48 * len(nm), angle=90)
for j, nm in enumerate(["SIG", "5V", "GND"]):
    text(nm, 6.6, y0 - 5.08 + 2.54 * j)
text("SERVOS", 13.97, 67.4)
header("J24", "BUTTON", 23.5, y0, ["3V3", "SIG", "GND"], ["3V3", "BTN", "GND"], label_side=-1, title="BUTTON")
header("J26", "LED_STRIP", 58.42, y0, ["5V", "DIN", "GND"], ["5V", "LED_DIN", "GND"], label_side=-1, title="FIN LED")
res("R3", "330R", 60.96, 52.6, 90, "LED_DATA", "LED_DIN", "C23138")

# ---------------- motor driver (under the dev board) ----------------
smd("Package_SO.pretty", "HTSSOP-16-1EP_4.4x5mm_P0.65mm_EP3.4x5mm_Mask2.46x2.31mm", "U2", "DRV8833PWP", 26.0, 34.3, 0,
    {"1": "3V3", "2": "MOTL_A", "3": "GND", "4": "MOTL_B", "5": "MOTR_B", "6": "GND", "7": "MOTR_A", "9": "MOT_BIN1", "10": "MOT_BIN2",
     "11": "DRV_VCP", "12": "VSW", "13": "GND", "14": "DRV_VINT", "15": "MOT_AIN2", "16": "MOT_AIN1", "17": "GND"}, "C50506")
cap("C4", "10uF 25V", 32.4, 37.2, 90, "VSW", "GND", **C10U)
cap("C5", "10nF", 31.0, 40.3, 0, "DRV_VCP", "VSW", lcsc="C57112")
cap("C6", "10uF 25V", 32.4, 31.6, 90, "GND", "DRV_VINT", **C10U)

# ---------------- speaker amplifier (under the dev board) ----------------
smd("Package_DFN_QFN.pretty", "TQFN-16-1EP_3x3mm_P0.5mm_EP1.23x1.23mm", "U3", "MAX98357AETE+T", 42.5, 34.3, 0,
    {"1": "I2S_DOUT", "3": "GND", "4": "AMP_SD", "7": "5V", "8": "5V", "9": "SPK+", "10": "SPK-", "11": "GND", "14": "I2S_WS", "15": "GND", "16": "I2S_BCLK", "17": "GND"}, "C910544")
for pn in ("3", "11", "15"):              # tie the amplifier's ground pins to its centre pad
    pd = [p for p in board.FindFootprintByReference("U3").Pads() if p.GetNumber() == pn][0].GetPosition()
    px, py = ToMM(pd.x), ToMM(pd.y)
    t = pcbnew.PCB_TRACK(board); t.SetStart(P(px, py)); t.SetEnd(P(42.5, py) if abs(px - 42.5) > abs(py - 34.3) else P(px, 34.3))
    t.SetWidth(FromMM(0.25)); t.SetLayer(pcbnew.F_Cu); t.SetNet(net("GND")); board.Add(t)
cap("C7", "10uF 25V", 42.5, 39.4, 0, "5V", "GND", **C10U)
cap("C8", "100nF", 46.4, 38.0, 90, "5V", "GND")
res("R4", "100k", 38.4, 37.6, 90, "AMP_SD", "5V", "C25803")

# ---------------- battery voltage sense ----------------
res("R1", "100k", 55.0, 31.0, 0, "VSW", "VBAT_SENSE", "C25803")
res("R2", "47k", 55.0, 34.0, 0, "VBAT_SENSE", "GND", "C25819")
cap("C3", "100nF", 55.0, 37.0, 0, "VBAT_SENSE", "GND")

# ---------------- 5 V converter (TPS563201, 3 A) ----------------
smd("Package_TO_SOT_SMD.pretty", "SOT-23-6", "U4", "TPS563201DDCR", 40.0, 58.0, 0,
    {"1": "GND", "2": "BUCK_SW", "3": "VSW", "4": "BUCK_FB", "5": "BUCK_EN", "6": "BUCK_BST"}, "C116592")
smd("Inductor_SMD.pretty", "L_Changjiang_FNR5040S", "L1", "3.3uH FNR5040S3R3NT", 46.6, 58.6, 0, {"1": "BUCK_SW", "2": "5V"}, "C167960")
cap("C10", "10uF 25V", 35.6, 56.6, 90, "VSW", "GND", **C10U)
cap("C11", "10uF 25V", 33.4, 56.6, 90, "VSW", "GND", **C10U)
cap("C15", "100nF", 42.6, 54.4, 0, "BUCK_BST", "BUCK_SW")
cap("C12", "10uF 25V", 51.6, 55.2, 0, "5V", "GND", **C10U)
cap("C13", "10uF 25V", 51.6, 58.0, 0, "5V", "GND", **C10U)
cap("C14", "10uF 25V", 51.6, 60.8, 0, "5V", "GND", **C10U)
res("R5", "56k", 44.4, 63.6, 180, "5V", "BUCK_FB", "C23206")
res("R6", "10k", 40.6, 63.6, 180, "BUCK_FB", "GND", "C25804")
res("R7", "100k", 35.6, 61.4, 90, "VSW", "BUCK_EN", "C25803")
text("5V 3A", 45.0, 66.2, size=0.9)
CPE = ("Capacitor_SMD.pretty", "CP_Elec_8x10")
smd(*CPE, "C1", "470uF 16V", 70.2, 58.6, 90, {"1": "5V", "2": "GND"}, "C82006")
smd(*CPE, "C2", "470uF 16V", 83.4, 58.6, 90, {"1": "VSW", "2": "GND"}, "C82006")

# ---------------- power in (right edge) and outputs (left edge) ----------------
TB = ("TerminalBlock.pretty", "TerminalBlock_bornier-2_P5.08mm")
def term(ref, title, x, y, top, bottom, lt, lb, right=True):
    """2-pin screw terminal, wire opening facing the board edge."""
    if right: fp = place(*TB, ref, "Screw terminal 2P 5.08mm", (x, y + 5.08), (x, y), {"1": bottom, "2": top})
    else:     fp = place(*TB, ref, "Screw terminal 2P 5.08mm", (x, y), (x, y + 5.08), {"1": top, "2": bottom})
    LCSC[ref] = ("C474881", "Screw terminal 2P 5.08mm")
    lx = x - 5.6 if right else x + 5.6
    text(lt, lx, y, size=0.9, angle=90); text(lb, lx, y + 5.08, size=0.9, angle=90)
    text(title, x - 7.6 if right else x + 7.6, y + 2.54, size=0.9, angle=90)
    return fp
xt = 92.71
term("J1", "BATTERY", xt, 13.97, "BAT+", "GND", "+", "-")
term("J2", "CHARGER", xt, 26.67, "BAT+", "GND", "+", "-")
term("J3", "SWITCH", xt, 39.37, "FUSED", "SW_B", "", "")
xl = 6.35
term("J4", "MOTOR L", xl, 20.32, "MOTL_A", "MOTL_B", "", "", right=False)
term("J5", "MOTOR R", xl, 30.48, "MOTR_A", "MOTR_B", "", "", right=False)
term("J6", "SPEAKER", xl, 40.64, "SPK+", "SPK-", "", "", right=False)
smd("Fuse.pretty", "Fuse_1812_4532Metric", "F1", "PTC 3A 16V", 80.6, 20.0, 90, {"1": "BAT+", "2": "FUSED"}, "C702820")
smd("Diode_SMD.pretty", "D_SMA", "D1", "SS34", 80.6, 44.0, 90, {"1": "VSW", "2": "SW_B"}, "C8678")
text("FUSE", 77.0, 20.0, size=0.8, angle=90); text("D1", 77.4, 44.0, size=0.8, angle=90)
text("DIMER MAIN v0.2", 84.0, 67.6, size=1.0, thick=0.18)
text("DIMER MAIN v0.2 - 2 x 18650 in (6.0-8.4 V) - assembled by JLCPCB", 50, 35, size=1.2, layer=pcbnew.B_SilkS, thick=0.2)

# ---------------- design rules ----------------
ds = board.GetDesignSettings()
ds.m_MinClearance = FromMM(0.15); ds.m_TrackMinWidth = FromMM(0.2); ds.m_ViasMinSize = FromMM(0.6)
ds.m_MinThroughDrill = FromMM(0.3); ds.m_CopperEdgeClearance = FromMM(0.4); ds.m_HoleClearance = FromMM(0.25)
ds.m_HoleToHoleMin = FromMM(0.45); ds.m_ViasMinAnnularWidth = FromMM(0.15)
ds.m_NetSettings.m_DefaultNetClass.SetClearance(FromMM(0.2))
ds.m_NetSettings.m_DefaultNetClass.SetTrackWidth(FromMM(0.25))
ds.m_NetSettings.m_DefaultNetClass.SetViaDiameter(FromMM(VIA_D)); ds.m_NetSettings.m_DefaultNetClass.SetViaDrill(FromMM(VIA_DRILL))
out = os.path.join(HERE, "dimer_main.kicad_pcb")
pcbnew.SaveBoard(out, board)
if "--place-only" in sys.argv:          # stop here to check the part placement before routing
    print("placed", len(board.GetFootprints()), "footprints, not routed"); sys.exit(0)

# ---------------- autoroute with freerouting ----------------
WORK = os.environ.get("DIMER_WORK", "/tmp/dimer_route"); os.makedirs(WORK, exist_ok=True)
dsn, ses = os.path.join(WORK, "dimer.dsn"), os.path.join(WORK, "dimer.ses")
board = pcbnew.LoadBoard(out)
pcbnew.ExportSpecctraDSN(board, dsn)
WIDTHS = {"BAT+": 1.2, "FUSED": 1.2, "SW_B": 1.2, "VSW": 0.6, "5V": 0.6, "BUCK_SW": 0.6, "GND": 0.4,
          "MOTL_A": 0.4, "MOTL_B": 0.4, "MOTR_A": 0.4, "MOTR_B": 0.4, "SPK+": 0.4, "SPK-": 0.4, "3V3": 0.4}
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
classes = '(class kicad_default "" %s\n      (circuit (use_via "%s"))\n      (rule (width 250) (clearance 200.1)))' % (" ".join(rest), via)
for w in sorted(set(WIDTHS.values())):
    ns = [n for n in allnets if WIDTHS.get(strip(n)) == w]
    if ns: classes += '\n    (class w%d %s\n      (circuit (use_via "%s"))\n      (rule (width %d) (clearance 200.1)))' % (w * 1000, " ".join(ns), via, w * 1000)
txt = txt[:i0] + classes + txt[j + 1:]
open(dsn, "w").write(txt)
if "--dsn-only" in sys.argv:            # write the router input and stop
    print("wrote", dsn); sys.exit(0)
if "--use-ses" not in sys.argv:         # --use-ses: reuse a session file routed in an earlier run
    if os.path.exists(ses): os.remove(ses)
    jar = os.environ.get("FREEROUTING", "freerouting-1.9.0.jar")
    subprocess.run(["xvfb-run", "-a", "java", "-jar", jar, "-de", dsn, "-do", ses, "-mp", "40"], check=False, timeout=1500,
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
        v = pcbnew.PCB_VIA(board); v.SetPosition(P(int(x) * SCALE, -int(y) * SCALE)); v.SetDrill(FromMM(VIA_DRILL)); v.SetWidth(FromMM(VIA_D))
        v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); v.SetNet(ni); board.Add(v); nvias += 1
print("routed: %d track segments, %d vias" % (ntracks, nvias))

# ---------------- ground pours ----------------
F, B = pcbnew.F_Cu, pcbnew.B_Cu
for layer in (F, B):
    z = pcbnew.ZONE(board); z.SetLayer(layer); z.SetNet(board.FindNet("GND")); z.SetZoneName("GND_" + ("F" if layer == F else "B"))
    o = z.Outline(); o.NewOutline()
    for x, y in ((0.6, 0.6), (W - 0.6, 0.6), (W - 0.6, H - 0.6), (0.6, H - 0.6)): o.Append(FromMM(x), FromMM(y))
    z.SetLocalClearance(FromMM(0.3)); z.SetMinThickness(FromMM(0.25)); z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
    z.SetThermalReliefGap(FromMM(0.3)); z.SetThermalReliefSpokeWidth(FromMM(0.4))
    z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    board.Add(z)
pcbnew.SaveBoard(out, board)
board = pcbnew.LoadBoard(out)          # fill on a reloaded board (filling the in-memory one crashes KiCad 7)
pcbnew.ZONE_FILLER(board).Fill(board.Zones())
pcbnew.SaveBoard(out, board)
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
zp = os.path.join(HERE, "dimer_main_gerbers_JLCPCB.zip")
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as zf:
    for f in sorted(glob.glob(os.path.join(gdir, "*"))): zf.write(f, os.path.basename(f))

# ---------------- JLCPCB assembly files: BOM + CPL ----------------
# JLCPCB's part library is rotated against KiCad's for some packages; these are the usual corrections.
ROT_FIX = [(r"^HTSSOP-", 270), (r"^TQFN-", 270), (r"^QFN-", 270), (r"^SOT-23", 180), (r"^CP_Elec_", 180)]
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
with open(os.path.join(HERE, "dimer_main_BOM_JLCPCB.csv"), "w", newline="") as f:
    w = csv.writer(f); w.writerow(["Comment", "Designator", "Footprint", "LCSC Part #"])
    for (comment, name, part), refs in sorted(groups.items(), key=lambda kv: key(sorted(kv[1], key=key)[0])):
        w.writerow([comment, ",".join(sorted(refs, key=key)), name, part])
with open(os.path.join(HERE, "dimer_main_CPL_JLCPCB.csv"), "w", newline="") as f:
    w = csv.writer(f); w.writerow(["Designator", "Mid X", "Mid Y", "Layer", "Rotation"])
    for row in sorted(cpl, key=lambda r: key(r[0])): w.writerow(row)
print("tracks", len(board.GetTracks()), "parts placed by JLCPCB", len(cpl), "BOM lines", len(groups), "gerber files", len(os.listdir(gdir)))
