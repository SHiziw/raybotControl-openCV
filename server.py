#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cv2
import zmq
import base64
import numpy as np

import socket
import time
import sys
import threading
from MotorDriver import MotorDriver

# define host ip: Rpi's IP
HOST_IP = "127.0.0.1"
HOST_PORT = 1811
print("Starting socket: TCP...")
# 1.create socket object:socket=socket.socket(family,type)
socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("TCP server listen @ %s:%d!" % (HOST_IP, HOST_PORT))
host_addr = (HOST_IP, HOST_PORT)
# 2.bind socket to addr:socket.bind(address)
socket_tcp.bind(host_addr)
# 3.listen connection request:socket.listen(backlog)
socket_tcp.listen(3)
# 5.handle

context = zmq.Context() #init tcp trans to send opencv catched camera frame.
footage_socket = context.socket(zmq.PUB) # zmq的广播模式
footage_socket.bind("tcp://*:5555")

# control 2 motor flags
is_working = 0
instant_shut = 0
l_speed = 0
r_speed = 0
Motor = MotorDriver(is_working, instant_shut)

# aim system init.
tolerance = 17
x_lock = 0
y_lock = 0
# target color.
colorUpper = (200, 255, 255)
colorLower = (155, 100, 100)
#相机参数设置
def Setcamera(cap):
    cap.set(6,cv2.VideoWriter.fourcc('M','J','P','G'))
    cap.set(3,160) #128
    cap.set(4,120) #96
    cap.set(5,30)

# init camera
camera = cv2.VideoCapture(0)
Setcamera(camera)

# 每0.1S计算一次帧率
t = 0.1 
counter = 0
fps = 0
start_time = time.time()

# visual servo control and frame transform powered by openCV.
def visual_servo():
    while(True):
        ret, frame_image = camera.read()
            
        # 测帧率    
        counter += 1    
        if (time.time() - start_time) > t:
            fps = counter / (time.time() - start_time)
            fps = str(fps)
            counter = 0
            start_time = time.time()       
        cv2.putText(frame_image, "FPS {0}" .format(fps), (10, 30), 1, 1.5, (255, 0, 255), 2)


        hsv = cv2.cvtColor(frame_image, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, colorLower, colorUpper)
        mask = cv2.erode(mask, None, iterations=2)    
        mask = cv2.dilate(mask,None,iterations=2)

        encoded, buffer = cv2.imencode('.jpg', frame_image) #sending frame_image.
        jpg_as_text = base64.b64encode(buffer)
        footage_socket.send(jpg_as_text)

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


def tcplink(sock, addr):
    while True:
        try:
            # all data is in data:
            data = sock.recv(1024)
            full_command = data.decode('utf-8')
            head_command = full_command[0:5]
            # if you want to change the data, change here above.
            if len(data) > 0:
                print("Received:%s" % data.decode('utf-8'))
                Motor.run_at_speed(head_command)
                if full_command == 'stop':
                    sock.send(b'stop now.')
                    Motor.stop()
                elif full_command == 'run':
                    sock.send(b'now running.')
                    Motor.runtest()
                cmd_finished = data.decode('utf-8') + ' already has been executed.'
                sock.send(cmd_finished.encode('utf-8'))
                time.sleep(0.1)
                continue
        except KeyboardInterrupt :
            socket_tcp.close()
            sys.exit(1)


# 主循环
while True:
    # 4.waite for client:connection,address=socket.accept(), 接受一个新连接:
    socket_con, client_addr = socket_tcp.accept()
    (client_ip, client_port) = client_addr
    print("Connection accepted from %s." % client_ip)
    socket_con.send(b"Welcome to RPi TCP server!")
    t = threading.Thread(target=tcplink, args=(socket_con, client_addr))
    t.start()



