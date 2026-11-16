# Ordering the Dimer main board from JLCPCB (v0.2, fully assembled)

JLCPCB makes the bare board and also solders every part onto it, so the board arrives ready to use.
You upload three files from the `pcb/` folder:

| File | What it is | Where it goes |
|---|---|---|
| `dimer_main_gerbers_JLCPCB.zip` | The board drawing | First upload, "Add gerber file" |
| `dimer_main_BOM_JLCPCB.csv` | The list of parts to fit | Assembly step, "Add BOM file" |
| `dimer_main_CPL_JLCPCB.csv` | Where each part sits | Assembly step, "Add CPL file" |

The JLCPCB site changes its wording from time to time. If a screen looks different from these steps, send me a screenshot.

## Steps

1. Go to jlcpcb.com, make an account, and press **Order now** (or **Instant quote**).
2. Press **Add gerber file** and upload `dimer_main_gerbers_JLCPCB.zip`. Wait until it shows a picture of the board. It should read the size as **100 x 70 mm** and **2 layers**.
3. Board options. Leave everything at its default except:
   - **PCB Qty:** 5 (the minimum)
   - **PCB Color:** any colour you like
   - **Surface Finish:** LeadFree HASL
4. Scroll down and switch on **PCB Assembly**.
   - **PCBA Type:** Standard. The board has plug-in connectors (pin rows, sockets, screw terminals) that the Economic type does not solder.
   - **Assembly Side:** Top Side
   - **PCBA Qty:** 2 (two finished boards, three bare spares)
   - **Confirm Parts Placement:** Yes. A JLCPCB engineer then checks that every part sits the right way round before building. This matters because nobody has built this board before.
   - Leave the rest at default and press **Next**.
5. Upload `dimer_main_BOM_JLCPCB.csv` and `dimer_main_CPL_JLCPCB.csv`, then press **Process BOM & CPL**.
6. Parts list screen. Every row should show a matched part with a tick.
   - If a row says **shortfall**, **out of stock** or is not matched, stop and tell me the part number in that row. I will pick a replacement.
   - Do not untick any row. Every part is needed.
7. Placement screen. It shows the parts on the board. You do not need to judge it yourself, because the engineer check from step 4 covers it. Press **Next**.
8. If it asks for a product description, choose something like **Research / Education / DIY**.
9. Save to cart, choose shipping to Korea, and pay. JLCPCB shows the exact price before you pay.

## After ordering

- If JLCPCB emails a question about part direction or a missing part, forward it to me before answering.
- When the boards arrive, do not connect a battery yet. Follow `docs/ASSEMBLY.md`.
