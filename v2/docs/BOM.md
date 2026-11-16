# Dimer V2 buying list (one robot)

Prices are rough estimates in USD, not live quotes, in the same style as the V1 list. Links are AliExpress searches. Where a seller offers "with pins soldered" or "welded headers", pick that option.

| Group | Part | Qty | Est. $ | Search | Why |
|---|---|---|---|---|---|
| Brain | ESP32-S3 Super Mini, headers soldered | 1 | 6 | [search](https://www.aliexpress.com/w/wholesale-ESP32-S3-SuperMini-soldered.html) | Same chip family as V1 on a 22 x 18 mm board. The V1 dev board is 69 mm long and does not fit. |
| Drive | N20 gear motor, 6 V, about 100 RPM, 3 mm D-shaft | 2 | 6 | [search](https://www.aliexpress.com/w/wholesale-N20-gear-motor-6V-100RPM.html) | Same motor as V1. One drives the rear left wheel, the other the front right wheel. |
| Drive | DRV8833 dual motor driver module | 1 | 1 | [search](https://www.aliexpress.com/w/wholesale-DRV8833-motor-driver-module.html) | Same as V1. |
| Drive | Rubber bands or O-rings, about 45 mm inner diameter, 2 per side | 1 | 3 | [search](https://www.aliexpress.com/w/wholesale-silicone-o-ring-45mm.html) | The tracks. No bought track set exists this small, so the four wheels are 3D printed and a band runs over them. A printed TPU belt also works. |
| Face | 0.96 inch IPS display, ST7735, 80x160, SPI | 1 | 3 | [search](https://www.aliexpress.com/w/wholesale-0.96-inch-IPS-ST7735-80x160-SPI.html) | The face. The 2.0 inch V1 screen is wider than the whole V2 head. |
| Senses | TCRT5000 infrared sensor module (with DO pin) | 2 | 1 | [search](https://www.aliexpress.com/w/wholesale-TCRT5000-infrared-sensor-module.html) | Table-edge detectors in front of each track. V2 has no rear pair: it only reverses over ground it has just driven. |
| Senses | VL53L0X distance sensor module | 1 | 3 | [search](https://www.aliexpress.com/w/wholesale-VL53L0X-ToF-distance-sensor-module.html) | Sees what is in front. Same as V1. |
| Voice | INMP441 I2S microphone module | 1 | 3 | [search](https://www.aliexpress.com/w/wholesale-INMP441-I2S-microphone-module.html) | Same as V1. |
| Voice | MAX98357A I2S amplifier module | 1 | 3 | [search](https://www.aliexpress.com/w/wholesale-MAX98357A-I2S-amplifier-module.html) | Same as V1. |
| Voice | Speaker, 20 mm, 8 ohm 1 W | 1 | 2 | [search](https://www.aliexpress.com/w/wholesale-20mm-speaker-8-ohm-1W.html) | Sits in the back of the head. |
| Power | 1S LiPo battery, 3.7 V, about 1000 mAh, with protection board, at most 40 x 30 x 10 mm (sizes 803040 or 103040) | 1 | 8 | [search](https://www.aliexpress.com/w/wholesale-103040-lipo-3.7V-1200mAh.html) | Replaces the two 18650 cells. Better bought locally in Korea. |
| Power | 1S USB-C charger with 5 V boost output (IP5306 or MH-CD42 type) | 1 | 2 | [search](https://www.aliexpress.com/w/wholesale-MH-CD42-charge-discharge-module.html) | Charges the battery and makes 5 V for everything. Replaces the V1 protection board, charger and 5 V converter. |
| Power | Mini slide switch | 1 | 1 | [search](https://www.aliexpress.com/w/wholesale-SS12D00-slide-switch.html) | On/off, on top behind the head. |
| Wiring | Dupont jumper wires, female-female, 10 cm | 1 | 3 | [search](https://www.aliexpress.com/w/wholesale-dupont-jumper-wire-female-to-female-10cm.html) | All signal wiring. V2 has no custom board. |
| Hardware | M2 and M3 self-tapping screw kit | 1 | 4 | [search](https://www.aliexpress.com/w/wholesale-M2-M3-self-tapping-screw-kit.html) | Lid, shovel, sensor boards and the two idler wheel axles. |
| Hardware | Double-sided foam tape | 1 | 2 | [search](https://www.aliexpress.com/w/wholesale-double-sided-foam-tape.html) | Holds the small boards on top of the battery. |

**Estimated total: about $51 per robot**, before shipping. That leaves roughly $30 to $40 under the $80 to $90 target for shipping, one spare motor and display, and filament.

## What is gone compared with V1

- 4 servos (no neck joint, no shovel joint, no spare), about $10.
- Bought track set, about $14.
- Custom main board and its small parts, about $25.
- 2 x 18650 cells, holder, 2S protection board, 2S charger, 5 V converter, about $21.
- Two of the four edge sensors, the optional motion sensor, the LED strip and the touch sensor.

## Open point: soldering

The battery, charger module and switch have bare pads, so power wiring is about 6 solder joints. Every other connection is a plug-in jumper wire. A tiny plug-in power board could remove those joints later.
