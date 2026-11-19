// Lesson 3: I/O expander and edge sensors
// 1) Looks for the expander chip on the I2C wires and says if it found it.
// 2) Prints what the two table-edge sensors see, 5 times a second.
// The motors stay asleep in this test, so nothing moves.
// Needs: power board on (battery + switch), HEAD wires 5V/G/DA/CL, both EDGE sensors plugged in.
#include "expander.h"

void setup() {
  Serial.begin(115200);
  delay(2000);                         // time to open the Serial Monitor
  Serial.println("Looking for the expander...");

  if (expanderBegin()) {
    Serial.println("Found it at address 0x20. Good!");
  } else {
    Serial.println("No answer. Check: switch on? DA to D4, CL to D5, G to GND?");
    Serial.println("Devices that did answer on the I2C wires:");
    for (int addr = 1; addr < 127; addr++) {
      Wire.beginTransmission(addr);
      if (Wire.endTransmission() == 0) { Serial.print("  0x"); Serial.println(addr, HEX); }
    }
  }
}

void loop() {
  bool left = edgeLeftNoTable();
  bool right = edgeRightNoTable();
  Serial.print("Left: ");
  Serial.print(left ? "NO TABLE " : "table    ");
  Serial.print("  Right: ");
  Serial.println(right ? "NO TABLE" : "table");
  delay(200);
}
