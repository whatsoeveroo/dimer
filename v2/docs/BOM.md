# Dimer V2 buying list (one robot)

> For the two-robot order with exact AliExpress listings, quantities and the soldering you will need, see [SHOPPING_LIST_2_ROBOTS.md](SHOPPING_LIST_2_ROBOTS.md).

Prices are rough estimates in USD, not live quotes. Links are AliExpress searches. Where a seller offers "with pins soldered" or "welded headers", pick that option.

| Group | Part | Qty | Est. $ | Search | Why |
|---|---|---|---|---|---|
| Brain and eye | Seeed XIAO ESP32S3 **Sense** (with OV2640 camera and microphone) | 1 | 14 | [search](https://www.aliexpress.com/w/wholesale-XIAO-ESP32S3-Sense.html) | Brain, camera and microphone in one 21 x 17.5 mm stack. It sits in the head, camera above the display. Must say "Sense", the plain XIAO has no camera. |
| Head | SG90 9 g micro servo (MG90S also fits) | 1 | 2 | [search](https://www.aliexpress.com/w/wholesale-SG90-micro-servo.html) | Tilts the head up to about 25 degrees. |
| Drive | N20 gear motor, 6 V, about 100 rpm, 3 mm D-shaft, **with wires and a noise capacitor** | 2 | 6 | [search](https://www.aliexpress.com/w/wholesale-N20-gear-motor-6V-100RPM.html) | One per track. |
| Drive | O-rings or rubber bands, about 60 mm inner diameter, 2 per side | 1 | 3 | [search](https://www.aliexpress.com/w/wholesale-silicone-o-ring-60mm.html) | The tracks, over four printed 22 mm wheels. A printed TPU belt also works. |
| Face | 0.96 inch IPS display, ST7735, 80x160, SPI | 1 | 3 | [search](https://www.aliexpress.com/w/wholesale-0.96-inch-IPS-ST7735-80x160-SPI.html) | Default face. Options B and C are in the README. |
| Senses | TCRT5000 infrared sensor module (with DO pin) | 2 | 1 | [search](https://www.aliexpress.com/w/wholesale-TCRT5000-infrared-sensor-module.html) | Table-edge detectors in front of each track. |
| Voice | MAX98357A I2S amplifier module, **pins already soldered** | 1 | 3 | [search](https://www.aliexpress.com/w/wholesale-MAX98357A-I2S-amplifier-module.html) | Drives the speaker. Sits on the head floor. |
| Voice | Speaker, 20 mm, 8 ohm 1 W, **with wires** | 1 | 2 | [search](https://www.aliexpress.com/w/wholesale-20mm-speaker-8-ohm-1W.html) | In the left cheek of the head. |
| Power | 1S LiPo battery, 3.7 V, about 1000 mAh, **with protection board and a JST PH 2.0 plug**, at most 40 x 30 x 10 mm | 1 | 8 | [search](https://www.aliexpress.com/w/wholesale-103040-lipo-3.7V-JST-PH2.0.html) | Plugs straight into the power board. Check the red wire goes to the + mark: sellers do not all wire the plug the same way. |
| Power | **Dimer V2 power board**, made and fully soldered by JLCPCB (`v2/pcb/`) | 1 | 12 to 20 | see `v2/pcb/README.md` | USB-C charging, on/off switch, 5 V and 3.3 V supplies, motor driver and I/O expander on one 39.5 x 33 mm board. About $20 each when you order 5, about $12 each when you order 10. |
| Wiring | Dupont jumper wires, female-female, 10 and 20 cm | 1 | 3 | [search](https://www.aliexpress.com/w/wholesale-dupont-jumper-wire-female-to-female-20cm.html) | The head moves, so its wires are 20 cm and loop over the tilt axis. |
| Wiring | Dupont splitter cables, 1 female to 3 female | 3 | 3 | [search](https://www.aliexpress.com/w/wholesale-dupont-1-to-3-female-splitter.html) | In the head, no soldering: 5 V from the board to the XIAO and the amplifier; the XIAO 3V3 to the screen's VCC, RES and BLK; GND to the screen GND, screen CS and amplifier GND. |
| Hardware | M2 self-tapping pan-head screw kit (4 and 6 mm) | 1 | 2 | [search](https://www.aliexpress.com/w/wholesale-m2-self-tapping-screw-pan-head-assortment-kit.html) | Needs 2 x M2 x 4 and 4 x M2 x 6: lid, shovel, power board. |
| Hardware | M3 screw and nut kit (6, 10 and 20 mm) | 1 | 3 | [search](https://www.aliexpress.com/w/wholesale-m3-pan-head-screw-nut-assortment-kit.html) | Needs 2 x M3 x 6, 1 x M3 x 10, 2 x M3 x 20 and 1 nut: edge sensors, head pivot, idler axles. |
| Hardware | Double-sided foam tape | 1 | 2 | [search](https://www.aliexpress.com/w/wholesale-double-sided-foam-tape.html) | Holds the amplifier and the brain in the head. |

**Estimated total: about $68 to $76 per robot**, before shipping (the range is the power board: $20 each in a batch of 5, $12 each in a batch of 10). Still inside the $80 to $90 target.

## Changes from the first V2 list

- Brain: ESP32-S3 Super Mini ($6) replaced by XIAO ESP32S3 Sense ($14), which brings the camera and the microphone.
- Microphone module dropped: it is on the camera board now.
- Distance sensor dropped: the camera sees what is in front, and there were no pins left. It can come back on the shared I2C wires later if you want it.
- Added: one micro servo for the head tilt, one I/O expander.

## Changes for the power board (V2.1 r1)

- Gone: the charger module, the slide switch on the lid, the DRV8833 module and the PCF8574 module ($5). They are all on the power board now.
- Added: the power board, $12 to $20 per robot depending on batch size.
- The bay lid is 2 mm taller (42 mm) so the jumper plugs fit under it.

## Soldering left

- None for power: the battery plugs into the board, USB-C and the switch are on the board.
- Motors: buy N20s that come with wires ending in a 2.54 mm (dupont or XH 2-pin) plug; they push onto the MOT pins. If the wires end bare, that is 4 joints (or crimp dupont ends).
- Amplifier and speaker: pick the "soldered" option of the MAX98357A module and a speaker with wires; the speaker wires go into the module's screw terminal.
- Head wiring: three 1-to-3 dupont splitters share 5 V, 3V3 and GND inside the head.
- XIAO: it comes without pins. Order it with headers soldered, or ask a shop (14 joints).
- Everything else is a plug-in jumper wire.

## Screws: where each one goes

Every screw cuts its own thread into a printed hole that is slightly smaller than the screw. Turn until snug, then stop. One small cross-head screwdriver does all of them. The 3D build page shows them in grey under "Screws".

| Where | Screw | How |
|---|---|---|
| Lid | 1 x M2 x 6 at the back, 2 x M2 x 4 at the front | From outside through the end walls into the lid tabs. Front ones before the shovel goes on (the shovel has clearance holes over their heads). |
| Shovel | 2 x M2 x 6 | From the front, through the shovel into the front wall. |
| Power board | 1 x M2 x 6 | Down through the board hole at the rear right into the pillar. |
| Idler wheels | 2 x M3 x 20, 1 nut | From outside through the free wheel (it spins on the screw) into the side wall. Nut inside the left wall. Leave the wheel free to turn. |
| Head pivot | 1 x M3 x 10 | From outside the right head arm into the boss on the right wall, then back off a quarter turn. |
| Edge sensors | 2 x M3 x 6 | Down through each sensor's hole into the shovel shelf. |
| Servo | screws from the servo bag | Two ear screws hold the servo; the horn screws fix the horn to the left head arm. |

## Soldering iron

Not needed if you get the pre-soldered XIAO and motors with plugs. If either is not on offer, a basic 60 W soldering iron kit (about $10 to $15) covers it: 14 joints for the XIAO pins, 4 for bare motor wires.
