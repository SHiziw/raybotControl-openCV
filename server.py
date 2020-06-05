#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
# control 2 motor
is_working = 0
instant_shut = 0
l_speed = 0
r_speed = 0
Motor = MotorDriver(is_working, instant_shut)


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



