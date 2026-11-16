"""Dimer main board generator (KiCad 7 pcbnew scripting).

Run:  python3 pcb/make_board.py        (needs KiCad 7+, shapely, numpy)
Writes pcb/dimer_main.kicad_pcb, a DRC report and JLCPCB-ready Gerbers.

The board is a through-hole "hub": the ESP32-S3 dev board plugs into sockets
and every other part of the robot plugs into a labelled pin header.
"""
import sys, os, math, heapq, zipfile, glob, shutil
sys.path.insert(0, "/usr/lib/python3/dist-packages")
import numpy as np, shapely
from shapely.geometry import Point, LineString, Polygon, box as sbox
from shapely.ops import unary_union
import pcbnew
from pcbnew import FromMM, ToMM, VECTOR2I

HERE = os.path.dirname(os.path.abspath(__file__))
LIB = "/usr/share/kicad/footprints/"
W, H = 100.0, 70.0
G = 0.635                      # routing grid
CLR = 0.25                     # router clearance (design rule is 0.20)
VIA_D, VIA_DRILL = 0.8, 0.4
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

# ---------------- ESP32-S3-DevKitC-1 sockets ----------------
J1 = ["3V3", "3V3", "RST", "LCD_CS", "LCD_DC", "LCD_MOSI", "LCD_SCK", "I2S_BCLK", "I2S_WS", "I2S_DOUT", "I2S_DIN",
      "I2C_SDA", None, None, "I2C_SCL", "VBAT_SENSE", "EDGE_FL", "EDGE_FR", "EDGE_RL", "EDGE_RR", "5V", "GND"]
J1_GPIO = ["3V3", "3V3", "RST", "4", "5", "6", "7", "15", "16", "17", "18", "8", "3", "46", "9", "10", "11", "12", "13", "14", "5V", "GND"]
J3 = ["GND", "UART_TX", "UART_RX", "BTN", "LED_DATA", "MOT_AIN1", "MOT_AIN2", "MOT_BIN1", "MOT_BIN2", "SERVO_SHOVEL",
      None, None, None, None, None, "SERVO_AUX", "SERVO_PAN", "SERVO_TILT", None, None, "GND", "GND"]
J3_GPIO = ["GND", "43", "44", "1", "2", "42", "41", "40", "39", "38", "37", "36", "35", "0", "45", "48", "47", "21", "20", "19", "GND", "GND"]
X1, YA, YB, YB2 = 71.12, 22.86, 45.72, 48.26     # pin 1 x, J1 row, J3 row (22.86 pitch), J3 row (25.40 pitch)
def devrow(ref, y, sig):
    return place(SOCK, "PinSocket_1x22_P2.54mm_Vertical", ref, "ESP32-S3-DevKitC-1", (X1, y), (X1 - 2.54 * 21, y), {str(i + 1): s for i, s in enumerate(sig)})
devrow("U1A", YA, J1); devrow("U1B", YB, J3); devrow("U1C", YB2, J3)
for i in range(22):
    x = X1 - 2.54 * i
    text(J1_GPIO[i], x, YA + 1.9 + 0.48 * len(J1_GPIO[i]), angle=90)
    text(J3_GPIO[i], x, YB - 1.9 - 0.48 * len(J3_GPIO[i]), angle=90)
text("ESP32-S3-DevKitC-1  (N16R8)", 55.0, 33.8, size=1.5, thick=0.2)
text("USB end", 13.0, 33.8, size=1.1); text("antenna end", 66.0, 38.6, size=1.1)
text("narrow board: inner row / wide board: outer row", 44.45, 50.6, size=0.9)

# ---------------- top strip: connectors fed from J1 ----------------
ya, yb = 5.08, 13.97
for i, nm in enumerate(["FL", "FR", "RL", "RR"]):
    header("J%d" % (10 + i), "EDGE_" + nm, 10.16 + 10.16 * i, ya, ["3V3", "GND", "DO"], ["3V3", "GND", "EDGE_" + nm], title="EDGE " + nm)
header("J14", "I2C_A", 50.8, ya, ["3V3", "GND", "SCL", "SDA"], ["3V3", "GND", "I2C_SCL", "I2C_SDA"], title="I2C A")
header("J15", "I2C_B", 63.5, ya, ["3V3", "GND", "SCL", "SDA"], ["3V3", "GND", "I2C_SCL", "I2C_SDA"], title="I2C B")
header("J16", "MIC_INMP441", 12.7, yb, ["3V3", "GND", "SCK", "WS", "SD", "L/R"], ["3V3", "GND", "I2S_BCLK", "I2S_WS", "I2S_DIN", "GND"], title="MIC")
header("J17", "AMP_MAX98357", 35.56, yb, ["5V", "GND", "BCLK", "LRC", "DIN"], ["5V", "GND", "I2S_BCLK", "I2S_WS", "I2S_DOUT"], title="SPEAKER AMP")
header("J18", "LCD_ST7789", 55.88, yb, ["GND", "VCC", "SCL", "SDA", "RES", "DC", "CS", "BLK"],
       ["GND", "3V3", "LCD_SCK", "LCD_MOSI", "RST", "LCD_DC", "LCD_CS", "3V3"], title="FACE LCD")

# ---------------- bottom strip: connectors fed from J3 ----------------
y0 = 63.5
for i, (nm, s) in enumerate([("TILT", "SERVO_TILT"), ("PAN", "SERVO_PAN"), ("AUX", "SERVO_AUX"), ("SHVL", "SERVO_SHOVEL")]):
    x = 10.16 + 2.54 * i
    place(HDR, "PinHeader_1x03_P2.54mm_Vertical", "J%d" % (20 + i), "SERVO_" + nm, (x, y0 - 5.08), (x, y0), {"1": s, "2": "5V", "3": "GND"})
    text(nm, x, y0 - 5.08 - 1.9 - 0.48 * len(nm), angle=90)
for j, nm in enumerate(["SIG", "5V", "GND"]):
    text(nm, 6.6, y0 - 5.08 + 2.54 * j)
text("SERVOS", 13.97, 67.4)
header("J24", "BUTTON", 25.4, y0, ["SIG", "GND"], ["BTN", "GND"], label_side=-1, title="BTN")
header("J25", "MOTOR_DRIVER", 35.56, y0, ["VM", "GND", "3V3", "AIN1", "AIN2", "BIN1", "BIN2"],
       ["VSW", "GND", "3V3", "MOT_AIN1", "MOT_AIN2", "MOT_BIN1", "MOT_BIN2"], label_side=-1, title="MOTOR DRIVER")
header("J26", "LED_STRIP", 58.42, y0, ["5V", "DIN", "GND"], ["5V", "LED_DIN", "GND"], label_side=-1, title="FIN LED")
header("J27", "UART", 68.58, y0, ["3V3", "GND", "TX", "RX"], ["3V3", "GND", "UART_TX", "UART_RX"], label_side=-1, title="UART")

# ---------------- passives ----------------
RES = ("Resistor_THT.pretty", "R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal")
place(*RES, "R1", "100k", (43.18, 30.48), (33.02, 30.48), {"1": "VSW", "2": "VBAT_SENSE"}); text("R1 100k", 38.1, 28.3, size=0.9)
place(*RES, "R2", "47k", (33.02, 36.83), (22.86, 36.83), {"1": "VBAT_SENSE", "2": "GND"}); text("R2 47k", 27.94, 39.0, size=0.9)
place("Capacitor_THT.pretty", "C_Disc_D5.0mm_W2.5mm_P5.00mm", "C3", "100nF", (27.94, 30.48), (22.94, 30.48), {"1": "VBAT_SENSE", "2": "GND"}); text("C3 100n", 25.4, 28.3, size=0.9)
place(*RES, "R3", "330R", (55.88, 54.61), (66.04, 54.61), {"1": "LED_DATA", "2": "LED_DIN"}); text("R3 330R", 60.96, 52.5, size=0.9)

# ---------------- power strip (right edge) ----------------
TB = ("TerminalBlock.pretty", "TerminalBlock_bornier-2_P5.08mm")
xt = 92.71
for ref, val, y, n1, n2, l1, l2 in [("J1", "BATTERY 2S", 13.97, "BAT+", "GND", "BAT+", "GND"), ("J2", "POWER SWITCH", 26.67, "FUSED", "SW_B", "SW", "SW"),
                                     ("J3", "BUCK IN", 39.37, "VSW", "GND", "VIN+", "GND"), ("J4", "BUCK OUT 5V", 52.07, "5V", "GND", "5V+", "GND")]:
    place(*TB, ref, val, (xt, y), (xt, y + 5.08), {"1": n1, "2": n2})
    text(l1, 98.3, y, angle=90); text(l2, 98.3, y + 5.08, angle=90)
xc = 83.82
place("Fuse.pretty", "Fuse_Bourns_MF-RHT300", "F1", "PTC 3A", (xc, 19.05), (xc, 24.13), {"1": "BAT+", "2": "FUSED"})
place("Diode_THT.pretty", "D_DO-201AD_P15.24mm_Horizontal", "D1", "1N5822", (xc, 45.72), (xc, 30.48), {"1": "VSW", "2": "SW_B"})
place("Capacitor_THT.pretty", "CP_Radial_D8.0mm_P3.50mm", "C2", "220uF 16V", (xc, 50.165), (xc, 53.665), {"1": "VSW", "2": "GND"})
place("Capacitor_THT.pretty", "CP_Radial_D8.0mm_P3.50mm", "C1", "470uF 16V", (xc, 60.325), (xc, 63.825), {"1": "5V", "2": "GND"})
text("F1", 79.6, 21.6); text("D1", 79.2, 38.1); text("1N5822", 87.3, 38.1, angle=90, size=0.9)
text("C2", 78.2, 52.0); text("C1", 78.6, 58.4)
text("DIMER MAIN v0.1", 83.5, 8.6, size=1.1, thick=0.18)
text("DIMER MAIN v0.1 - 2S Li-ion 6.0-8.4V in, 5V via external buck", 50, 35, size=1.3, layer=pcbnew.B_SilkS, thick=0.2)

# ================= router =================
NX, NY = int(round(W / G)) + 1, int(round(H / G)) + 1
F, B = pcbnew.F_Cu, pcbnew.B_Cu
obs = {0: [], 1: []}                      # layer -> [(geom, net)]
padnodes = {}                              # net -> [(i, j, x, y)]
for fp in board.GetFootprints():
    for p in fp.Pads():
        pos = p.GetPosition(); x, y = ToMM(pos.x), ToMM(pos.y)
        poly = p.GetEffectivePolygon()
        if poly.OutlineCount() == 0 or p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH:        # NPTH hole
            g = Point(x, y).buffer(ToMM(p.GetDrillSize().x) / 2 + 0.6)
        else:
            o = poly.Outline(0)
            g = Polygon([(ToMM(o.CPoint(k).x), ToMM(o.CPoint(k).y)) for k in range(o.PointCount())]).buffer(0.01)
        nm = p.GetNetname() or ("~%s.%s" % (fp.GetReference(), p.GetNumber()))
        obs[0].append((g, nm)); obs[1].append((g, nm))
        if p.GetNetname():
            padnodes.setdefault(nm, []).append((int(round(x / G)), int(round(y / G)), x, y))

WIDTH = {"BAT+": 1.5, "FUSED": 1.5, "SW_B": 1.5, "VSW": 1.2, "5V": 1.2, "3V3": 0.6, "GND": 0.8}
XS, YS = np.meshgrid(np.arange(NX) * G, np.arange(NY) * G, indexing="ij")
SQ2 = math.sqrt(2)
MOVES = [(1, 0, 1), (-1, 0, 1), (0, 1, 1), (0, -1, 1), (1, 1, SQ2), (1, -1, SQ2), (-1, 1, SQ2), (-1, -1, SQ2)]
tracks, vias, failed = [], [], []

def masks(netname, hw):
    """free-node mask per layer and free-edge masks (sampled along each edge)"""
    out = {}
    for l in (0, 1):
        blk = unary_union([g.buffer(hw + CLR) for g, n in obs[l] if n != netname])
        shapely.prepare(blk)
        def free(dx, dy):
            return ~shapely.contains_xy(blk, XS + dx, YS + dy)
        node = free(0, 0)
        m = 2
        node[:m, :] = False; node[-m:, :] = False; node[:, :m] = False; node[:, -m:] = False
        edge = {}
        for dx, dy, _ in MOVES:
            if (dx, dy) in ((1, 0), (0, 1), (1, 1), (1, -1)):
                ok = node.copy()
                for f in (0.25, 0.5, 0.75):
                    ok &= free(dx * G * f, dy * G * f)
                edge[(dx, dy)] = ok
        vblk = unary_union([g.buffer(VIA_D / 2 + CLR) for g, n in obs[l] if n != netname]); shapely.prepare(vblk)
        out[l] = (node, edge, ~shapely.contains_xy(vblk, XS, YS))
    return out

def route_net(netname):
    hw = WIDTH.get(netname, 0.3) / 2
    pads = padnodes[netname]
    if len(pads) < 2: return True
    mk = masks(netname, hw)
    padset = {(i, j) for i, j, _, _ in pads}
    def edge_ok(l, i, j, dx, dy):
        node, edge, _ = mk[l]
        ni, nj = i + dx, j + dy
        if not (0 <= ni < NX and 0 <= nj < NY) or not node[ni, nj]: return False
        if (dx, dy) in edge: return bool(edge[(dx, dy)][i, j])
        return bool(edge[(-dx, -dy)][ni, nj])
    tree = {(pads[0][0], pads[0][1], 0), (pads[0][0], pads[0][1], 1)}
    todo = {(i, j) for i, j, _, _ in pads[1:]} - {(pads[0][0], pads[0][1])}
    ok = True
    while todo:
        dist = {n: 0.0 for n in tree}; prev = {}
        pq = [(0.0, n) for n in tree]; heapq.heapify(pq); hit = None
        while pq:
            d, n = heapq.heappop(pq)
            if d > dist.get(n, 1e18): continue
            i, j, l = n
            if (i, j) in todo: hit = n; break
            cand = []
            for dx, dy, c in MOVES:
                if edge_ok(l, i, j, dx, dy): cand.append(((i + dx, j + dy, l), c))
            if (i, j) in padset or (mk[0][2][i, j] and mk[1][2][i, j] and mk[0][0][i, j] and mk[1][0][i, j]):
                cand.append(((i, j, 1 - l), 0.0 if (i, j) in padset else 12.0))
            for m, c in cand:
                nd = d + c
                if nd < dist.get(m, 1e18):
                    dist[m] = nd; prev[m] = n; heapq.heappush(pq, (nd, m))
        if hit is None:
            failed.append((netname, sorted(todo))); ok = False; break
        path = [hit]
        while path[-1] in prev: path.append(prev[path[-1]])
        todo.discard((hit[0], hit[1]))
        for a, b in zip(path, path[1:]):
            if a[2] != b[2]:
                if (a[0], a[1]) not in padset:
                    vias.append((netname, a[0] * G, a[1] * G))
                    for l in (0, 1): obs[l].append((Point(a[0] * G, a[1] * G).buffer(VIA_D / 2), netname))
            else:
                tracks.append((netname, a[2], a[0] * G, a[1] * G, b[0] * G, b[1] * G, 2 * hw))
                obs[a[2]].append((LineString([(a[0] * G, a[1] * G), (b[0] * G, b[1] * G)]).buffer(hw), netname))
        for n in path:
            tree.add(n)
            if (n[0], n[1]) in padset: tree.add((n[0], n[1], 1 - n[2]))
    # stubs for pads that are not exactly on the grid
    for i, j, x, y in pads:
        if abs(i * G - x) > 0.005 or abs(j * G - y) > 0.005:
            for l in (0, 1):
                tracks.append((netname, l, x, y, i * G, j * G, min(2 * hw, 0.8)))
    return ok

def span(n):
    xs = [p[2] for p in padnodes[n]]; ys = [p[3] for p in padnodes[n]]
    return (max(xs) - min(xs)) + (max(ys) - min(ys))
order = ["BAT+", "FUSED", "SW_B", "VSW", "5V"] + sorted([n for n in padnodes if n not in WIDTH], key=span) + ["3V3", "GND"]
for n in order:
    route_net(n)
print("routed nets:", len(order), "failed:", failed)

# merge collinear grid steps into long segments
def merged(tr):
    out = []
    for t in tr:
        if out:
            p = out[-1]
            if p[0] == t[0] and p[1] == t[1] and p[6] == t[6]:
                for (ax, ay, bx, by) in ((t[2], t[3], t[4], t[5]), (t[4], t[5], t[2], t[3])):
                    for (px, py, qx, qy, tail) in ((p[2], p[3], p[4], p[5], True), (p[4], p[5], p[2], p[3], False)):
                        if abs(qx - ax) < 1e-6 and abs(qy - ay) < 1e-6:
                            cross = (qx - px) * (by - ay) - (qy - py) * (bx - ax)
                            dot = (qx - px) * (bx - ax) + (qy - py) * (by - ay)
                            if abs(cross) < 1e-9 and dot > 0:
                                out[-1] = (p[0], p[1], px, py, bx, by, p[6]); break
                    else: continue
                    break
                else:
                    out.append(t)
                continue
        out.append(t)
    return out
tracks = merged(tracks)
for (n, l, x1, y1, x2, y2, w) in tracks:
    t = pcbnew.PCB_TRACK(board); t.SetStart(P(x1, y1)); t.SetEnd(P(x2, y2)); t.SetWidth(FromMM(w))
    t.SetLayer(F if l == 0 else B); t.SetNet(net(n)); board.Add(t)
for (n, x, y) in vias:
    v = pcbnew.PCB_VIA(board); v.SetPosition(P(x, y)); v.SetDrill(FromMM(VIA_DRILL)); v.SetWidth(FromMM(VIA_D))
    v.SetLayerPair(F, B); v.SetNet(net(n)); board.Add(v)

# ---------------- design rules + ground pours ----------------
ds = board.GetDesignSettings()
ds.m_MinClearance = FromMM(0.2); ds.m_TrackMinWidth = FromMM(0.25); ds.m_ViasMinSize = FromMM(0.6)
ds.m_MinThroughDrill = FromMM(0.3); ds.m_CopperEdgeClearance = FromMM(0.4); ds.m_HoleClearance = FromMM(0.25)
ds.m_HoleToHoleMin = FromMM(0.45); ds.m_ViasMinAnnularWidth = FromMM(0.15)
ds.m_NetSettings.m_DefaultNetClass.SetClearance(FromMM(0.2))
ds.m_NetSettings.m_DefaultNetClass.SetTrackWidth(FromMM(0.3))
for layer in (F, B):
    z = pcbnew.ZONE(board); z.SetLayer(layer); z.SetNet(net("GND")); z.SetZoneName("GND_" + ("F" if layer == F else "B"))
    o = z.Outline(); o.NewOutline()
    for x, y in ((0.6, 0.6), (W - 0.6, 0.6), (W - 0.6, H - 0.6), (0.6, H - 0.6)): o.Append(FromMM(x), FromMM(y))
    z.SetLocalClearance(FromMM(0.3)); z.SetMinThickness(FromMM(0.25)); z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
    z.SetThermalReliefGap(FromMM(0.4)); z.SetThermalReliefSpokeWidth(FromMM(0.6))
    z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    board.Add(z)
out = os.path.join(HERE, "dimer_main.kicad_pcb")
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
print("tracks", len(tracks), "vias", len(vias), "gerber files", len(os.listdir(gdir)))
