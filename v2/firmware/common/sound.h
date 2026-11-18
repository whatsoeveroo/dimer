// Dimer's voice: little robot chirps through the MAX98357A amplifier (I2S).
// Sounds play in the background, so the robot keeps checking its edge sensors while it talks.
// Use: soundBegin() once, then say(SND_HAPPY) etc.
#pragma once
#include <ESP_I2S.h>
#include "dimer_v2_pins.h"
#include "dimer_settings.h"

enum Sound { SND_BEEP, SND_HELLO, SND_HAPPY, SND_QUESTION, SND_SCARED, SND_SLEEPY, SND_WHEE };

#define SOUND_RATE 16000
I2SClass speaker(I2S_NUM_1);   // I2S unit 1; unit 0 is kept for the microphone
QueueHandle_t soundQueue;
volatile bool soundPlaying = false;
float soundPhase = 0;

// Plays a tone that slides from startHz to endHz over ms milliseconds.
void playSweep(float startHz, float endHz, int ms) {
  const int CHUNK = 128;
  int16_t buf[CHUNK];
  int total = SOUND_RATE * ms / 1000;
  int fade = SOUND_RATE / 200;                    // 5 ms fade in and out, so it does not click
  for (int i = 0; i < total; i += CHUNK) {
    int n = min(CHUNK, total - i);
    for (int k = 0; k < n; k++) {
      int s = i + k;
      float hz = startHz + (endHz - startHz) * s / total;
      soundPhase += 2 * PI * hz / SOUND_RATE;
      if (soundPhase > 2 * PI) soundPhase -= 2 * PI;
      float env = 1.0;
      if (s < fade) env = (float)s / fade;
      if (total - s < fade) env = (float)(total - s) / fade;
      buf[k] = (int16_t)(sin(soundPhase) * SOUND_VOLUME * env);
    }
    speaker.write((uint8_t *)buf, n * sizeof(int16_t));
  }
}

void playSilence(int ms) {
  int16_t buf[128] = {0};
  int total = SOUND_RATE * ms / 1000;
  for (int i = 0; i < total; i += 128) speaker.write((uint8_t *)buf, sizeof(buf));
}

void playSound(int s) {
  switch (s) {
    case SND_BEEP:     playSweep(1200, 1200, 80); break;
    case SND_HELLO:    playSweep(600, 1200, 120); playSilence(40); playSweep(900, 1600, 160); break;
    case SND_HAPPY:    playSweep(900, 1400, 80); playSweep(1400, 1100, 80); playSweep(1100, 1800, 120); break;
    case SND_QUESTION: playSweep(700, 700, 90); playSweep(700, 1500, 200); break;
    case SND_SCARED:   playSweep(2000, 700, 120); playSilence(30); playSweep(2000, 700, 120); break;
    case SND_SLEEPY:   playSweep(900, 300, 500); break;
    case SND_WHEE:     playSweep(500, 2200, 450); break;
  }
  playSilence(30);
}

void soundTask(void *) {
  int s;
  for (;;) {
    if (xQueueReceive(soundQueue, &s, portMAX_DELAY)) {
      soundPlaying = true;
      playSound(s);
      soundPlaying = false;
    }
  }
}

bool soundBegin() {
  speaker.setPins(PIN_I2S_BCLK, PIN_I2S_WS, PIN_I2S_DOUT);
  if (!speaker.begin(I2S_MODE_STD, SOUND_RATE, I2S_DATA_BIT_WIDTH_16BIT, I2S_SLOT_MODE_MONO)) return false;
  soundQueue = xQueueCreate(4, sizeof(int));
  xTaskCreatePinnedToCore(soundTask, "sound", 4096, NULL, 1, NULL, 0);
  return true;
}

void say(Sound s) {
  int v = s;
  xQueueSend(soundQueue, &v, 0);   // if the queue is full, the sound is skipped
}
