"""Detailed stand-in models of the bought parts for Dimer (CadQuery).

Each function returns a cq.Assembly built around a documented local origin.
Sizes follow typical datasheet / seller drawings; they are good for layout
and rendering, not a substitute for measuring the part you actually receive.
"""
import math
import cadquery as cq

C = dict(black=(0.08, 0.08, 0.09), dark=(0.2, 0.2, 0.22), steel=(0.72, 0.73, 0.75), brass=(0.78, 0.62, 0.25), gold=(0.85, 0.68, 0.2),
         servo=(0.13, 0.33, 0.75), white=(0.93, 0.93, 0.9), pcb_blue=(0.08, 0.2, 0.55), pcb_purple=(0.33, 0.12, 0.45), pcb_green=(0.05, 0.4, 0.2),
         pcb_black=(0.1, 0.1, 0.12), pcb_red=(0.65, 0.1, 0.1), glass=(0.03, 0.05, 0.08), screen=(0.1, 0.75, 0.85), rubber=(0.12, 0.12, 0.13),
         cell=(0.2, 0.55, 0.3), red=(0.8, 0.1, 0.1), copper=(0.72, 0.42, 0.2), grey=(0.5, 0.52, 0.55), yellow=(0.9, 0.75, 0.1))

def B(x, y, z, cx=0, cy=0, z0=0):
    return cq.Workplane("XY").box(x, y, z, centered=(True, True, False)).translate((cx, cy, z0))
def CZ(d, h, cx=0, cy=0, z0=0):
    return cq.Workplane("XY").circle(d / 2).extrude(h).translate((cx, cy, z0))
def CY(d, length, x=0, z=0, y0=0):
    return cq.Workplane("XZ").circle(d / 2).extrude(-length).translate((x, y0, z))
def CX(d, length, y=0, z=0, x0=0):
    return cq.Workplane("YZ").circle(d / 2).extrude(length).translate((x0, y, z))
def asm(name, parts):
    a = cq.Assembly(name=name)
    for i, (shape, col) in enumerate(parts):
        a.add(shape, name="%s_%02d" % (name, i), color=cq.Color(*C[col]))
    return a
def header(n, cx=0, cy=0, z0=0, along="x", down=False):
    """n-pin 2.54 mm header: plastic strip + pins. Returns parts list."""
    L = 2.54 * n
    strip = B(L, 2.5, 2.5, z0=0) if along == "x" else B(2.5, L, 2.5, z0=0)
    pins = None
    for i in range(n):
        o = -L / 2 + 1.27 + 2.54 * i
        p = B(0.64, 0.64, 11.5, cx=o if along == "x" else 0, cy=0 if along == "x" else o, z0=-3)
        pins = p if pins is None else pins.union(p)
    if down:
        strip = strip.mirror("XY"); pins = pins.mirror("XY")
    return [(strip.translate((cx, cy, z0)), "black"), (pins.translate((cx, cy, z0)), "gold")]

def servo_mg90s(horn=True):
    """Origin: output shaft axis is +Z through (0,0); Z=0 is the underside of the mounting ears. Body runs toward -X."""
    cx = -5.4
    body = B(22.8, 12.2, 22.5, cx=cx, z0=-15.9).edges("|Z").fillet(0.8)
    ears = B(32.3, 12.2, 2.5, cx=cx).edges("|Z").fillet(1.0)
    for dx in (-13.9, 13.9):
        ears = ears.cut(CZ(2.2, 4, cx=cx + dx, z0=-1)).cut(B(3, 1.2, 4, cx=cx + dx + (1.6 if dx > 0 else -1.6), z0=-1))
    top = CZ(11.8, 4.3, z0=6.6).union(CZ(5.5, 4.3, cx=-6.5, z0=6.6)).union(B(6.5, 5.5, 4.3, cx=-3.2, z0=6.6))
    spline = CZ(4.8, 3.2, z0=10.9)
    lid = B(22.8, 12.2, 0.3, cx=cx, z0=-9.0 - 0.15).cut(B(22.2, 11.6, 1, cx=cx, z0=-9.5))
    cable = B(3, 3.6, 1.2, cx=cx - 11.4 - 1.5, z0=-14.5)
    parts = [(body, "servo"), (ears, "servo"), (top, "servo"), (spline, "brass"), (lid, "dark"), (cable, "copper")]
    if horn:
        arm = (cq.Workplane("XY").polyline([(0, -3.5), (16, -2), (16, 2), (0, 3.5)]).close().extrude(1.5).translate((0, 0, 12.6))
               .union(CZ(7, 3.6, z0=11.0)).union(CZ(4, 1.5, cx=16, z0=12.6)))
        for k in range(5):
            arm = arm.cut(CZ(1.0, 4, cx=5 + 2.4 * k, z0=12))
        parts += [(arm, "white"), (CZ(2.6, 0.8, z0=14.6), "steel")]
    return asm("servo_mg90s", parts)

def motor_n20():
    """Origin: shaft axis is +Y; Y=0 is the gearbox front face. Gearbox and motor run toward -Y."""
    plates = None
    for y in (-0.8, -4.9, -9.0):
        p = cq.Workplane("XZ").rect(12, 10).extrude(0.8).translate((0, y + 0.8, 0))
        plates = p if plates is None else plates.union(p)
    posts = None
    for sx in (-4.6, 4.6):
        for sz in (-3.6, 3.6):
            q = CY(1.6, 9, x=sx, z=sz, y0=-9)
            posts = q if posts is None else posts.union(q)
    gears = CY(7.5, 3.0, x=0, z=0, y0=-4.0).union(CY(5, 3.2, x=2.6, z=1.4, y0=-8.2)).union(CY(6, 3.0, x=-2.2, z=-1.2, y0=-8.0))
    can = CY(12, 15, y0=-24).intersect(B(13, 16, 10, cy=-16.5, z0=-5))
    cap = CY(11.2, 1.6, y0=-25.6).intersect(B(13, 4, 9.4, cy=-25, z0=-4.7))
    tabs = B(0.4, 2.5, 2.2, cx=-4, cy=-27, z0=-1.1).union(B(0.4, 2.5, 2.2, cx=4, cy=-27, z0=-1.1))
    shaft = CY(3, 10, y0=0).cut(B(4, 9, 2, cy=5.5, z0=1.0))
    boss = CY(4.2, 0.8, y0=0)
    return asm("motor_n20", [(plates, "brass"), (posts, "brass"), (gears, "steel"), (can, "steel"), (cap, "black"), (tabs, "gold"), (shaft, "steel"), (boss, "brass")])

def wheel(d, w, bore=3.0, spokes=6):
    """Origin: axle is +Y, wheel centred on Y=0."""
    rim = CY(d, w, y0=-w / 2).cut(CY(d - 5, w + 2, y0=-w / 2 - 1))
    disc = CY(d - 4.5, 2.4, y0=-1.2)
    for k in range(spokes):
        a = 2 * math.pi * k / spokes
        disc = disc.cut(CY(d * 0.2, 4, x=d * 0.27 * math.cos(a), z=d * 0.27 * math.sin(a), y0=-2))
    hub = CY(8, w - 2, y0=-(w - 2) / 2).cut(CY(bore, w + 2, y0=-w / 2 - 1))
    fl = CY(d + 1.5, 1.0, y0=-w / 2 - 1.0).cut(CY(d - 5, 3, y0=-w / 2 - 2)).union(CY(d + 1.5, 1.0, y0=w / 2).cut(CY(d - 5, 3, y0=w / 2 - 1)))
    return [(rim.union(disc).union(fl), "steel"), (hub, "dark")]

def track_set(wheelbase, d, w, t, bogies=3):
    """One track with drive wheel (rear, -X), idler (front, +X) and small road wheels. Origin: midway between axles, on the axle line, centred in width."""
    parts = []
    for x in (-wheelbase / 2, wheelbase / 2):
        for s, col in wheel(d, w - 4):
            parts.append((s.translate((x, 0, 0)), col))
    for k in range(bogies):
        x = -wheelbase / 2 + wheelbase * (k + 1) / (bogies + 1)
        bd = d * 0.5
        for s, col in wheel(bd, w - 6, spokes=4):
            parts.append((s.translate((x, 0, -(d - bd) / 2)), col))
    belt = (cq.Workplane("XZ").slot2D(wheelbase + d + 2 * t, d + 2 * t).extrude(-w)
            .cut(cq.Workplane("XZ").slot2D(wheelbase + d, d).extrude(-w - 2).translate((0, 1, 0))).translate((0, -w / 2, 0)))
    parts.append((belt, "rubber"))
    # tread lugs along the loop
    R = d / 2 + t; pitch = 7.0
    per = 2 * wheelbase + 2 * math.pi * R; n = int(per // pitch); lugs = []
    for i in range(n):
        s = i * per / n
        if s < wheelbase: x, z, ang = -wheelbase / 2 + s, R, 0
        elif s < wheelbase + math.pi * R:
            a = (s - wheelbase) / R; x, z, ang = wheelbase / 2 + R * math.sin(a), R * math.cos(a), math.degrees(a)
        elif s < 2 * wheelbase + math.pi * R: x, z, ang = wheelbase / 2 - (s - wheelbase - math.pi * R), -R, 180
        else:
            a = (s - 2 * wheelbase - math.pi * R) / R; x, z, ang = -wheelbase / 2 - R * math.sin(a), -R * math.cos(a), 180 + math.degrees(a)
        lug = cq.Workplane("XY").box(2.6, w, 1.6).translate((0, 0, 0.6)).rotate((0, 0, 0), (0, 1, 0), ang).translate((x, 0, z))
        lugs.append(lug.val())
    parts.append((cq.Workplane("XY").newObject([cq.Compound.makeCompound(lugs)]), "rubber"))
    return asm("track_set", parts)

def battery_2x18650():
    """Origin: centre of the holder footprint, Z=0 at the holder underside. Cells run along X."""
    tray = B(77, 41, 15).cut(B(73, 37, 15, z0=2)).union(B(73, 1.6, 13, z0=2))
    for sy in (-1, 1):
        tray = tray.cut(B(60, 3, 12, cy=sy * 20, z0=6))
    cells = CX(18.4, 65, y=-9.7, z=11.2, x0=-32.5).union(CX(18.4, 65, y=9.7, z=11.2, x0=-32.5))
    caps = None
    for sy in (-1, 1):
        for x0 in (-33.5, 32.5):
            c = CX(8 if (x0 > 0) == (sy > 0) else 17, 1.0, y=sy * 9.7, z=11.2, x0=x0)
            caps = c if caps is None else caps.union(c)
    springs = B(1.0, 12, 10, cx=-35.5, cy=-9.7, z0=5).union(B(1.0, 12, 10, cx=35.5, cy=9.7, z0=5)).union(B(1.0, 30, 10, cx=35.5, cy=-2, z0=5).intersect(B(2, 12, 12, cx=35.5, cy=-9.7, z0=4))).union(B(1.0, 12, 10, cx=-35.5, cy=9.7, z0=5))
    return asm("battery_2x18650", [(tray, "black"), (cells, "cell"), (caps, "steel"), (springs, "steel")])

def esp32_s3_devkit():
    """Origin: board centre, Z=0 at the board underside. Antenna end is +X, USB end is -X."""
    pcb = B(69, 25.4, 1.6).edges("|Z").fillet(1.0)
    shield = B(15.6, 17.6, 2.4, cx=14, z0=2.4)
    module = B(25.5, 18, 0.8, cx=21.5, z0=1.6)
    ant = B(5.5, 16, 0.1, cx=31.3, z0=2.4)
    usb = None
    for sy in (-7.2, 7.2):
        u = B(7.4, 8.9, 3.2, cx=-31, cy=sy, z0=1.6).edges("|X").fillet(1.2)
        usb = u if usb is None else usb.union(u)
    btn = B(3.5, 4, 1.6, cx=-22, cy=-7, z0=1.6).union(B(3.5, 4, 1.6, cx=-22, cy=7, z0=1.6)).union(B(3, 3, 1.4, cx=-8, z0=1.6)).union(B(5, 5, 1.0, cx=-15, cy=0, z0=1.6))
    led = B(1.6, 1.6, 0.8, cx=2, cy=6, z0=1.6)
    parts = [(pcb, "pcb_black"), (module, "pcb_black"), (shield, "steel"), (ant, "gold"), (usb, "steel"), (btn, "dark"), (led, "white")]
    for sy in (-11.43, 11.43):
        parts += header(22, cx=0.0, cy=sy, z0=0, along="x", down=True)
    return asm("esp32_s3_devkit", parts)

def lcd_2in():
    """2.0 inch ST7789 module, landscape. Origin: centre of the glass, screen faces +X, X=0 at the glass front."""
    pcb = B(1.6, 58, 35, cx=-3.4, z0=-17.5)
    glass = B(2.6, 48, 34.5, cx=-1.3, cy=-3, z0=-17.25)
    active = B(0.1, 40.8, 30.6, cx=0.02, cy=-3, z0=-15.3)
    flex = B(0.3, 6, 16, cx=-2.5, cy=23, z0=-8)
    parts = [(pcb, "pcb_blue"), (glass, "glass"), (active, "screen"), (flex, "copper")]
    hp = header(8, along="x")
    for s, col in hp:
        parts.append((s.rotate((0, 0, 0), (0, 1, 0), -90).translate((-4.2, 26.5, 0)), col))
    return asm("lcd_2in_st7789", parts)

def speaker_28mm():
    """Origin: centre of the front rim, sound comes out toward -X (magnet toward +X)."""
    rim = CX(28, 1.2, x0=0).cut(CX(24, 3, x0=-1))
    cone = cq.Workplane("YZ").circle(12).workplane(offset=4).circle(6).loft().translate((0.6, 0, 0))
    dome = CX(11, 0.8, x0=0.6)
    basket = CX(20, 2.5, x0=1.2)
    magnet = CX(15, 3.2, x0=3.7)
    lugs = B(1, 6, 3, cx=3, cy=11, z0=-1.5)
    return asm("speaker_28mm", [(rim, "steel"), (cone, "dark"), (dome, "black"), (basket, "steel"), (magnet, "grey"), (lugs, "gold")])

def tcrt5000_module():
    """Origin: centre of the sensor head on the PCB underside plane (Z=0); the sensor looks toward -Z. Board runs toward -Y."""
    pcb = B(14, 32, 1.6, cy=-11).cut(CZ(3.2, 4, cy=-10, z0=-1))
    head = B(10.2, 5.8, 6.3, z0=-6.3).edges("|Z").fillet(0.8)
    eyes = CZ(3.0, 1.0, cx=-2.6, z0=-7.0).union(CZ(3.0, 1.0, cx=2.6, z0=-7.0))
    pot = B(6.8, 6.8, 4.8, cy=-17, z0=1.6)
    screw = CZ(2.6, 0.6, cy=-17, z0=6.4)
    ic = B(5, 4, 1.5, cy=-8.5, z0=1.6)
    parts = [(pcb, "pcb_blue"), (head, "black"), (eyes, "pcb_blue"), (pot, "pcb_blue"), (screw, "brass"), (ic, "black")]
    for s, col in header(4, along="x"):
        parts.append((s.translate((0, -25.5, 1.6)), col))
    return asm("tcrt5000_module", parts)

def small_board(name, x, y, colour, chips, pins=None, hole=None, pins_down=False):
    """Generic small module. Origin: board centre, Z=0 underside. chips = [(sx, sy, sz, cx, cy, colour)]"""
    pcb = B(x, y, 1.6)
    if hole:
        for hx, hy in hole: pcb = pcb.cut(CZ(2.4, 4, cx=hx, cy=hy, z0=-1))
    parts = [(pcb, colour)]
    for sx, sy, sz, cx, cy, col in chips:
        parts.append((B(sx, sy, sz, cx=cx, cy=cy, z0=1.6), col))
    for n, cx, cy, along in (pins or []):
        for s, col in header(n, along=along, down=pins_down):
            parts.append((s.translate((cx, cy, 0 if pins_down else 1.6)), col))
    return asm(name, parts)

def tof200f():
    """Housed laser distance sensor (TOF200F). Origin: board centre, Z=0 underside, lens looks toward +Z, cable socket toward -X."""
    pcb = B(22, 18, 1.2)
    for hx in (-8.5, 8.5):
        for hy in (-6.5, 6.5): pcb = pcb.cut(CZ(2.2, 4, cx=hx, cy=hy, z0=-1))
    cover = B(12, 10, 3.4, cx=2, z0=1.2).edges("|Z").fillet(1.5)
    lens = B(7, 3.4, 0.4, cx=2, z0=4.6).edges("|Z").fillet(1.5)
    sock = B(4.2, 9.5, 3.6, cx=-8.6, z0=-3.6)
    return asm("distance_sensor_tof200f", [(pcb, "pcb_black"), (cover, "black"), (lens, "glass"), (sock, "white")])

def rocker_round():
    """Round rocker switch with wire leads (20 mm panel hole). Origin: centre of the bezel back face. Rocker toward -X, body toward +X."""
    body = CX(19.6, 16, x0=0)
    bezel = CX(23, 2, x0=-2)
    rock = CX(15, 2.2, x0=-3.6).rotate((-2.6, 0, 0), (-2.6, 1, 0), 8)
    tabs = B(7, 0.6, 4.8, cx=19.5, cy=-4, z0=-2.4).union(B(7, 0.6, 4.8, cx=19.5, cy=4, z0=-2.4))
    return asm("rocker_switch_round", [(body, "black"), (bezel, "black"), (rock, "red"), (tabs, "gold")])

def dc_jack_panel():
    """Panel DC socket 5.5 x 2.1 with wire leads (8 mm panel hole). Origin: centre of the flange back face. Plug enters from -X."""
    flange = CX(11, 1.6, x0=-1.6).cut(CX(6.2, 3, x0=-2))
    barrel = CX(7.8, 14, x0=0)
    nut = cq.Workplane("YZ").polygon(6, 12.5).extrude(2.2).translate((3.2, 0, 0)).cut(CX(7.8, 4, x0=3))
    pin = CX(2.0, 9, x0=-1)
    tails = B(5, 0.5, 2.4, cx=16.5, cy=-2, z0=-1.2).union(B(5, 0.5, 2.4, cx=16.5, cy=2, z0=-1.2))
    return asm("charging_socket_dc", [(flange, "black"), (barrel, "black"), (nut, "steel"), (pin, "steel"), (tails, "gold")])

def main_board_v02():
    """Simplified model of the v0.2 main board (placeholder until the routed board is exported from KiCad).
    Origin: board top-left corner as in KiCad, X right, Y toward -Y (KiCad y is negated), Z=0 underside."""
    def k(x, y): return (x, -y)
    pcb = B(100, 70, 1.6, cx=50, cy=-35)
    for hx in (4, 96):
        for hy in (4, 66): pcb = pcb.cut(CZ(3.2, 4, cx=hx, cy=-hy, z0=-1))
    parts = [(pcb, "pcb_green")]
    sock = None
    for y in (22.86, 45.72, 48.26):                       # dev board sockets (3 rows of 22)
        s = B(2.54 * 22, 2.5, 8.5, cx=71.12 - 2.54 * 10.5, cy=-y, z0=1.6)
        sock = s if sock is None else sock.union(s)
    parts.append((sock, "black"))
    def hdr(n, x, y, along="x"):
        cx = x + (2.54 * (n - 1) / 2 if along == "x" else 0); cy = y + (2.54 * (n - 1) / 2 if along == "y" else 0)
        for s, col in header(n, along=along):
            parts.append((s.translate((cx, -cy, 1.6)), col))
    for i in range(4): hdr(3, 10.16 + 10.16 * i, 5.08)   # edge sensors
    hdr(4, 50.8, 5.08); hdr(4, 63.5, 5.08)                # eye, spare
    hdr(8, 55.88, 13.97)                                  # face LCD
    for i in range(4): hdr(3, 10.16 + 2.54 * i, 58.42, along="y")   # servos
    hdr(3, 23.5, 63.5); hdr(3, 58.42, 63.5)               # button, fin LED
    blocks = None; screws = None
    def term(x, y, right):
        nonlocal blocks, screws
        blk = B(7.6, 10.16, 10.0, cx=x, cy=-(y + 2.54), z0=1.6)
        for d in (0, 5.08):
            blk = blk.cut(B(4.0, 3.6, 4.2, cx=x + (2.8 if right else -2.8), cy=-(y + d), z0=3.0)).cut(CZ(3.4, 3, cx=x, cy=-(y + d), z0=9.2))
            sc = CZ(3.0, 0.6, cx=x, cy=-(y + d), z0=8.9); screws = sc if screws is None else screws.union(sc)
        blocks = blk if blocks is None else blocks.union(blk)
    for y in (13.97, 26.67, 39.37): term(92.71, y, True)      # battery, charger, switch
    for y in (20.32, 30.48, 40.64): term(6.35, y, False)      # motor L, motor R, speaker
    parts += [(blocks, "pcb_blue"), (screws, "steel")]
    caps = CZ(8, 10.2, cx=70.2, cy=-58.6, z0=1.6).union(CZ(8, 10.2, cx=83.4, cy=-58.6, z0=1.6))
    parts.append((caps, "steel"))
    chips = B(5, 4.4, 1.1, cx=26, cy=-34.3, z0=1.6).union(B(3, 3, 0.8, cx=42.5, cy=-34.3, z0=1.6)).union(B(2.9, 1.6, 1.1, cx=40, cy=-58, z0=1.6)).union(B(4.5, 3.2, 1.2, cx=80.6, cy=-20, z0=1.6)).union(B(4.3, 2.6, 2.2, cx=80.6, cy=-44, z0=1.6))
    parts.append((chips, "black"))
    parts.append((B(5, 5, 4, cx=46.6, cy=-58.6, z0=1.6), "dark"))
    parts.append((B(3.5, 2.65, 1.0, cx=27, cy=-14.6, z0=1.6), "steel"))
    return asm("main_board_v02", parts)
