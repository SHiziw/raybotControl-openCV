#coding=utf-8
from struct import pack,unpack

byte="ML".encode("UTF-8")+pack('f',900.04)+";".encode("UTF-8")
print(byte)
print([i for i in byte])