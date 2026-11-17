# Ordering the Dimer V2 power board at JLCPCB

About 15 minutes with two people: one clicks, one checks against this sheet.

## The three files you upload

| File | What it is | Where it goes |
|---|---|---|
| `dimer_v2_power_gerbers_JLCPCB.zip` | the board itself (copper, holes, outline) | step 1 |
| `dimer_v2_power_BOM_JLCPCB.csv` | which part goes where (29 lines, every line has an LCSC number) | step 4 |
| `dimer_v2_power_CPL_JLCPCB.csv` | where each part sits and how it is turned (49 parts) | step 4 |

Every LCSC number was checked on jlcpcb.com on 17 Nov 2026. All 29 were in stock.

## Steps

1. **Sign in** at https://jlcpcb.com, click **Order now**, then **Add gerber file**. Upload the zip, and don't unzip it first. Wait for the preview. It should read **39.5 x 33 mm, 2 layers**, and the outline has a small notch cut out of one corner.
2. **PCB options:** leave the defaults: Base Material FR-4, Layers 2, Thickness 1.6 mm, Surface Finish HASL (or LeadFree HASL), Copper 1 oz. Any PCB colour works; green is cheapest and fastest. **PCB Qty: 5.** Leave "Remove Order Number" at its default.
3. **PCB Assembly:** switch it on.
   - PCBA Type: **Standard**. Economic can't solder the pin headers or the battery socket.
   - Assembly Side: **Top Side**
   - PCBA Qty: **5**, or 2 to save money (2 robots, no spare)
   - Tooling holes: **Added by JLCPCB**
   - Leave everything else at its default, then click **Confirm**.
4. **Upload BOM and CPL.** Pick the BOM file for "Add BOM file" and the CPL file for "Add CPL file", then click **Process BOM & CPL**. If it asks which column is which, the headers are already named Comment, Designator, Footprint, LCSC Part #, and Designator, Mid X, Mid Y, Layer, Rotation.
5. **Parts page.** Every row should show a part with a tick and enough stock. Check these against the table:

   | Designator | Must show | LCSC |
   |---|---|---|
   | U1 | TP4056-42-ESOP8 | C16581 |
   | U2 | MT3608 | C84817 |
   | U3 | AP2112K-3.3TRG1 | C51118 |
   | U4 | DRV8833PWPR | C50506 |
   | U5 | TCA9534DWR | C2870609 |
   | L1 | FNR5040S4R7MT | C167963 |
   | Q1 | AO3401A | C15127 |
   | SW1 | PCM12SMTR | C221841 |
   | J1 | TYPE-C-31-M-12 | C165948 |
   | J2 | B2B-PH-K-S(LF)(SN) | C131337 |
   | J3 to J9, J11 | pin headers 1x2 / 1x3 / 1x4 | C124375 / C49257 / C124378 |

   - If a row says "shortfall" or "out of stock", click the part, search the same text, and pick one with the same package that is in stock. Tell me which row.
   - If a row is greyed out with "No part selected", don't skip it: search its LCSC number.
   - U5 changed on purpose: TCA9534DWR is TI's version of the PCA9534. Same pins, address and registers, and JLCPCB had 846 in stock against 1 for the PCA9534.
   - D2 (green LED) is now KT-0603G (C12624), because the old one was out of stock.
6. **Placement preview.** This is the step where a careful look matters. Zoom in on each chip. The dot or bevel on the part (pin 1) must sit on the pin-1 mark on the board. Check:
   - **U1, U4, U5:** the dot sits on the corner marked with a small triangle or dot.
   - **U2, U3, Q1:** the single pin sits on the side with one pad.
   - **D1, D2 (LEDs):** the green cathode mark points to the side away from R4 and R5. **D3, D4 (diodes):** the band lines up with the band on the silkscreen.
   - **J1 (USB-C):** its open mouth faces off the board edge.
   - **SW1:** its lever sticks out over the board edge.
   - **J2 (battery socket):** the opening faces the inside of the board.

   If a part is turned the wrong way, select it and use the rotate buttons. JLCPCB's engineers also review this and email if something looks wrong.
7. **Quote and order.** Click Next, choose a product description (e.g. "DIY / Robotics / Educational"), and pick shipping. DHL or FedEx to Korea takes about 3 to 5 days after the boards are built, which is 3 to 5 working days for Standard PCBA. Pay. Expect about $95 to $105 for 5 assembled boards, shipping included, with the extended-part fees (about $3 each) making up most of it.
8. **After ordering,** watch your email. JLCPCB sometimes asks a question about a part or orientation, and answering quickly keeps the order moving. Forward it to me if unsure.

## When the boards arrive

Follow the power-up checklist in `README.md`: switch off, plug the battery, measure 5 V and 3.3 V before plugging anything else in.
