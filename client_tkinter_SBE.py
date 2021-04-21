#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 通讯协议：[x][x][xxx][x][xxx]
# A部分：A+[...]
# M部分：M+[F/B]+[000]+[F/B]+[000]，分别表示左边的前进/后退+速度，右边的前进/后退+速度
#        对于TSF，M+F+[float],浮点数为两侧波动频率
#        M+L+[float],单独调整左频率
#        M+R+[float],单独调整右频率
#        M+U+[float],设置波幅的上确界
#        M+R+[float],设置波幅的下确界
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
debug = False

import tkinter as tk
if not debug:
    import serial
    ser = serial.Serial("/dev/ttyAMA0", 9600)

def hit_me():
    if not debug:    
        ser.write("MF000F000".encode("UTF-8"))

root= tk.Tk()
root.title('RB3tcp控制端')
root.geometry('480x320') # 这里的乘号不是 * ，而是小写英文字母 x
if not debug:
    root.attributes('-fullscreen', True)


botton_frame = tk.Frame(root)
botton_frame.pack()

botton_estabilish = tk.Button(botton_frame, text='建立连接', font=('黑体', 6), width=10, height=2, command=root.quit)
botton_estabilish.pack(side="left")

botton_send = tk.Button(botton_frame, text='发送命令', font=('黑体', 6), width=10, height=2, command=hit_me)
botton_send.pack(side="right")

root.mainloop()