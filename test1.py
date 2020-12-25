import socket
import threading

HOST_IP = "192.168.50.11"
#HOST_IP = "192.168.50.99"
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
global_message = ""
def tcp_server():
    i = 0
    while True:
       i += 1
       tcp_client, client_addr = socket_tcp.accept() # blocked point！阻塞式！
       (client_ip, client_port) = client_addr
       print("Connection accepted from {0}: {1}.".format(client_ip,client_port))
       tcp_client.send(b"Welcome to RPi TCP server!")
       reader = threading.Thread(name="tcp_reader{}".format(i), target=tcp_reader, args=(tcp_client,))
       reader.start()
       writer = threading.Thread(name="tcp_server%d"%(i), target=tcp_writer, args=(tcp_client,))
       writer.start()

def tcp_reader(tcp_client):
    global global_message
    while True:
        try:
            global_message = tcp_client.recv(128).decode('utf-8')
            print(global_message)
        except Exception :
            print("reader: tcp connect closed. error.")
            tcp_client.shutdown(2)
            tcp_client.close()
            break

def tcp_writer(tcp_client):
    global global_message
    while True:
        try:
            if global_message == "closed":
                tcp_client.shutdown(2)
                tcp_client.close()
                break
            if len(global_message) > 0:
                #lock.acquire()
                tcp_client.send(global_message.encode('utf-8'))
                global_message = ""
                #lock.release()
        except Exception :
            print("writer: tcp connect closed. error.")
            tcp_client.shutdown(2)
            tcp_client.close()
            break

tcp_server()