# Dimer

A tabletop pet robot, under 20 cm: two tracks, a head that turns to look around, table-edge sensing,
a front shovel, a face display, and voice through the OpenAI API.

| Folder | What is in it |
|---|---|
| `cad/` | `dimer_frame.py` generates the frame guideline and places every part. `dimer_components.py` holds the models of the bought parts. `cad/step/` has one STEP per printed part, `dimer_guideline_assembly.step` with everything in place, and `components/` with one STEP per bought part. |
| `pcb/` | `make_board.py` generates the main board. `dimer_main_3d.step` is the board with its connectors in 3D. `dimer_main.kicad_pcb` opens in KiCad. `dimer_main_gerbers_JLCPCB.zip` is the file to upload at jlcpcb.com. `drc_report.txt` is the rule check. |
| `docs/` | `BOM.md` buying list, preview images. |
| `firmware/` | `dimer_pins.h` pin map for the ESP32-S3. |

## Status (v0.1)

- Frame: rough guideline only. Track and wheel sizes are placeholders until a track set is chosen.
- Component models: drawn from typical seller dimensions for layout and rendering. Measure the real parts before final fits.
- PCB: routed, KiCad rule check shows 0 clearance errors and 0 unconnected pads. Not yet built or powered.
- Firmware: pin map only.

## Regenerating

```
pip install cadquery shapely numpy
python cad/dimer_frame.py        # frame STEP files
python pcb/make_board.py         # board, rule check, Gerbers (needs KiCad 7 or newer)
```

Axes in the CAD: X forward, Y left, Z up, table at Z = 0, units mm.
