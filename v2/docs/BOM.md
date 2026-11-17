# Dimer V2 buying list (one robot)

Prices are rough estimates in USD, not live quotes. Links are AliExpress searches. Where a seller offers "with pins soldered" or "welded headers", pick that option.

| Group | Part | Qty | Est. $ | Search | Why |
|---|---|---|---|---|---|
| Brain and eye | Seeed XIAO ESP32S3 **Sense** (with OV2640 camera and microphone) | 1 | 14 | [search](https://www.aliexpress.com/w/wholesale-XIAO-ESP32S3-Sense.html) | Brain, camera and microphone in one 21 x 17.5 mm stack. It sits in the head, camera above the display. Must say "Sense", the plain XIAO has no camera. |
| Brain and eye | PCF8574 I2C I/O expander module | 1 | 1 | [search](https://www.aliexpress.com/w/wholesale-PCF8574-IO-expansion-module.html) | The XIAO has 11 pins. This adds 8 more over two wires, for the edge sensors and motor directions. |
| Head | SG90 9 g micro servo (MG90S also fits) | 1 | 2 | [search](https://www.aliexpress.com/w/wholesale-SG90-micro-servo.html) | Tilts the head up to about 25 degrees. |
| Drive | N20 gear motor, 6 V, about 100 rpm, 3 mm D-shaft | 2 | 6 | [search](https://www.aliexpress.com/w/wholesale-N20-gear-motor-6V-100RPM.html) | One per track. |
| Drive | DRV8833 dual motor driver module | 1 | 1 | [search](https://www.aliexpress.com/w/wholesale-DRV8833-motor-driver-module.html) | Same as V1. |
| Drive | O-rings or rubber bands, about 60 mm inner diameter, 2 per side | 1 | 3 | [search](https://www.aliexpress.com/w/wholesale-silicone-o-ring-60mm.html) | The tracks, over four printed 22 mm wheels. A printed TPU belt also works. |
| Face | 0.96 inch IPS display, ST7735, 80x160, SPI | 1 | 3 | [search](https://www.aliexpress.com/w/wholesale-0.96-inch-IPS-ST7735-80x160-SPI.html) | Default face. Options B and C are in the README. |
| Senses | TCRT5000 infrared sensor module (with DO pin) | 2 | 1 | [search](https://www.aliexpress.com/w/wholesale-TCRT5000-infrared-sensor-module.html) | Table-edge detectors in front of each track. |
| Voice | MAX98357A I2S amplifier module | 1 | 3 | [search](https://www.aliexpress.com/w/wholesale-MAX98357A-I2S-amplifier-module.html) | Drives the speaker. Sits on the head floor. |
| Voice | Speaker, 20 mm, 8 ohm 1 W | 1 | 2 | [search](https://www.aliexpress.com/w/wholesale-20mm-speaker-8-ohm-1W.html) | In the left cheek of the head. |
| Power | 1S LiPo battery, 3.7 V, about 1000 mAh, with protection board, at most 40 x 30 x 10 mm | 1 | 8 | [search](https://www.aliexpress.com/w/wholesale-103040-lipo-3.7V-1200mAh.html) | Better bought locally in Korea. |
| Power | 1S USB-C charger with 5 V boost output (IP5306 or MH-CD42 type) | 1 | 2 | [search](https://www.aliexpress.com/w/wholesale-MH-CD42-charge-discharge-module.html) | Charges the battery and makes 5 V for everything. |
| Power | Mini slide switch | 1 | 1 | [search](https://www.aliexpress.com/w/wholesale-SS12D00-slide-switch.html) | On/off, on the lid. |
| Wiring | Dupont jumper wires, female-female, 10 and 20 cm | 1 | 4 | [search](https://www.aliexpress.com/w/wholesale-dupont-jumper-wire-female-to-female-20cm.html) | The head moves, so its wires are 20 cm and loop over the tilt axis. |
| Hardware | M2 and M3 self-tapping screw kit | 1 | 4 | [search](https://www.aliexpress.com/w/wholesale-M2-M3-self-tapping-screw-kit.html) | Lid, shovel, sensors, idler axles, head pivot. |
| Hardware | Double-sided foam tape | 1 | 2 | [search](https://www.aliexpress.com/w/wholesale-double-sided-foam-tape.html) | Holds the small boards. |

**Estimated total: about $57 per robot**, before shipping. Still well inside the $80 to $90 target.

## Changes from the first V2 list

- Brain: ESP32-S3 Super Mini ($6) replaced by XIAO ESP32S3 Sense ($14), which brings the camera and the microphone.
- Microphone module dropped: it is on the camera board now.
- Distance sensor dropped: the camera sees what is in front, and there were no pins left. It can come back on the shared I2C wires later if you want it.
- Added: one micro servo for the head tilt, one I/O expander.

## Open point: soldering

The battery, charger module and switch have bare pads, so power wiring is about 6 solder joints. The XIAO comes without its pins, so order it with headers soldered or ask a shop to do it (14 joints). Every other connection is a plug-in jumper wire.
