import cv2
import zmq
import base64

import time
import numpy as np
from collections import deque
 
tolerance = 17
x_lock = 0
y_lock = 0

IP = '192.168.50.11'

colorUpper = (200, 255, 255)
colorLower = (155, 100, 100)
#相机参数设置
def Setcamera(cap):
    cap.set(6,cv2.VideoWriter.fourcc('M','J','P','G'))
    cap.set(3,128)
    cap.set(4,96)

context = zmq.Context() #init tcp transfer.
footage_socket = context.socket(zmq.PUB)
footage_socket.bind("tcp://*:5555")

camera = cv2.VideoCapture(0)
Setcamera(camera)


# 每0.1S计算一次帧率
t = 0.1 
counter = 0
fps = 0
start_time = time.time()

while(True):
    ret, frame_image = camera.read()
        
#测帧率    
    counter += 1    
    if (time.time() - start_time) > t:
        fps = counter / (time.time() - start_time)
        fps = str(fps)
        counter = 0
        start_time = time.time()       
    cv2.putText(frame_image, "FPS {0}" .format(fps), (10, 30), 1, 1.5, (255, 0, 255), 2)


    hsv = cv2.cvtColor(frame_image, cv2.COLOR_BGR2HSV)
    #cv2.imshow('frame', hsv)
    mask = cv2.inRange(hsv, colorLower, colorUpper)
    #cv2.imshow('frame', mask)
    mask = cv2.erode(mask, None, iterations=2)
    #cv2.imshow('frame', mask)
    mask = cv2.dilate(mask,None,iterations=2)

    encoded, buffer = cv2.imencode('.jpg', frame_image) #sending frame_image.
    jpg_as_text = base64.b64encode(buffer)
    footage_socket.send(jpg_as_text)
    #cv2.imshow('frame', mask)
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
            break
        else:
            print("detected but not locked?")
    if cv2.waitKey(1) == ord('q'):
        break

