// The I/O expander (PCA9534 / TCA9534 at address 0x20) on the power board.
// It gives the XIAO 8 extra pins over just two wires (the I2C bus, SDA and SCL).
// P0, P1 = track directions, P2, P3 = edge sensors, P4 = motor driver on/off.
#pragma once
#include <Wire.h>
#include "dimer_v2_pins.h"

#define EXP_REG_INPUT   0x00
#define EXP_REG_OUTPUT  0x01
#define EXP_REG_CONFIG  0x03

uint8_t expOutputBits = 0x00;   // what we last wrote to the output pins
bool expanderOk = false;

bool expWriteReg(uint8_t reg, uint8_t value) {
  Wire.beginTransmission(EXP_ADDR);
  Wire.write(reg);
  Wire.write(value);
  return Wire.endTransmission() == 0;   // 0 means the chip answered
}

int expReadReg(uint8_t reg) {           // returns -1 if the chip did not answer
  Wire.beginTransmission(EXP_ADDR);
  Wire.write(reg);
  if (Wire.endTransmission(false) != 0) return -1;
  if (Wire.requestFrom((uint8_t)EXP_ADDR, (uint8_t)1) != 1) return -1;
  return Wire.read();
}

// Call once in setup(). Order from the pin map: outputs low first, then the pin directions.
bool expanderBegin() {
  Wire.begin(PIN_I2C_SDA, PIN_I2C_SCL, 100000);
  expOutputBits = 0x00;
  expanderOk = expWriteReg(EXP_REG_OUTPUT, 0x00) && expWriteReg(EXP_REG_CONFIG, 0xEC);
  return expanderOk;
}

void expSetPin(uint8_t pin, bool high) {
  if (high) expOutputBits |= (1 << pin);
  else      expOutputBits &= ~(1 << pin);
  expWriteReg(EXP_REG_OUTPUT, expOutputBits);
}

// Edge sensors: true means "no table under this sensor".
// If the chip does not answer we also say true, so the robot stops instead of driving off.
bool edgeLeftNoTable() {
  int v = expReadReg(EXP_REG_INPUT);
  if (v < 0) return true;
  return v & (1 << EXP_EDGE_FL);
}
bool edgeRightNoTable() {
  int v = expReadReg(EXP_REG_INPUT);
  if (v < 0) return true;
  return v & (1 << EXP_EDGE_FR);
}

// Reads both edge sensors with one question to the chip (faster than asking twice).
// Returns false if the chip did not answer; then both are set to true, so the robot stops.
bool edgesRead(bool &left, bool &right) {
  int v = expReadReg(EXP_REG_INPUT);
  if (v < 0) { left = right = true; return false; }
  left = v & (1 << EXP_EDGE_FL);
  right = v & (1 << EXP_EDGE_FR);
  return true;
}
