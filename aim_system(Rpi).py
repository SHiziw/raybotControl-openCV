import cv2
import time
import argparse
import imutils
import numpy as np
from collections import deque
 
tolerance = 17
x_lock = 0
y_lock = 0

colorUpper = (44, 255, 255)
coloerLower = (24, 100, 100)

ap = argparse.ArgumentParser()
ap.add_argument("-b", "--buffer", type=int, default=64,help="max buffer size")
args = vars(ap.parse_args())
pts = deque(maxlen=args["buffer"])

camera = cv2.VideoCapture(0)
#camera = picamera.PiCamera()
#camera.resolution = (640,480)
#camera.framerate = 20
#rawCapture = PiRGBArray(camera, size=(640,480))

width, height, fps = camera.get(3), camera.get(4), camera.get(5)
print(width, height, fps)

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    frame_image = frame.array

    hsv = cv2.cvtColor(frame_image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, colorLower, colorUpper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask,None,iterations=2)
    cnts = cv2.findContours(mask.copy(),cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
    if len(cnts)>0:
        c = max(cnts, key=cv2.contourArea)
        ((X,Y), radius) = cv2.minEnclosingCircle(c)

        if Y < (240-tolerance):
            error = (240-Y)/5
            print("up   (error:%d"%(error))
            y_lock = 0
        elif Y > (240+tolerance):
            error = (Y-240)/5
            print("down   (error:%d"%(error))
            y_lock = 0
        else:
            y_lock = 1

        if X < (320-tolerance):
            error = (320-X)/5
            print("left   (error:%d"%(error))
            x_lock = 0
        elif X > (320+tolerance):
            error = (X-320)/5
            print("right   (error:%d"%(error))
            x_lock = 0
        else:
            x_lock = 1

        if x_lock ==1 and y_lock == 1:
            print("locked!")
        else:
            print("detected but not locked?")

while(True):
    # 获取一帧
    ret, frame = camera.read()
    # 将这帧转换为灰度图
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    cv2.imshow('frame', gray)
    if cv2.waitKey(1) == ord('q'):
        break



