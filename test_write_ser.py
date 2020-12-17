#!/usr/bin/python3
import os, serial
import time

ser = serial.Serial("/dev/ttyAMA0", 9600)


def main():
    while True:
        send_thing = input()
        if send_thing != None:
            print("sending: {0}".format(send_thing))
            ser.write(send_thing)
        time.sleep(0.1)
   
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        if ser != None:
            ser.close()