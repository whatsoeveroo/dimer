"""Mesh of Dimer 2.0 for the web viewer: python v2/cad/dimer_2_0_mesh.py out.json"""
import json, os, sys
os.environ["DIMER_NO_CHECK"] = "1"
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import dimer_2_0 as D
from cadtree import Node, flatten

TOL, ANG = float(os.environ.get("MESH_TOL", "0.06")), 0.35
items = []
def add(name, node, kind, group, label):
    cols = {}
    for _, shape, rgb, faces in flatten(node):
        for i, f in enumerate(shape.Faces()):
            c = tuple(round(x, 3) for x in (faces[i] if faces else rgb))
            try:
                v, t = f.tessellate(TOL, ANG)
            except Exception:
                continue
            if not t:
                continue
            V, I = cols.setdefault(c, ([], []))
            base = len(V) // 3
            V.extend(round(x, 2) for vv in v for x in vv.toTuple())
            I.extend(base + k for tri in t for k in tri)
    bb = None
    for _, shape, _, _ in flatten(node):
        b = shape.BoundingBox()
        bb = [b.xmin, b.ymin, b.zmin, b.xmax, b.ymax, b.zmax] if bb is None else [min(bb[0], b.xmin), min(bb[1], b.ymin), min(bb[2], b.zmin), max(bb[3], b.xmax), max(bb[4], b.ymax), max(bb[5], b.zmax)]
    nsol = sum(1 for _ in flatten(node)); nf = sum(len(s.Faces()) for _, s, _, _ in flatten(node))
    items.append({"name": name, "label": label, "kind": kind, "group": group, "solids": nsol, "faces": nf,
                  "min": [round(x, 1) for x in bb[:3]], "max": [round(x, 1) for x in bb[3:]],
                  "geo": [{"c": list(c), "v": V, "t": I} for c, (V, I) in cols.items()]})

for leaf in D.shell.children:
    add(leaf.name, Node(leaf.name, [leaf]), "shell", "Shell 2.0", D.LABELS[leaf.name])
for g, glabel in D.GROUPS:
    for ch in D.groups[g].children:
        add(ch.name, Node("x", [ch]), "part", glabel, D.LABELS.get(ch.name, ch.name))
json.dump({"items": items}, open(sys.argv[1], "w"), separators=(",", ":"))
print(len(items), "items", os.path.getsize(sys.argv[1]) // 1024, "kB")
