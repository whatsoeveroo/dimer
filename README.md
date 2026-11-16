# Dimer

A tabletop pet robot, under 20 cm: two tracks, a head that turns to look around, table-edge sensing,
a front shovel, a face display, and voice through the OpenAI API.

| Folder | What is in it |
|---|---|
| `docs/` | `BOM.md` buying list with one product link per part. `ASSEMBLY.md` step-by-step assembly guideline. `JLCPCB.md` how to order the built board. |
| `cad/` | `dimer_frame.py` generates the frame guideline and places every part. `dimer_components.py` holds the models of the bought parts. `cad/step/` has one STEP per printed part, `dimer_guideline_assembly.step` with everything in place, and `components/` with one STEP per bought part. |
| `pcb/` | `make_board.py` generates the v0.2 board (all chips and connectors fitted by JLCPCB). Upload `dimer_main_gerbers_JLCPCB.zip`, `dimer_main_BOM_JLCPCB.csv` and `dimer_main_CPL_JLCPCB.csv`. `dimer_main.kicad_pcb` opens in KiCad, `dimer_main_3d.step` is the board in 3D, `drc_report.txt` is the rule check. |
| `web/` | `build_page.py` and `template.html` build the web page (`dimer_build_plan.html`) and `docs/ASSEMBLY.md` from one list of steps. |
| `firmware/` | `dimer_pins.h` pin map for the ESP32-S3. |

## Status (v0.2, no soldering)

- Buying list: every part arrives with pins or wires attached. Links checked on AliExpress on 2026-11-16. Track set not chosen yet.
- Assembly guide: written for the v0.2 board and frame.
- Frame: rough guideline only. Holes for the round switch, charging socket and distance sensor use typical sizes. Some parts have no fixing designed yet.
- PCB v0.2: routed with freerouting, KiCad rule check shows 0 clearance errors and 0 unconnected pads. Not yet built or powered. Order it assembled, see `docs/JLCPCB.md`.
- Firmware: pin map only.

## Regenerating

```
pip install cadquery shapely numpy
python cad/dimer_frame.py        # frame STEP files
python pcb/make_board.py         # board, rule check, Gerbers (needs KiCad 7 or newer and freerouting)
python cad/dimer_frame.py web/mesh.json && python web/build_page.py   # web page and docs/ASSEMBLY.md
```

Axes in the CAD: X forward, Y left, Z up, table at Z = 0, units mm.
