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
from RayPID import PID
lock = threading.Lock()

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
Motor = MotorDriver()
#a PID controler.
RPID = PID(1, 0.1, 0.1)
#Globale variables
l_speed = 100
r_speed = 100
global_message = ""
auto_tracer = False # a controlable flag.

def output_handle(output):
    global l_speed
    global r_speed
    global global_message
    if r == 100:
        l_speed = l_speed + output
        if l_speed>100:
           r_speed = r_speed - (l_speed-100)
           l_speed = 100
    elif l_speed == 100:
        r_speed = r_speed - output
        if r_speed > 100:
            l_speed = l_speed - (r_speed-100)
            r_speed = 100
    else:
        print("wrong speed!")
        global_message = "handle get wrong speed!"
    Motor.MotorRun(1, 'forward', l_speed)
    Motor.MotorRun(0, 'forward', r_speed)

# visual servo control and frame transform powered by openCV.
def visual_servo():
    global auto_tracer
    global global_message
    # target color.
    colorUpper = (200, 255, 255)
    colorLower = (155, 100, 100)
    frame_width = 160
    frame_height = 120

    #相机参数设置
    def Setcamera(cap):
        cap.set(6,cv2.VideoWriter.fourcc('M','J','P','G'))
        cap.set(3,frame_width) #128
        cap.set(4,frame_height) #96
        cap.set(5,30)

    # init camera
    camera = cv2.VideoCapture(0)
    Setcamera(camera)

    # 每0.1S计算一次帧率
    t = 0.1 
    counter = 0
    fps = 0
    start_time = time.time()
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

        while (auto_tracer):
            cnts = cv2.findContours(mask.copy(),cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
            if len(cnts)>0:
                c = max(cnts, key=cv2.contourArea)
                ((X,Y), radius) = cv2.minEnclosingCircle(c)

                delta_Y = Y - frame_height
                delta_X = X - frame_width
                RPID.update(delta_X)
                output_handle(RPID.output)
                print("trying to lock in center...")
                global_message = "PID controler trying to lock in center..."

            if cv2.waitKey(1) == ord('q'):
                break
            

def tcplink(sock, addr):
    global auto_tracer
    global global_message
    while True:
        try:
            # all data is in data:
            data_buffer = []
            while True:
                # 每次最多接收16字节:
                d = sock.recv(16)
                if d:
                    data_buffer.append(d)
                else:
                    break
            data = b''.join(data_buffer)
            full_command = data.decode('utf-8')
            head_command = full_command[0:9]
            # if you want to change the data, change here above.
            if len(data) > 0:
                print("Received:%s" % data.decode('utf-8'))
                if head_command[0] == "A":
                    #转到自动模式
                    auto_tracer = True
                    sock.send(b'now auto sailing.')
                elif head_command[0] == "M":
                    auto_tracer = False
                    Motor.run_at_speed(head_command)
                    cmd_finished = data.decode('utf-8') + ' already has been executed.'
                    sock.send(cmd_finished.encode('utf-8'))
                 elif head_command[0] == "S":
                    Motor.stop()
                    sock.send(b'now stopped.')
                elif head_command[0] == "Q":
                    Motor.stop()
                    #退出连接，请检查还需要补充吗
                    socket_tcp.close()
                else:
                    cmd_finished = data.decode('utf-8') + ' the data has been broken during transform!'
                    sock.send(cmd_finished.encode('utf-8'))
            if len(global_message) > 0:
                lock.acquire()
                sock.send(global_message.encode('utf-8'))
                global_message = ""
                lock.release()


        except KeyboardInterrupt :
            auto_tracer = False
            socket_tcp.close()
            sys.exit(1)

#开启视觉伺服控制线程
t2 = threading.Thread(name="Opencv_PID", target=visual_servo, args=None)
t2.start()

while True:
    # 4.waite for client:connection,address=socket.accept(), 接受一个新连接:
    socket_con, client_addr = socket_tcp.accept() # blocked point！阻塞式！
    (client_ip, client_port) = client_addr
    print("Connection accepted from %s." % client_ip)
    socket_con.send(b"Welcome to RPi TCP server!")
    t1 = threading.Thread(name="TCP_control_thread", target=tcplink, args=(socket_con, client_addr))
    
    t1.start()

