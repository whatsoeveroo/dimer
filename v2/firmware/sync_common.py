"""Copies the pin map (dimer_v2_pins.h) and the shared files in common/ into each sketch folder.

The Arduino IDE only sees files inside a sketch's own folder, so each sketch carries
its own copy of the tabs it uses. Edit the files in common/, then run:  python3 sync_common.py
"""
import shutil
from pathlib import Path

HERE = Path(__file__).parent
NEEDS = {
    "02_face": ["dimer_v2_pins.h", "dimer_settings.h", "face.h"],
    "03_expander_edges": ["dimer_v2_pins.h", "expander.h"],
    "04_motors": ["dimer_v2_pins.h", "dimer_settings.h", "expander.h", "motors.h"],
    "05_tilt_servo": ["dimer_v2_pins.h", "dimer_settings.h", "tilt.h"],
    "06_speaker": ["dimer_v2_pins.h", "dimer_settings.h", "sound.h"],
    "07_microphone": ["dimer_settings.h", "mic.h"],
    "09_dimer_brain": ["dimer_v2_pins.h", "dimer_settings.h", "expander.h", "motors.h",
                       "tilt.h", "face.h", "sound.h", "mic.h"],
}
for sketch, files in NEEDS.items():
    for f in files:
        src = HERE / f if f == "dimer_v2_pins.h" else HERE / "common" / f
        shutil.copy(src, HERE / sketch / f)
    print(sketch, "<-", ", ".join(files))
