// Dimer V2 (half size) - pin map for the ESP32-S3 Super Mini.
// The board exposes GPIO 1-13, 43 and 44. All 15 are used. Check the labels printed on your board.
// No custom board: every line below is one jumper wire.
#pragma once

// Tracks (DRV8833: two inputs per motor, PWM one, hold the other low)
#define PIN_MOT_AIN1 1    // left track (rear motor)
#define PIN_MOT_AIN2 2
#define PIN_MOT_BIN1 3    // right track (front motor)
#define PIN_MOT_BIN2 4

// Table-edge sensors (TCRT5000 module, DO pin). HIGH = no table under the sensor.
// Front pair only. Reverse only over ground the robot has just driven.
#define PIN_EDGE_FL 5
#define PIN_EDGE_FR 6

// Face display (0.96 inch ST7735, 80x160). CS wired to GND, RES and BLK wired to 3V3.
#define PIN_LCD_SCK  7
#define PIN_LCD_MOSI 8
#define PIN_LCD_DC   9

// Audio (I2S). Microphone and amplifier share the two clock lines.
#define PIN_I2S_BCLK 10
#define PIN_I2S_WS   11
#define PIN_I2S_DOUT 12   // to MAX98357A DIN (speaker)
#define PIN_I2S_DIN  13   // from INMP441 SD (microphone)

// I2C bus (distance sensor VL53L0X). The USB port is used for programming and logs, so the UART pins are free.
#define PIN_I2C_SDA 43
#define PIN_I2C_SCL 44

// No servos, no battery-voltage sense, no LED strip in V2.
