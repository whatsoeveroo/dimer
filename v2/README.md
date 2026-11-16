# Dimer V2 (half size)

A second, smaller Dimer. V1 in the folders above is unchanged and still builds on its own.

| | V1 | V2 |
|---|---|---|
| Size (L x W x H) | 197 x 144 x 118 mm | 101 x 66 x 64 mm |
| Head | turns on a servo | fixed, part of the lid |
| Shovel | lifts on a servo | fixed to the front |
| Battery | 2 x 18650 (7.4 V) | one flat 1S LiPo (3.7 V), boosted to 5 V |
| Electronics | custom main board | small modules joined by jumper wires |
| Tracks | bought track set | printed wheels with a rubber band or TPU belt |
| Edge sensors | 4 | 2, front only |
| Parts cost | about $134 | about $51 |

![V2 preview](docs/assembly_preview.png)

| Folder | What is in it |
|---|---|
| `cad/` | `dimer_v2_frame.py` generates the three printed parts and places every bought part. It reuses the part models in `../cad/dimer_components.py`. `cad/step/` has one STEP per printed part, the full assembly, and `components/` with the parts V1 does not have. |
| `docs/` | `BOM.md` buying list, preview image, and `web/dimer_v2_build_plan.html`, the 3D build page (live at https://claude.ai/artifact/1GJJysHat3mT6KsMUrrWHj). |
| `firmware/` | `dimer_v2_pins.h` pin map for the ESP32-S3 Super Mini. |

## Printed parts

- `v2_frame_chassis`: the tub. Motors, battery and boards sit inside.
- `v2_frame_top`: lid and head in one piece. Holds the display, speaker and microphone.
- `v2_frame_shovel`: blade, plus the shelf that carries the two edge sensors. Two screws into the front wall.

## Things that differ from a plain 0.5x scale

- Length and width are at half or under. Height is 64 mm instead of 59 mm, because jumper-wire plugs need about 16 mm above each board.
- Two N20 motors do not fit end to end in a 34 mm wide body. One drives the rear left wheel, the other the front right wheel.
- The battery pocket takes at most 40 x 30 x 10 mm.

## Status

Rough guideline, same as V1. Part sizes are typical seller dimensions, so measure the real parts before final fits. The script checks that no bought part overlaps the frame or another part. Nothing is built or powered yet.

```
pip install cadquery
python v2/cad/dimer_v2_frame.py
```
