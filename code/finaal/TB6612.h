#ifndef TB6612_H
#define TB6612_H

#include <Arduino.h>

enum MotorSelect {
    MOTOR_A,
    MOTOR_B,
};


class MotorDriver {
public:
    
    MotorDriver(uint8_t pmwA, uint8_t in1A, uint8_t in2A, uint8_t pmwB, uint8_t in1B, uint8_t in2B);
  
    void motor_init(void);
    
    void set_speed(int16_t motor_a, int16_t motor_b);


private:
    
    uint8_t pwmA_pin, pwmB_pin; // PWM pins for motor A and B
    uint8_t in1A_pin, in2A_pin; // Direction control pins for motor A 
    uint8_t in1B_pin, in2B_pin; // Direction control pins for motor B

    uint8_t ChannelA, ChannelB; // PWM channels for motor A and B
    uint32_t pwm_freq; // PWM frequency in Hz (1000-10000) 5000 optimal with finetuning
    uint8_t pwm_res; // PWM resolution in bits (1-20) 8-10 optimal
};

#endif /* TB6612_H */
