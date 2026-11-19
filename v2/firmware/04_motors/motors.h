// The two tracks. Speed goes from -255 (full reverse) through 0 (stop) to 255 (full forward).
// The XIAO makes the speed signal (PWM) and the expander sets the direction.
#pragma once
#include "dimer_v2_pins.h"
#include "dimer_settings.h"
#include "expander.h"

#define MOTOR_LEFT  0
#define MOTOR_RIGHT 1

int motorSpeedNow[2] = {0, 0};

void motorsBegin() {
  ledcAttach(PIN_MOT_L_PWM, 20000, 8);   // 20 kHz, so the motors do not whine; 8 bits = 0-255
  ledcAttach(PIN_MOT_R_PWM, 20000, 8);
  ledcWrite(PIN_MOT_L_PWM, 0);
  ledcWrite(PIN_MOT_R_PWM, 0);
  expSetPin(EXP_MOT_SLEEP, true);        // wake the motor driver
}

void motorSet(int side, int speed) {
  speed = constrain(speed, -255, 255);
  int pwmPin = (side == MOTOR_LEFT) ? PIN_MOT_L_PWM : PIN_MOT_R_PWM;
  int dirPin = (side == MOTOR_LEFT) ? EXP_MOT_L_DIR : EXP_MOT_R_DIR;
  bool flip  = (side == MOTOR_LEFT) ? MOT_L_FLIP : MOT_R_FLIP;

  int old = motorSpeedNow[side];
  bool oldReverse = (old < 0) != flip && old != 0;
  bool newReverse = (speed < 0) != flip && speed != 0;

  if (old != 0 && oldReverse != newReverse) {  // changing direction: stop for 20 ms first
    ledcWrite(pwmPin, oldReverse ? 255 : 0);
    delay(20);
  }
  if (oldReverse != newReverse) expSetPin(dirPin, newReverse);
  int amount = abs(speed);
  ledcWrite(pwmPin, newReverse ? 255 - amount : amount);
  motorSpeedNow[side] = speed;
}

void drive(int left, int right) {
  motorSet(MOTOR_LEFT, left);
  motorSet(MOTOR_RIGHT, right);
}

void stopMotors();   // defined below, after the smooth-start helpers

void motorsSleep() {                     // stop and switch the driver off
  stopMotors();
  expSetPin(EXP_MOT_SLEEP, false);
}

// ---------- Smooth starts ----------
// Starting both motors at full speed at once pulls a big gulp of current, which can make the
// 5 V dip and reset the XIAO. driveSmooth() sets where we want to go; motorsUpdate(), called
// every loop, climbs there over about 0.25 s. Stopping (stopMotors) is always instant.
int motorTarget[2] = {0, 0};
unsigned long motorLastRampMs = 0;
#define MOTOR_RAMP_PER_SEC 1000   // speed units per second

void driveSmooth(int left, int right) {
  motorTarget[MOTOR_LEFT] = constrain(left, -255, 255);
  motorTarget[MOTOR_RIGHT] = constrain(right, -255, 255);
}

void motorsUpdate() {
  unsigned long now = millis();
  int step = max(1, (int)(MOTOR_RAMP_PER_SEC * (now - motorLastRampMs) / 1000));
  motorLastRampMs = now;
  for (int side = 0; side < 2; side++) {
    int cur = motorSpeedNow[side], tgt = motorTarget[side];
    if (cur == tgt) continue;
    if ((cur > 0 && tgt < 0) || (cur < 0 && tgt > 0)) tgt = 0;    // pass through 0 when reversing
    int next = (cur < tgt) ? min(cur + step, tgt) : max(cur - step, tgt);
    motorSet(side, next);
  }
}

void stopMotors() {                      // instant stop, and forget any smooth target
  motorTarget[MOTOR_LEFT] = motorTarget[MOTOR_RIGHT] = 0;
  drive(0, 0);
}
