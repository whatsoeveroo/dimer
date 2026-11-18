// Head tilt servo (SG90). Angles are in degrees: 0 = looking ahead, TILT_MAX_DEG = looking up.
// The head moves smoothly to the target; call tiltUpdate() often (every loop).
#pragma once
#include "dimer_v2_pins.h"
#include "dimer_settings.h"

float tiltNowDeg = 0;
float tiltTargetDeg = 0;
float tiltSpeedDegPerSec = 60;
unsigned long tiltLastMs = 0;

void tiltWriteDeg(float deg) {
  deg = constrain(deg, TILT_MIN_DEG, TILT_MAX_DEG);   // never past the stops
  float us = TILT_ZERO_US + TILT_DIRECTION * deg * TILT_US_PER_DEG;
  ledcWrite(PIN_SERVO_TILT, (uint32_t)(us * 16383.0 / 20000.0));  // one pulse every 20 ms
}

void tiltWriteMicros(int us) {           // raw pulse, for finding TILT_ZERO_US in lesson 5
  ledcWrite(PIN_SERVO_TILT, (uint32_t)(us * 16383.0 / 20000.0));
}

void tiltBegin() {
  ledcAttach(PIN_SERVO_TILT, 50, 14);    // 50 pulses a second, 14-bit detail
  tiltNowDeg = tiltTargetDeg = 0;
  tiltWriteDeg(0);
  tiltLastMs = millis();
}

void tiltTo(float deg, float degPerSec = 60) {
  tiltTargetDeg = constrain(deg, TILT_MIN_DEG, TILT_MAX_DEG);
  tiltSpeedDegPerSec = degPerSec;
}

void tiltUpdate() {
  unsigned long now = millis();
  float step = tiltSpeedDegPerSec * (now - tiltLastMs) / 1000.0;
  tiltLastMs = now;
  if (tiltNowDeg < tiltTargetDeg) tiltNowDeg = min(tiltNowDeg + step, tiltTargetDeg);
  else if (tiltNowDeg > tiltTargetDeg) tiltNowDeg = max(tiltNowDeg - step, tiltTargetDeg);
  tiltWriteDeg(tiltNowDeg);
}
