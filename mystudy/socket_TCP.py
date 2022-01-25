# -*- coding: utf-8 -*-
# @Time    : 2021/1/4 20:01
# @Author  : liuxiang
# @FileName: socket_TCP.py
# @Software: PyCharm
# @email    ：liuxiang@hesaitech.com

import socket
import struct
import os
class PTC():
    def __init__(self):
        self.port = 9347
        self.host = '192.168.1.201'
        local_folder = os.path.join(os.path.dirname(
            __file__), "angle_calibration_file")
        if not os.path.exists(local_folder):
            os.makedirs(local_folder)
        self.local_angle_file = os.path.join(
            local_folder, 'angle' + ".csv")
        self.lidar_file = os.path.join(
            local_folder, 'angle' + "_from_lidar.csv")
        try:
            self.udp = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self.udp.settimeout(3)
            self.udp.connect((self.host, self.port))
        except:
            print('雷达连接失败')
        self.sn()

    def sender(self):
        payload_len = 0
        p = '4774' + "05" + "00" + struct.pack('>L', payload_len).hex()
        data = bytes.fromhex(p)
        self.udp.send(data)
        response = self.udp.recv(8)
        if bytes.hex(response[4:8]) == "\x00\x00\x00\x00":
            r_length = 0
            response_payload = ""
            return ("获取的角度文件失败")
        else:
            r_length = int(bytes.hex(response[4:8]), 16)
            try:
                response_payload = self.udp.recv(r_length)
                if not response_payload:
                    return ("获取的角度文件为空")
                with open(self.lidar_file, "w", encoding="utf-8", newline="") as f:
                    f.write(str(response_payload, encoding="utf-8"))
                return True
            except Exception:
                response_payload = ""
                # print("can't get angle calibration file from lidar")
                return ("获取上的角度文件失败")

    def sn(self):
        payload_len = 0
        p = '4774' + "07" + "00" + struct.pack('>L', payload_len).hex()
        data = bytes.fromhex(p)
        self.udp.send(data)
        response = self.udp.recv(2600)
        sn_data = response[8:26]
        print(sn_data)

if __name__ == "__main__":
    k = PTC()