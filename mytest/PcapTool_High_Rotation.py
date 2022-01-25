# -*- coding: utf-8 -*-
import time
import re
# import datetime
from datetime import datetime
from socket import *
from time import ctime
import numpy as np
from time import sleep
import struct
import sys
import csv
import os
import pandas as pd
import matplotlib.pyplot as plt
from pandas import DataFrame
import math
from matplotlib.ticker import MultipleLocator, FormatStrFormatter


class PcapTool:
    def __init__(self, monitor_time, enable_date_folder, high, rotation, host="192.168.1.201"):
        # monitor_time unit: seconds
        self.monitor_time = monitor_time

        if high.upper()== "Y":
            self.high = 2
            print("High Resolution Mode")
        else:
            self.high = 1
            print("Stand Resolution Mode")
        if rotation.upper()== "Y":
            self.rotation = 1
            print("Clockwise Rotation")
        else:
            self.rotation =-1
            print("CounterClockwise Rotation")

        print(self.high)
        print(self.rotation)
        # data_length : [type, header_length, block_size, block_number, motor_speed_start]
        self.lidar_type = {1270: ['20P', 8, 62, 20, -14], 1274: ['20P', 8, 62, 20, -18], 1256: ['40AC', 2, 124, 10, -8],
                           1260: ['40AC', 2, 124, 10, -8],
                           1262: ['40P', 2, 124, 10, -14], 1266: ['40P', 2, 124, 10, -18], 1062: ['P64', 8, 258, 4, -14],
                           1066: ['P64', 8, 258, 4, -18], 1068: ['128', 12, 514, 2, -18],
                           812: ['128', 12, 386, 2, -18], 1090: ['P64T5', 12, 258, 4, -36]}
        self.HOST = ''
        self.PORT = 2368
        self.BUFSIZ = 2048
        ADDR = (self.HOST, self.PORT)
        self.udpSerSock = socket(AF_INET, SOCK_DGRAM) #创建UDPsocket
        self.udpSerSock.bind(ADDR) #指定主机和端口
        # global x, y
        self.x = float()
        self.y = float()
        if enable_date_folder.upper()=="Y":
            self.path = r"./data_%s" % datetime.now().strftime("%Y%m%d%H%M%S") #通过相对路径改变文件名，格式是年月日时分秒；
        else:
            self.path = r"./data"
        if not (os.path.exists(self.path)): #询问路径是否存在，否则新路径
            os.makedirs(self.path)

        data, addr = self.udpSerSock.recvfrom(self.BUFSIZ) #接受UDP套接字的数据u，与recv()类似，但返回值是tuple(data, address)。其中data是包含接受数据的字符串，address是发送数据的套接字地址
        self.flag = [0, 0, True, 3]
        # 0: lidar type| 1: motor speed | 2: return mode | 3: saved block number
        self.flag[0] = len(data)
        print(self.flag[0])
        if self.flag[0] in [1274, 1260, 1266, 1062, 1068, 812, 1090]:
            self.udp_sequence_enabled = True
        else:
            self.udp_sequence_enabled = False
            print("Please enable Udp Sequence firstly.")
        self.data_len = self.lidar_type.get(self.flag[0]) #128为例，就是得到data_len=['128', 12, 386, 2, -18]；字典中键操作
        j = self.data_len[4]
        print('Type is :' + self.data_len[0])
        if self.data_len == 12:
            self.new = True
            self.savefile = os.path.join(self.path, "newLidarData.csv")
        else:
            self.new = False
            self.savefile= os.path.join(self.path, "LidarData.csv") #正常计算的时候，self.data_len是不等于12的；进入的是FALSE状态
        self.outputfile = ""
        dual_mode = struct.unpack('<B', data[j + 6:j + 7])[0] #解析的方式是字节格式,将data的数据替换为 b'\x39'，可以验证这个问题；
        if dual_mode == 57:
            print('Current return mode is dual return')
            self.flag[2] = True
            self.flag[3] = self.data_len[3] // 2
            self.k = 1000 / 55.56 / self.data_len[3] * 2
        else:
            print('Current return mode is single return')
            self.flag[2] = False
            self.flag[3] = self.data_len[3]
            self.k = 1000 / 55.56 / self.data_len[3]
        self.udpSerSock.close()

    def starttime(self):
        t = datetime.now()
        print('Start at:')
        print(t)
        return t

    def endtime(self):
        t = datetime.now()
        print('End at:')
        print(t)
        return t

    def get_temp(self, tp):
        temp_r1 = 1000.
        temp_r2 = temp_r1 * tp / abs(2 ** 12 - tp)
        b = 4100.
        t0 = 298.15
        t = ((math.log(temp_r2) - math.log(temp_r1)) / b + 1 / t0)
        t = 1 / t
        return t

    def getData(self):
        with open(self.savefile, 'w+') as f:
            count = 0
            packet_loss = 0
            udp_sequence = 0
            timestamp = 0
            timestamp_in_count_list = []
            ADDR = (self.HOST, self.PORT)
            self.udpSerSock = socket(AF_INET, SOCK_DGRAM)
            self.udpSerSock.bind(ADDR)
            while self.y < (self.monitor_time * 1000): #monitor_time表示的是模拟时间，秒的单位，乘以1000表示的是微妙；
                count += 1
                data, addr = self.udpSerSock.recvfrom(self.BUFSIZ)
                now = datetime.now()
                angle = ''
                i = self.data_len[1] #data_len=['128', 12, 386, 2, -18] i=12
                if self.flag[2]: #表示双回波
                    while i < self.data_len[2] * self.data_len[3]:
                        angle_p = data[i:i + 2]
                        # angle.append(struct.unpack('<H',angle_p))
                        angle = angle + str(struct.unpack('<H', angle_p))
                        i += self.data_len[2] * 2
                else: #表示单回波
                    while i < self.data_len[2] * self.data_len[3]:
                        angle_p = data[i:i + 2]
                        angle = angle + str(struct.unpack('<H', angle_p))
                        i += self.data_len[2]
                j = self.data_len[4]
                Motor_speed = struct.unpack('<H', data[j:j + 2])[0]
                timestamp_old = timestamp
                timestamp = struct.unpack('<I', data[j + 2:j + 6])[0]
                udp_sequence_old = udp_sequence
                if not self.udp_sequence_enabled:
                    udp_sequence = 0
                else:
                    if j + 18 == 0:
                        udp_sequence = struct.unpack('<I', data[j + 14:])[0] #执行这条UDP information
                    else:
                        udp_sequence = struct.unpack('<I', data[j + 14:j + 18])[0]

                if self.x > 1:
                    if udp_sequence < udp_sequence_old:
                        udp_v = udp_sequence - udp_sequence_old + 4294967295
                    else:
                        udp_v = udp_sequence - udp_sequence_old
                    if udp_v > 1:
                        packet_loss += udp_v
                    if timestamp < timestamp_old:
                        timestamp_gap = timestamp - timestamp_old + 1000000
                    else:
                        timestamp_gap = timestamp - timestamp_old
                    timestamp_in_count_list.append(timestamp_gap)
                if self.new:
                    temp_1 = struct.unpack('<H', data[j - 10:j - 8])[0]
                    temp_id = struct.unpack('<B', data[j - 8:j - 7])[0]
                    temp_2 = struct.unpack('<H', data[j - 7:j - 5])[0]
                    temp2_id = struct.unpack('<B', data[j - 5:j - 4])[0]
                    if temp_id == 9:
                        temp1_name = "FPGA"
                        # count += 1
                    elif temp_id == 3:
                        temp1_name = "CB3"
                        # count += 1
                    else:
                        temp1_name = "Lidar_Temp1"
                    if temp2_id == 6:
                        temp2_name = "BMB2_TEM"
                    else:
                        temp2_name = "Lidar_Temp2"
                else:
                    temp_1 = struct.unpack('<H', data[j - 8:j - 6])[0]
                    temp_id = struct.unpack('<B', data[j - 6:j - 5])[0]
                    if temp_id == 9:
                        temp1_name = "FPGA"
                        # count += 1
                    elif temp_id == 3:
                        temp1_name = "CB3"
                        # count += 1
                    else:
                        temp1_name = "Lidar_Temp1"
                    temp_2 = "0"
                    temp2_name = "Lidar_Temp2"
                if self.x > 500 * self.k * self.monitor_time and self.x < 500 * self.k * self.monitor_time + 11:
                    self.flag[1] = self.flag[1] + float(Motor_speed)

                angle1 = angle
                angle1 = angle1.replace('(', '')
                angle1 = angle1.replace(')', '')
                angle1 = angle1.rstrip(',')
                if self.monitor_time > 20 and count % 1000 == 0:
                    timestamp_max = max(timestamp_in_count_list)
                    # time, angle in block, motor_speed, timestamp, temp1_name, temp_1, temp2_name, temp_2, packet_loss_num
                    f.write(str(now) + ',' + angle1 + ',' + str(Motor_speed) + ',' + str(timestamp) + ',' + str(
                        temp1_name) + ',' + str(temp_1) + ',' + str(temp2_name) + ',' + str(temp_2) + ',' + str(
                        packet_loss) + ',' + str(timestamp_max) + '\n')
                    packet_loss = 0
                    count = 0
                    timestamp_in_count_list = []
                elif self.monitor_time <= 20:
                    if self.x > 1:
                        timestamp_max = max(timestamp_in_count_list)
                    else:
                        timestamp_max = 0
                    f.write(str(now) + ',' + angle1 + ',' + str(Motor_speed) + ',' + str(timestamp) + ',' + str(
                        temp1_name) + ',' + str(temp_1) + ',' + str(temp2_name) + ',' + str(temp_2) + ',' + str(
                        packet_loss) + ',' + str(timestamp_max) + '\n')
                    packet_loss = 0
                    count = 0
                    timestamp_in_count_list = []
                self.x += 1
                self.y = self.x / self.k  / self.high
            self.udpSerSock.close()
        self.flag[1] = self.flag[1] / 10
        # global beginangle
        # names = locals()
        # beginangle = float()

        # path = r'./%s' % path
        f1 = pd.read_csv(self.savefile)
        # define f1.column name
        temp_b = ['time']
        i = 1
        while i <= self.flag[3]:
            temp_b.append('angle%s' % i)
            i += 1
        temp_b.append('Motor_speed')
        temp_b.append('timestamp')
        temp_b.append('temp1_name')
        temp_b.append('temp1')
        temp_b.append('temp2_name')
        temp_b.append('temp2')
        temp_b.append('packet_loss_num')
        temp_b.append('timestamp_max')
        f1.columns = temp_b
        # divide by 100 for angle
        i = 1
        while i <= self.flag[3]:
            exec('f1.angle%s=f1.angle%s/100' % (i, i))
            i += 1

        # f1.to_csv('%s/Output_data.csv' % self.path, index=False, mode="w+")
        timedata = f1.time
        # get the angle data in last block
        angledata_temp = []
        exec('angledata_temp.append(list(f1.angle%s))' % self.flag[3])
        angledata = angledata_temp[0]

        # rpm = list(f1.Motor_speed)
        time_stamp = list(f1.timestamp)
        record_time = list(f1.time)
        # f_lost = f1.loc[f1["packet_loss_num"] > 0]
        # if f_lost.size > 0:
        #     packet_lost = list(f_lost["packet_loss_num"])
        # else:
        #     packet_lost = list(f1.packet_loss_num)
        # f_FPGA = list(f1.loc[f1["temp1_name"] == "FPGA"]["temp1"])
        # f_CB3 = list(f1.loc[f1["temp1_name"] == "CB3"]["temp1"])
        # temp1 = list(f1.loc[f1["temp1_name"] == "Lidar_Temp1"]["temp1"])
        # i = 0
        # while i < len(temp1):
        #     temp1[i] = self.get_temp(temp1[i])
        #     i += 1

        l = []
        l_angle = []
        time_now = 0
        time_val = 0
        angle = 0
        angle_val = 0
        val = 0
        i = 0
        # flag[1] is the motor speed averaged 10 times
        while i < len(time_stamp):
            if i > 0:
                ms = (datetime.strptime(record_time[i], "%Y-%m-%d %H:%M:%S.%f") - datetime.strptime(record_time[i-1], "%Y-%m-%d %H:%M:%S.%f")).seconds
                if time_stamp[i] > time_stamp[i - 1] and ms == 0:
                    val = time_stamp[i] - time_stamp[i - 1]
                else:
                    val = time_stamp[i] - time_stamp[i - 1] + 1000000 * (ms + 1)
            time_now = time_now + val
            l.append(time_now / 1000)

            if self.flag[1] > 900:
                time_val = time_stamp[i] % 50000
                angle_val = round((angledata[i] - time_val * 360 * self.rotation / 50000), 2)
            else:
                time_val = time_stamp[i] % 100000
                angle_val = round((angledata[i] - time_val * 360  * self.rotation/ 100000), 2)

            if angle_val < 0 or angle_val > 360:
                angle_val = round((angle_val + 360 * self.rotation), 2)
            l_angle.append(angle_val)
            i += 1

        f1['realtime'] = l
        f1['angle_deviation'] = l_angle
        # f1['temperature'] = temp1
        f1.to_csv('%s/Output_data.csv' % self.path, index=False, mode="w+")
        self.outputfile = os.path.join(self.path, "Output_data.csv")
        return self.outputfile

    def generate_figure_all(self, file):
        f1 = pd.read_csv(file)
        rpm = list(f1.Motor_speed)
        time_stamp = list(f1.timestamp_max)
        ts_gap = []
        for ij in range(len(time_stamp)):
            ts1 = round(time_stamp[ij] / 100, 1)
            if ts1 < 1.0:
                time_stamp[ij] = 1.0
            else:
                time_stamp[ij] = ts1
                ts_gap.append(ts1)
                # if ts > 500000:
                #     time_stamp[j] = round(ts/100000,1)
                # else:
                #     time_stamp[j] = 0.0
        if len(ts_gap) == 0:
            ts_gap = [1.0]
        f_lost = f1.loc[f1["packet_loss_num"] > 0]
        if f_lost.size > 0:
            packet_lost = list(f_lost["packet_loss_num"])
        else:
            packet_lost = list(f1.packet_loss_num)
        np.array(f1['realtime'])
        f1['realtime'] = f1['realtime'] / 1000

        a_max = f1['angle_deviation'].max()
        a_min = f1['angle_deviation'].min()

        d_max = math.ceil(a_max)
        d_min = math.floor(a_min)
        print('range of d: [', d_min, ',', d_max, ']')

        a_max = round(a_max, 1)
        a_min = round(a_min, 1)
        a_mean = np.mean(f1['angle_deviation'])
        a_mean = round(a_mean, 1)
        a_sigma = np.std(f1['angle_deviation'], ddof=1)
        a_sigma = round(a_sigma, 1)

        rpm_max = math.ceil(max(rpm))
        rpm_min = math.ceil(min(rpm))
        print('range of speed: [', rpm_min, ',', rpm_max, ']')

        s_mean = np.mean(rpm)
        s_mean = round(s_mean, 1)
        s_sigma = np.std(rpm, ddof=1)
        s_sigma = round(s_sigma, 1)

        pl_max = np.max(packet_lost)
        pl_min = np.min(packet_lost)
        print("packet lost: [", pl_min, ",", pl_max, "]")

        ts_max = max(ts_gap)
        ts_min = min(ts_gap)
        print("timestamp gap: [", ts_min, ",", ts_max, "]")

        plt.figure(figsize=(16, 14))

        ax1 = plt.subplot2grid((4, 2), (0, 0), colspan=1, rowspan=1)
        ax1.plot(f1['realtime'], f1['angle_deviation'], label='angle_deviation')
        ax1.axis([0, self.monitor_time, d_min, d_max])
        ax1.set_xlabel('Time/s')
        ax1.set_ylabel('Angle_deviation/o')

        ax2 = plt.subplot2grid((4, 2), (0, 1), colspan=1, rowspan=1)
        ax2.hist(f1['angle_deviation'], density=True, bins=30, edgecolor='black')
        ax2.set_xlabel('Angle_deviation/Degree')
        ax2.set_ylabel('Density')
        ax2.set_title(
            r'Angle d_range: [' + str(a_min) + ',' + str(a_max) + '], ($\mu$,$\sigma$)=(' + str(a_mean) + ', ' + str(
                a_sigma) + ')',
            fontsize=10)

        ax3 = plt.subplot2grid((4, 2), (1, 0), colspan=1, rowspan=1)
        ax3.plot(f1['realtime'], rpm, label='rpm')
        ax3.axis([0, self.monitor_time, rpm_min - 1, rpm_max + 1])

        ax3.set_xlabel('Time/s')
        ax3.set_ylabel('Motor Speed/rpm')
        ymajorLocator = MultipleLocator(1)
        ymajorFormatter = FormatStrFormatter('%1.1f')
        ax3.yaxis.set_major_locator(ymajorLocator)
        ax3.yaxis.set_major_formatter(ymajorFormatter)

        ax4 = plt.subplot2grid((4, 2), (1, 1), colspan=1, rowspan=1)
        s_cal = np.histogram(rpm, bins=rpm_max - rpm_min + 1)
        bar_y = []
        bar_x = np.arange(rpm_min, rpm_max + 1, 1)
        s_sum = sum(s_cal[0])
        for flag in s_cal[0]:
            bar_y.append(flag / s_sum * 100)
        ax4.bar(bar_x, bar_y, width=0.5)

        ax4.set_xlabel('Motor Speed/rpm')
        ax4.set_ylabel('Percent/%')
        ax4.set_title(
            r'Speed_range: [' + str(rpm_min) + ', ' + str(rpm_max) + '], ($\mu$,$\sigma$)=(' + str(s_mean) + ', ' + str(
                s_sigma) + ')',
            fontsize=10)
        if rpm_max - rpm_min > 10:
            xmajorLocator = MultipleLocator(2)
            xmajorFormatter = FormatStrFormatter('%1.1f')
            ax4.xaxis.set_major_locator(xmajorLocator)
            ax4.xaxis.set_major_formatter(xmajorFormatter)
        else:
            xmajorLocator = MultipleLocator(1)
            xmajorFormatter = FormatStrFormatter('%1.1f')
            ax4.xaxis.set_major_locator(xmajorLocator)
            ax4.xaxis.set_major_formatter(xmajorFormatter)

        ax5 = plt.subplot2grid((4, 2), (2, 0), colspan=1, rowspan=1)
        ax5.plot(f1['realtime'], f1['packet_loss_num'], label='packet_loss_num')
        ax5.axis([0, self.monitor_time, pl_min, pl_max])
        ax5.set_xlabel('Time/s')
        ax5.set_ylabel('packet_loss_num')

        ax6 = plt.subplot2grid((4, 2), (2, 1), colspan=1, rowspan=1)
        if f_lost.size > 0:
            ax6.hist(f_lost['packet_loss_num'], density=True, bins="auto", edgecolor='black', rwidth=0.8)
        else:
            ax6.hist(f1['packet_loss_num'], density=True, bins="auto", edgecolor='black', rwidth=0.8)
        ax6.set_xlabel('packet_loss_num')
        ax6.set_ylabel('Density')
        ax6.set_title("Packet_Lost_Density: [" + str(pl_min) + "," + str(pl_max) + "]", fontsize=10)

        ax7 = plt.subplot2grid((4, 2), (3, 0), colspan=1, rowspan=1)
        ax7.plot(f1['realtime'], time_stamp, label='timestamp_gap')
        ax7.axis([0, self.monitor_time, ts_min, ts_max])
        ax7.set_xlabel('Time/s')
        ax7.set_ylabel('timestamp_max')

        ax8 = plt.subplot2grid((4, 2), (3, 1), colspan=1, rowspan=1)
        ax8.hist(ts_gap, density=True, bins="auto", edgecolor='black', rwidth=0.8)
        ax8.set_xlabel('timestamp_max/*100μs')
        ax8.set_ylabel('Density')
        ax8.set_title("timestamp gap: [" + str(ts_min) + "," + str(ts_max) + "]", fontsize=10)

        plt.tight_layout()
        plt.subplots_adjust(hspace=0.3)

        plt.savefig('%s/Output_fig.png' % self.path)
        plt.show()

    def generate_figure_Speed_UDPSequence(self, file):
        f1 = pd.read_csv(file)
        rpm = list(f1.Motor_speed)
        # time_stamp = list(f1.timestamp)
        f_lost = f1.loc[f1["packet_loss_num"] > 0]
        if f_lost.size > 0:
            packet_lost = list(f_lost["packet_loss_num"])
        else:
            packet_lost = list(f1.packet_loss_num)
        np.array(f1['realtime'])
        f1['realtime'] = f1['realtime'] / 1000

        rpm_max = math.ceil(max(rpm))
        rpm_min = math.ceil(min(rpm))
        print('range of speed: [', rpm_min, ',', rpm_max, ']')

        s_mean = np.mean(rpm)
        s_mean = round(s_mean, 1)
        s_sigma = np.std(rpm, ddof=1)
        s_sigma = round(s_sigma, 1)

        pl_max = np.max(packet_lost)
        pl_min = np.min(packet_lost)

        plt.figure(figsize=(16, 9))

        ax3 = plt.subplot2grid((2, 2), (0, 0), colspan=1, rowspan=1)
        ax3.plot(f1['realtime'], rpm, label='rpm')
        ax3.axis([0, self.monitor_time, rpm_min - 1, rpm_max + 1])

        ax3.set_xlabel('Time/s')
        ax3.set_ylabel('Motor Speed/rpm')
        ymajorLocator = MultipleLocator(1)
        ymajorFormatter = FormatStrFormatter('%1.1f')
        ax3.yaxis.set_major_locator(ymajorLocator)
        ax3.yaxis.set_major_formatter(ymajorFormatter)

        ax4 = plt.subplot2grid((2, 2), (0, 1), colspan=1, rowspan=1)
        s_cal = np.histogram(rpm, bins=rpm_max - rpm_min + 1)
        bar_y = []
        bar_x = np.arange(rpm_min, rpm_max + 1, 1)
        s_sum = sum(s_cal[0])
        for flag in s_cal[0]:
            bar_y.append(flag / s_sum * 100)
        ax4.bar(bar_x, bar_y, width=0.5)

        ax4.set_xlabel('Motor Speed/rpm')
        ax4.set_ylabel('Percent/%')
        ax4.set_title(
            r'Speed_range: [' + str(rpm_min) + ', ' + str(rpm_max) + '], ($\mu$,$\sigma$)=(' + str(s_mean) + ', ' + str(
                s_sigma) + ')',
            fontsize=10)
        if rpm_max - rpm_min > 10:
            xmajorLocator = MultipleLocator(2)
            xmajorFormatter = FormatStrFormatter('%1.1f')
            ax4.xaxis.set_major_locator(xmajorLocator)
            ax4.xaxis.set_major_formatter(xmajorFormatter)
        else:
            xmajorLocator = MultipleLocator(1)
            xmajorFormatter = FormatStrFormatter('%1.1f')
            ax4.xaxis.set_major_locator(xmajorLocator)
            ax4.xaxis.set_major_formatter(xmajorFormatter)

        ax5 = plt.subplot2grid((2, 2), (1, 0), colspan=1, rowspan=1)
        ax5.plot(f1['realtime'], f1['packet_loss_num'], label='packet_loss_num')
        ax5.axis([0, self.monitor_time, pl_min, pl_max])
        ax5.set_xlabel('Time/s')
        ax5.set_ylabel('packet_loss_num')

        ax6 = plt.subplot2grid((2, 2), (1, 1), colspan=1, rowspan=1)
        if f_lost.size > 0:
            ax6.hist(f_lost['packet_loss_num'], density=True, bins="auto", edgecolor='black')
        else:
            ax6.hist(f1['packet_loss_num'], density=True, bins="auto", edgecolor='black')
        ax6.set_xlabel('packet_loss_num')
        ax6.set_ylabel('Density')
        ax6.set_title("Packet_Lost_Density", fontsize=10)

        plt.tight_layout()
        plt.subplots_adjust(hspace=0.3)

        plt.savefig('%s/Output_fig.png' % self.path)
        plt.show()

    def statistics_UDP_Lost(self):
        savefile = os.path.join(self.path, "LidarData_udp.csv")
        with open(savefile, 'w+') as f:
            count = 0
            udp_sequence = 0
            y = 0
            x = 0
            # packet_loss = []
            packet_loss = 0
            starttime = datetime.now()
            print("start at: ", starttime)
            ADDR = (self.HOST, self.PORT)
            self.udpSerSock = socket(AF_INET, SOCK_DGRAM)
            self.udpSerSock.bind(ADDR)
            while y < (self.monitor_time * 1000):
                count += 1
                data, addr = self.udpSerSock.recvfrom(self.flag[0])
                now = datetime.now()
                j = self.data_len[4]
                # Motor_speed = struct.unpack('<H', data[j:j + 2])[0]
                udp_sequence_old = udp_sequence
                if not self.udp_sequence_enabled:
                    udp_sequence = 0
                else:
                    if j + 18 == 0:
                        udp_sequence = struct.unpack('<I', data[j + 14:])[0]
                    else:
                        udp_sequence = struct.unpack('<I', data[j + 14:j + 18])[0]

                if x > 1:
                    if udp_sequence < udp_sequence_old:
                        udp_v = udp_sequence - udp_sequence_old + 4294967295
                    else:
                        udp_v = udp_sequence - udp_sequence_old
                    if udp_v > 1:
                        packet_loss += udp_v
                    # packet_loss.append(udp_v)

                if count % 1000 == 0:
                    # time, packet_loss_num
                    f.write(str((now-starttime).total_seconds()) + ',' + str(packet_loss) + '\n')
                    packet_loss = 0
                    count = 0
                x += 1
                y = x / self.k
            self.udpSerSock.close()
        endtime = datetime.now()
        print("end at: ", endtime)
        df = pd.read_csv(savefile, names=["time", "lost_packets"])
        lost_max = df['lost_packets'].max()
        lost_min = df['lost_packets'].min()
        plt.plot(df['time'], df['lost_packets'], label='lost_packets')
        plt.xlabel("time/s")
        plt.ylabel("lost packets numbers")
        plt.title("Packet_Lost: [" + str(lost_min) + "," + str(lost_max) + "]", fontsize=10)
        plt.savefig('%s/Output_udp_fig.png' % self.path)
        plt.show()


if __name__ == '__main__':
    print("If input sampling time >20, it will record data per 1000 packets, else will record data each packet")
    t, e = input('Input sampling time(Seconds) and enable random folder(Y/N):\n').split() #可同时输入多个参数；
    t = float(t)
    # HighResolution 模式为"Y"，Standard模式为"N"，否则会出错
    high = "Y"

    # 正转为"Y"，反转为"N"，否则会出错
    rotation = "Y"
    p = PcapTool(t, e, high, rotation)
    p.starttime()
    f = p.getData()
    p.endtime()
    # # p.generate_figure_Speed_UDPSequence(f)
    # # f = r"D:\Code\TestScript\SmartTools\data_20200106224042\Output_data.csv"
    p.generate_figure_all(f)
    # p.statistics_UDP_Lost()
