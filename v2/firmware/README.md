# Dimer V2 firmware

Arduino sketches for the XIAO ESP32S3 Sense. Start with the beginner guide
("Dimer V2: programming the robot from zero"), which walks through installing the tools and each lesson.

| Sketch | Tests | Needs |
|---|---|---|
| `01_blink` | First upload, Serial Monitor | XIAO only |
| `02_face` | ST7735 screen, eyes and moods | XIAO + screen |
| `03_expander_edges` | PCA9534 expander at 0x20, TCRT5000 edge sensors | Power board |
| `04_motors` | Both tracks (hold the robot up) | Power board + motors |
| `05_tilt_servo` | Head tilt servo, finding its zero | Power board + servo |
| `06_speaker` | MAX98357A amplifier, robot chirps | Power board + amplifier |
| `07_microphone` | Sense board microphone, clap level | XIAO Sense only |
| `08_camera` | Sense camera, live picture over Wi-Fi | XIAO Sense only |
| `09_dimer_brain` | The robot: wander, avoid edges, react to lifting and claps, sleep | Everything |

Arduino IDE 2, board **esp32 > XIAO_ESP32S3** (esp32 core 3.x by Espressif), Tools > PSRAM > **OPI PSRAM**.
Library: **Adafruit ST7735 and ST7789 Library** (with its dependencies). Everything else is in the esp32 core.

## Shared code

The pin map is `dimer_v2_pins.h` here. `common/` holds the tunable numbers (`dimer_settings.h`) and one tab per part
(`expander.h`, `motors.h`, `tilt.h`, `face.h`, `sound.h`, `mic.h`). The Arduino IDE only sees files inside a sketch's
own folder, so each sketch carries copies. Edit the pin map or `common/`, then run `python3 sync_common.py`.

The tuned numbers for your robot go in `09_dimer_brain/dimer_settings.h`.
