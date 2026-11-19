// Dimer's face on the 0.96" ST7735 screen (160 x 80 pixels).
// We draw each frame on an invisible canvas in memory first, then copy it to the screen
// in one go, so the eyes move without flicker.
// Use: faceBegin() once, faceMood(...) / faceLook(...) whenever you like, faceUpdate() every loop.
#pragma once
#include <SPI.h>
#include <Adafruit_GFX.h>
#include <Adafruit_ST7735.h>
#include "dimer_v2_pins.h"
#include "dimer_settings.h"

enum Mood { MOOD_NORMAL, MOOD_HAPPY, MOOD_SURPRISED, MOOD_SCARED, MOOD_SLEEPY, MOOD_DIZZY };

// CS is wired to GND and RES to 3V3, so we pass -1 for both.
Adafruit_ST7735 tft(&SPI, -1, PIN_LCD_DC, -1);
GFXcanvas16 faceCanvas(160, 80);

Mood faceMoodNow = MOOD_NORMAL;
float faceLookX = 0, faceLookY = 0;          // where the eyes are now (-1 .. 1)
float faceLookTargetX = 0, faceLookTargetY = 0;
float faceOpen = 1.0;                         // 1 = eyes open, 0 = shut
unsigned long faceNextBlinkMs = 0, faceBlinkStartMs = 0, faceLastDrawMs = 0;
bool faceBlinking = false;
uint16_t faceEyeColor;

void faceBegin() {
  SPI.begin(PIN_LCD_SCK, -1, PIN_LCD_MOSI, -1);   // only clock and data out; D9 is used for DC
  // The library sends the software reset (0x01) and waits, because RES is not wired to a pin.
  tft.initR(FACE_IPS_PLUGIN ? INITR_MINI160x80_PLUGIN : INITR_MINI160x80);
  tft.setRotation(FACE_ROTATION);
  tft.fillScreen(ST77XX_BLACK);
  faceEyeColor = tft.color565(FACE_EYE_R, FACE_EYE_G, FACE_EYE_B);
  faceNextBlinkMs = millis() + 2000;
}

void faceMood(Mood m) { faceMoodNow = m; }
void faceLook(float x, float y) {             // -1 = left/up, 1 = right/down
  faceLookTargetX = constrain(x, -1, 1);
  faceLookTargetY = constrain(y, -1, 1);
}
void faceBlink() { faceBlinking = true; faceBlinkStartMs = millis(); }

// Draws one eye. cx, cy = centre; side = -1 for the left eye, 1 for the right.
void faceDrawEye(int cx, int cy, int side) {
  GFXcanvas16 &c = faceCanvas;
  uint16_t col = faceEyeColor;
  int w = 30, h = 40;
  if (faceMoodNow == MOOD_SURPRISED) { w = 36; h = 48; }
  if (faceMoodNow == MOOD_SCARED)    { w = 22; h = 30; }
  if (faceMoodNow == MOOD_SLEEPY)    { h = 10; }
  int hh = max(3, (int)(h * faceOpen));

  if (faceMoodNow == MOOD_DIZZY) {          // X-shaped eyes
    for (int t = -2; t <= 2; t++) {
      c.drawLine(cx - 12 + t, cy - 12, cx + 12 + t, cy + 12, col);
      c.drawLine(cx - 12 + t, cy + 12, cx + 12 + t, cy - 12, col);
    }
    return;
  }
  c.fillRoundRect(cx - w / 2, cy - hh / 2, w, hh, min(10, hh / 2), col);

  if (faceMoodNow == MOOD_HAPPY && faceOpen > 0.5) {   // cut the bottom with a black circle: a smiling eye
    c.fillCircle(cx, cy + hh / 2 + 10, w / 2 + 6, ST77XX_BLACK);
  }
  if (faceMoodNow == MOOD_SCARED) {                    // worried eyebrows
    for (int t = 0; t < 3; t++)
      c.drawLine(cx - 14, cy - 22 - side * 4 + t, cx + 14, cy - 22 + side * 4 + t, col);
  }
  if (faceMoodNow == MOOD_SLEEPY) {                    // heavy lid
    c.fillRect(cx - w / 2, cy - hh / 2, w, hh / 2, ST77XX_BLACK);
  }
}

void faceDraw() {
  faceCanvas.fillScreen(ST77XX_BLACK);
  int dx = (int)(faceLookX * 22);
  int dy = (int)(faceLookY * 12);
  faceDrawEye(50 + dx, 40 + dy, -1);
  faceDrawEye(110 + dx, 40 + dy, 1);
  tft.drawRGBBitmap(0, 0, faceCanvas.getBuffer(), 160, 80);
}

void faceUpdate() {
  unsigned long now = millis();
  if (now - faceLastDrawMs < 33) return;      // about 30 pictures a second is plenty
  faceLastDrawMs = now;

  // Eyes glide towards where they should look.
  faceLookX += (faceLookTargetX - faceLookX) * 0.25;
  faceLookY += (faceLookTargetY - faceLookY) * 0.25;

  // Blink by itself every 2 to 6 seconds.
  if (!faceBlinking && now > faceNextBlinkMs && faceMoodNow != MOOD_DIZZY) faceBlink();
  if (faceBlinking) {
    float t = (now - faceBlinkStartMs) / 160.0;   // a blink takes 160 ms
    if (t >= 1) { faceBlinking = false; faceOpen = 1; faceNextBlinkMs = now + random(2000, 6000); }
    else faceOpen = (t < 0.5) ? 1 - t * 2 : (t - 0.5) * 2;
  }
  faceDraw();
}
