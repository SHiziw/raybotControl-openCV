import time
import math
import smbus
from PCA9685 import PCA9685

Dir = [
    'forward',
    'backward',
]
pwm = PCA9685(0x46, debug=False)
pwm.setPWMFreq(800)

class MotorDriver():
    def __init__(self):
        self.PWMA = 0
        self.AIN1 = 1
        self.AIN2 = 2
        self.PWMB = 5
        self.BIN1 = 3
        self.BIN2 = 4

    def MotorRun(self, motor, index, speed):
        if speed > 100:
            speed = 100
        elif speed < 10:
            if speed >-10:
                speed = 0
            elif speed >-100:
                index = 'backward'
                speed = -speed
            else :
                speed = 100
                index = 'backward'
        else:
            pass

        if(motor == 0):
            pwm.setDutycycle(self.PWMA, speed)
            if(index == Dir[0]):
                pwm.setLevel(self.AIN1, 0)
                pwm.setLevel(self.AIN2, 1)
            else:
                pwm.setLevel(self.AIN1, 1)
                pwm.setLevel(self.AIN2, 0)
        else:
            pwm.setDutycycle(self.PWMB, speed)
            if(index == Dir[0]):
                pwm.setLevel(self.BIN1, 0)
                pwm.setLevel(self.BIN2, 1)
            else:
                pwm.setLevel(self.BIN1, 1)
                pwm.setLevel(self.BIN2, 0)

    def MotorStop(self, motor):
        if (motor == 0):
            pwm.setDutycycle(self.PWMA, 0)
        else:
            pwm.setDutycycle(self.PWMB, 0)
    
    def stop(self):
        print("stop!")
        self.MotorStop(0)
        self.MotorStop(1)



    def run_at_speed(self, head_command):
        # use head_command(recieve from client) to change the motor.
        if head_command[0] in ['M', 'm']:
            pass
        elif  head_command[0] in ['A', 'a']:
            # 自动模式！
            print("error in mode!")
        else:
            return

        if head_command[1] in ['f', 'F']:
            left_idx = 'forward'
        elif  head_command[1] in ['b', 'B']:
            left_idx = 'backward'
        else: 
            return
        if head_command[5] in ['f', 'F']:
            right_idx = 'forward'
        elif  head_command[5] in ['b', 'B']:
            right_idx = 'backward'
        else: 
            return

        left_spd = int(head_command[2:5])
        if left_spd <= 100:
            if left_spd >= 0:
                self.MotorRun(1, left_idx, left_spd)
            else:
                return
        else:
            return

        right_spd = int(head_command[6:9])
        if right_spd <= 100:
            if right_spd >= 0:
                self.MotorRun(0, right_idx, right_spd)
            else:
                return
        else:
            return
        