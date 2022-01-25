import os
import time
from selenium import webdriver
import configparser
# from WebUpgrade.Ele.ElementsFinding import *
# from WebUpgrade.Ele.ElementsWaiting import *
# import win32gui
# import win32con
# import win32com.client
# from WebUpgrade.RelayController import *
# from WebUpgrade.DataParse import DataParse
import requests
import re
# from WebUpgrade import Log
import random
import pandas as pd
# import numpy as np
import logging
# from MultiSystem import multisystem
# from MultiSystem.HTTP_Sender import HTTP_API
from datetime import datetime
from selenium.common.exceptions import WebDriverException, UnexpectedAlertPresentException, TimeoutException
from requests.exceptions import ConnectTimeout
# from PointCloud.LidarDataFromRealTime import *
import csv
from PIL import ImageGrab
import socket
# import random
import struct
import time
import pandas as pd
from datetime import datetime, timezone
# from pykeyboard import *
# from pymouse import *
# from pynput.keyboard import Controller, Key, Listener

# logs = Log.SetLog("MultiSystem")

class UDP_Data_V45():
    def __init__(self, host="192.168.1.201", port=2368, data_size=861):
        self.host = host
        self.port = port
        self.data_size = data_size
        print('1')
        # self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.sock.settimeout(3)
        # self.sock.connect((self.host, 9347))

    def read_UDP_data_once(self, data_size):
        self.udpsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udpsock.bind(('', self.port))
        data, addr = self.udpsock.recvfrom(int(data_size) + 28)
        return data

    def read_UDP_data_multi_times(self, times=5):
        self.udpsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udpsock.bind(('', self.port))
        datas = []
        for t_idx in range(times):
            data, addr = self.udpsock.recvfrom(int(self.data_size) + 28)
            datas.append(data)
        return datas


# def read_p128_v40_tail(RTD, data_size=812, j_bit=-18):
#     data = read_UDP_data_once(RTD, data_size)
#     attr_data = data[j_bit - 10:]
#     pcap_data = RTD._tail_new_v1(attr_data, j_bit)
#     return [pcap_data[0], pcap_data[1], pcap_data[6]]  # UTC, timestamp, motor speed

def gen_timestamp(time_bytes):
    if len(time_bytes) == 6:
        """
        解析按 年，月，日，时，分，秒 排列的UTC时间戳到timestamp
        """
        detail_time = struct.unpack("<BBBBBB", time_bytes)
        y = detail_time[0]
        if y >= 100:
            year = y + 1900
        else:
            year = y + 1970
        month = detail_time[1]
        day = detail_time[2]
        hour = detail_time[3]
        minute = detail_time[4]
        second = detail_time[5]
        dt = datetime(year, month, day, hour, minute, second)
        dt = dt.replace(tzinfo=timezone.utc)
        ts = dt.timestamp()
        return int(ts)
    elif len(time_bytes) == 4:
        """
        解析包中timestamp，时间为微秒
        """
        detail_time = struct.unpack("<I", time_bytes)
        ts = detail_time[0]
        return int(ts)
    else:
        return 0

def parse_p128_v45_cs_tail_with_imu_unit(data_all, data_size=861, tail_size=56):
    # if len(data_all) == data_size:
    #     print("data size correct")
    # else:
    #     print("wrong data size, break")
    data_tail = data_all[0-tail_size:]
    temp_1 = struct.unpack('<H', data_tail[0:2])[0]
    temp1_id = struct.unpack('<B', data_tail[2:3])[0]
    # 如果是老的雷达，则temp2数据无意义
    temp_2 = struct.unpack('<H', data_tail[3:5])[0]
    temp2_id = struct.unpack('<B', data_tail[5:6])[0]
    # 时分复用的reserved 3位（误码率）
    error_code = struct.unpack('<H', data_tail[6:8])[0]
    error_code_id = struct.unpack('<B', data_tail[8:9])[0]
    # Aziumuth flag
    azimuth_flag = struct.unpack('<H', data_tail[9:11])[0]
    # 高温shutdown 1位
    high_t_shutdown = struct.unpack('<B', data_tail[11:12])[0]
    # return mode 1位
    return_mode = struct.unpack('<B', data_tail[12:13])[0]
    # 转速 2位
    motor_speed = struct.unpack('<H', data_tail[13:15])[0]
    # UTC 6位
    utc_time = gen_timestamp(data_tail[15:21])
    # 时间戳 4位
    pcap_timestamp = gen_timestamp(data_tail[21:25])
    # 工厂信息 1位
    factory_info = struct.unpack('<B', data_tail[25:26])[0]
    # udp sequence number 4 bytes
    udp_sequence = struct.unpack('<I', data_tail[26:30])[0]
    # imu info 26 bytes
    imu_info = struct.unpack("<HHHIHHHHHHI", data_tail[30:56])
    tail_list=[]
    tail_list.extend([temp_1, temp1_id, temp_2, temp2_id, error_code, error_code_id, azimuth_flag,
                      high_t_shutdown, return_mode, motor_speed, utc_time, pcap_timestamp, factory_info, udp_sequence])
    return tail_list

def parse_p128_v45_cs_header(data_all, data_size=861, header_size=6):
    # if len(data_all) == data_size:
    #     print("data size correct")
    # else:
    #     print("wrong data size, break")
    data_tail = data_all[6:6+header_size]
    laser_num = struct.unpack('<B', data_tail[0:1])[0]
    block_num =struct.unpack('<B', data_tail[1:2])[0]
    fs_block = struct.unpack('<B', data_tail[2:3])[0]
    dist_unit = struct.unpack('<B', data_tail[3:4])[0]
    ret_num = struct.unpack('<B', data_tail[4:5])[0]
    flags = struct.unpack('<B', data_tail[5:6])[0]
    header_list=[]
    header_list.extend([laser_num, block_num, fs_block, dist_unit, ret_num, flags])
    return header_list

def parse_p128_v45_cs_body(data_all, data_size=861, body_size=776):
    # if len(data_all) == data_size:
    #     print("data size correct")
    # else:
    #     print("wrong data size, break")
    data_body = data_all[12:12+body_size]
    azmth1 = struct.unpack('<H', data_body[0:2])[0]
    dist_list1 = []
    int_list1 = []
    for idx in range(128):
        temp_dist = struct.unpack('<H', data_body[2+idx*2:2+idx*2+2])[0]
        temp_int = struct.unpack('<B', data_body[4+idx*2:4+idx*2+1])[0]
        dist_list1.append(round(temp_dist*0.004, 2))
        int_list1.append(temp_int)
    azmth2 = struct.unpack('<H', data_body[386:388])[0]
    dist_list2 = []
    int_list2 = []
    for idx in range(128):
        temp_dist = struct.unpack('<H', data_body[2 + idx * 2:2 + idx * 2 + 2])[0]
        temp_int = struct.unpack('<B', data_body[4 + idx * 2:4 + idx * 2 + 1])[0]
        dist_list2.append(round(temp_dist*0.004, 2))
        int_list2.append(temp_int)
    return [azmth1, dist_list1, int_list1], [azmth2, dist_list2, int_list2]

def get_temps_workmode_wcsv_one_row(UDV, savefile="temps_and_workmode_128v45.csv"):
        # writer: LiYuda, date:2020/10/31
        # used for Lidar dynamic character depending on Temperature, main goal of this function is to get temperatures of RFB, CB_3, CB_5 and TMB_FPGA from first 3 bytes of Tail(UDP)
        udpSerSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udpSerSock.bind(('', UDV.port))
        csv_row = []

        # initialize parameters
        read_once_flag = 0
        rfb_temp_flag = 0
        cb3_temp_flag = 0
        cb5_temp_flag = 0
        tmb_fpga_temp_flag = 0
        # get udp data once:
        while read_once_flag != 15:
            data, addr = udpSerSock.recvfrom(UDV.data_size+28)
            tail_list = parse_p128_v45_cs_tail_with_imu_unit(data)

            # j = self.lidar_attr["motor_speed_start"]  # should be checked?!!
            # if self.lidar_attr["lidar_type"] in self.old_lidar:
            #     attr_data = data[j - 8:]
            #     pcap_data = self._gen_attr(attr_data)
            # elif self.lidar_attr["lidar_type"] in self.tail_new_model:
            #     attr_data = data[j - 11:]
            #     pcap_data = self._gen_attr(attr_data)
            # else:
            #     attr_data = data[j - 13:]
            #     pcap_data = self._gen_attr_v4(attr_data)

            # [pcap_time, pcap_timestamp, temp_1, temp1_id, temp_2, temp2_id, motor_speed, high_t_shutdown, return_mode, factory_info, error_code, error_code_id, udp_sequence, azimuth_flag]
            if tail_list[1] == 0 and rfb_temp_flag == 0:
                rfb_temp = round(tail_list[0]*0.1, 1)
                rfb_temp_flag = 1
            elif tail_list[1] == 3 and cb3_temp_flag == 0:
                cb3_temp = round(tail_list[0]*0.1, 1)
                cb3_temp_flag = 2
            elif tail_list[1] == 4 and cb5_temp_flag == 0:
                cb5_temp = round(tail_list[0] * 0.1, 1)
                cb5_temp_flag = 4
            elif tail_list[1] == 9 and tmb_fpga_temp_flag == 0:
                tmb_fpga_temp = round(tail_list[0]*0.1, 1)
                tmb_fpga_temp_flag = 8
            read_once_flag = rfb_temp_flag+cb3_temp_flag+cb5_temp_flag+tmb_fpga_temp_flag
            # print(pcap_data[3], rfb_temp_flag, cb3_temp_flag, cb5_temp_flag, tmb_fpga_temp_flag)
            if read_once_flag == 15:
                work_mode = round(tail_list[7])
                time = tail_list[10]
        csv_row.extend([time, rfb_temp, cb3_temp, cb5_temp, tmb_fpga_temp, work_mode])
        print('rfb_temp: %s, tmb_fpga_temp: %s,cb3: %s, cb5_temp: %s, work_mode: %s' % (rfb_temp,tmb_fpga_temp,cb3_temp,cb5_temp, work_mode))
        # return csv_row
        with open(savefile, 'a+', encoding="utf8", newline="") as csvfile:
            myWriter = csv.writer(csvfile)
            myWriter.writerow(csv_row)

        # self.udpSerSock.close()
        return savefile

def write_csv_header(savefile):
    with open(savefile, "w", encoding="utf8", newline="") as csvfile:
        myWriter = csv.writer(csvfile)
        header = ["Time", "rfb_Temp", "cb3_Temp", "cb5_Temp", "TMB_FPGA_Temp", "work_mode"]
        # 写入header
        myWriter.writerow(header)


if __name__ == "__main__":
    # host = '192.168.1.201'
    # port = 2368
    # data_size = 861
    # UDV = UDP_Data_V45(host, port, data_size)
    # savefile = "temps_and_workmode_128v45.csv"
    # test_seconds = 36000
    #
    # write_csv_header(savefile)
    # starttime = datetime.now()
    # while (datetime.now() - starttime).seconds <= test_seconds:
    #     get_temps_workmode_wcsv_one_row(UDV)
    #     time.sleep(5)

    host = '192.168.1.201'
    port = 2368
    data_size = 1409
    UDV = UDP_Data_V45(host, port, data_size)
    time_now = time.strftime('%Y.%m.%d.%H.%M.%S')
    savefile = "temps_and_workmode_128v45.csv"
    # savefile = "temps_and_workmode_128v45_%s_.csv" %time_now
    test_seconds = 1000000

    write_csv_header(savefile)
    starttime = datetime.now()
    while (datetime.now() - starttime).seconds <= test_seconds:
        get_temps_workmode_wcsv_one_row(UDV)
        time.sleep(5)