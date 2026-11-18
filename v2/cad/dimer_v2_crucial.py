"""Dimer V2: light STEP with only the parts that matter for modelling a new body.

Takes the placed parts from dimer_v2_frame.py and keeps what a body has to fit around:
tracks, motors, battery, power board, tilt servo, display, brain with camera, speaker,
amplifier and the two edge sensors. Each one is a single named body in its real position.

Left out: every screw and nut. The tracks are plain envelopes (the space they sweep, no lugs). The power board loses its small chips (under 1.5 mm tall)
and its loose header pins: each header becomes one block that already includes the pin height,
so the space the jumper plugs need is still there.

    python v2/cad/dimer_v2_crucial.py [mesh.json]
writes into v2/cad/step/crucial/
    dimer_v2_crucial_parts.step        bought parts only, no frame
    dimer_v2_crucial_with_frame.step   the same plus the four printed frame pieces (in their own group)
Axes as in the frame script: X forward, Y left, Z up, table at Z = 0, units mm.
"""
import json, os, runpy, sys, tempfile
import cadquery as cq

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "step", "crucial")
os.makedirs(OUT, exist_ok=True)

os.environ["DIMER_OUT"] = tempfile.mkdtemp()      # the frame script writes its usual files there, not over the real ones
os.environ["DIMER_NO_CHECK"] = "1"
g = runpy.run_path(os.path.join(HERE, "dimer_v2_frame.py"))

MIN_H = 1.5          # power board parts lower than this are dropped
PIN_UP = 6.0         # header pins reach this far above the part body (as in the frame script)

LABELS = {"track_left": "Track, left", "track_right": "Track, right", "motor_left": "N20 motor, left (rear)",
          "motor_right": "N20 motor, right (front)", "battery": "LiPo 803040", "power_board": "Power board",
          "servo_tilt": "SG90 tilt servo", "face_display": "0.96 in display", "brain_camera": "XIAO ESP32S3 Sense",
          "speaker": "20 mm speaker", "speaker_amplifier": "MAX98357A amplifier",
          "edge_sensor_front_left": "Edge sensor, left", "edge_sensor_front_right": "Edge sensor, right"}


def light_board():
    """Power board: outline with notch and hole, plus one block per part that is taller than MIN_H."""
    B, b2r, xbox = g["BOARD"], g["board_to_robot"], g["xbox"]
    t = B["thickness"]
    full = g["power_board"]()                       # take the finished PCB plate (outline, notch, hole) from the original
    pcb = full.children[0].obj if full.children else None
    def rbox(X0, X1, Y0, Y1, z0, z1):
        (xa, ya), (xb, yb) = b2r(X0, Y0), b2r(X1, Y1)
        return xbox(min(xa, xb), max(xa, xb), min(ya, yb), max(ya, yb), z0, z1)
    a = cq.Assembly(name="power_board")
    a.add(pcb, name="pcb", color=cq.Color(0.1, 0.1, 0.1))
    for i, p in enumerate(B["parts"]):
        if p["h"] < MIN_H and not p.get("pins"):
            continue
        top = t + p["h"] + (PIN_UP if p.get("pins") else 0)
        pins_below = 3.0 if p.get("pins") else 0      # through-hole pins poke out under the board
        a.add(rbox(p["x0"], p["x1"], p["y0"], p["y1"], t, top), name="p%d" % i, color=cq.Color(0.85, 0.85, 0.82))
        if pins_below:
            a.add(rbox(p["x0"], p["x1"], p["y0"], p["y1"], -pins_below, 0), name="p%d_tails" % i, color=cq.Color(0.8, 0.65, 0.2))
    return a


def track_envelope(name, loc):
    """Track as a plain stadium: the space it sweeps, without lugs (215 faces down to a handful)."""
    r, wb, w = g["AXLE_Z"], g["WHEELBASE"], g["TRACK_W"]
    body = (cq.Workplane("XZ").center(-wb / 2, 0).circle(r).center(wb, 0).circle(r).extrude(w / 2, both=True)
            .union(cq.Workplane("XY").box(wb, w, 2 * r)))
    a = cq.Assembly(name=name)
    a.add(body, name="envelope", color=cq.Color(0.15, 0.15, 0.15))
    return a


def leaves(a, loc):
    here = loc * a.loc if a.loc is not None else loc
    for o in (a.shapes if hasattr(a, "shapes") else []):
        yield o.moved(here), a.color
    for ch in a.children:
        yield from leaves(ch, here)


def one_body(name, a, loc):
    """All leaves of a placed part as one compound in robot coordinates, coloured by its biggest leaf."""
    shapes = list(leaves(a, loc))
    big = max(shapes, key=lambda s: s[0].Volume())
    col = big[1].toTuple()[:3] if big[1] is not None else (0.5, 0.5, 0.5)
    return cq.Compound.makeCompound([s for s, _ in shapes]), col


bodies = []
for name, a, loc in g["placed"]:
    if name.startswith("screw"):
        continue
    if name == "power_board":
        a = light_board()
    if name.startswith("track"):
        a = track_envelope(name, loc)
    shape, col = one_body(name, a, loc)
    bodies.append((name, shape, col))

parts_only = cq.Assembly(name="dimer_v2_crucial_parts")
with_frame = cq.Assembly(name="dimer_v2_crucial_with_frame")
bought = cq.Assembly(name="bought_parts")
for name, shape, col in bodies:
    parts_only.add(shape, name=name, color=cq.Color(*col))
    bought.add(shape, name=name, color=cq.Color(*col))
frame = cq.Assembly(name="printed_frame")
for name, (shape, col) in g["parts"].items():
    frame.add(shape.val(), name=name, color=cq.Color(*col))
with_frame.add(bought, name="bought_parts")
with_frame.add(frame, name="printed_frame")

# no pcurves: the file only keeps the 3D geometry, which is all a CAD program needs to import it (about a third of the size)
parts_only.export(os.path.join(OUT, "dimer_v2_crucial_parts.step"), write_pcurves=False)
with_frame.export(os.path.join(OUT, "dimer_v2_crucial_with_frame.step"), write_pcurves=False)

summary = []
for name, shape, col in bodies:
    bb = shape.BoundingBox()
    summary.append({"name": name, "label": LABELS.get(name, name), "faces": len(shape.Faces()),
                    "min": [round(bb.xmin, 1), round(bb.ymin, 1), round(bb.zmin, 1)],
                    "max": [round(bb.xmax, 1), round(bb.ymax, 1), round(bb.zmax, 1)]})
    print("%-26s %5d faces  x %6.1f..%6.1f  y %6.1f..%6.1f  z %5.1f..%5.1f" % (name, len(shape.Faces()), bb.xmin, bb.xmax, bb.ymin, bb.ymax, bb.zmin, bb.zmax))
for f in ("dimer_v2_crucial_parts.step", "dimer_v2_crucial_with_frame.step"):
    print(f, "%.0f kB" % (os.path.getsize(os.path.join(OUT, f)) / 1024))

if len(sys.argv) > 1:   # mesh for the web viewer
    mesh = []
    items = [(n, s, c, "part") for n, s, c in bodies] + [(n, s.val(), c, "frame") for n, (s, c) in g["parts"].items()]
    for name, shape, col, kind in items:
        v, t = shape.tessellate(0.08, 0.35)
        mesh.append({"name": name, "kind": kind, "color": [round(c, 3) for c in col],
                     "v": [round(c, 2) for p in v for c in p.toTuple()], "t": [i for tri in t for i in tri]})
    json.dump({"mesh": mesh, "parts": summary}, open(sys.argv[1], "w"), separators=(",", ":"))
