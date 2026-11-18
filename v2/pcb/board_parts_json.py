"""Write v2/pcb/dimer_v2_power_parts.json: outline and part blocks of the V2 power board,
read from dimer_v2_power.kicad_pcb.  The frame generator (v2/cad/dimer_v2_frame.py)
builds the board's 3D model from it, so the CAD always matches the board.
Run after make_board_v2.py."""
import sys, os, json
sys.path.append("/usr/lib/python3/dist-packages")
import pcbnew
from pcbnew import ToMM
HERE = os.path.dirname(os.path.abspath(__file__))
b = pcbnew.LoadBoard(os.path.join(HERE, "dimer_v2_power.kicad_pcb"))
# body height above the board (mm) and colour, by reference prefix or full reference
HEIGHT = {"J1": (3.2, "steel"), "SW1": (1.5, "black"), "J2": (6.0, "white"), "L1": (4.0, "dark"), "D3": (2.3, "black"),
          "U1": (1.6, "black"), "U2": (1.1, "black"), "U3": (1.8, "black"), "U4": (1.2, "black"), "U5": (2.65, "black"),
          "Q1": (1.1, "black"), "D1": (0.6, "red"), "D2": (0.6, "cell"), "C": (0.8, "brass"), "R": (0.5, "black"), "J": (2.5, "black")}
parts = []
for fp in b.GetFootprints():
    ref = fp.GetReference()
    if ref.startswith("H"): continue
    items = [g for g in fp.GraphicalItems() if g.GetLayer() == pcbnew.F_Fab and g.GetClass() != "PCB_TEXT" and g.GetClass() != "FP_TEXT"]
    if not items: continue
    bb = items[0].GetBoundingBox()
    for g in items[1:]: bb.Merge(g.GetBoundingBox())
    h, col = HEIGHT.get(ref) or HEIGHT.get(ref.rstrip("0123456789")) or (1.0, "black")
    if fp.GetValue().startswith("10uF"): h = 1.25                 # 0805 capacitors are taller than the 0603 parts
    part = {"ref": ref, "x0": ToMM(bb.GetLeft()), "y0": ToMM(bb.GetTop()), "x1": ToMM(bb.GetRight()), "y1": ToMM(bb.GetBottom()), "h": h, "color": col}
    if ref.startswith("J") and ref not in ("J1", "J2"):        # pin header: pins above and below the plastic
        part["pins"] = [[ToMM(p.GetPosition().x), ToMM(p.GetPosition().y)] for p in fp.Pads()]
    if ref == "SW1":                                         # the lever sticks out past the rear edge
        part["lever"] = [ToMM(fp.GetPosition().x), ToMM(fp.GetPosition().y)]
    parts.append(part)
edges = []
for d in b.GetDrawings():
    if d.GetLayer() == pcbnew.Edge_Cuts and d.GetShape() == pcbnew.SHAPE_T_SEGMENT:
        edges.append([ToMM(d.GetStart().x), ToMM(d.GetStart().y), ToMM(d.GetEnd().x), ToMM(d.GetEnd().y)])
holes = [[ToMM(fp.GetPosition().x), ToMM(fp.GetPosition().y)] for fp in b.GetFootprints() if fp.GetReference().startswith("H")]
json.dump({"thickness": 1.6, "corner_r": 2.0, "edges": edges, "holes": holes, "parts": parts}, open(os.path.join(HERE, "dimer_v2_power_parts.json"), "w"), indent=1)
print(len(parts), "parts,", len(edges), "edge lines")
