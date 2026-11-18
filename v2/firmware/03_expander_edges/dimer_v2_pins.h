// Dimer V2.1 - pin map for the Seeed XIAO ESP32S3 Sense (brain + camera + microphone in the head).
// The camera and microphone are wired inside the Sense board, so they use no pins below.
// The XIAO has 11 pins (D0-D10). All 11 are used; the rest goes through the PCA9534 I2C expander
// on the power board (v2/pcb). The XIAO reaches the power board over 8 jumper wires, plugged into
// the board's HEAD pins:
//   HEAD row J8:  5V  GND  SDA(D4)  SCL(D5)    5V feeds the XIAO's 5V pin (through a diode on the board,
//                                              so the XIAO's own USB cable cannot back-feed the board)
//   J9:           SERVO(D2)  GND  3V  GND       3V/GND spare for a later I2C sensor
//   J11 (PL PR):  PWM L(D0)  PWM R(D1)
// Board plugs: EDGE L / EDGE R (V G S) for the TCRT5000 DO pins, TILT (G 5V S) for the servo,
// MOT L / MOT R for the motors.
// Charge lights on the board: red = charging, green = full.
// Leave the microSD card slot empty: it shares D8 and D10 with the display.
#pragma once

// Tracks (DRV8833). One PWM pin per motor on the XIAO, the direction pin on the expander.
// Forward: DIR = 0, PWM = speed. Reverse: DIR = 1, PWM = 255 - speed.
#define PIN_MOT_L_PWM  D0   // DRV8833 AIN1
#define PIN_MOT_R_PWM  D1   // DRV8833 BIN1
#define EXP_MOT_L_DIR  0    // PCA9534 P0 -> DRV8833 AIN2 (10k pull-down)
#define EXP_MOT_R_DIR  1    // PCA9534 P1 -> DRV8833 BIN2 (10k pull-down)
#define EXP_MOT_SLEEP  4    // PCA9534 P4 -> DRV8833 nSLEEP (10k pull-down): motors are off until this is 1
// Start-up order: write output register 0x01 = 0x00 first, then config register 0x03 = 0xEC
// (P0, P1, P4 outputs; the rest inputs), then set P4 = 1 to wake the motor driver.
// Before reversing a motor, set its PWM to 0 for ~20 ms.

// Head tilt servo (SG90). 0 deg = looking ahead, about 25 deg = looking up. Do not drive past the stop.
#define PIN_SERVO_TILT D2
#define TILT_MIN_DEG   0
#define TILT_MAX_DEG   25

// I2C bus: PCA9534 expander (address 0x20). Registers: 0x00 input, 0x01 output, 0x02 polarity, 0x03 config (1 = input)
#define PIN_I2C_SDA    D4
#define PIN_I2C_SCL    D5
#define EXP_ADDR       0x20   // A0-A2 tied to GND on the power board; it also has the 4.7k pull-ups

// Table-edge sensors (TCRT5000 DO pin) on the expander. HIGH = no table under the sensor.
#define EXP_EDGE_FL    2    // PCA9534 P2
#define EXP_EDGE_FR    3    // PCA9534 P3

// Audio out (I2S to MAX98357A). The microphone is on the Sense board.
#define PIN_I2S_BCLK   D6
#define PIN_I2S_WS     D7
#define PIN_I2S_DOUT   D3

// Face display (0.96 inch ST7735, SPI). CS wired to GND, RES and BLK wired to 3V3 (use a 1-to-3 dupont splitter
// from the XIAO 3V3 pin). RES is not driven, so send the software reset command (0x01) and wait 120 ms at start-up.
#define PIN_LCD_SCK    D8
#define PIN_LCD_DC     D9
#define PIN_LCD_MOSI   D10
