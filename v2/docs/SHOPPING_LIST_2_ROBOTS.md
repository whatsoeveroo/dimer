# Dimer V2 shopping list: 2 robots (prototype + final) plus spares

**Changed 17 Nov: now one robot plus one spare of each part.** The Parts Tracker page has the current quantities (motors 3, XIAO 2, displays 2, batteries 2, one pack of servos, sensors and speakers, 2 assembled boards). The quantities below are the older two-robot plan.

The ☐ boxes are for printing or editing. The live version, where you click the boxes and they save, is the Parts Tracker page: https://claude.ai/artifact/USBwgfyAA6Et9oBisdf7PH

Checked on AliExpress (Korea storefront) on 17 Nov 2026, then reviewed by GPT-6 Astra (Extra High). Prices are what the listing showed that day and will move. "Pick" is the option to choose on the listing.

| # | Part | Link | Pick | Order | Why this many | Bought | Got it |
|---|---|---|---|---|---|---|---|
| 1 | XIAO ESP32S3 Sense (Seeed official store) | [1005006988111963](https://www.aliexpress.com/item/1005006988111963.html) | Bundle: 3pcs (about ₩53,300) | 1 bundle = 3 boards | 2 robots + 1 spare. Headers come loose: 14 joints per board. | ☐ | ☐ |
| 2 | SG90 micro servo, 2-pack | [1005010044091396](https://www.aliexpress.com/item/1005010044091396.html) | 180 degree (positional, not 360) | 2 packs = 4 | 2 + 2 spare (the plastic gears strip easily) | ☐ | ☐ |
| 3 | N20 gear motor (GA12-N20) | [1005003431435613](https://www.aliexpress.com/item/1005003431435613.html) | Speed 100RPM, Voltage 6V | 6 | 4 + 2 spare | ☐ | ☐ |
| 4 | 0.96 in IPS ST7735 80 x 160 display | [1005007038493106](https://www.aliexpress.com/item/1005007038493106.html) | 0.96 inch, 80 x 160 | 3 | 2 + 1 spare | ☐ | ☐ |
| 5 | TCRT5000 edge sensor, 4-pack | [1005006627237602](https://www.aliexpress.com/item/1005006627237602.html) | 4Pcs | 2 packs = 8 | 4 + 4 spare / rear sensors later | ☐ | ☐ |
| 6 | MAX98357A I2S amplifier | [1005007003802663](https://www.aliexpress.com/item/1005007003802663.html) | 5PCS | 1 = 5 boards | 2 + 3 spare. Header and screw terminal come loose: 9 joints per board. | ☐ | ☐ |
| 7 | 20 mm 8 ohm 1 W speaker with wires, 2-pack | [1005006335969407](https://www.aliexpress.com/item/1005006335969407.html) | 20 mm, 8R, 1 W, with wire | 2 packs = 4 | 2 + 2 spare | ☐ | ☐ |
| 8 | 1S LiPo 803040, 1000 mAh (Soshine official) | [1005009794083258](https://www.aliexpress.com/item/1005009794083258.html) | 803040 battery 1pc | 3 | 2 + 1 spare. See battery notes. | ☐ | ☐ |
| 9 | Power board | JLCPCB, files in `v2/pcb/` | Standard PCBA, top side | 5 boards | JLCPCB minimum; 3 spare | ☐ | ☐ |
| 10 | Dupont jumper wires, female-female | [1005002349042216](https://www.aliexpress.com/item/1005002349042216.html) | F-F 10 cm and F-F 20 cm (40 each) | 1 of each length | Head cable (8 wires x 2), sensors, display; cut 4 in half for motor leads | ☐ | ☐ |
| 11 | Self-tapping pan-head screws, 304 stainless (ZONSANTA) | [4000982209705](https://www.aliexpress.com/item/4000982209705.html) | M2 x 4, M2 x 6, M3 x 6, M3 x 10 | the biggest pack of each (aim 50 to 100 per size) | Needs per robot: 2 / 4 / 2 / 1. Plenty for reprints and stripped holes. | ☐ | ☐ |
| 12 | M3 x 20 pan-head machine screws with nuts and washers | [1005009347629578](https://www.aliexpress.com/item/1005009347629578.html) | M3 x 20 | 20 sets | Idler axles: 2 per robot | ☐ | ☐ |
| 13 | Brass tube, 4 mm outside / 3 mm inside | [1005007123893361](https://www.aliexpress.com/item/1005007123893361.html) | 4 mm, 300 mm long | 1 | Sleeve the idler axle so the wheel spins on smooth brass, not on screw thread. Cut 12 mm pieces. | ☐ | ☐ |
| 14 | NBR O-rings, 3 mm thick | [1005006417147355](https://www.aliexpress.com/item/1005006417147355.html) | CS 3 mm, OD 60, 62 and 64 mm | one pack of each size | Try sizes to get the track tension right | ☐ | ☐ |
| 15 | 100 nF ceramic capacitors (104) | [32973259342](https://www.aliexpress.com/item/32973259342.html) | 100NF (104) | 1 pack of 100 | One across each motor's tabs to cut electrical noise | ☐ | ☐ |
| 16 | Soldering iron kit, 60 W adjustable (JCD) | [1005007959407616](https://www.aliexpress.com/item/1005007959407616.html) | 220 V, EU plug (fits Korean sockets), kit with solder | 1 | See soldering below | ☐ | ☐ |

## Tools and supplies (added after the step-by-step assembly review)

| Part | Link | Pick | Order | Bought | Got it |
|---|---|---|---|---|---|
| JST PH 2.0 2-pin plug with wire | [4001235017139](https://www.aliexpress.com/item/4001235017139.html) | PH2.0, 2P, female plug with wire | 1 pack | ☐ | ☐ |
| Heat-shrink assortment, 2:1 | [1005009874296174](https://www.aliexpress.com/item/1005009874296174.html) | 328pcs | 1 | ☐ | ☐ |
| Self-adjusting wire stripper | [1005006361181391](https://www.aliexpress.com/item/1005006361181391.html) | | 1 | ☐ | ☐ |
| Flush cutters | [1005007311057877](https://www.aliexpress.com/item/1005007311057877.html) | | 1 | ☐ | ☐ |
| Flux paste, Amaoe M50 | [1005007791588474](https://www.aliexpress.com/item/1005007791588474.html) | 10cc | 1 | ☐ | ☐ |
| Solder wick, MECHANIC | [4000580523448](https://www.aliexpress.com/item/4000580523448.html) | 2.0 mm | 1 | ☐ | ☐ |
| Precision screwdriver set, 26 in 1 | [1005006782813833](https://www.aliexpress.com/item/1005006782813833.html) | | 1 | ☐ | ☐ |
| Hobby knife, EZARC | [1005008284807591](https://www.aliexpress.com/item/1005008284807591.html) | | 1 | ☐ | ☐ |
| Digital caliper, 150 mm | [1005001432768333](https://www.aliexpress.com/item/1005001432768333.html) | | 1 | ☐ | ☐ |
| Multimeter, ANENG DM850 | [1005013266138262](https://www.aliexpress.com/item/1005013266138262.html) | | 1 | ☐ | ☐ |
| USB-C data cable, UGREEN | [1005006471612403](https://www.aliexpress.com/item/1005006471612403.html) (C-to-C: [1005002965907702](https://www.aliexpress.com/item/1005002965907702.html)) | 1 m | 1 | ☐ | ☐ |
| Foam tape, 3M VHB 4229P | [1005009972190961](https://www.aliexpress.com/item/1005009972190961.html) | 10 mm | 1 | ☐ | ☐ |
| Kapton tape | [1005007518587827](https://www.aliexpress.com/item/1005007518587827.html) | 20 mm | 1 | ☐ | ☐ |
| PLA+ filament, eSUN | [1005001298882187](https://www.aliexpress.com/item/1005001298882187.html) | 1.75 mm, 1 kg | 1 | ☐ | ☐ |

Buy locally: superglue gel (Daiso). It can't go by air, and a drop holds each drive wheel on its motor shaft.

Print: one frame set (chassis, top, head, shovel) per robot, plus 6 drive and 6 idler wheels from `v2/cad/step/wheels/` (made by `v2/cad/dimer_v2_wheels.py`).

## Soldering, honestly

No listing offered N20 motors with plugs on their wires, and the amplifier ships with loose pins, so a soldering iron is needed. Per robot:

- XIAO pins: 14 joints. A pre-soldered Sense exists ([1005010765598162](https://www.aliexpress.com/item/1005010765598162.html), Sense variant, ₩37,000 each), but it is from a reseller with 3 sales and the official store's own pre-soldered Sense was sold out, so neither reviewer could vouch for it.
- Amplifier: 7 pins + 2 for the screw terminal.
- Motors: 2 tabs each. Cut a female-female jumper in half, solder the bare end to the tab, add heat-shrink; the female end plugs onto MOT L / MOT R. Solder one 100 nF capacitor across the two tabs too.
- Head power splits: 5 V needs to reach the XIAO and the amplifier, 3.3 V the display's VCC, RES and BLK. Make these Y-leads by soldering jumper halves together and covering with heat-shrink. Lever connectors were dropped: the jumper wire is too thin for them.

About 30 joints per robot, all on big pins. Practise on a spare jumper first.

## Battery notes

- The plug looks like PH 2.0 in the photos, but the listing does not say so and sellers wire polarity differently. Before plugging in, check the red wire lines up with + on the board. If the plug does not fit, a local shop can swap it, or buy a locally stocked 803040 with a PH 2.0 plug.
- Faster local option: Coms 803040 3.7 V 1000 mAh with protection circuit, KC certified, at DeviceMart: https://www.devicemart.co.kr/goods/view?no=15808399 (₩4,300; 3 to 4 days to prepare, then 1 to 3 days by courier). Its leads look bare in the photo, so plan to fit a JST PH 2.0 plug.
- The listing showed delivery around 27 Nov to 3 Dec, slower than the other parts, because LiPo cells ship by restricted routes. If you need it sooner, buy it locally.

## From the GPT-6 Astra review

What changed because of it:
- Lever connectors dropped; Y-leads are soldered instead.
- Brass sleeves on the idler axles instead of bare screw thread.
- O-ring sizes moved up to 60 to 64 mm.
- 100 nF motor capacitors added.
- Battery plug and polarity must be checked by hand.

Already handled in the design: 5 V for the servo, PCA9534 start-up, the AP2112K 3.3 V regulator, and the head-cable diode.

Left open, as before: whether the 5 V boost holds up with the servo, camera and speaker all busy on a low battery. Test that on the prototype before building the final robot.

The head cable is 8 jumpers (5V G DA CL, SV G, PL PR). The review counted 10 because the question listed the spare 3V and G pins too.

When printing: make the idler wheel's center hole 4.2 mm so it turns freely on the brass sleeve.
