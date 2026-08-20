#include <TB6612.h>
#include <Arduino.h>
#include "soc/gpio_struct.h" // helper voor GPIO
#include "soc/gpio_reg.h"

// Constructor
MotorDriver::MotorDriver(uint8_t pwmA, uint8_t in1A, uint8_t in2A, uint8_t pwmB, uint8_t in1B, uint8_t in2B)
{
  pwmA_pin = pwmA;
  in1A_pin = in1A;
  in2A_pin = in2A;
  pwmB_pin = pwmB;
  in1B_pin = in1B;
  in2B_pin = in2B;
  

  pwm_freq = 5000;  // standaard 5 kHz
  pwm_res = 8;      // standaard 8-bit
}

void MotorDriver::motor_init(void)
{
  // pin setup
  pinMode(in1A_pin, OUTPUT);
  pinMode(in2A_pin, OUTPUT);
  pinMode(in1B_pin, OUTPUT);
  pinMode(in2B_pin, OUTPUT);
  pinMode(pwmA_pin, OUTPUT);
  pinMode(pwmB_pin, OUTPUT);

  // configureer LEDC PWM
  if (!ledcAttach(pwmA_pin, pwm_freq, pwm_res)) {
    Serial.println("PWM A attach failed!");
  }
  
  if (!ledcAttach(pwmB_pin, pwm_freq, pwm_res)) {
    Serial.println("PWM B attach failed!");
  }

  // reset alle GPIO schakelregisters 
  GPIO.out_w1tc = (1 << in1A_pin) | (1 << in2A_pin) | (1 << in1B_pin) | (1 << in2B_pin);
}

void MotorDriver::set_speed(int16_t motor_a, int16_t motor_b)
{
  int16_t maxDuty = (1 << pwm_res) - 1;

  motor_a = constrain(motor_a, -maxDuty, maxDuty);
  motor_b = constrain(motor_b, -maxDuty, maxDuty);

  // duty berekenen
 
  uint32_t dutyA = abs(motor_a);
  uint32_t dutyB = abs(motor_b);



  // motor A richting
  if (motor_a > 0) {
    GPIO.out_w1ts = (1 << in1A_pin); // 1A hoog 
    GPIO.out_w1tc = (1 << in2A_pin); // 2A laag 
  } else if (motor_a < 0) {
    GPIO.out_w1tc = (1 << in1A_pin); // 1A laag
    GPIO.out_w1ts = (1 << in2A_pin); // 2A hoog
  }

  // motor B richting
  if (motor_b > 0) {
    GPIO.out_w1ts = (1 << in1B_pin); // 1B hoog
    GPIO.out_w1tc = (1 << in2B_pin); // 2B laag
  } else if (motor_b < 0) {
    GPIO.out_w1tc = (1 << in1B_pin); // 1B laag
    GPIO.out_w1ts = (1 << in2B_pin); // 2B hoog
  } 

  // PWM duty schrijven
  ledcWrite(pwmA_pin, dutyA);
  ledcWrite(pwmB_pin, dutyB);
}
