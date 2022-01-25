'''
@Author: Weisong Wang
@Date: 2020-04-19 18:51:14
@description: 对比ERP里角度文件和雷达上的角度文件是否一致
LastEditors: Weisong Wang
LastEditTime: 2020-12-11 19:49:57
'''
# -*- coding: utf-8 -*-
import json
import os
import struct
import requests
import socket
import pandas as pd
# from pandas.testing import assert_frame_equal


class CompareAngleFile():
    def __init__(self, lidar_id, Host="192.168.1.201", port=9347):
        self.lidar_id = lidar_id
        self.host = Host
        self.port = port
        self.ERP = "https://erp.hesaitech.com"       # erp server
        self.UPLOAD_FILE = "/erp/lidar/workstation/upload_angle_file"
        self.DOWNLOAD_FILE = "/erp/lidar/workstation/get_angle_file"
        self.CHECK_LIDAR_STS = "/erp/lidar/validate/exists"
        local_folder = os.path.join(os.path.dirname(
            __file__), "angle_calibration_file")
        if not os.path.exists(local_folder):
            os.makedirs(local_folder)
        self.local_angle_file = os.path.join(
            local_folder, str(self.lidar_id)+".csv")
        self.lidar_file = os.path.join(
            local_folder, str(self.lidar_id)+"_from_lidar.csv")

    def check_ip(self, host):
        addr = host.strip().split('.')  # 切割IP地址为一个列表
        # print addr
        if len(addr) != 4:  # 切割后列表必须有4个参数
            return ("IP地址错误")
        for i in range(4):
            try:
                addr[i] = int(addr[i])  # 每个参数必须为数字，否则校验失败
            except Exception:
                return ("IP地址错误")
            if addr[i] <= 255 and addr[i] >= 0:  # 每个参数值必须在0-255之间
                pass
            else:
                return ("IP地址错误")
        return True

    def check_lidar_sts(self, lidar_id):
        data = {"lidar_name": str(lidar_id)}
        url = self.ERP + self.CHECK_LIDAR_STS
        r = requests.post(url, data=data)
        ret = json.loads(r.content)
        if ret.get('code') == 0:
            print(lidar_id, ' exists')
            return True
        else:
            print(lidar_id, " doesn't exist")
            return False

    def download_angle_file(self):
        url = self.ERP + self.DOWNLOAD_FILE
        r = requests.get(
            url, params={'lidar_name': str(self.lidar_id)}, timeout=2)
        ret = json.loads(str(r.content, encoding="utf-8"))
        if ret.get('code') != 0:
            # print("download_angle_file failed, code: ", str(ret.get('code')))
            return ("下载 %s 角度文件失败" % self.lidar_id)
        try:
            file = ret['result']['url']
            if file == '':
                return ("下载 %s 角度文件失败" % self.lidar_id)
            else:
                rsp = requests.get(file)
                with open(self.local_angle_file, 'wb') as f:
                    f.write(rsp.content)
                return True
        except Exception:
            return ("下载 %s 角度文件失败" % self.lidar_id)

    def get_lidar_angle_file(self):
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.settimeout(3)
            self.s.connect((self.host, self.port))
        except Exception:
            return ("雷达连接失败")
        payload_len = 0
        p = '4774' + "05" + "00" + struct.pack('>L', payload_len).hex()
        data = bytes.fromhex(p)
        self.s.send(data)
        response = self.s.recv(8)
        if bytes.hex(response[4:8]) == "\x00\x00\x00\x00":
            r_length = 0
            response_payload = ""
            return ("获取 %s 上的角度文件失败" % self.lidar_id)
        else:
            r_length = int(bytes.hex(response[4:8]), 16)
            try:
                response_payload = self.s.recv(r_length)
                if not response_payload:
                    return ("获取 %s 上的角度文件为空" % self.lidar_id)
                with open(self.lidar_file, "w", encoding="utf-8", newline="") as f:
                    f.write(str(response_payload, encoding="utf-8"))
                return True
            except Exception:
                response_payload = ""
                # print("can't get angle calibration file from lidar")
                return ("获取 %s 上的角度文件失败" % self.lidar_id)

    def compare_angles(self):
        results = ""
        ip_check = self.check_ip(self.host)
        if ip_check != True:
            return ip_check
        down_status = self.download_angle_file()
        if down_status != True:
            return down_status
        lidar_status = self.get_lidar_angle_file()
        if lidar_status != True:
            return lidar_status
        if down_status and lidar_status:
            df1 = pd.read_csv(self.local_angle_file)
            df2 = pd.read_csv(self.lidar_file)
            for num in range(int(df1.shape[0])):
                if "XT" in self.lidar_id.upper():
                    if round(df1["Elevation"][num], 3) == round(df2["Elevation"][num], 3) and round(df1["Azimuth"][num], 3) == round(df2["Azimuth"][num], 3):
                        pass
                    else:
                        results = results + ("ERP: %s, Lidar: %s \n" %
                                            (list(round(df1.loc[num], 3)), list(round(df2.loc[num], 3))))
                else:
                    # P128的角度文件与其他的不一样了，放弃Laser id的对比
                    if df1["Elevation"][num] == df2["Elevation"][num] and df1["Azimuth"][num] == df2["Azimuth"][num]:
                        pass
                    else:
                        results = results + ("ERP: %s, Lidar: %s \n" %
                                            (list(df1.loc[num]), list(df2.loc[num])))
            if len(results) == 0:
                results = "比对成功，没问题"
                return results
            else:
                return results

    def get_snumber(self,lidar_id): #增加可用于读取SN的功能并打印出来；
        data = {"lidar_name": str(lidar_id)}
        url = self.ERP + self.CHECK_LIDAR_STS+'?'
        r = requests.post(url, data=data)
        ret = json.loads(r.content)
        if ret.get('code') == 0:
            print(lidar_id, ' exists')
            p = ret.get('result')['sn']
            return p
        else:
            print(lidar_id, " doesn't exist")
            return False



if __name__ == "__main__":
    lidar_id = "ZEUS-T1-0451"
    df = CompareAngleFile(lidar_id)
    df.download_angle_file()
    k = df.get_snumber(lidar_id)
    print(k)
    # pl = df.get_lidar_angle_file()
    # results = df.compare_angles()
    # print(results)
