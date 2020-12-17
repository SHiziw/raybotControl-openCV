#!/usr/bin/python3
import os, serial
import time

ser = serial.Serial("/dev/ttyAMA0", 9600)


def main():
    while True:
        print("type in your command：",end="")
        send_thing = input()
        if send_thing != None:
            print("sending: {0} ...".format(send_thing))
            ser.write(send_thing.encode("UTF-8"))
            print("OK!")
        time.sleep(0.1)
   
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        if ser != None:
            ser.close()