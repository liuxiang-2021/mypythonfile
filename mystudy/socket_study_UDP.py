# -*- coding: utf-8 -*-
# @Time    : 2021/1/4 15:41
# @Author  : liuxiang
# @FileName: socket_study.py
# @Software: PyCharm
# @email    ：liuxiang@hesaitech.com

import socket
class Pointdata():
    def __init__(self):
        self.port = 2368
        self.host = ''
        self.udp = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.udp.bind(('', self.port))
        k = 10
        while k>0:
            data, addr = self.udp.recvfrom(2048)
            print(len(data))
            print(data)
            print(addr)
            k-=1


if __name__ == '__main__':
    m = Pointdata()




