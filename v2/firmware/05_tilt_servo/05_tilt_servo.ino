// Lesson 5: Head tilt servo
// Part A (before the horn is on): upload, and the servo moves to TILT_ZERO_US and stays there.
//   Now push the horn on so the head looks straight ahead.
// Part B: type a number in the Serial Monitor and press Enter:
//   0 to 25        -> move the head to that angle (0 = ahead, 25 = up)
//   1000 to 2000   -> send that raw pulse in microseconds, to find TILT_ZERO_US
// Needs: power board on, HEAD wires, SV wire to D2, servo plugged into TILT (brown wire on G).
#include "tilt.h"

bool rawMode = false;   // true while you are testing raw pulses

void setup() {
  Serial.begin(115200);
  tiltBegin();                          // goes to 0 degrees = looking ahead
  delay(2000);
  Serial.println("Servo at 0 degrees (looking ahead).");
  Serial.println("Type 0-25 for an angle, or 1000-2000 for a raw pulse, then Enter.");
}

void loop() {
  if (Serial.available()) {
    String text = Serial.readStringUntil('\n');
    int value = text.toInt();
    if (value >= 1000 && value <= 2000) {
      rawMode = true;
      tiltWriteMicros(value);
      Serial.print("Raw pulse: "); Serial.print(value); Serial.println(" us");
    } else if (value >= TILT_MIN_DEG && value <= TILT_MAX_DEG) {
      rawMode = false;
      tiltTo(value, 40);
      Serial.print("Angle: "); Serial.println(value);
    } else {
      Serial.println("Out of range, ignored.");
    }
  }
  if (!rawMode) tiltUpdate();
  delay(10);
}
