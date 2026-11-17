// Dimer V2.1 - pin map for the Seeed XIAO ESP32S3 Sense (brain + camera + microphone in the head).
// The camera and microphone are wired inside the Sense board, so they use no pins below.
// The XIAO has 11 pins (D0-D10). All 11 are used; the rest goes through a PCF8574 I2C expander.
// Leave the microSD card slot empty: it shares D8 and D10 with the display.
#pragma once

// Tracks (DRV8833). One PWM pin per motor on the XIAO, the direction pin on the expander.
// Forward: DIR = 0, PWM = speed. Reverse: DIR = 1, PWM = 255 - speed.
#define PIN_MOT_L_PWM  D0   // DRV8833 AIN1
#define PIN_MOT_R_PWM  D1   // DRV8833 BIN1
#define EXP_MOT_L_DIR  0    // PCF8574 P0 -> DRV8833 AIN2
#define EXP_MOT_R_DIR  1    // PCF8574 P1 -> DRV8833 BIN2

// Head tilt servo (SG90). 0 deg = looking ahead, about 25 deg = looking up. Do not drive past the stop.
#define PIN_SERVO_TILT D2
#define TILT_MIN_DEG   0
#define TILT_MAX_DEG   25

// I2C bus: PCF8574 expander (address 0x20)
#define PIN_I2C_SDA    D4
#define PIN_I2C_SCL    D5
#define EXP_ADDR       0x20

// Table-edge sensors (TCRT5000 DO pin) on the expander. HIGH = no table under the sensor.
#define EXP_EDGE_FL    2    // PCF8574 P2
#define EXP_EDGE_FR    3    // PCF8574 P3

// Audio out (I2S to MAX98357A). The microphone is on the Sense board.
#define PIN_I2S_BCLK   D6
#define PIN_I2S_WS     D7
#define PIN_I2S_DOUT   D3

// Face display (0.96 inch ST7735, SPI). CS wired to GND, RES and BLK wired to 3V3.
#define PIN_LCD_SCK    D8
#define PIN_LCD_DC     D9
#define PIN_LCD_MOSI   D10
