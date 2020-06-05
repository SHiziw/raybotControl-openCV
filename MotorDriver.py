import time
import math
import smbus
from PCA9685 import PCA9685

Dir = [
    'forward',
    'backward',
]
pwm = PCA9685(0x40, debug=False)
pwm.setPWMFreq(800)

class MotorDriver():
    def __init__(self, is_working, instant_shut):
        self.PWMA = 0
        self.AIN1 = 1
        self.AIN2 = 2
        self.PWMB = 5
        self.BIN1 = 3
        self.BIN2 = 4
        self.is_working = is_working
        self.instant_shut = instant_shut

    def MotorRun(self, motor, index, speed):
        if speed > 100:
            return
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


    def runtest(self, count=5):
        n = 0
        while n < count:
            self.MotorRun(0, 'forward', 50)
            time.sleep(2.0)
            self.MotorRun(0, 'backward', 30)
            time.sleep(3.0)
            self.MotorStop(0)
            self.MotorStop(1)
            time.sleep(1.0)
            n += 1

    def run_at_speed(self, head_command):
        # use head_command(recieve from client) to change the motor.
        if head_command[0] in ['r', 'R']:
            mtr = 0
        elif  head_command[0] in ['l', 'L']:
            mtr = 1
        else:
            return
        if head_command[1] in ['f', 'F']:
            idx = 'forward'
        elif  head_command[1] in ['b', 'B']:
            idx = 'backward'
        else: 
            return

        spd = int(head_command[2:5])
        if spd <= 100:
            if spd >= 0:
                self.MotorRun(mtr, idx, spd)
            else:
                return
        else:
            return

        