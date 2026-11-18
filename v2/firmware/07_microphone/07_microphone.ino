// Lesson 7: Microphone
// Prints how loud it is, 10 times a second, with a little bar.
// Clap near the robot and note the number: put something a bit lower into CLAP_LEVEL.
// Tip: Tools > Serial Plotter draws it as a graph.
// Needs: only the XIAO Sense (the microphone is on the camera board).
#include "mic.h"
#include "dimer_settings.h"

void setup() {
  Serial.begin(115200);
  delay(2000);
  if (!micBegin()) Serial.println("Microphone did not start. Is this the Sense version with the camera board on?");
}

void loop() {
  int loudest = 0;
  for (int i = 0; i < 12; i++) loudest = max(loudest, micLoudness());   // about 100 ms of listening
  Serial.print("loudness:");
  Serial.print(loudest);
  if (loudest > CLAP_LEVEL) Serial.print("   CLAP!");
  Serial.println();
}
