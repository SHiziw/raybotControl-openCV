#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 通讯协议：[x][x][xxx][x][xxx]
# A部分：A+[...]
# M部分：M+[F/B]+[000]+[F/B]+[000]，分别表示左边的前进/后退+速度，右边的前进/后退+速度
#        对于TSF，M+F+[float],浮点数为两侧波动频率
#        M+L+[float],单独调整左频率,后接终止符X
#        M+R+[float],单独调整右频率,后接终止符X
#        M+U+[float],设置波幅的上确界,后接终止符X
#        M+D+[float],设置波幅的下确界,后接终止符X
# P部分： P+P+[float],比例增益,后接终止符X
#        P+I+[float],积分增益 ,后接终止符X
#        P+D+[float],微分增益,后接终止符X
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

from struct import pack,unpack #用于编码浮点数为字节流
import time
import tkinter as tk
if not debug:
    import serial
    ser = serial.Serial("/dev/ttyAMA0", 9600)

fl = 2.0
fr = 2.0
fu = 2100.0
fd =900.0
tune_old = 1.0
para_list = {"ML":fr,"MR":fl,"MU":fu,"MD":fd}

def hit_me():
    for key in para_list.keys():
        sender(key,para_list[key])
        print_selection("全部命令已发送")

def sender(header,var):
    byte=header.encode("UTF-8") +pack('f',var)+"X".encode("UTF-8")
    if not debug:    
        ser.write(byte)
        time.sleep(0.02)
        ser.write(byte)
    return byte

def sync_method(header,var):
    para_list[header] = float(var.get())
    #print_selection("---------------------------")
    print_selection("表头：{0}，更新为：{1}".format(header,para_list[header]))
    # print_selection("---------------------------")

def trun_method(header,var):
    sender("ML",0.0)
    sender("MR",0.0)
    command = sender(header,var)
    #print_selection("---------------------------")
    print_selection("主动鳍：{0}，频率：{1}".format(header,var))
    # print_selection("---------------------------")

def forward_start_method(event):
    sender("ML",para_list["ML"])
    sender("MR",para_list["MR"])
    print_selection("左频率：{0}，右频率：{1}".format(para_list["ML"],para_list["MR"]))
def end_method(event):
    sender("MR",0.0)
    sender("ML",0.0)
    print_selection(" ")
def print_selection(v):
    l.config(text=v)

# ----循环器----
def looper():
    global tune_old
    if fine_tuning.get() != tune_old:
        tune_old = fine_tuning.get()
        print_selection("微调比例：{0}".format(tune_old))
        sender("ML",para_list["ML"]*float(fine_tuning.get()))
        sender("MR",para_list["ML"]*(-float(fine_tuning.get()) + 2.0))
    root.after(20,looper)   #10ms检查一次
# ----循环器----

root= tk.Tk()
root.title('RB3tcp控制端')
root.geometry('480x320') # 这里的乘号不是 * ，而是小写英文字母 x
if not debug:
    root.attributes('-fullscreen', True)


left_frame = tk.Frame(root,height=320, width=240)
left_frame.place(relx=0.25, rely=0.5, relheight=0.95, relwidth=0.5, anchor='center')
right_frame = tk.Frame(root)
right_frame.place(relx=0.75, rely=0.5, relheight=0.95, relwidth=0.5, anchor='center')

#----左边-----
#布局
botton_frame = tk.Frame(left_frame)
botton_frame.pack(side="top")
arrow_frame = tk.Frame(left_frame)
arrow_frame.pack(side="bottom",fill='both',expand='yes')
#顶部按钮
botton_estabilish = tk.Button(botton_frame, text='退出系统', width=4, height=1, command=root.quit)
botton_estabilish.pack(side="left")
botton_send = tk.Button(botton_frame, text='发送命令', width=4, height=1, command=hit_me)
botton_send.pack(side="right")
#方向键
forward_key = tk.Button(arrow_frame, text='前进', width=4, height=2)
forward_key.bind('<Button-1>',forward_start_method)
forward_key.bind('<ButtonRelease-1>',end_method)
forward_key.place(relx=0.5, rely=0.2, anchor='center')

left_key = tk.Button(arrow_frame, text='左转', width=4, height=2)
left_key.bind('<Button-1>',lambda event:trun_method("MR",para_list["ML"]))
left_key.bind('<ButtonRelease-1>',end_method)
left_key.place(relx=0.3, rely=0.45, anchor='center')

right_key = tk.Button(arrow_frame, text='右转', width=4, height=2)
right_key.bind('<Button-1>',lambda event:trun_method("ML",para_list["MR"]))
right_key.bind('<ButtonRelease-1>',end_method)
right_key.place(relx=0.7, rely=0.45, anchor='center')

#显示框
l = tk.Label(left_frame, bg='yellow', width=20, text=' ',height = 2,wraplength=100)
l.pack(side="top")

#微调摇杆
fine_tuning=tk.DoubleVar()
fine_tuning.set(1.0) 
tuner1 = tk.Scale(left_frame,orient=tk.HORIZONTAL,from_=0.5,to=1.5,font=('黑体',6),resolution=0.01,length=100,variable=fine_tuning)
tuner1.bind('<ButtonRelease-1>',end_method)
tuner1.pack(side="top")
#----左边-----

#----右边-----
freq_left=tk.DoubleVar() #定义变量
freq_right=tk.DoubleVar()
fin_up=tk.DoubleVar()
fin_down=tk.DoubleVar()
freq_left.set(fl) #设定初始值
freq_right.set(fr) 
fin_up.set(fu)
fin_down.set(fd)


tk.Label(right_frame, text='左频率').grid(row=0, column=0, padx=10, pady=5, sticky='w')
tk.Label(right_frame, text='右频率').grid(row=1, column=0, padx=10, pady=5, sticky='w')
tk.Label(right_frame, text='拍动上限').grid(row=2, column=0, padx=10, pady=5, sticky='w')
tk.Label(right_frame, text='拍动下限').grid(row=3, column=0, padx=10, pady=5, sticky='w')

slider1 = tk.Scale(right_frame,orient=tk.HORIZONTAL,from_=0,to=10,font=('黑体',6),resolution=0.01,length=150,variable=freq_left)
slider1.bind('<ButtonRelease-1>',lambda event:sync_method("ML",freq_left))
slider1.grid(row=0, column=1, padx=10, pady=5)

slider2 = tk.Scale(right_frame,orient=tk.HORIZONTAL,from_=0,to=10,font=('黑体',6),resolution=0.01,length=150,variable=freq_right)
slider2.bind('<ButtonRelease-1>',lambda event:sync_method("MR",freq_right))
slider2.grid(row=1, column=1, padx=10, pady=5)

slider3 = tk.Scale(right_frame,orient=tk.HORIZONTAL,from_=900,to=2100,font=('黑体',6),resolution=0.01,length=150,variable=fin_up)
slider3.bind('<ButtonRelease-1>',lambda event:sync_method("MU",fin_up))
slider3.grid(row=2, column=1, padx=10, pady=5)

slider4 = tk.Scale(right_frame,orient=tk.HORIZONTAL,from_=900,to=2100,font=('黑体',6),resolution=0.01,length=150,variable=fin_down)
slider4.bind('<ButtonRelease-1>',lambda event:sync_method("MD",fin_down))
slider4.grid(row=3, column=1, padx=10, pady=5)
#----右边-----


looper()
root.mainloop()
root.destroy()

