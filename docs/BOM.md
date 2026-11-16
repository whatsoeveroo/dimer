# Dimer buying list (v0.2, no soldering)

Every link below opens one product from one seller. Each page was opened and checked on 2026-11-16 from Korea.
Prices are what the page showed that day in KRW and they move daily. Where a page has several options, the
"Pick this option" column says which one to click.

This list goes with the v0.2 main board, which JLCPCB builds with all chips and connectors already fitted.
You only plug things in and tighten screw terminals.

## AliExpress

| # | Part | Buy | Pick this option | Qty to order | Price seen | Checked on the page |
|---|---|---|---|---|---|---|
| 1 | Brain: ESP32-S3 DevKitC-1 N16R8 | [product page](https://www.aliexpress.com/item/1005006240070551.html) | "ESP32-S3 soldered" (N16R8) | 1 | ₩4,080 | Pins already soldered |
| 2 | Face: 2.0 inch IPS display, ST7789, 8 pins | [product page](https://www.aliexpress.com/item/1005002363748586.html) | only one option | 1 | ₩3,480 | 8 pins already soldered |
| 3 | Table-edge sensors: TCRT5000 module | [product page](https://www.aliexpress.com/item/1005008965242714.html) | "4PCS" | 1 | ₩2,472 | 3 pins already soldered |
| 4 | Distance sensor: TOF200F (housed VL53L0X with cable) | [product page](https://www.aliexpress.com/item/1005008657721399.html) | "TOF0200F" | 1 | ₩9,506 | Comes with a plug-in cable that ends in jumper sockets |
| 5 | Drive motors: N20 gear motor with encoder and cable | [product page](https://www.aliexpress.com/item/1005007886406269.html) | 6 V, 100 rpm | 2 | ₩16,284 | Cable included, so nothing to solder on the motor |
| 6 | Servos: MG90S metal gear, 4 pieces | [product page](https://www.aliexpress.com/item/4001193413905.html) | only one option | 1 | ₩11,477 | Two used (head, shovel), two spare |
| 7 | Speaker: 28 mm, 4 ohm, with cable, 2 pieces | [product page](https://www.aliexpress.com/item/1005009922386828.html) | 4 ohm | 1 | ₩11,650 | Cable attached. Cut the small plug off and strip the two wires |
| 8 | Battery holder: 2 x 18650 with wire leads | [product page](https://www.aliexpress.com/item/1005004429543070.html) | "2X" | 1 | ₩454 | Red and black leads attached |
| 9 | Charger: 8.4 V 1 A, 5.5 x 2.1 mm plug | [product page](https://www.aliexpress.com/item/1005001803376849.html) | EU plug | 1 | ₩6,100 | For 2 cells in series |
| 10 | Charging socket: panel DC jack with cable, 2 pieces | [product page](https://www.aliexpress.com/item/1005012665509644.html) | 5.5 x 2.1 | 1 | ₩2,835 | Wires attached |
| 11 | Power switch: round rocker with wires | [product page](https://www.aliexpress.com/item/1005012714169914.html) | 1PC | 1 | ₩1,494 | Red and black leads attached |
| 12 | Jumper wires: female to female, 20 cm, 40 pieces | [product page](https://www.aliexpress.com/item/1005006205169394.html) | "F-F(20CM) 40PCS" | 1 | ₩1,997 | |
| 13 | Screws: M3 button head kit with nuts | [product page](https://www.aliexpress.com/item/1005007278965396.html) | "M3 x 392pcs" | 1 | about ₩7,000 | Price shown was for another option, check after clicking |
| 14 | Tracks and wheels (choose by eye) | [option A](https://www.aliexpress.com/item/1005012018149833.html) or [option B](https://www.aliexpress.com/item/1005010530113079.html) | see note 1 | 1 | ₩7,770 or ₩11,350 | Not yet a sure fit, see note 1 |

**AliExpress total: about ₩87,000 to ₩90,000** before shipping and coupons.

## Not AliExpress

| Part | Where | Qty | Rough cost | Note |
|---|---|---|---|---|
| 18650 Li-ion cells, **protected**, name brand | Korean shop (batteries ship badly from AliExpress) | 2 | about ₩12,000 | Must be the "protected" type, see note 2 |
| Dimer main board v0.2, built by JLCPCB | jlcpcb.com | 5 boards, 2 built | my guess is ₩70,000 to ₩110,000 with shipping | I have no real quote yet. JLCPCB shows the exact price when the files are uploaded |

**Whole robot: roughly ₩170,000 to ₩210,000**, compared with about ₩225,000 ($162) for the v0.1 list that needed soldering.

## What was cut from the v0.1 list, and why

- DRV8833 motor driver, MAX98357A amplifier, INMP441 microphone, Mini560 converter modules: these chips are now on the main board, fitted by JLCPCB.
- 2S BMS board and USB-C charger module: replaced by protected cells plus a ready-made 8.4 V wall charger. Both needed soldering.
- Screw terminals, pin headers, sockets, resistor kit, capacitor kit, diode, fuse: all fitted by JLCPCB.
- Silicone wire: every bought part now comes with its own wires.
- Heat-set inserts: they need a soldering iron. Screws go straight into the printed plastic instead.
- Soldering iron kit and multimeter.
- MPU6050 tilt sensor, LED strip, touch sensor: not needed for the first working robot. The board keeps plugs for them, so they can be added later.
- Spares of everything except servos and the items sold in packs.

## Notes

1. **Tracks.** Both track sets have wheels with 4 mm (or 6 mm) holes, and the N20 motor shaft is 3 mm. I have not found a track set that
   is sure to fit a 3 mm shaft. Choose the look you like, then the frame gets a small printed 3-to-4 mm sleeve, or we look for a different
   set together. Do not order tracks until this is settled.
2. **Protected cells.** With the BMS board gone, the cells' own protection circuit is what stops over-discharge and short circuits.
   Protected cells are about 3 to 4 mm longer than bare ones and can be tight in some holders. If they do not fit holder #8, tell me the
   cell length and I will pick another holder.
3. **Speaker and motor cables** end in small plugs that do not match the board. You cut the plug off with scissors, strip about 6 mm of
   insulation, and clamp the bare wire in a screw terminal. No solder.
4. **Distance sensor.** The TOF200F is a different module from the one in v0.1, so the head frame gets new mounting holes for it.
