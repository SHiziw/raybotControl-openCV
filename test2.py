#coding=utf-8
from struct import pack,unpack

byte="ML".encode("UTF-8")+pack('f',123432.523424)
print(byte)
print([i for i in byte])