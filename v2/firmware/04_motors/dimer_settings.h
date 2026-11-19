// Dimer V2 settings: the numbers you tune once the robot is built.
// The test sketches help you find each value. When a test tells you to change one,
// change it here in the 09_dimer_brain sketch too, because that is the one that runs the robot.
#pragma once

// ---------- Face (lesson 2) ----------
// Turn the picture: 1 or 3. If the face is upside down, swap.
#define FACE_ROTATION     3
// Most 0.96" IPS screens need the "PLUGIN" setting. If colours look wrong
// (eyes are orange instead of cyan, or the picture is shifted), set this to 0.
#define FACE_IPS_PLUGIN   1
// Eye colour as red, green, blue (0-255 each).
#define FACE_EYE_R        40
#define FACE_EYE_G        220
#define FACE_EYE_B        255

// ---------- Tracks (lesson 4) ----------
// If a track runs backwards when it should go forwards, change its 0 to 1.
#define MOT_L_FLIP        0
#define MOT_R_FLIP        0
// Cruising speed, 0-255. Start slow.
#define DRIVE_SPEED       150
#define TURN_SPEED        150

// ---------- Head tilt (lesson 5) ----------
// Servo pulse (in microseconds) where the head looks straight ahead.
#define TILT_ZERO_US      1500
// 1 if a bigger angle lifts the head up, -1 if it pushes the head down.
#define TILT_DIRECTION    1
// About 11 microseconds per degree for an SG90.
#define TILT_US_PER_DEG   11.0

// ---------- Voice (lesson 6) ----------
// Loudness, 0-10000. 3000 is polite, 8000 is loud.
#define SOUND_VOLUME      3000

// ---------- Ears (lesson 7) ----------
// How loud a clap must be (see the number lesson 7 prints when you clap).
#define CLAP_LEVEL        6000
