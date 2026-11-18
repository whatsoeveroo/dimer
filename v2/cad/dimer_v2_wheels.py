"""Printable track wheels for Dimer V2 (stock O-ring track).

Per robot print 2 drive wheels and 2 idler wheels. Each wheel carries two 3 mm O-rings side by side.

  drive wheel: D-hole for the N20 shaft (3 mm, flat at 2.5 mm). Press it on until it is
               about 2 mm from the body wall, then a drop of superglue.
  idler wheel: 4.2 mm hole that turns on a 12 mm piece of 4 mm brass tube. The M3 x 20 screw
               goes through the washer, the tube and into the side wall. The boss on the inner
               face keeps the wheel off the wall.

Sizes match dimer_v2_frame.py: axle 13.6 mm above the table, track 11 mm wide centred 7 mm
outside the body wall, so O-rings (3 mm thick) sit on a 21.2 mm groove floor.

    python v2/cad/dimer_v2_wheels.py      writes STEP and STL into v2/cad/step/wheels/
Print flat, inner face down, PLA or PETG, 0.2 mm layers, 100 % infill for the drive hub is fine.
"""
import os
import cadquery as cq

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "step", "wheels")

GROOVE_D = 21.2      # floor of the O-ring grooves: 21.2 + 2 x 3 mm O-ring = 27.2 mm track = 2 x 13.6 axle height
FLANGE_D = 23.0      # 0.9 mm lips keep the O-rings on
GROOVE_W = 3.3       # one 3 mm O-ring per groove
LIP, RIB = 0.8, 1.0  # outer lips and centre rib
WIDTH = 2 * LIP + 2 * GROOVE_W + RIB   # 9.2 mm


def wheel_body():
    w = cq.Workplane("XY").circle(FLANGE_D / 2).extrude(WIDTH)
    for z0 in (LIP, LIP + GROOVE_W + RIB):
        ring = (cq.Workplane("XY").circle(FLANGE_D / 2 + 1).circle(GROOVE_D / 2).extrude(GROOVE_W)
                .translate((0, 0, z0)))
        w = w.cut(ring)
    # lighten: six holes between hub and rim
    holes = cq.Workplane("XY").polarArray(6.2, 0, 360, 6).circle(1.7).extrude(WIDTH)
    return w.cut(holes)


def drive_wheel():
    w = wheel_body()
    # N20 D-shaft: 3.0 mm round with a flat leaving 2.5 mm. Hole 3.1 mm, flat 1.0 mm from the centre
    # (2.55 across), so it presses on by hand
    d_hole = (cq.Workplane("XY").circle(1.55).extrude(WIDTH)
              .cut(cq.Workplane("XY").center(0, 2.0).rect(4, 2).extrude(WIDTH)))
    return w.cut(d_hole)


def idler_wheel():
    w = wheel_body()
    boss = cq.Workplane("XY").circle(3.6).extrude(2.0).translate((0, 0, -2.0))   # inner face, toward the wall
    w = w.union(boss)
    bore = cq.Workplane("XY").circle(2.1).extrude(WIDTH + 4).translate((0, 0, -2.5))
    return w.cut(bore)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for name, part in (("v2_wheel_drive", drive_wheel()), ("v2_wheel_idler", idler_wheel())):
        cq.exporters.export(part, os.path.join(OUT, name + ".step"))
        cq.exporters.export(part, os.path.join(OUT, name + ".stl"), tolerance=0.02, angularTolerance=0.1)
        bb = part.val().BoundingBox()
        print(f"{name}: {bb.xlen:.1f} x {bb.ylen:.1f} x {bb.zlen:.1f} mm, volume {part.val().Volume():.0f} mm3")
