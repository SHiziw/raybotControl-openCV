#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 通讯协议：[x][x][xxx][x][xxx]
# A部分：A+[...]
# M部分：M+[F/B]+[000]+[F/B]+[000]，分别表示左边的前进/后退+速度，右边的前进/后退+速度
#        对于TSF，M+F+[float],浮点数为波动频率
#        M+L+[float],左转
#        M+R+[float],右转
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
# version         :1.1
# notes           :
# python_version  :3.8.3
# ==============================================================================

import numpy as np
from PIL import ImageTk, Image

import socket
import time
import threading
import tkinter as tk
from tkinter.simpledialog import askstring, askinteger, askfloat

#RPi's IP
#SERVER_IP = "192.168.43.35"
SERVER_IP = "192.168.50.99"
SERVER_PORT = 1811
server_addr = (SERVER_IP, SERVER_PORT)
# waiting for a recieve from server.
is_conneted = False
received_data = "no data received..."
l_command = "100"
l_command_old = "100" 
r_command = "100"
r_command_old = "100" 
socket_tcp = None

#context = zmq.Context()
#footage_socket = context.socket(zmq.SUB)
#footage_socket.connect('tcp://%s:5555'%SERVER_IP)
#footage_socket.setsockopt(zmq.SUBSCRIBE,''.encode('utf-8'))  # 接收所有消息


def read_from_server():
    global is_conneted
    global received_data
    global socket_tcp
    while is_conneted:
        try:
            data = socket_tcp.recv(1024)
            full_command = data.decode('utf-8')
            if len(data)>0:
                # decode as utf-8
                received_data = data.decode('utf-8')
                print("Received: %s" % received_data)
            continue
        except Exception:
            is_conneted = False
            socket_tcp.close()

def send_commands():
    global l_command
    global l_command_old
    global r_command
    global r_command_old
    global is_conneted
    while is_conneted:
        try:
            if l_command != l_command_old: 
                transl = "M"+standard_command(l_command)+standard_command(r_command)
                # encode to ascii
                socket_tcp.send(transl.encode('utf-8')) 
                l_command_old = l_command
            if r_command != r_command_old: 
                transr = "M"+standard_command(l_command)+standard_command(r_command)
                # encode to ascii
                socket_tcp.send(transr.encode('utf-8')) 
                r_command_old = r_command
             
        except KeyboardInterrupt:
            is_conneted = False
            socket_tcp.close()

        time.sleep(0.03)
def close_tcplink():
    global is_conneted
    global received_data
    is_conneted = False
    socket_tcp.send(b'QB100B100') 
    received_data = "  "
    socket_tcp.close()
    print("socket closed!")

def backgroud_establish():
    global is_conneted
    global socket_tcp
    print("Starting socket: TCP...")
    socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    started_time = time.time()
    while True:
        try:
            now_time = time.time()
            if now_time - started_time > 10:
                print("time out...")
                return
            print("Connecting to server @ %s:%d..." %(SERVER_IP, SERVER_PORT))
            socket_tcp.connect(server_addr)
            is_conneted = True
            break
        except Exception:
            print("Can't connect to server,try it latter!")
            time.sleep(1)
            continue
    print("Please tell me what should I do with commands!")

    t1 = threading.Thread(name="reader",target=read_from_server)
    t1.start()
    t2 = threading.Thread(name="sender",target=send_commands)
    t2.start()

def sync_command():
    global received_data
    global is_conneted

    data_from_raybot3.set(received_data)
    
    #frame = footage_socket.recv_string()
    #img = base64.b64decode(frame)
    #npimg = np.frombuffer(img, dtype=np.uint8)
    #source = cv2.imdecode(npimg, 1)
    #cv2image = cv2.cvtColor(source, cv2.COLOR_BGR2RGB)
    #cv2image = cv2.resize(cv2image, (800,600), interpolation = cv2.INTER_AREA)
    #img = Image.fromarray(cv2image)
    #imgtk = ImageTk.PhotoImage(image=img)
    #lmain.configure(image=imgtk)
    lmain.update()
    
    if is_conneted == False:
        connection_status.set('trying to connect Raybot3...')
    else:
        connection_status.set('Raybot3 online!')
    left_subtitle.configure(text=str(left_speed.get()))
    right_subtitle.configure(text=str(right_speed.get())) 
    root.after(0,sync_command)   # 每隔1s调用函数 gettime 自身获取时间

def set_KP():
    res = askfloat("设置KP", "将Kp增益设置为：")
    command = "PP"+str(res)
    socket_tcp.send(command.encode('utf-8'))
    print("Kp: "+str(res))
def set_KI():
    res = askfloat("设置Ki", "将Ki增益设置为：")
    command = "PI"+str(res)
    socket_tcp.send(command.encode('utf-8'))
    print("Ki: "+str(res))
def set_KD():
    res = askfloat("设置Kd", "将Kd增益设置为：")
    command = "PD"+str(res)
    socket_tcp.send(command.encode('utf-8'))
    print("Kd: "+str(res))

def show(event):
    s = '左侧的取值为' + str(left_speed.get())
    global l_command
    #print("---------------------------")
    l_command = str(left_speed.get())
   # print(command)
   # print("---------------------------")
    left_label.config(text=s)
def showR(event):
    s = '右侧的取值为' + str(right_speed.get())
    global r_command
    #print("---------------------------")
    r_command = str(right_speed.get())
   # print(command)
   # print("---------------------------")
    right_label.config(text=s)
def standard_command(command):
    cmd = float(command)
    print("cmd is "+str(cmd))
    if cmd <10.0 and cmd>-10.0:
        return "f000"
    elif cmd == 100.0:
        return "f100"
    elif cmd == -100.0:
        return "b100"
    elif cmd<0.0:
        return "b"+"0"+str(-1*cmd)[0:2]
    elif cmd>0.0:
        return "f"+"0"+str(cmd)[0:2]
    else: return "f000"

def do_job(x):  #处理C字头命令
    cmd = "C"+x
    socket_tcp.send(cmd.encode('utf-8')) 

def command_up():
    socket_tcp.send("MF{0}F{1}".format(standard_command(l_command)[1:],standard_command(r_command)[1:]).encode('utf-8')) 
def command_down():
    socket_tcp.send('MB{0}B{0}'.format(standard_command(l_command)[1:],standard_command(r_command)[1:]).encode('utf-8')) 
def command_left():
    socket_tcp.send('MB{0}F{0}'.format(standard_command(l_command)[1:],standard_command(r_command)[1:]).encode('utf-8'))
def command_right():
    socket_tcp.send('MF{0}B{0}'.format(standard_command(l_command)[1:],standard_command(r_command)[1:]).encode('utf-8'))
def command_stop():
    socket_tcp.send(b'MF000F000')
def command_auto():
    socket_tcp.send(b'AF100F100')
def command_record():
    socket_tcp.send(b'IF100F100')
def command_stop_record():
    socket_tcp.send(b'OF100F100')    

def hit_me():
    global is_conneted
    if is_conneted == False:
        backgroud_establish()
    else:
        connection_status.set('Raybot3 is online!')

root= tk.Tk()
root.title('RB3tcp控制端')
root.geometry('480x800') # 这里的乘号不是 * ，而是小写英文字母 x

connection_status = tk.StringVar()
l = tk.Label(root, textvariable=connection_status)
l.pack()

botton_frame = tk.Frame(root)
botton_frame.pack()
botton_estabilish = tk.Button(botton_frame, text='建立连接', font=('黑体', 6), width=10, height=1, command=hit_me)
botton_close = tk.Button(botton_frame, text='断开连接', font=('黑体', 6), width=10, height=1, command=close_tcplink)
botton_auto = tk.Button(botton_frame, text='自动模式', font=('黑体', 6), width=10, height=1, command=command_auto)
botton_estabilish.pack(side="left")
botton_close.pack(side="left")
botton_auto.pack()

botton_frame2 = tk.Frame(root)
botton_frame2.pack()
botton_record = tk.Button(botton_frame2, text='开始采集', font=('黑体', 6), width=10, height=1, command=command_record)
botton_stop_record = tk.Button(botton_frame2, text='停止采集', font=('黑体', 6), width=10, height=1, command=command_stop_record)
botton_record.pack(side="left")
botton_stop_record.pack(side="left")

l = tk.Label(root, width=10, height=1, text=" ")
l.pack()

lmain = tk.Label(root)
lmain.pack()

l = tk.Label(root, width=10, height=1, text=" ")
l.pack()
arrow_frame = tk.Frame(root)
arrow_frame.pack()
arrow_frame0 = tk.Frame(arrow_frame)
arrow_frame1 = tk.Frame(arrow_frame)
arrow_frame2 = tk.Frame(arrow_frame)
arrow_frame0.pack(side="left")
arrow_frame1.pack(side="left")
arrow_frame2.pack(side="right")
img_left = tk.PhotoImage(file='left.png') 
arrow_left = tk.Button(arrow_frame0, image=img_left, width = 120,height=120, command=command_left).pack(side="left")
img_up = tk.PhotoImage(file='up.png') 
arrow_up = tk.Button(arrow_frame1, image=img_up,width = 120,height=120,  command=command_up).pack()
img_stop = tk.PhotoImage(file='stop.png') 
arrow_stop = tk.Button(arrow_frame1, image=img_stop,width = 120,height=120,  command=command_stop).pack()
img_down = tk.PhotoImage(file='down.png') 
arrow_dowm = tk.Button(arrow_frame1, image=img_down,width = 120,height=120,  command=command_down).pack()
img_right = tk.PhotoImage(file='right.png') 
arrow_right = tk.Button(arrow_frame2, image=img_right,width = 120,height=120,  command=command_right).pack(side="right")

l = tk.Label(root, width=10, height=1, text=" ")
l.pack()

 # 建立菜单栏
menubar = tk.Menu(root)
filemenu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label='File', menu=filemenu)
filemenu.add_command(label='New', command=do_job)
filemenu.add_command(label='Land', command=lambda:do_job("L")) # 开启陆地模式
filemenu.add_command(label='Water', command=lambda:do_job("W")) #开启海洋模式
filemenu.add_separator()    # 添加一条分隔线
filemenu.add_command(label='Exit', command=root.quit) # 用tkinter里面自带的quit()函数
# 第7步，创建一个Edit菜单项（默认不下拉，下拉内容包括Cut，Copy，Paste功能项）
editmenu = tk.Menu(menubar, tearoff=0)
# 将上面定义的空菜单命名为 Edit，放在菜单栏中，就是装入那个容器中
menubar.add_cascade(label='Edit', menu=editmenu)
# 同样的在 Edit 中加入Cut、Copy、Paste等小命令功能单元，如果点击这些单元, 就会触发do_job的功能
editmenu.add_command(label='Kp', command=set_KP)
editmenu.add_command(label='Ki', command=set_KI)
editmenu.add_command(label='Kd', command=set_KD)
# 第8步，创建第二级菜单，即菜单项里面的菜单
submenu = tk.Menu(filemenu) # 和上面定义菜单一样，不过此处实在File上创建一个空的菜单
filemenu.add_cascade(label='Color', menu=submenu, underline=0) # 给放入的菜单submenu命名为Import
# 第9步，创建第三级菜单命令，即菜单项里面的菜单项里面的菜单命令（有点拗口，笑~~~）
submenu.add_command(label='raw', command=lambda:do_job("T"))   # 这里和上面创建原理也一样，在Import菜单项中加入一个小菜单命令Submenu_1
submenu.add_command(label='color_1', command=lambda:do_job("A"))   # 这里和上面创建原理也一样，在Import菜单项中加入一个小菜单命令Submenu_1
submenu.add_command(label='hsv', command=lambda:do_job("B"))   # 这里和上面创建原理也一样，在Import菜单项中加入一个小菜单命令Submenu_1
submenu.add_command(label='color_3', command=lambda:do_job("C"))   # 这里和上面创建原理也一样，在Import菜单项中加入一个小菜单命令Submenu_1

left_label = tk.Label(root,text='左侧精确调速',anchor="w", font=('黑体',6),\
        width=30,\
        height=1)

left_speed=tk.DoubleVar()
left_slider = tk.Scale(root,orient=tk.HORIZONTAL,length=750,sliderlength=120,width=50,from_=-100,to=100, font=('黑体',6),tickinterval=25,resolution=1,variable=left_speed)
left_slider.bind('<ButtonRelease-1>',show)

left_subtitle = tk.Label(root,text="left_speed.get()")

right_label = tk.Label(root,text='右侧精确调速', anchor="w", font=('黑体',6),\
        width=30,\
        height=1)

right_speed=tk.DoubleVar()
right_slider = tk.Scale(root,orient=tk.HORIZONTAL,length=750,width=50,from_=-100,to=100,font=('黑体',6),sliderlength=120,tickinterval=25,resolution=1,variable=right_speed)
right_slider.bind('<ButtonRelease-1>',showR)

right_subtitle = tk.Label(root,text="right_speed.get()")

left_label.pack()
left_slider.pack()
left_subtitle.pack()
right_label.pack()
right_slider.pack()
right_subtitle.pack()

data_from_raybot3 = tk.StringVar()
show_TCP_msg = tk.Label(root, textvariable=data_from_raybot3)
show_TCP_msg.pack()

root.config(menu=menubar)
sync_command()
root.mainloop() #阻塞，除非窗口关闭
