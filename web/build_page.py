"""Builds the Dimer build-plan web page (web/dimer_build_plan.html) and docs/ASSEMBLY.md.

Run:  python cad/dimer_frame.py web/mesh.json && python web/build_page.py
The assembly steps below are the single source for the page, the 3D step player and the Markdown guide.
"""
import html, json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
REPO = "https://github.com/whatsoeveroo/dimer/blob/main/"
ALI = "https://www.aliexpress.com/item/%s.html"

# ---------------------------------------------------------------- parts shown in the 3D view
PARTS = [  # (mesh name, label, group)
    ("frame_chassis", "Chassis tub", "Printed frame"),
    ("frame_neck_bridge", "Neck bridge", "Printed frame"),
    ("frame_head", "Head box", "Printed frame"),
    ("frame_shovel", "Shovel", "Printed frame"),
    ("part_motor_left", "Motor, left", "Drive"),
    ("part_motor_right", "Motor, right", "Drive"),
    ("part_track_left", "Track, left", "Drive"),
    ("part_track_right", "Track, right", "Drive"),
    ("part_servo_shovel", "Shovel servo", "Motion"),
    ("part_servo_pan", "Head servo", "Motion"),
    ("part_main_pcb", "Main board", "Electronics"),
    ("part_esp32_s3_devkit", "ESP32-S3 brain", "Electronics"),
    ("part_battery", "Battery holder", "Electronics"),
    ("part_power_switch", "Power switch", "Electronics"),
    ("part_charging_socket", "Charging socket", "Electronics"),
    ("part_speaker", "Speaker", "Electronics"),
    ("part_face_display", "Face display", "Head"),
    ("part_distance_sensor", "Distance sensor", "Head"),
    ("part_edge_sensor_front_left", "Edge sensor FL", "Edge sensors"),
    ("part_edge_sensor_front_right", "Edge sensor FR", "Edge sensors"),
    ("part_edge_sensor_rear_left", "Edge sensor RL", "Edge sensors"),
    ("part_edge_sensor_rear_right", "Edge sensor RR", "Edge sensors"),
]

# ---------------------------------------------------------------- assembly steps
# (title, one-line summary, [detail bullets], [mesh names added in this step], camera (az, el, dist))
STEPS = [
    ("Lay out the parts and tools",
     "Check every part against the buying list before you start.",
     ["Tools: a 2 mm hex key (for the M3 screws), a small flat screwdriver (for the screw terminals), a small cross-head screwdriver (for the tiny servo screws), scissors, and tape for labelling wires.",
      "Leave the two battery cells in their box. They go in last, at step 12.",
      "Keep the main board in its bag until step 6. Touch a metal tap or radiator before handling it, to drain static.",
      "The printed frame is a rough guideline. A few parts are held with double-sided tape for now. Each step says so where that is the case."],
     ["frame_chassis"], (-0.95, 0.42, 520)),
    ("Fit the two drive motors",
     "Press each motor into its cradle at the back of the tub, shaft pointing out through the wall.",
     ["The cradles are the two blocks at the rear, one on each side. The gearbox end (brass) sits in the slot and the shaft goes out through the 4 mm hole in the side wall.",
      "The cable plug on the back of each motor points toward the middle of the tub. Plug the 6-wire cable into each motor now.",
      "If a motor is loose in its cradle, put a strip of double-sided tape under it.",
      "Put a piece of tape on each cable and write L (left) and R (right) on it. Left and right are as seen from behind the robot, looking forward."],
     ["part_motor_left", "part_motor_right"], (-2.2, 0.75, 430)),
    ("Fit the shovel servo",
     "The servo sits inside the left wall near the front, with its shaft poking out through the rectangular opening.",
     ["Use one of the four blue MG90S servos. Do not screw a horn (the white plastic arm) onto it yet.",
      "Push the servo's shaft end through the opening from the inside. The servo cable runs back toward the middle of the tub.",
      "Fixing: the guideline frame has no screw holes for this servo yet. Hold it with double-sided tape against the wall for the first test.",
      "Label its cable SHVL."],
     ["part_servo_shovel"], (0.9, 0.7, 430)),
    ("Mount the four table-edge sensors",
     "One sensor on each corner tab, black sensor head pointing down at the table.",
     ["First plug three jumper wires onto the three pins of each sensor (VCC, GND, DO). Use the same three colours on every sensor so you can tell them apart later, for example red on VCC, black on GND, yellow on DO.",
      "Fix each sensor on its corner tab with one M3 screw from below and a nut on top, through the hole in the sensor board.",
      "Label each bundle of wires: FL (front left), FR (front right), RL (rear left), RR (rear right).",
      "Lead the wires up over the wall into the tub."],
     ["part_edge_sensor_front_left", "part_edge_sensor_front_right", "part_edge_sensor_rear_left", "part_edge_sensor_rear_right"], (-0.6, 0.95, 520)),
    ("Fit the speaker, power switch and charging socket",
     "All three go on the rear wall: speaker behind the grille holes, switch in the big round hole, charging socket in the small round hole.",
     ["Speaker: cone facing the grille holes, from inside. Hold it with a ring of double-sided tape around the rim. Do not press on the cone.",
      "Power switch: push it into the 20 mm hole from the outside until it clicks. Its two wires end up inside the tub.",
      "Charging socket: unscrew its nut, push the socket through the 8 mm hole from the outside, and tighten the nut on the inside.",
      "Measure your real switch and socket first. If they differ from 20 mm and 8 mm, tell me and I change the two numbers in the frame script."],
     ["part_speaker", "part_power_switch", "part_charging_socket"], (-2.6, 0.45, 430)),
    ("Place the battery holder",
     "The empty holder sits on the floor in the middle of the tub. No cells yet.",
     ["Stick it down with double-sided tape, wires pointing toward the front of the robot.",
      "Check the holder is empty. The cells stay out until step 12."],
     ["part_battery"], (-0.95, 1.0, 460)),
    ("Screw down the main board",
     "The board sits on the four posts above the battery, held by four M3 screws.",
     ["Orientation: the three blue screw terminals marked BATTERY, CHARGER and SWITCH face the front of the robot. The corner printed DIMER MAIN is front right.",
      "Before lowering the board, lead these wires up past its edges so they are not trapped: both motor cables and the speaker cable at the back, the battery, switch and charging-socket wires at the front, and the servo and sensor wires at the sides.",
      "Use four M3 x 8 mm screws straight into the plastic posts. Stop when the screw feels firm. Over-tightening strips the plastic."],
     ["part_main_pcb"], (-0.95, 0.9, 460)),
    ("Connect the screw terminals",
     "Six pairs of wires clamp into the six blue terminals. This is the only wiring that needs a screwdriver.",
     ["How a screw terminal works: turn the screw anticlockwise until the metal jaw opens, push 6 mm of bare wire into the side opening, tighten the screw, then pull gently on the wire to check it holds.",
      "Speaker and motor cables end in small plugs that do not fit. Cut the plug off with scissors and strip 6 mm of insulation from each wire. To strip: pinch the insulation lightly with the scissors, turn once around the wire, and pull the end off.",
      "MOTOR L and MOTOR R (rear edge): each motor cable has 6 wires. Only the two motor wires are used, usually the two outer ones, marked M1 and M2 or M+ and M- on the motor's little board. Clamp one in each side of the terminal. Tape the four unused wires back so they cannot touch anything. If a track later runs backwards, swap these two wires.",
      "SPEAKER (rear edge): the two speaker wires, either way round.",
      "SWITCH (front edge): the two switch wires, either way round.",
      "CHARGER (front edge): the charging-socket wires. Red to +, black to -.",
      "BATTERY (front edge): the holder wires. Red to +, black to -. Do this one last, and check again that the holder is empty.",
      "Lengths: the switch and charging-socket wires need about 13 cm to reach from the rear wall to the front edge of the board. If yours are shorter, stop and tell me."],
     [], (-0.95, 1.2, 380)),
    ("Fit the neck bridge and head servo",
     "The bridge is the flat plate across the front of the tub. The head servo hangs in its cut-out with the shaft pointing up.",
     ["Drop a servo into the rectangular cut-out from above so its two ears rest on the plate. Fix it with the two small screws from the servo bag.",
      "Lay the plate across the tub walls and fix it with four M3 screws at its corners.",
      "Lead the servo cable back to the board and label it PAN."],
     ["frame_neck_bridge", "part_servo_pan"], (0.6, 0.8, 460)),
    ("Build the head",
     "The display sits behind the big window, the distance sensor behind the small window below it.",
     ["Display: plug eight jumper wires onto its eight pins first. Use the wires as a strip of eight still joined together, so the order stays the same at both ends. Then place the display behind the window, screen facing out, and hold it with tape at its corners.",
      "Distance sensor: plug in its cable, then fix the sensor behind the small window with two of the tiny screws left over in the servo bags, lens facing out.",
      "Lead both cables out through the slot in the head floor.",
      "Push a servo horn onto the head servo shaft, set the head box on it facing forward, and fix it through the round hole in the head floor with the horn screw. Do not turn the servo by hand more than gently."],
     ["frame_head", "part_face_display", "part_distance_sensor"], (0.35, 0.5, 430)),
    ("Plug in the sensors, display and servos",
     "Every remaining wire pushes onto a labelled pin on the board. Match the printed names, not the positions.",
     ["EDGE FL, FR, RL, RR (along the left edge of the board): three pins each, printed 3V3, GND, DO. The sensor's VCC wire goes to 3V3, GND to GND, DO to DO.",
      "EYE (I2C): the distance sensor. Its cable has six wires and only four are used. The names are printed on the sensor: VIN goes to 3V3, GND to GND, SCL to SCL, SDA to SDA. Leave the other two free.",
      "FACE LCD: eight pins printed GND, VCC, SCL, SDA, RES, DC, CS, BLK, the same names and order as on the display. The strip of eight wires goes straight across.",
      "SERVOS: the servo plugs fit directly. The brown wire goes to the pin row printed GND, the orange wire to SIG. Head servo on PAN, shovel servo on SHVL.",
      "Wrong way round on a 3-pin plug can damage a sensor, so read the printed names twice before pushing each plug on."],
     [], (-0.95, 1.2, 380)),
    ("Plug in the brain",
     "The ESP32-S3 board pushes into the two long black socket rows in the middle of the main board.",
     ["The USB sockets point to the rear of the robot, where the board is printed USB END. The metal can with the antenna points to the front.",
      "The board has three socket rows because ESP32 boards come in two widths. Use the top row and whichever of the two lower rows lines up with your board's pins.",
      "Line up all pins, check none is hanging outside the socket at either end, then press down evenly with two thumbs."],
     ["part_esp32_s3_devkit"], (-0.95, 0.9, 420)),
    ("First power-on",
     "Switch off, insert the two cells, switch on, and look for the small light on the brain.",
     ["Set the switch to off (O).",
      "Insert the two protected 18650 cells the way the + and - marks in the holder show. The flat end of each cell goes against a spring.",
      "Switch on. A small light on the ESP32 board should come on within a second.",
      "If nothing lights, or anything gets warm or smells, switch off straight away, take one cell out and tell me what you saw. The board has a fuse and a reverse-polarity diode, so a swapped battery wire should not destroy it.",
      "To charge: switch off and plug the 8.4 V charger into the charging socket. The charger's light turns green when the cells are full. Never leave charging cells unattended."],
     [], (-0.95, 0.42, 520)),
    ("Fit the tracks and the shovel",
     "Wheels and tracks go on the outside, then the shovel hooks onto its servo.",
     ["Tracks: this step depends on the track set you choose, and the fit on the 3 mm motor shaft is not settled yet. I will write this step properly once the set is picked.",
      "Shovel: the left arm fixes to a servo horn on the shovel servo, the right arm turns on an M3 screw through the hole in the right wall.",
      "After this the mechanical build is done and the next job is the first test program."],
     ["part_track_left", "part_track_right", "frame_shovel"], (-0.95, 0.42, 520)),
]

# ---------------------------------------------------------------- buying list
BUY = [  # (group, part, why, option, qty, price, link, checked)
    ("Brain", "ESP32-S3 DevKitC-1 N16R8", "The robot's computer, with Wi-Fi.", "ESP32-S3 soldered", "1", "₩4,080", ALI % "1005006240070551", "Pins already soldered"),
    ("Face", "2.0 inch IPS display, ST7789, 8 pins", "The face.", "only one option", "1", "₩3,480", ALI % "1005002363748586", "8 pins already soldered"),
    ("Senses", "TCRT5000 table-edge sensor", "One per corner, looking down.", "4PCS", "1", "₩2,472", ALI % "1005008965242714", "Pins already soldered"),
    ("", "TOF200F distance sensor with cable", "Sits in the head and measures what is in front.", "TOF0200F", "1", "₩9,506", ALI % "1005008657721399", "Cable ends in jumper sockets"),
    ("Drive", "N20 gear motor with encoder and cable", "Two track motors. The cable saves soldering.", "6 V, 100 rpm", "2", "₩16,284", ALI % "1005007886406269", "Cable included"),
    ("", "Track and wheel set", "Choose by eye. Do not order yet, see the note.", "", "1", "₩7,770 or ₩11,350", ALI % "1005012018149833", "Fit on 3 mm shaft not settled"),
    ("Motion", "MG90S metal-gear servo, 4 pieces", "Head and shovel, two spare.", "only one option", "1", "₩11,477", ALI % "4001193413905", ""),
    ("Voice", "Speaker 28 mm, 4 ohm, with cable, 2 pieces", "The voice. Microphone and amplifier are on the main board.", "4 ohm", "1", "₩11,650", ALI % "1005009922386828", "Cable attached"),
    ("Power", "Battery holder, 2 x 18650, with wires", "Holds the two cells.", "2X", "1", "₩454", ALI % "1005004429543070", "Leads attached"),
    ("", "Charger 8.4 V 1 A, 5.5 x 2.1 mm plug", "Charges the two cells through the socket.", "EU plug", "1", "₩6,100", ALI % "1005001803376849", ""),
    ("", "Charging socket, panel DC jack with cable, 2 pieces", "Goes in the rear wall.", "5.5 x 2.1", "1", "₩2,835", ALI % "1005012665509644", "Wires attached"),
    ("", "Round rocker switch with wires", "On and off.", "1PC", "1", "₩1,494", ALI % "1005012714169914", "Leads attached"),
    ("Wiring", "Jumper wires, female to female, 20 cm, 40 pieces", "Plug-in wires from the board to sensors and display.", "F-F(20CM) 40PCS", "1", "₩1,997", ALI % "1005006205169394", ""),
    ("Hardware", "M3 button-head screw kit with nuts", "Holds frame, board and shell together.", "M3 x 392pcs", "1", "about ₩7,000", ALI % "1005007278965396", "Check price after picking the option"),
]

def esc(s): return html.escape(s, quote=True)

def steps_html():
    out = []
    for i, (title, summary, bullets, _, _) in enumerate(STEPS):
        out.append('<details class="step" id="step-%d"%s><summary><span class="n">%d</span><span class="t"><b>%s</b><span>%s</span></span></summary><ul>%s</ul><button class="see" data-step="%d">Show this step in 3D</button></details>'
                   % (i, " open" if i == 0 else "", i, esc(title), esc(summary), "".join("<li>%s</li>" % esc(b) for b in bullets), i))
    return "\n".join(out)

def buy_html():
    rows = []
    for g, part, why, opt, qty, price, link, chk in BUY:
        rows.append('<tr><td class="grp">%s</td><td><strong>%s</strong><span class="why">%s</span>%s</td><td>%s</td><td class="num">%s</td><td class="num">%s</td><td><a href="%s">Product page</a>%s</td></tr>'
                    % (esc(g), esc(part), esc(why), '<span class="ok">%s</span>' % esc(chk) if chk else "", esc(opt), qty, price, link,
                       ' · <a href="%s">second option</a>' % (ALI % "1005010530113079") if part.startswith("Track") else ""))
    return "\n".join(rows)

def parts_html():
    out, groups = [], []
    for name, label, grp in PARTS:
        if grp not in groups: groups.append(grp)
    for grp in groups:
        chips = "".join('<label class="chip"><input type="checkbox" id="vis-%s" data-part="%s" checked><span>%s</span></label>' % (n, n, esc(l)) for n, l, g in PARTS if g == grp)
        out.append('<div class="pgroup"><span class="pg">%s</span>%s</div>' % (esc(grp), chips))
    return "".join(out)

def board_svg():
    """Top view of the v0.2 board: where each plug and wire goes. Coordinates in mm, drawn at 8 px per mm."""
    S = 8
    def r(x, y, w, h, cls, rx=0.6): return '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%.1f" class="%s"/>' % (x * S, y * S, w * S, h * S, rx * S, cls)
    def t(x, y, s, cls="lb", rot=0, anchor="middle"):
        tr = ' transform="rotate(%d %.1f %.1f)"' % (rot, x * S, y * S) if rot else ""
        return '<text x="%.1f" y="%.1f" class="%s" text-anchor="%s"%s>%s</text>' % (x * S, y * S, cls, anchor, tr, esc(s))
    o = ['<svg viewBox="-150 -40 1100 660" role="img" aria-label="Top view of the main board showing where each part plugs in">']
    o.append(r(0, 0, 100, 70, "bd", 3))
    for hx in (4, 96):
        for hy in (4, 66): o.append('<circle cx="%d" cy="%d" r="13" class="hole"/>' % (hx * S, hy * S))
    for i, nm in enumerate(["FL", "FR", "RL", "RR"]):
        x = 10.16 + 10.16 * i
        o.append(r(x - 1.3, 3.8, 7.7, 2.6, "hd")); o.append(t(x + 2.54, 2.6, "EDGE " + nm))
    o.append(r(50.8 - 1.3, 3.8, 10.2, 2.6, "hd")); o.append(t(50.8 + 3.8, 2.6, "EYE"))
    o.append(r(63.5 - 1.3, 3.8, 10.2, 2.6, "hd dim")); o.append(t(63.5 + 3.8, 2.6, "SPARE", "lb dimt"))
    o.append(r(55.88 - 1.3, 12.7, 20.4, 2.6, "hd")); o.append(t(55.88 + 8.9, 11.6, "FACE LCD"))
    for y in (22.86, 45.72, 48.26): o.append(r(71.12 - 2.54 * 21 - 1.3, y - 1.3, 2.54 * 22, 2.6, "sk"))
    o.append(r(16.5, 25.2, 57, 19.2, "esp", 1)); o.append(t(45, 34, "ESP32-S3 brain plugs in here", "big")); o.append(t(19, 38.5, "USB end", "lb", 0, "start")); o.append(t(71, 38.5, "antenna end", "lb", 0, "end"))
    for i, nm in enumerate(["TILT", "PAN", "AUX", "SHVL"]):
        x = 10.16 + 2.54 * i
        o.append(r(x - 1.1, 57.2, 2.2, 7.6, "hd" if nm in ("PAN", "SHVL") else "hd dim"))
        o.append(t(x + 0.5, 56.4, nm, "lb" if nm in ("PAN", "SHVL") else "lb dimt", -90, "start"))
    o.append(t(13.97, 67.6, "SERVOS"))
    o.append(r(23.5 - 1.3, 62.2, 7.7, 2.6, "hd dim")); o.append(t(27, 67.6, "BUTTON", "lb dimt"))
    o.append(r(58.42 - 1.3, 62.2, 7.7, 2.6, "hd dim")); o.append(t(62, 67.6, "FIN LED", "lb dimt"))
    o.append('<circle cx="%.1f" cy="%.1f" r="9" class="mic"/>' % (27 * S, 14.6 * S)); o.append(t(27, 18.6, "MIC"))
    for y, nm in ((13.97, "BATTERY"), (26.67, "CHARGER"), (39.37, "SWITCH")):
        o.append(r(88.9, y - 2.54, 7.6, 10.16, "tb")); o.append(t(104, y + 3.4, nm, "out", 0, "start"))
        for d in (0, 5.08): o.append('<circle cx="%.1f" cy="%.1f" r="11" class="scr"/>' % (92.71 * S, (y + d) * S))
        if nm != "SWITCH": o.append(t(87.2, y + 0.9, "+", "pm")); o.append(t(87.2, y + 6, "−", "pm"))
    for y, nm in ((20.32, "MOTOR L"), (30.48, "MOTOR R"), (40.64, "SPEAKER")):
        o.append(r(2.55, y - 2.54, 7.6, 10.16, "tb")); o.append(t(-4, y + 3.4, nm, "out", 0, "end"))
        for d in (0, 5.08): o.append('<circle cx="%.1f" cy="%.1f" r="11" class="scr"/>' % (6.35 * S, (y + d) * S))
    o.append('<circle cx="%.1f" cy="%.1f" r="32" class="cap"/><circle cx="%.1f" cy="%.1f" r="32" class="cap"/>' % (70.2 * S, 58.6 * S, 83.4 * S, 58.6 * S))
    o.append(t(50, -2.2, "← rear of robot          front of robot →", "out"))
    o.append("</svg>")
    return "".join(o)

def assembly_md():
    L = ["# Dimer assembly guideline (v0.2, no soldering)", "",
         "The short version. The web page has the same steps with a 3D view of each one.", "",
         "Rule one: the two battery cells go in last, at step 12.", ""]
    for i, (title, summary, bullets, _, _) in enumerate(STEPS):
        L.append("## %d. %s" % (i, title)); L.append(""); L.append(summary); L.append("")
        for b in bullets: L.append("- " + b)
        L.append("")
    L += ["## Where each wire goes", "",
          "| Board label | What connects | How |", "|---|---|---|",
          "| MOTOR L, MOTOR R | The two motor wires of each track motor | Screw terminal, rear edge |",
          "| SPEAKER | Speaker, two wires | Screw terminal, rear edge |",
          "| BATTERY | Battery holder, red to +, black to - | Screw terminal, front edge |",
          "| CHARGER | Charging socket, red to +, black to - | Screw terminal, front edge |",
          "| SWITCH | Power switch, two wires | Screw terminal, front edge |",
          "| EDGE FL, FR, RL, RR | Table-edge sensors: VCC to 3V3, GND to GND, DO to DO | 3 jumper wires each |",
          "| EYE (I2C) | Distance sensor: VIN to 3V3, GND, SCL, SDA | Its own cable |",
          "| FACE LCD | Display, 8 wires straight across | 8 jumper wires |",
          "| SERVOS: PAN, SHVL | Head servo, shovel servo. Brown wire on GND | Servo plug fits directly |",
          "| Socket rows | ESP32-S3 board, USB end to the rear | Push in |", ""]
    return "\n".join(L)

TEMPLATE = open(os.path.join(HERE, "template.html"), encoding="utf8").read()
mesh = open(os.path.join(HERE, "mesh.json"), encoding="utf8").read()
steps_js = json.dumps([{"title": s[0], "summary": s[1], "add": s[3], "cam": s[4]} for s in STEPS], ensure_ascii=False)
page = (TEMPLATE.replace("{{STEPS_HTML}}", steps_html()).replace("{{BUY_ROWS}}", buy_html()).replace("{{PARTS_HTML}}", parts_html())
        .replace("{{BOARD_SVG}}", board_svg()).replace("{{STEPS_JSON}}", steps_js).replace("{{NSTEPS}}", str(len(STEPS) - 1))
        .replace("{{MESH_JSON}}", mesh))
assert "{{" not in re.sub(r"\{\{\s*\}\}", "", page[:page.index("var MESH")]), "unfilled placeholder"
open(os.path.join(HERE, "dimer_build_plan.html"), "w", encoding="utf8").write(page)
open(os.path.join(ROOT, "docs", "ASSEMBLY.md"), "w", encoding="utf8").write(assembly_md())
print("page bytes:", len(page.encode("utf8")), "steps:", len(STEPS))
