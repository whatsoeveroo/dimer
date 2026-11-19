// Lesson 4: Tracks
// HOLD THE ROBOT IN THE AIR (or stand it on a cup) so the tracks spin freely.
// It runs: left forward, left back, right forward, right back, both forward, spin, stop,
// then waits 5 seconds and does it again. The Serial Monitor says which step it is on.
// Needs: power board on, HEAD wires, PL PR wires to D0 D1, both motors plugged in.
#include "motors.h"

void step(const char *name, int left, int right) {
  Serial.println(name);
  drive(left, right);
  delay(1500);
  stopMotors();
  delay(500);
}

void setup() {
  Serial.begin(115200);
  delay(2000);
  if (!expanderBegin()) {
    Serial.println("Expander not found: do lesson 3 first. Motors stay off.");
    while (true) delay(1000);         // stop here forever
  }
  motorsBegin();
  Serial.println("Motors ready. Starting in 3 seconds. Hold the robot up!");
  delay(3000);
}

void loop() {
  step("Left track FORWARD",  DRIVE_SPEED, 0);
  step("Left track BACK",    -DRIVE_SPEED, 0);
  step("Right track FORWARD", 0,  DRIVE_SPEED);
  step("Right track BACK",    0, -DRIVE_SPEED);
  step("Both FORWARD",        DRIVE_SPEED,  DRIVE_SPEED);
  step("Spin RIGHT (left forward, right back)", TURN_SPEED, -TURN_SPEED);
  Serial.println("Stopped. Again in 5 seconds.");
  delay(5000);
}
