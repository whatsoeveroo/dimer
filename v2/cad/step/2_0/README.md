# Dimer 2.0 STEP files

Made by `v2/cad/dimer_2_0.py` (assembly and Shell 2.0) and `v2/cad/dimer_parts_2_0.py` (the bought parts).
Axes: X forward, Y left, Z up, table at Z = 0, millimetres.

| File | What is in it |
|---|---|
| `dimer_2_0_full_assembly.step` | Shell 2.0, every bought part in detail, screws and nuts, in folders |
| `dimer_2_0_parts_only.step` | The bought parts and screws without the shell: model your own body over this |
| `dimer_2_0_shell_only.step` | The five printed pieces |
| `shell/*.step` | Each printed piece on its own |
| `parts/*.step` | Each bought part on its own, in its own frame |

## Where the part data comes from

- **Pololu 22T track set**: Pololu's own STEP (`v2/cad/vendor/pololu_22t_track_set.step`), one solid with the track and both sprockets.
- **Power board**: exported from `v2/pcb/dimer_v2_power.kicad_pcb` with the official KiCad 3D model of every footprint (`v2/cad/kicad3d/`). The USB-C socket has no KiCad model, so it is modelled from the HRO TYPE-C-31-M-12 drawing. Chip pins keep their own colour.
- **Everything else** is modelled from seller drawings and datasheets: GA12-N20 (gear train, M1.6 holes, 3 mm D-shaft), SG90 (21-tooth spline, ears, case screws, lead, single-arm horn), XIAO ESP32S3 Sense (camera, FPC, SD slot, microphone, shield, USB-C, castellations, 2 x 7 headers), 0.96 in ST7735 IPS module, MAX98357A breakout, TCRT5000 module, 803040 LiPo with protection board and JST PH plug, 20 mm speaker with leads.

Measure what you received before printing anything tight. The sellers' parts vary by a few tenths.

## Part frames (in `parts/`)

| Part | Origin |
|---|---|
| GA12-N20 motor | Shaft axis +Y, Y = 0 at the gearbox front face |
| SG90 servo | Shaft axis +Z, Z = 0 under the ears, body toward -X |
| XIAO ESP32S3 Sense | Camera lens tip, looking +X |
| ST7735 display | Centre of the glass front, looking +X |
| MAX98357A, LiPo | Board or cell centre, Z = 0 underside |
| TCRT5000 | Centre of the sensor head on the board underside, looking -Z |
| Speaker | Centre of the front rim, sound toward -X |
| Pololu track | Drive sprocket axis (along Z, hub side +Z), idler at +48 mm X |
| Power board | KiCad origin, Y = -KiCad Y, Z = 0 board underside |

## Fit notes

- The gearbox front plate sits in a 1 mm pocket in the side wall, so 6.2 mm of the 10 mm shaft is inside the sprocket's 8.5 mm D bore. A drop of superglue holds it.
- Each idler turns on an M3 x 20 screw through a spacer boss on the wall, with a nut in a trap inside.
- The tilt servo hangs by its ears from the inside of the left wall (two M2 screws); its single-arm horn is screwed to the left head arm with two M2 screws through the horn holes. The right head arm turns on an M3 x 10 screw in the boss on the right wall.
- Clash check: no overlaps between parts and shell except the intended fits, with the head level and tilted up 25 degrees.
