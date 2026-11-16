# Dimer

A tabletop pet robot, under 20 cm: two tracks, a head that turns to look around, table-edge sensing,
a front shovel, a face display, and voice through the OpenAI API.

| Folder | What is in it |
|---|---|
| `docs/` | `BOM.md` buying list with one product link per part. `ASSEMBLY.md` step-by-step assembly guideline. |
| `cad/` | `dimer_frame.py` generates the frame guideline and places every part. `dimer_components.py` holds the models of the bought parts. `cad/step/` has one STEP per printed part, `dimer_guideline_assembly.step` with everything in place, and `components/` with one STEP per bought part. |
| `pcb/` | `make_board.py` is the generator for the v0.2 board (all chips and connectors fitted by JLCPCB). The board files next to it are still the old v0.1 board. |
| `web/` | `build_page.py` and `template.html` build the web page (`dimer_build_plan.html`) and `docs/ASSEMBLY.md` from one list of steps. |
| `firmware/` | `dimer_pins.h` pin map for the ESP32-S3. |

## Status (v0.2, no soldering)

- Buying list: every part arrives with pins or wires attached. Links checked on AliExpress on 2026-11-16. Track set not chosen yet.
- Assembly guide: written for the v0.2 board and frame.
- Frame: rough guideline only. Holes for the round switch, charging socket and distance sensor use typical sizes. Some parts have no fixing designed yet.
- PCB v0.2: parts placed in `make_board.py`, **not routed or rule-checked yet**. Do not order the v0.1 files in `pcb/`; they need soldering and do not match the new buying list.
- Firmware: pin map only.

## Regenerating

```
pip install cadquery shapely numpy
python cad/dimer_frame.py        # frame STEP files
python pcb/make_board.py         # board, rule check, Gerbers (needs KiCad 7 or newer and freerouting)
python cad/dimer_frame.py web/mesh.json && python web/build_page.py   # web page and docs/ASSEMBLY.md
```

Axes in the CAD: X forward, Y left, Z up, table at Z = 0, units mm.
