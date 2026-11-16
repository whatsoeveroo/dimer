# Dimer assembly guideline (v0.2, no soldering)

The short version. The web page has the same steps with a 3D view of each one.

Rule one: the two battery cells go in last, at step 12.

## 0. Lay out the parts and tools

Check every part against the buying list before you start.

- Tools: a 2 mm hex key (for the M3 screws), a small flat screwdriver (for the screw terminals), a small cross-head screwdriver (for the tiny servo screws), scissors, and tape for labelling wires.
- Leave the two battery cells in their box. They go in last, at step 12.
- Keep the main board in its bag until step 6. Touch a metal tap or radiator before handling it, to drain static.
- The printed frame is a rough guideline. A few parts are held with double-sided tape for now. Each step says so where that is the case.

## 1. Fit the two drive motors

Press each motor into its cradle at the back of the tub, shaft pointing out through the wall.

- The cradles are the two blocks at the rear, one on each side. The gearbox end (brass) sits in the slot and the shaft goes out through the 4 mm hole in the side wall.
- The cable plug on the back of each motor points toward the middle of the tub. Plug the 6-wire cable into each motor now.
- If a motor is loose in its cradle, put a strip of double-sided tape under it.
- Put a piece of tape on each cable and write L (left) and R (right) on it. Left and right are as seen from behind the robot, looking forward.

## 2. Fit the shovel servo

The servo sits inside the left wall near the front, with its shaft poking out through the rectangular opening.

- Use one of the four blue MG90S servos. Do not screw a horn (the white plastic arm) onto it yet.
- Push the servo's shaft end through the opening from the inside. The servo cable runs back toward the middle of the tub.
- Fixing: the guideline frame has no screw holes for this servo yet. Hold it with double-sided tape against the wall for the first test.
- Label its cable SHVL.

## 3. Mount the four table-edge sensors

One sensor on each corner tab, black sensor head pointing down at the table.

- First plug three jumper wires onto the three pins of each sensor (VCC, GND, DO). Use the same three colours on every sensor so you can tell them apart later, for example red on VCC, black on GND, yellow on DO.
- Fix each sensor on its corner tab with one M3 screw from below and a nut on top, through the hole in the sensor board.
- Label each bundle of wires: FL (front left), FR (front right), RL (rear left), RR (rear right).
- Lead the wires up over the wall into the tub.

## 4. Fit the speaker, power switch and charging socket

All three go on the rear wall: speaker behind the grille holes, switch in the big round hole, charging socket in the small round hole.

- Speaker: cone facing the grille holes, from inside. Hold it with a ring of double-sided tape around the rim. Do not press on the cone.
- Power switch: push it into the 20 mm hole from the outside until it clicks. Its two wires end up inside the tub.
- Charging socket: unscrew its nut, push the socket through the 8 mm hole from the outside, and tighten the nut on the inside.
- Measure your real switch and socket first. If they differ from 20 mm and 8 mm, tell me and I change the two numbers in the frame script.

## 5. Place the battery holder

The empty holder sits on the floor in the middle of the tub. No cells yet.

- Stick it down with double-sided tape, wires pointing toward the front of the robot.
- Check the holder is empty. The cells stay out until step 12.

## 6. Screw down the main board

The board sits on the four posts above the battery, held by four M3 screws.

- Orientation: the three blue screw terminals marked BATTERY, CHARGER and SWITCH face the front of the robot. The corner printed DIMER MAIN is front right.
- Before lowering the board, lead these wires up past its edges so they are not trapped: both motor cables and the speaker cable at the back, the battery, switch and charging-socket wires at the front, and the servo and sensor wires at the sides.
- Use four M3 x 8 mm screws straight into the plastic posts. Stop when the screw feels firm. Over-tightening strips the plastic.

## 7. Connect the screw terminals

Six pairs of wires clamp into the six blue terminals. This is the only wiring that needs a screwdriver.

- How a screw terminal works: turn the screw anticlockwise until the metal jaw opens, push 6 mm of bare wire into the side opening, tighten the screw, then pull gently on the wire to check it holds.
- Speaker and motor cables end in small plugs that do not fit. Cut the plug off with scissors and strip 6 mm of insulation from each wire. To strip: pinch the insulation lightly with the scissors, turn once around the wire, and pull the end off.
- MOTOR L and MOTOR R (rear edge): each motor cable has 6 wires. Only the two motor wires are used, usually the two outer ones, marked M1 and M2 or M+ and M- on the motor's little board. Clamp one in each side of the terminal. Tape the four unused wires back so they cannot touch anything. If a track later runs backwards, swap these two wires.
- SPEAKER (rear edge): the two speaker wires, either way round.
- SWITCH (front edge): the two switch wires, either way round.
- CHARGER (front edge): the charging-socket wires. Red to +, black to -.
- BATTERY (front edge): the holder wires. Red to +, black to -. Do this one last, and check again that the holder is empty.
- Lengths: the switch and charging-socket wires need about 13 cm to reach from the rear wall to the front edge of the board. If yours are shorter, stop and tell me.

## 8. Fit the neck bridge and head servo

The bridge is the flat plate across the front of the tub. The head servo hangs in its cut-out with the shaft pointing up.

- Drop a servo into the rectangular cut-out from above so its two ears rest on the plate. Fix it with the two small screws from the servo bag.
- Lay the plate across the tub walls and fix it with four M3 screws at its corners.
- Lead the servo cable back to the board and label it PAN.

## 9. Build the head

The display sits behind the big window, the distance sensor behind the small window below it.

- Display: plug eight jumper wires onto its eight pins first. Use the wires as a strip of eight still joined together, so the order stays the same at both ends. Then place the display behind the window, screen facing out, and hold it with tape at its corners.
- Distance sensor: plug in its cable, then fix the sensor behind the small window with two of the tiny screws left over in the servo bags, lens facing out.
- Lead both cables out through the slot in the head floor.
- Push a servo horn onto the head servo shaft, set the head box on it facing forward, and fix it through the round hole in the head floor with the horn screw. Do not turn the servo by hand more than gently.

## 10. Plug in the sensors, display and servos

Every remaining wire pushes onto a labelled pin on the board. Match the printed names, not the positions.

- EDGE FL, FR, RL, RR (along the left edge of the board): three pins each, printed 3V3, GND, DO. The sensor's VCC wire goes to 3V3, GND to GND, DO to DO.
- EYE (I2C): the distance sensor. Its cable has six wires and only four are used. The names are printed on the sensor: VIN goes to 3V3, GND to GND, SCL to SCL, SDA to SDA. Leave the other two free.
- FACE LCD: eight pins printed GND, VCC, SCL, SDA, RES, DC, CS, BLK, the same names and order as on the display. The strip of eight wires goes straight across.
- SERVOS: the servo plugs fit directly. The brown wire goes to the pin row printed GND, the orange wire to SIG. Head servo on PAN, shovel servo on SHVL.
- Wrong way round on a 3-pin plug can damage a sensor, so read the printed names twice before pushing each plug on.

## 11. Plug in the brain

The ESP32-S3 board pushes into the two long black socket rows in the middle of the main board.

- The USB sockets point to the rear of the robot, where the board is printed USB END. The metal can with the antenna points to the front.
- The board has three socket rows because ESP32 boards come in two widths. Use the top row and whichever of the two lower rows lines up with your board's pins.
- Line up all pins, check none is hanging outside the socket at either end, then press down evenly with two thumbs.

## 12. First power-on

Switch off, insert the two cells, switch on, and look for the small light on the brain.

- Set the switch to off (O).
- Insert the two protected 18650 cells the way the + and - marks in the holder show. The flat end of each cell goes against a spring.
- Switch on. A small light on the ESP32 board should come on within a second.
- If nothing lights, or anything gets warm or smells, switch off straight away, take one cell out and tell me what you saw. The board has a fuse and a reverse-polarity diode, so a swapped battery wire should not destroy it.
- To charge: switch off and plug the 8.4 V charger into the charging socket. The charger's light turns green when the cells are full. Never leave charging cells unattended.

## 13. Fit the tracks and the shovel

Wheels and tracks go on the outside, then the shovel hooks onto its servo.

- Tracks: this step depends on the track set you choose, and the fit on the 3 mm motor shaft is not settled yet. I will write this step properly once the set is picked.
- Shovel: the left arm fixes to a servo horn on the shovel servo, the right arm turns on an M3 screw through the hole in the right wall.
- After this the mechanical build is done and the next job is the first test program.

## Where each wire goes

| Board label | What connects | How |
|---|---|---|
| MOTOR L, MOTOR R | The two motor wires of each track motor | Screw terminal, rear edge |
| SPEAKER | Speaker, two wires | Screw terminal, rear edge |
| BATTERY | Battery holder, red to +, black to - | Screw terminal, front edge |
| CHARGER | Charging socket, red to +, black to - | Screw terminal, front edge |
| SWITCH | Power switch, two wires | Screw terminal, front edge |
| EDGE FL, FR, RL, RR | Table-edge sensors: VCC to 3V3, GND to GND, DO to DO | 3 jumper wires each |
| EYE (I2C) | Distance sensor: VIN to 3V3, GND, SCL, SDA | Its own cable |
| FACE LCD | Display, 8 wires straight across | 8 jumper wires |
| SERVOS: PAN, SHVL | Head servo, shovel servo. Brown wire on GND | Servo plug fits directly |
| Socket rows | ESP32-S3 board, USB end to the rear | Push in |
