#!/usr/bin/python3
import os, serial
import time

ser = serial.Serial("/dev/ttyAMA0", 9600)
ser.flushInput()  # 清空缓冲区

def main():
    while True:
        count = ser.inWaiting()
        if count !=0 :
            recv = ser.read(ser.in_waiting).decode("UTF-8") 
            print(time.time()," ---  recv --> ", recv)
        time.sleep(0.1)



if __name__ == '__main__':
    main()