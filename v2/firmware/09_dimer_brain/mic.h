// The microphone on the XIAO Sense camera board (PDM type, wired inside the board:
// clock on GPIO 42, data on GPIO 41). We only use it to hear how loud it is, e.g. a clap.
#pragma once
#include <ESP_I2S.h>

#define MIC_CLK_PIN  42
#define MIC_DATA_PIN 41
I2SClass mic(I2S_NUM_0);   // PDM microphones only work on I2S unit 0

bool micBegin() {
  mic.setPinsPdmRx(MIC_CLK_PIN, MIC_DATA_PIN);
  return mic.begin(I2S_MODE_PDM_RX, 16000, I2S_DATA_BIT_WIDTH_16BIT, I2S_SLOT_MODE_MONO);
}

// Listens for 8 ms and returns how loud the loudest moment was (0 = silent, up to 32767).
int micLoudness() {
  int16_t buf[128];
  size_t got = mic.readBytes((char *)buf, sizeof(buf)) / sizeof(int16_t);
  if (got == 0) return 0;
  long sum = 0;
  for (size_t i = 0; i < got; i++) sum += buf[i];
  int mean = sum / (long)got;                  // remove the steady offset
  int peak = 0;
  for (size_t i = 0; i < got; i++) peak = max(peak, abs(buf[i] - mean));
  return peak;
}
