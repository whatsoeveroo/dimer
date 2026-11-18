// Lesson 6: Speaker
// Plays each of Dimer's sounds, one per second, and says its name in the Serial Monitor.
// Needs: power board on, HEAD wires, amplifier BCLK to D6, LRC to D7, DIN to D3,
// amplifier VIN to 5V and GND to GND, speaker in the amplifier's screw terminal.
#include "sound.h"

const char *names[] = { "beep", "hello", "happy", "question", "scared", "sleepy", "whee" };

void setup() {
  Serial.begin(115200);
  delay(2000);
  if (soundBegin()) Serial.println("Speaker ready");
  else Serial.println("Speaker did not start. Check the wiring.");
}

void loop() {
  for (int s = SND_BEEP; s <= SND_WHEE; s++) {
    Serial.print("Playing: ");
    Serial.println(names[s]);
    say((Sound)s);
    delay(1500);
  }
  delay(2000);
}
