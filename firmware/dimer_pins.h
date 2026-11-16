// Dimer main board v0.2 - pin map for ESP32-S3-DevKitC-1 (N16R8)
// Matches pcb/make_board.py. GPIO numbers, not header positions.
#pragma once

// Tracks (DRV8833 motor driver: two inputs per motor, PWM one, hold the other low)
#define PIN_MOT_AIN1 42   // left track
#define PIN_MOT_AIN2 41
#define PIN_MOT_BIN1 40   // right track
#define PIN_MOT_BIN2 39

// Servos (5 V power from the buck converter, 3.3 V signal is fine)
#define PIN_SERVO_PAN    47   // head left/right
#define PIN_SERVO_TILT   21   // head up/down (optional)
#define PIN_SERVO_SHOVEL 38   // may also blink the on-board RGB LED on some dev boards
#define PIN_SERVO_AUX    48   // spare; on-board RGB LED on most clones

// Table-edge sensors (TCRT5000 module, DO pin). HIGH = no table under the sensor.
#define PIN_EDGE_FL 11
#define PIN_EDGE_FR 12
#define PIN_EDGE_RL 13
#define PIN_EDGE_RR 14

// Face display (ST7789 SPI). RES is wired to the board reset, BLK to 3V3.
#define PIN_LCD_CS   4
#define PIN_LCD_DC   5
#define PIN_LCD_MOSI 6
#define PIN_LCD_SCK  7

// Audio (I2S). Microphone and amplifier share the two clock lines.
#define PIN_I2S_BCLK 15
#define PIN_I2S_WS   16
#define PIN_I2S_DOUT 17   // to the on-board MAX98357A (speaker)
#define PIN_I2S_DIN  18   // from the on-board ICS-43434 microphone

// EYE plug: TOF200F distance sensor (I2C, or UART on the same two pins), optional MPU6050 on the spare plug
#define PIN_I2C_SDA 8
#define PIN_I2C_SCL 9

// Misc
#define PIN_VBAT_SENSE 10  // battery / 3.13 (100k : 47k divider), ADC1
#define PIN_BUTTON     1   // to GND, use INPUT_PULLUP
#define PIN_LED_DATA   2   // fin LED strip (WS2812) through 330R
#define PIN_UART_TX    43
#define PIN_UART_RX    44

#define VBAT_DIVIDER   3.128f   // (100k + 47k) / 47k
#define VBAT_LOW_VOLTS 6.4f     // stop driving below this (2S Li-ion)
