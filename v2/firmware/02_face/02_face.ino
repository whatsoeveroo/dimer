// Lesson 2: Face
// Shows Dimer's eyes on the screen and goes through every mood, two seconds each,
// while the eyes look around and blink.
// Needs: the XIAO and the screen wired as in the guide (only 3V3, GND, D8, D9, D10).
#include "face.h"

Mood moods[] = { MOOD_NORMAL, MOOD_HAPPY, MOOD_SURPRISED, MOOD_SCARED, MOOD_SLEEPY, MOOD_DIZZY };
const char *moodNames[] = { "normal", "happy", "surprised", "scared", "sleepy", "dizzy" };
int moodIndex = 0;
unsigned long lastChangeMs = 0;

void setup() {
  Serial.begin(115200);
  faceBegin();
  Serial.println("Face test started");
}

void loop() {
  if (millis() - lastChangeMs > 2000) {     // every 2 seconds: next mood, look somewhere new
    lastChangeMs = millis();
    moodIndex = (moodIndex + 1) % 6;
    faceMood(moods[moodIndex]);
    faceLook(random(-10, 11) / 10.0, random(-10, 11) / 10.0);
    Serial.print("Mood: ");
    Serial.println(moodNames[moodIndex]);
  }
  faceUpdate();
}
