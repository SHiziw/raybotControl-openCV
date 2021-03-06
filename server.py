#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 通讯协议：[x][x][xxx][x][xxx]
# A部分：A+[...]
# M部分：M+[F/B]+[000]+[F/B]+[000]，分别表示左边的前进/后退+速度，右边的前进/后退+速度
#        对于TSF，M+F+[float],浮点数为两侧波动频率
#        M+L+[float],单独调整左频率
#        M+R+[float],单独调整右频率
#        M+U+[float],设置波幅的上确界
#        M+D+[float],设置波幅的下确界
# P部分： P+P+[float],比例增益
#        P+I+[float],积分增益 
#        P+D+[float],微分增益
#C部分：C+[cmd]
#       cmd列表：L陆地模式，W海洋模式，T原色摄像头 C滤色后摄像头
#Q部分：退出，断开tcp连接
#I部分：开启功率采集
#O部分：关闭并保存功率采集
#S部分：直接停止
# title           :server.py
# description     :树莓派控制程序入口，包括了指令接收，图像回传，电机控制，视觉PID伺服控制
#                  Arduino部分则包括了姿态传感器、PID和速度控制
# author          :Vic Lee 
# date            :20210112
# version         :1.2
# notes           :
# python_version  :3.8.3
# ==============================================================================
import cv2
import zmq
import base64
import numpy as np
import time
import csv
import socket
import serial
import threading

import board
from adafruit_ina219 import ADCResolution, BusVoltageRange, INA219

from MotorDriver import MotorDriver
from RayPID import PID

lock = threading.Lock()

#Globale variables
l_speed = 100
r_speed = 100
global_message = ""
auto_tracer = False # a controlable flag.
land_mode = False
global_color = ""
is_saving = False
command_item = ""

# define host ip: Rpi's IP, if you want to use frp, you should set IP to 127.0.0.1
#HOST_IP = "192.168.43.35"
HOST_IP = "192.168.50.99"
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

#context = zmq.Context() #init tcp trans to send opencv catched camera frame.
#footage_socket = context.socket(zmq.PUB) # zmq的广播模式
#footage_socket.bind("tcp://*:5555")

# control 2 motor flags
Motor = MotorDriver()
# a PID controler.
RPID = PID(0.006, 0.0001, 0.005)
# use UART to connect LFC chip
ser_LFC = serial.Serial("/dev/ttyAMA0", 9600)
i2c_bus = board.I2C() # 配置电流功率检测版

ina1 = INA219(i2c_bus,addr=0x40)
ina2 = INA219(i2c_bus,addr=0x41)
ina3 = INA219(i2c_bus,addr=0x42)
ina4 = INA219(i2c_bus,addr=0x43)

ina1.bus_adc_resolution = ADCResolution.ADCRES_12BIT_32S
ina1.shunt_adc_resolution = ADCResolution.ADCRES_12BIT_32S
ina1.bus_voltage_range = BusVoltageRange.RANGE_16V

ina2.bus_adc_resolution = ADCResolution.ADCRES_12BIT_32S
ina2.shunt_adc_resolution = ADCResolution.ADCRES_12BIT_32S
ina2.bus_voltage_range = BusVoltageRange.RANGE_16V

ina3.bus_adc_resolution = ADCResolution.ADCRES_12BIT_32S
ina3.shunt_adc_resolution = ADCResolution.ADCRES_12BIT_32S
ina3.bus_voltage_range = BusVoltageRange.RANGE_16V

ina4.bus_adc_resolution = ADCResolution.ADCRES_12BIT_32S
ina4.shunt_adc_resolution = ADCResolution.ADCRES_12BIT_32S
ina4.bus_voltage_range = BusVoltageRange.RANGE_16V

def set_PID(code):
    if code[1] in ["P","p"]:
        RPID.setKp(float(code[2:]))
    elif code[1] in ["I","i"]:
        RPID.setKi(float(code[2:]))
    elif code[1] in ["D","d"]:
        RPID.setKd(float(code[2:]))
    else:
        pass

def set_color(code):    #包含了一些特殊指令（如陆地模式）
    global land_mode
    global global_color
    if code[1] in ["A","a"]:
        global_color = "A"
    elif code[1] in ["B","b"]:
        global_color = "B"
    elif code[1] in ["C","c"]:
        global_color = "C"
    elif code[1] in ["L","l"]: #开启陆地模式
        land_mode = True
    elif code[1] in ["W","w"]:#海洋模式
        land_mode = False
    else:
        global_color = "T"

def output_handle(output):
    global l_speed
    global r_speed
    global global_message
    global land_mode
    if land_mode == True:
        output = -output
    if r_speed == 100:
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
    if land_mode == False:
        Motor.MotorRun(0, 'forward', r_speed)
        Motor.MotorRun(1, 'forward', l_speed)
    else: 
        Motor.MotorRun(0, 'forward', -r_speed)
        Motor.MotorRun(1, 'forward', -l_speed)
# visual servo control and frame transform powered by openCV.
'''
def visual_servo():
    global auto_tracer
    global global_message
    # target color.
    colorUpper = (26, 212, 174)
    colorLower = (13, 30, 25)
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
        cv2.putText(frame_image, "FPS {0}" .format(fps), (5, 10), 1, 0.5, (255, 0, 255), 1)

        hsv = cv2.cvtColor(frame_image, cv2.COLOR_BGR2HSV)
        mask1 = cv2.inRange(hsv, colorLower, colorUpper)
        mask2 = cv2.erode(mask1, None, iterations=2)    
        mask3 = cv2.dilate(mask2,None,iterations=2)
        target = frame_image
        if global_color in ["C"]:
            target = mask3
        elif global_color in ["B"]:
            target = hsv
        elif global_color in ["A"]:
            target = mask1
        else:
            pass
        encoded, buffer = cv2.imencode('.jpg', target) #sending frame_image.
        jpg_as_text = base64.b64encode(buffer)
        #footage_socket.send(jpg_as_text)

        if (auto_tracer):
            cnts = cv2.findContours(mask3.copy(),cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
            if len(cnts)>0:
                c = max(cnts, key=cv2.contourArea)
                ((X,Y), radius) = cv2.minEnclosingCircle(c)
                delta_Y = Y - frame_height*0.5
                delta_X = X - frame_width*0.5
                RPID.update(delta_X)
                print("Delta: {0}".format(delta_X))
                print(RPID.output)
                output_handle(RPID.output)
                print("l: {0}, r:{1}".format(l_speed, r_speed))
                global_message = "PID controler trying to lock in center..."

            if cv2.waitKey(1) == ord('q'):
                break
 '''           

def command_handler():
    global auto_tracer
    global global_message
    global l_speed
    global r_speed
    global is_saving
    global command_item
    while True:
        try:
            if len(command_item) > 0:
                full_command = command_item
                head_command = full_command[0:9]
                 # if you want to change the data, change here above.
                print("Received:%s" % command_item)
                if head_command[0] == "A":
                    #转到自动模式
                    l_speed = 100
                    r_speed = 100
                    auto_tracer = True
                    global_message = 'now auto sailing.'
                elif head_command[0] == "P":
                    #设置PID
                    set_PID(full_command)
                    global_message = 'setting PID..'
                elif head_command[0] == "C":
                    #设置PID
                    set_color(full_command)
                    global_message = 'setting color..'
                elif head_command[0] == "M":
                    auto_tracer = False
                    Motor.run_at_speed(head_command)
                    global_message = command_item + ' already has been executed.'
                elif head_command[0] == "S":
                    #停机
                    auto_tracer = False
                    Motor.stop()
                    global_message = 'now stopped.'
                elif head_command[0] == "Q":
                    Motor.stop()
                    #退出连接，请检查还需要补充吗
                    auto_tracer = False
                    global_message = "closed"
                elif head_command[0] == "I":
                    is_saving = True
                    global_message = "开始采集"
                    #开始功率采集写入
                elif head_command[0] == "O":    
                    is_saving = False
                    global_message = "停止采集" 
                    #停止功率采集写入
                else:
                    global_message = command_item + ' the data has been broken during transform!'
            command_item = ""
            time.sleep(0.01)

        except Exception :
            print("command handler: error.")
            auto_tracer = False
            break

def LFC_reader():
    global command_item
    while True:
        count = ser_LFC.inWaiting()
        if count >8 : # if string long enough
            command_item = ser_LFC.read(9).decode("UTF-8") # read only one command 
        time.sleep(0.01)

def LFC_writer():
    global global_message
    while True:
        try:
            if global_message == "NaN":
                pass
            elif global_message == "closed":
                global_message = "NaN"
                break
            elif len(global_message) > 0:
                lock.acquire()
                ser_LFC.write(global_message.encode("UTF-8"))
                global_message = "NaN"
                lock.release()
            time.sleep(0.01)
        except Exception :
            print("writer: LFC connect closed. error.")
            break

def tcp_server():
    i = 0
    while True:
       i += 1
       tcp_client, client_addr = socket_tcp.accept() # blocked point！阻塞式！
       (client_ip, client_port) = client_addr
       print("Connection accepted from {0}: {1}.".format(client_ip,client_port))
       tcp_client.send(b"Welcome to RPi TCP server!")
       reader = threading.Thread(name="tcp_reader_{}".format(i), target=tcp_reader, args=(tcp_client,))
       reader.start()
       writer = threading.Thread(name="tcp_writer_{}".format(i), target=tcp_writer, args=(tcp_client,))
       writer.start()

def tcp_reader(tcp_client):
    global command_item
    while True:
        try:
            command_item = tcp_client.recv(128).decode('utf-8')
            time.sleep(0.01)
        except Exception :
            print("reader: tcp connect closed. error.")
            tcp_client.shutdown(2)
            tcp_client.close()
            break

def tcp_writer(tcp_client):
    global global_message
    while True:
        try:
            if global_message == "NaN":
                pass
            elif global_message == "closed":
                global_message = "NaN"
                tcp_client.shutdown(2)
                tcp_client.close()
                break
            elif len(global_message) > 0:
                lock.acquire()
                tcp_client.send(global_message.encode('utf-8'))
                global_message = "NaN"
                lock.release()
            time.sleep(0.01)
        except Exception :
            print("writer: tcp connect closed. error.")
            break

def data_saving():
    global is_saving
    global global_message
    while True:
        if  is_saving:
            with open("/home/pi/raybotControl/power_{}.csv".format(int(round(time.time()*1000))),"w", newline='') as csvfile: 
                writer = csv.writer(csvfile)
                t=int(round(time.time()*1000))
                writer.writerow([time.asctime(time.localtime(t/1000)),t])
                writer.writerow(["passed_time","bus_voltage1", "shunt_voltage1", "power1", "current1", "bus_voltage2", "shunt_voltage2", "power2", "current2"])
                while is_saving:
                    bus_voltage1 = ina1.bus_voltage        # voltage on V- (load side)
                    shunt_voltage1 = ina1.shunt_voltage    # voltage between V+ and V- across the shunt
                    power1 = ina1.power
                    current1 = ina1.current                # current in mA

                    bus_voltage2 = ina2.bus_voltage        # voltage on V- (load side)
                    shunt_voltage2 = ina2.shunt_voltage    # voltage between V+ and V- across the shunt
                    power2 = ina2.power
                    current2 = ina2.current                # current in mA
                    
                    bus_voltage3 = ina3.bus_voltage        # voltage on V- (load side)
                    shunt_voltage3 = ina3.shunt_voltage    # voltage between V+ and V- across the shunt
                    power3 = ina3.power
                    current3 = ina3.current                # current in mA
                    
                    bus_voltage4 = ina4.bus_voltage        # voltage on V- (load side)
                    shunt_voltage4 = ina4.shunt_voltage    # voltage between V+ and V- across the shunt
                    power4 = ina4.power
                    current4 = ina4.current                # current in mA
    
                    writer.writerow([int(round(time.time()*1000))-t,bus_voltage1, shunt_voltage1, power1, current1, bus_voltage2,shunt_voltage2,power2,current2])
                    time.sleep(0.1)
            global_message = "文件写入完成{0}".format(time.asctime(time.localtime(time.time()))) # 存在显示不及时的问题 TO-DO
        time.sleep(0.01)

t1=threading.Thread(name="serial_reading_thread", target=LFC_reader) 
t1.start()
#t2 = threading.Thread(name="Opencv_PID", target=visual_servo)#开启视觉伺服控制线程
#t2.start()
t3 = threading.Thread(name="data_saving", target=data_saving)
t3.start()

t4 = threading.Thread(name="tcp_server", target=tcp_server)
t4.start()

command_handler()