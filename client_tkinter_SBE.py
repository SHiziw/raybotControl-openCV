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
debug = True

import tkinter as tk
if not debug:
    import serial
    ser = serial.Serial("/dev/ttyAMA0", 9600)

def hit_me():
    if not debug:    
        ser.write("MF000F000".encode("UTF-8"))
def method(event):
    s = '右侧的取值为' + str(right_speed.get())
    global r_command
    #print("---------------------------")
    r_command = str(right_speed.get())
   # print(command)
   # print("---------------------------")



root= tk.Tk()
root.title('RB3tcp控制端')
root.geometry('480x320') # 这里的乘号不是 * ，而是小写英文字母 x
if not debug:
    root.attributes('-fullscreen', True)


botton_frame = tk.Frame(root)
botton_frame.pack()
left_frame = tk.Frame(root)
left_frame.pack(side="left",fill='both',expand='yes')
right_frame = tk.Frame(root)
right_frame.pack(side="right",fill='both',expand='yes')

botton_estabilish = tk.Button(left_frame, text='退出系统', font=('黑体', 6), width=10, height=2, command=root.quit)
botton_estabilish.pack()
 
botton_send = tk.Button(right_frame, text='发送命令', font=('黑体', 6), width=10, height=2, command=hit_me)
botton_send.pack()


right_speed=tk.DoubleVar()
right_slider = tk.Scale(right_frame,orient=tk.HORIZONTAL,from_=-100,to=100,font=('黑体',6),resolution=1,variable=right_speed)
right_slider.bind('<ButtonRelease-1>',method)
right_slider.pack()




root.mainloop()


