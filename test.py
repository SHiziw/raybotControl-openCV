
import socket
import time
import sys
import threading
import tkinter as tk
#RPi's IP
SERVER_IP = "192.168.50.99"
SERVER_PORT = 1811
# waiting for a recieve from server.
is_conneted = False
received_data = "no data received..."
l_command = "0"
l_command_old = "0" 
r_command = "0"
r_command_old = "0" 



def close_tcplink(socket_tcp):
    global is_conneted
    is_conneted = False
    socket_tcp.send(b'QB100B100') 
    socket_tcp.close()

def establish_connection(socket_tcp, server_addr,SERVER_IP, SERVER_PORT):
    global is_conneted
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


def backgroud_establish():
    print("Starting socket: TCP...")
    server_addr = (SERVER_IP, SERVER_PORT)
    socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    t0 = threading.Thread(name="connecting", target=establish_connection, args=(socket_tcp, server_addr, SERVER_IP, SERVER_PORT))
    t0.start()
    return socket_tcp

socket_tcp=backgroud_establish()
time.sleep(4)
close_tcplink(socket_tcp)
time.sleep(0.5)
backgroud_establish()