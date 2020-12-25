import socket

HOST_IP = "192.168.50.11"
#HOST_IP = "192.168.50.99"
HOST_PORT = 1811
server_addr = (HOST_IP,HOST_PORT)
socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket_tcp.connect(server_addr)
while True:
    command = input()
    socket_tcp.send(command.encode('utf-8'))
    global_message = socket_tcp.recv(128).decode('utf-8')
    print(global_message)