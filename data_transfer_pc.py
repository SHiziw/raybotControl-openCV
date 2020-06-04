#!/usr/bin/python3

import cv2
import zmq
import base64
import numpy as np

Rpi_ip = '192.168.50.99'

context = zmq.Context()
footage_socket = context.socket(zmq.SUB)
footage_socket.connect('tcp://%s:5555'%Rpi_ip)
footage_socket.setsockopt(zmq.SUBSCRIBE,''.encode('utf-8'))  # 接收所有消息


while True:
    frame = footage_socket.recv_string()
    img = base64.b64decode(frame)
    npimg = np.frombuffer(img, dtype=np.uint8)
    source = cv2.imdecode(npimg, 1)
    cv2.imshow("Stream", source)
    cv2.waitKey(1)