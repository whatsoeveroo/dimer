"""Dimer V2: two other track styles to try, next to the stock O-ring track.

  A  clean belt   - a bought GT2 closed timing belt (rubber, 10 mm wide, 188 mm loop) on
                    printed 34-tooth flanged wheels. Smooth outside, quiet, very little to print.
                    Needs a 60 mm wheelbase (stock is 58), see README.
  B  chain links  - printed hard links joined by 1.75 mm filament pins, each with a grouser
                    outside and a guide tooth inside: the "mechanical chain" look.

Run:  python3 v2/cad/track_options.py
Writes v2/cad/track_options/track_A_belt.step, track_B_chain.step, chain_link.step,
belt_wheel.step, sprocket.step and a comparison picture (docs/track_options.png).
Origin of each track: midway between the axles, on the axle line, centred in width (same as the stock track).
"""
import math, os, sys, json
import cadquery as cq
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "cad"))
from dimer_components import asm
OUT = os.path.join(HERE, "track_options"); os.makedirs(OUT, exist_ok=True)
W = 11.0                                   # track width (stock)

def ycyl(d, length, x=0, z=0):
    return cq.Workplane("XZ").circle(d / 2).extrude(length / 2, both=True).translate((x, 0, z))

def loop_points(wheelbase, R, n):
    """n points evenly spaced around a stadium loop of radius R: (x, z, angle in degrees)."""
    per = 2 * wheelbase + 2 * math.pi * R; pts = []
    for i in range(n):
        s = (i + 0.5) * per / n
        if s < wheelbase: pts.append((-wheelbase / 2 + s, R, 0))
        elif s < wheelbase + math.pi * R:
            a = (s - wheelbase) / R; pts.append((wheelbase / 2 + R * math.sin(a), R * math.cos(a), math.degrees(a)))
        elif s < 2 * wheelbase + math.pi * R: pts.append((wheelbase / 2 - (s - wheelbase - math.pi * R), -R, 180))
        else:
            a = (s - 2 * wheelbase - math.pi * R) / R; pts.append((-wheelbase / 2 - R * math.sin(a), -R * math.cos(a), 180 + math.degrees(a)))
    return pts, per

def place(shape, x, z, ang):
    return shape.rotate((0, 0, 0), (0, 1, 0), ang).translate((x, 0, z))

# ---------------- A: GT2 timing belt on flanged pulleys ----------------
GT2_PD = 34 * 2.0 / math.pi                # 21.65 mm pitch diameter, 34 teeth
A_WB = (188 - math.pi * GT2_PD) / 2        # 60.0 mm centre distance for a 188 mm (94 tooth) loop

def belt_wheel():
    """34-tooth GT2 pulley with two flanges and a D-shaft hub, printed. Origin: centre."""
    od = GT2_PD - 0.5
    core = ycyl(od, W - 0.4)
    gap = cq.Workplane("XY").box(1.1, W, 0.9).translate((0, 0, od / 2 - 0.3))
    for k in range(34):
        core = core.cut(gap.rotate((0, 0, 0), (0, 1, 0), k * 360 / 34))
    flange = ycyl(od + 4, 1.2)
    w = core.union(flange.translate((0, W / 2 + 0.4, 0))).union(flange.translate((0, -W / 2 - 0.4, 0)))
    w = w.cut(ycyl(3.1, W + 4)).cut(ycyl(14, 3, ).translate((0, -W / 2 - 1.0, 0)))   # bore, recess on the outer face
    return w

def track_A():
    belt_t = 1.5; R = GT2_PD / 2 + 0.6
    outer = cq.Workplane("XZ").slot2D(A_WB + 2 * (R + belt_t / 2), 2 * (R + belt_t / 2)).extrude(W / 2 - 0.5, both=True)
    inner = cq.Workplane("XZ").slot2D(A_WB + 2 * (R - belt_t / 2), 2 * (R - belt_t / 2)).extrude(W, both=True)
    belt = outer.cut(inner)
    pts, per = loop_points(A_WB, R - belt_t / 2, 94)
    tooth = cq.Workplane("XY").box(1.0, W - 1, 0.75).translate((0, 0, -0.35))
    teeth = cq.Compound.makeCompound([place(tooth, x, z, a).val() for x, z, a in pts])
    wheel = belt_wheel()
    parts = [(belt, "rubber"), (cq.Workplane("XY").newObject([teeth]), "rubber")]
    for x in (-A_WB / 2, A_WB / 2):
        parts.append((wheel.translate((x, 0, 0)), "white"))
    return asm("track_A_gt2_belt", parts)

# ---------------- B: printed chain links ----------------
P = 6.0                                     # link pitch
PIN = 1.75                                  # filament pin
def chain_link():
    """One link, outside up (+Z), running along X. Pin axes at x = -P/2 and x = +P/2, z = 0."""
    plate = cq.Workplane("XY").box(P - 0.6, W, 1.6).translate((0, 0, 0.5)).edges("|Y").fillet(0.5)
    grouser = cq.Workplane("XY").box(1.4, W - 1.0, 1.4).translate((0.6, 0, 1.9)).edges("|Y and >Z").fillet(0.5)
    guide = cq.Workplane("XZ").polyline([(-1.4, -0.3), (1.4, -0.3), (0.7, -2.6), (-0.7, -2.6)]).close().extrude(1.6, both=True)
    link = plate.union(grouser).union(guide)
    k = 2.8
    for x, segs in ((-P / 2, ((-W / 2 + 1.6, 3.2), (W / 2 - 1.6, 3.2))), (P / 2, ((-3.1, 2.6), (3.1, 2.6)))):
        for yc, L in segs:
            link = link.union(cq.Workplane("XZ").circle(k / 2).extrude(L / 2, both=True).translate((x, yc, 0)))
    link = link.cut(ycyl(PIN + 0.25, W + 2, -P / 2)).cut(ycyl(PIN + 0.25, W + 2, P / 2))
    return link

def sprocket(n_teeth=11):
    """Drive / idler sprocket: two discs with a groove between them for the guide teeth, pins in the pockets. Origin: centre."""
    R = n_teeth * P / (2 * math.pi)        # pitch radius where the pins sit
    disc = ycyl(2 * R - 1.0, W - 1.0)
    disc = disc.cut(ycyl(2 * R + 2, 3.6))                                   # groove for the guide teeth
    pocket = ycyl(3.4, W + 2)
    for k in range(n_teeth):
        a = 2 * math.pi * (k + 0.5) / n_teeth
        disc = disc.cut(pocket.translate((R * math.cos(a), 0, R * math.sin(a))))
    disc = disc.union(ycyl(7, 3.6)).cut(ycyl(3.1, W + 4))                    # hub across the groove, shaft bore
    for k in range(5):                                                       # lightening holes
        a = 2 * math.pi * k / 5
        disc = disc.cut(ycyl(3.2, W + 2, 0.55 * R * math.cos(a), 0.55 * R * math.sin(a)))
    return disc, R

def track_B(wheelbase=58.0):
    spr, R = sprocket()
    pts, per = loop_points(wheelbase, R, 999)
    n = round(per / P); pts, per = loop_points(wheelbase, R, n)
    link = chain_link()
    links = cq.Compound.makeCompound([place(link, x, z, a).val() for x, z, a in pts])
    pins = cq.Compound.makeCompound([place(ycyl(PIN, W - 0.4, P / 2), x, z, a).val() for x, z, a in pts])
    parts = [(cq.Workplane("XY").newObject([links]), "dark"), (cq.Workplane("XY").newObject([pins]), "white")]
    for x in (-wheelbase / 2, wheelbase / 2):
        parts.append((spr.translate((x, 0, 0)), "servo"))
    return asm("track_B_chain", parts), n, R

if __name__ == "__main__":
    a = track_A(); a.save(os.path.join(OUT, "track_A_belt.step"))
    cq.exporters.export(belt_wheel(), os.path.join(OUT, "belt_wheel.step"))
    b, n, R = track_B(); b.save(os.path.join(OUT, "track_B_chain.step"))
    cq.exporters.export(chain_link(), os.path.join(OUT, "chain_link.step"))
    cq.exporters.export(sprocket()[0], os.path.join(OUT, "sprocket.step"))
    info = {"A_wheelbase": round(A_WB, 2), "A_pulley_pd": round(GT2_PD, 2), "B_links": n, "B_sprocket_pitch_d": round(2 * R, 2),
            "A_height": round(GT2_PD + 2 * 2.1, 1), "B_height": round(2 * R + 2 * 3.3, 1)}
    print(json.dumps(info))
    if len(sys.argv) > 1:                   # mesh dump for the comparison picture
        mesh = {}
        for name, asy in (("A", a), ("B", b)):
            m = []
            for ch in asy.children:
                for o in ch.shapes:
                    v, t = o.tessellate(0.05, 0.3); m.append({"c": list(ch.color.toTuple()[:3]), "v": [p.toTuple() for p in v], "t": t})
            mesh[name] = m
        json.dump(mesh, open(sys.argv[1], "w"))
