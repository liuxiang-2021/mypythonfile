# import os
# import time
# from selenium import webdriver
# import configparser
# from WebUpgrade.Ele.ElementsFinding import *
# from WebUpgrade.Ele.ElementsWaiting import *
# import win32gui
# import win32con
# import win32com.client
# from WebUpgrade.RelayController import *
# # from WebUpgrade.Upgrade_P128_MultiSystem_lyd import SetUp, WebControl
# from WebUpgrade.DataParse import DataParse
# import requests
# import re
# from WebUpgrade import Log
# import random
# import pandas as pd
# # import numpy as np
# import logging
# # from MultiSystem import multisystem
# # from MultiSystem.HTTP_Sender import HTTP_API
# from datetime import datetime
# from selenium.common.exceptions import WebDriverException, UnexpectedAlertPresentException, TimeoutException
# from requests.exceptions import ConnectTimeout
# from PointCloud.LidarDataFromRealTime import *
import csv
# import json
# from PIL import ImageGrab
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

class SetUp:
    def __init__(self):
        self.BASE_DIR = os.path.dirname(os.path.realpath(__file__))
        cfg = configparser.ConfigParser()
        cfgFile = os.path.join(self.BASE_DIR, 'ATConfig.ini')
        cfg.read(cfgFile, encoding='utf-8')
        self.usingBrowser = cfg.get('Settings', 'usingBrowser')
        url = cfg.get('Settings', 'url')
        # Set the threshold for selenium to WARNING
        from selenium.webdriver.remote.remote_connection import LOGGER as seleniumLogger
        seleniumLogger.setLevel(logging.WARNING)
        # Set the threshold for urllib3 to WARNING
        from urllib3.connectionpool import log as urllibLogger
        urllibLogger.setLevel(logging.WARNING)

    # def _config(self):

    def set_driver(self):
        Browse_Driver_Path = os.path.join(self.BASE_DIR, 'WebDriver')
        if Browse_Driver_Path not in os.environ['PATH'].split(os.pathsep):
            os.environ['PATH'] += os.pathsep + Browse_Driver_Path

        file_time = time.strftime("%Y-%m-%d", time.localtime(time.time()))

        if self.usingBrowser.upper() == 'FIREFOX':
            options = webdriver.FirefoxOptions()
            # options.add_argument('--ignore-ssl-errors')
            options.add_argument('-accept_insecure_certs')
            log_name = 'GeckoDriver-' + file_time + '.log'
            log_file = os.path.join(self.BASE_DIR, 'Logs', log_name)
            driver1 = webdriver.Firefox(firefox_options=options, service_log_path=log_file)
            driver1.maximize_window()
            driver1.implicitly_wait(20)
        elif self.usingBrowser.upper() == 'CHROME':
            options = webdriver.ChromeOptions()
            # options.add_argument('-headless')
            options.add_argument('-accept_insecure_certs')
            log_name = 'ChromeDriver-' + file_time + '.log'
            log_file = os.path.join(self.BASE_DIR, 'Logs', log_name)
            driver1 = webdriver.Chrome(chrome_options=options, service_log_path=log_file)
            driver1.maximize_window()
            driver1.implicitly_wait(20)

        return driver1

class WebControl(SetUp):
    def __init__(self, url):
        super(WebControl, self).__init__()
        self.driver = self.set_driver()
        self.url = r"http://" + url
        self.filename = None
        self.sensor_version = ""
        self.control_version = ""
        self.software_version = ""

    def connectWeb(self):
        self.driver.get(self.url)
        time.sleep(2)

    def connectWeb_except_error_page(self):
        # writer: liyuda
        while True:
            try:
                self.driver.get(self.url)
                time.sleep(2)
                break
            except WebDriverException as WDE:
                # print(WDE.msg)
                if "error page" in WDE.msg:
                    print(WDE.msg.split(':')[0])
                    pass

    def connectWeb_return_time(self):
        # writer: liyuda
        while True:
            try:
                self.driver.get(self.url)
                return datetime.now()
                # break
            except WebDriverException as WDE:
                # print(WDE.msg)
                if "error page" in WDE.msg:
                    print(WDE.msg.split(':')[0])
                    pass

    def checkVersion(self, version):
        version_else = "v" + version
        # self.connectWeb()
        self.connectWeb_except_error_page()
        time.sleep(2)
        c = self.getVersion()
        print("c: %s" % c)
        # huyun新加的打印当前几个版本号
        current_version = "".join(c)
        print("current_version: %s" % current_version)
        # huyun新加的打印当前版本号
        logs.info("check %s if in %s" % (version, current_version))
        if "xxxxx" in current_version:
            version_status = False
        elif version in current_version or version_else in current_version:
            version_status = True
        else:
            version_status = False
        return version_status

    def getVersion(self):
        # return ["sensor version","controller version", "software version"]
        upgrade_page = findXpath(self.driver, "//a[contains(text(),'Upgrade')]")
        upgrade_page.click()
        time.sleep(3)
        current_version = []
        self.software_version = findXpath(self.driver, "//td[@id='s-version']").text
        self.sensor_version = findXpath(self.driver, "//td[@id='fs-version']").text
        self.control_version = findXpath(self.driver, "//td[@id='fc-version']").text
        current_version.append(self.software_version)
        current_version.append(self.sensor_version)
        current_version.append(self.control_version)
        print("current_version: %s" % current_version)

        return current_version

    def getStatistics(self):
        # return ["sensor version","controller version", "software version"]
        Statistics_page = findXpath(self.driver, "//a[contains(text(),'Operation Statistics')]")
        Statistics_page.click()
        time.sleep(3)
        Statistics = []
        self.startuptimes = findXpath(self.driver, "//td[@id='startuptimes']").text
        self.WorkingTemperature = findXpath(self.driver, "//td[@id='WorkingTemperature']").text
        self.workingtime = findXpath(self.driver, "//td[@id='workingtime']").text
        Statistics.append(self.startuptimes)
        Statistics.append(self.WorkingTemperature)
        Statistics.append(self.workingtime)
        print("Statistics: %s" % Statistics)
        return Statistics

    def closeWeb(self):
        self.driver.quit()

class UDP_Data_Parser():

    def __init__(self, host, port, relay_host, relay_port, relay_channel):
        self.host = host
        self.port = port
        self.relay_host = relay_host
        self.relay_port = relay_port
        self.header_size = 12
        self.relay_channel = relay_channel
        self.data_size = None

    def __get_binfo_from_udp__(self):
        # udp data can only be recieved while power supplied
        if not self.data_size:
            data = self.read_UDP_data_once()
        else:
            data = self.read_UDP_data_once(new_udp=0)
        self.laser_num = struct.unpack('<B', data[6:7])[0]
        self.block_num = struct.unpack('<B', data[7:8])[0]
        pv_major = struct.unpack('<B', data[2:3])[0]
        pv_minor = struct.unpack('<B', data[3:4])[0]
        self.protocol_version = int(pv_major) + round(int(pv_minor) / 10, 1)
        self.flag = struct.unpack('<B', data[11:12])[0]
        self.data_size = len(data)
        # print(self.data_size)
        self.conf_flag = (self.flag >> 4) % 2  # value of bit4
        self.sign_flag = (self.flag >> 3) % 2  # value of bit3
        self.l2_flag = (self.flag >> 2) % 2  # value of bit2
        self.imu_flag = (self.flag >> 1) % 2  # value of bit1
        self.udp_seq_flag = self.flag % 2  # value of bit0
        self.pt_byte_num = 3 + self.conf_flag
        self.udp_num_psec = 36000 * (self.protocol_version in [1.3, 1.4]) + 3000 * (self.protocol_version == 3.1) + \
                            5000 * (self.protocol_version == 6.1) + 6000 * (self.protocol_version == 64.6)
        # dual return mode
        # self.__set_cs_flag__()
        # self.__set_fac_flag__()
        if self.protocol_version in [1.3]:
            self.body_size = self.block_num * (self.laser_num * self.pt_byte_num + 2)
            self.tail_size = 24 + 4 * self.udp_seq_flag
            self.tail_start_bit = self.header_size + self.body_size + 17 * self.l2_flag
            self.cs_flag = 0
        elif self.protocol_version in [1.4]:
            self.body_size = self.block_num * (self.laser_num * self.pt_byte_num + 2) + 4
            self.tail_size = 26 + 22 * self.imu_flag + 4 * self.udp_seq_flag + self.sign_flag * 32 + 4 * self.udp_seq_flag
            self.tail_start_bit = self.header_size + self.body_size + 17 * self.l2_flag
        elif self.protocol_version in [64.6]:
            self.laser_num = pv_major
            self.block_num = pv_minor
            self.header_size = 8
            self.flag = 0
            self.conf_flag = (self.flag >> 4) % 2  # value of bit4
            self.sign_flag = (self.flag >> 3) % 2  # value of bit3
            self.l2_flag = (self.flag >> 2) % 2  # value of bit2
            self.imu_flag = (self.flag >> 1) % 2  # value of bit1
            self.udp_seq_flag = self.flag % 2  # value of bit0
            self.pt_byte_num = 3 + self.conf_flag
            self.body_size = self.block_num * (self.laser_num * self.pt_byte_num + 2)
            self.tail_size = self.data_size - self.body_size - self.header_size
            # print("tail_size :{}".format(self.tail_size))
            self.tail_start_bit = self.header_size + self.body_size + 17 * self.l2_flag
            self.cs_flag = 0
            if not self.get_device_info_cgi(info_type='udp_sequence'):
                self.set_udp_seq_ena_cgi(ena_value=1)  # enable udp sequence
                self.udp_seq_flag = 1
                self.data_size = self.data_size+4
        elif self.protocol_version in [6.1, 3.1]:
            self.body_size = self.block_num * (self.laser_num * 4 + 2)
            self.tail_size = 24 + 4 * self.udp_seq_flag
            self.tail_start_bit = self.header_size + self.body_size + 17 * self.l2_flag
            self.cs_flag = 0
        else:
            self.laser_num = 40
            self.block_num = 10
            self.header_size = 0
            self.flag = 0
            self.conf_flag = (self.flag >> 4) % 2  # value of bit4
            self.sign_flag = (self.flag >> 3) % 2  # value of bit3
            self.l2_flag = (self.flag >> 2) % 2  # value of bit2
            self.imu_flag = (self.flag >> 1) % 2  # value of bit1
            self.udp_seq_flag = self.flag % 2  # value of bit0
            self.pt_byte_num = 3 + self.conf_flag
            # self.body_size = self.block_num * (self.laser_num * self.pt_byte_num + 2)
            self.body_size = 1240
            self.tail_size = self.data_size - self.body_size - self.header_size
            self.tail_start_bit = self.header_size + self.body_size + 17 * self.l2_flag
            self.cs_flag = 0
            self.udp_num_psec = 3600
            if not UDV.get_device_info_cgi(info_type='udp_sequence'):
                self.set_udp_seq_ena_cgi(ena_value=1)  # enable udp sequence
                self.udp_seq_flag = 1
                self.data_size = self.data_size+4
        body_dict = self.parse_udp_body_general(data, data_type='all', info_type='azmth')
        self.body_keys = list(body_dict.keys())
        l2_tail_dict = self.parse_udp_tail_general(data, data_type='all', return_type='dict')
        l2_tail_dict_wo_reserved = self.parse_udp_tail_general(data, data_type='all', return_type='dict_wo_reserveds')
        self.l2_tail_keys = list(l2_tail_dict.keys())
        self.l2_tail_keys_wo_reserveds = list(l2_tail_dict_wo_reserved.keys())

    def __set_fac_flag__(self):
        # self.cookies is also filled after this step
        get_p = {
            "action": "get",
            "object": "register",
            "key": "down",
            "value": "43c082d0"
        }
        self.login_p128_release_cgi(r'admin', r'123456')
        # todo: release vesrion has no factory page
        if self.cs_flag == 1:
            response = requests.get(self.base_url, get_p, cookies=self.cookies, verify=False)
        else:
            response = requests.get(self.base_url, get_p)
        r = json.loads(response.text)
        # print(r)
        if "not support" in r["Head"]["Message"] or '3' in r["Head"]["ErrorCode"]:
            self.fac_flag = 0
        elif "Success" in r["Head"]["Message"]:
            self.fac_flag = 1
        else:
            print(r)
            self.fac_flag = -1
            print("factory or release, that is a question!")

    def __get_cp_sign_flag_p128_cs__(self):
        # todo
        data = self.read_UDP_data_once()
        if len(data) > self.body_size:
            self.cp_sign_size = len(data) - self.body_size
            print("point cloud signifiture size is %s" % self.cp_sign_size)
            self.body_size = len(data)
            self.tail_size = self.tail_size + self.cp_sign_size
            self.cp_sign_flag = 1

    def __get_model_and_laser_num_ptc__(self):
        r = self.ptc_sender(7, None)
        self.laser_num = int.from_bytes(r["response_payload"][108:109], 'big')
        self.model_id = int.from_bytes(r["response_payload"][106:107], 'big')

    def __parse_udp_tail_v13_qt__(self, data_all, return_type="list"):
        # return tail information in form of list or dictionary, "list"/"dict"
        data_tail = data_all[0 - self.tail_size:]
        temp_1 = struct.unpack('<H', data_tail[0:2])[0]
        temp1_id = struct.unpack('<B', data_tail[2:3])[0]
        temp_2 = struct.unpack('<H', data_tail[3:5])[0]
        temp2_id = struct.unpack('<B', data_tail[5:6])[0]
        # 高温shutdown 1位
        high_t_shutdown = (struct.unpack('<B', data_tail[6:7])[0]) % 8
        # 时分复用的reserved 3位（误码率）
        error_code = struct.unpack('<H', data_tail[7:9])[0]
        error_code_id = struct.unpack('<B', data_tail[9:10])[0]
        # 转速 2位
        motor_speed = struct.unpack('<H', data_tail[10:12])[0]
        # 时间戳 4位
        pcap_timestamp = gen_timestamp(data_tail[12:16])
        # return mode
        return_mode = struct.unpack('<B', data_tail[16:17])[0]
        # 工厂信息 1位
        factory_info = struct.unpack('<B', data_tail[17:18])[0]
        # UTC 6位
        utc_time = gen_timestamp(data_tail[18:24])
        # udp sequence number 4 bytes
        udp_sequence = None
        if self.udp_seq_flag:
            udp_sequence = struct.unpack('<I', data_tail[24:28])[0]
        tail_list = [temp_1, temp1_id, temp_2, temp2_id, high_t_shutdown, error_code, error_code_id, motor_speed,
                     pcap_timestamp, return_mode, factory_info, utc_time, udp_sequence]
        dict_keys = ["temp_1", "temp1_id", "temp_2", "temp2_id", "high_t_shutdown", "error_code", "error_code_id",
                     "motor_speed", "pcap_timestamp", "return_mode", "factory_info", "utc_time", "udp_sequence"]
        tail_dict = dict(zip(dict_keys, tail_list))
        tail_dict_wo_reserveds = dict(zip(dict_keys[6:], tail_list[6:]))
        if return_type == "list":
            return tail_list
        elif return_type == "dict":
            return tail_dict
        elif return_type == "dict_wo_reserveds":
            return tail_dict_wo_reserveds
        else:
            print("wrong input type!")
            return None

    def __parse_udp_tail_xt__(self, data_all, return_type="list"):
        # UDV = UDP_Data_Parser(host, port, data_size=1153, header_size=6, body_size=1036, tail_sign_size=88)
        # UDV.__get_binfo_from_udp__()
        data_tail = data_all[0 - self.tail_size:]
        temp_1 = struct.unpack('<H', data_tail[0:2])[0]
        temp1_id = struct.unpack('<B', data_tail[2:3])[0]
        temp_2 = struct.unpack('<H', data_tail[3:5])[0]
        temp2_id = struct.unpack('<B', data_tail[5:6])[0]
        # 时分复用的reserved 3位（误码率）
        error_code = struct.unpack('<H', data_tail[6:8])[0]
        error_code_id = struct.unpack('<B', data_tail[8:9])[0]
        # 高温shutdown 1位
        high_t_shutdown = (struct.unpack('<B', data_tail[9:10])[0]) % 8
        # return mode
        return_mode = struct.unpack('<B', data_tail[10:11])[0]
        # 转速 2位
        motor_speed = struct.unpack('<H', data_tail[11:13])[0]
        # UTC 6位
        utc_time = gen_timestamp(data_tail[13:19])
        # 时间戳 4位
        pcap_timestamp = gen_timestamp(data_tail[19:23])
        # 工厂信息 1位
        factory_info = struct.unpack('<B', data_tail[23:24])[0]
        # udp sequence number 4 bytes
        udp_sequence = None
        if self.udp_seq_flag:
            udp_sequence = struct.unpack('<I', data_tail[24:28])[0]
        tail_list = [temp_1, temp1_id, temp_2, temp2_id, error_code, error_code_id, high_t_shutdown, return_mode,
                     motor_speed, utc_time, pcap_timestamp, factory_info, udp_sequence]
        dict_keys = ["temp_1", "temp1_id", "temp_2", "temp2_id", "error_code", "error_code_id", "high_t_shutdown",
                     "return_mode",
                     "motor_speed", "utc_time", "pcap_timestamp", "factory_info", "udp_sequence"]
        tail_dict = dict(zip(dict_keys, tail_list))
        tail_dict_wo_reserveds = dict(zip(dict_keys[6:], tail_list[6:]))
        if return_type == "list":
            return tail_list
        elif return_type == "dict":
            return tail_dict
        elif return_type == "dict_wo_reserveds":
            return tail_dict_wo_reserveds
        else:
            print("wrong input type!")
            return None

    def __parse_function_safety_v14__(self, data_all, data_type='all', return_type='dict'):
        if self.l2_flag == 0:
            print('function safety excluded')
            return None
        elif data_type == 'safety+tail':
            data_l2 = data_all[0:17]
        elif data_type == 'all':
            data_l2 = data_all[self.header_size + self.body_size:self.header_size + self.body_size + 17]
        elif data_type == 'safety':
            data_l2 = data_all
        else:
            print('wrong data type input!')
            return None

        FS_version = struct.unpack('<B', data_l2[0:1])[0]
        raw_bits1 = struct.unpack('<B', data_l2[1:2])[0]
        lidar_state = raw_bits1 >> 5
        code_type = (raw_bits1 >> 3) % 4  # 1: current; 2: history
        roll_cnt = raw_bits1 % 8
        raw_bits2 = struct.unpack('<B', data_l2[2:3])[0]
        total_cd_num = raw_bits2 >> 4
        flt_cd_id = raw_bits2 % 16
        flt_code = hex(struct.unpack('<H', data_l2[3:5])[0])
        reserved = data_l2[5:13]
        crc2 = struct.unpack('<I', data_l2[13:17])[0]
        l2_dict_keys = ['FS_version', 'lidar_state', 'code_type', 'rolling_counter', 'total_code_num', 'fault_code_id',
                        'fault_code', 'crc2']
        l2_list = [FS_version, lidar_state, code_type, roll_cnt, total_cd_num, flt_cd_id, flt_code, crc2]
        l2_dict = dict(zip(l2_dict_keys, l2_list))
        if return_type == "list":
            return l2_list
        elif return_type == "dict":
            return l2_dict
        else:
            print("wrong input type!")
            return None

    def __parse_udp_tail_v14__(self, data_all, data_type='all', return_type="list"):
        # data_type: 'all', 'tail', 'safety+tail'; for 'safety+tail' return_type can only set as "dict"
        if data_type == 'all' and not self.l2_flag:
            data_tail = data_all[self.tail_start_bit:]
        elif data_type == 'all' and self.l2_flag:
            # print('both safety and tail data will be parsed, return data in form of dictionary')
            if 'dict' not in return_type:
                return_type = 'dict'
            data_tail = data_all[self.tail_start_bit:]
            data_l2 = data_all[self.header_size + self.body_size:self.header_size + self.body_size + 17]
            l2_dict = self.__parse_function_safety_v14__(data_l2, data_type='safety', return_type='dict')
        elif data_type == 'safety+tail' and self.l2_flag:
            # print('both safety and tail data will be parsed, return data in form of dictionary')
            if 'dict' not in return_type:
                return_type = 'dict'
            data_l2 = data_all[0:17]
            data_tail = data_all[17:]
            l2_dict = self.__parse_function_safety_v14__(data_l2, data_type='safety', return_type=return_type)
        elif data_type == 'safety+tail' and not self.l2_flag:
            print('this lidar has no function safety data, wrong data type input')
            return None
        elif data_type == 'tail':
            data_tail = data_all
        else:
            print('wrong data type input!')
            return None

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
        tail_list = [temp_1, temp1_id, temp_2, temp2_id, error_code, error_code_id, azimuth_flag,
                     high_t_shutdown, return_mode, motor_speed, utc_time, pcap_timestamp, factory_info, udp_sequence]
        dict_keys = ["temp_1", "temp1_id", "temp_2", "temp2_id", "error_code", "error_code_id", "azimuth_flag",
                     "high_t_shutdown", "return_mode", "motor_speed", "utc_time", "pcap_timestamp", "factory_info",
                     "udp_sequence"]
        tail_dict = dict(zip(dict_keys, tail_list))
        tail_dict_wo_reserveds = dict(zip(dict_keys[6:], tail_list[6:]))
        if return_type == "list":
            return tail_list
        elif return_type == "dict":
            l2_dict.update(tail_dict)
            return l2_dict
        elif return_type == "dict_wo_reserveds":
            l2_dict.update(tail_dict_wo_reserveds)
            return l2_dict
        else:
            print("wrong input type!")
            return None

    def __parse_udp_tail_unnmb__(self, data_all, return_type="list"):
        # if self.tail_size == 56:
        #     data_tail = data_all[0 - self.tail_size:]
        # else:
        #     data_tail = data_all[0 - self.tail_size:56 - self.tail_size]
        data_tail = data_all[0 - self.tail_size:]
        # 高温shutdown 1位
        high_t_shutdown = struct.unpack('<B', data_tail[5:6])[0]
        # reserved2 2bytes: defined as crc_code at 64P
        # reserved2 = struct.unpack('<H', data_tail[6:8])[0]
        crc_code = struct.unpack('<H', data_tail[6:8])[0]
        # 转速 2位
        motor_speed = struct.unpack('<H', data_tail[8:10])[0]
        # 时间戳 4位
        pcap_timestamp = gen_timestamp(data_tail[10:14])
        # return mode 1位
        return_mode = struct.unpack('<B', data_tail[14:15])[0]
        # 工厂信息 1位
        factory_info = struct.unpack('<B', data_tail[15:16])[0]
        # UTC 6位
        utc_time = gen_timestamp(data_tail[16:22])
        if len(data_tail) == 26:
            udp_sequence = struct.unpack('<I', data_tail[22:26])[0]
            tail_list = [crc_code, high_t_shutdown, motor_speed, pcap_timestamp, return_mode, factory_info, utc_time,
                         udp_sequence]
            dict_keys = ["crc_code", "high_t_shutdown", "motor_speed", "pcap_timestamp", "return_mode", "factory_info",
                         "utc_time", "udp_sequence"]
        elif len(data_tail) == 22:
            tail_list = [crc_code, high_t_shutdown, motor_speed, pcap_timestamp, return_mode, factory_info, utc_time]
            dict_keys = ["crc_code", "high_t_shutdown", "motor_speed", "pcap_timestamp", "return_mode", "factory_info",
                         "utc_time"]
        else:
            print("this lidar supposed to be Pandar64P, but udp tail parse failed")
        tail_dict = dict(zip(dict_keys, tail_list))
        # tail_dict_wo_reserveds = dict(zip(dict_keys[1:], tail_list[1:]))
        if return_type == "list":
            return tail_list
        elif return_type == "dict":
            return tail_dict
        elif return_type == "dict_wo_reserveds":
            return tail_dict
        else:
            print("wrong input type!")
            return None

    def __set_cs_flag__(self):
        # action=set&object=lidar_data&key=security_code&value=921223'
        get_p = {
            "action": "get",
            "object": "lidar_config"
        }
        try:
            base_url = 'https://192.168.1.201'
            response = requests.get(base_url)
        except SSLError:
            base_url = 'https://192.168.1.201/pandar.cgi?'
            self.cs_flag = 1
            self.release = 1

        except ConnectionError:
            base_url = 'http://192.168.1.201/pandar.cgi?'
            response = requests.get(base_url, get_p)
            r = json.loads(response.text)
            if 'authorization failed' in r['Head']['Message']:
                print('this lidar has cyber security, login cookie needed')
                self.cs_flag = 1
            elif r['Head']['ErrorCode'] == '0':
                self.cs_flag = 0
            else:
                self.cs_flag = -1
            self.release = 0
        self.base_url = base_url
        self.url = self.base_url[:-12]
        # if self.cs_flag:
        #     self.ptc = PTCS_D(host=self.host)

    def ptc_sender(self, cmd_code, payload):
        '''
        @description: 用于发送ptc指令
        @param {cmd_code}: ptc 命令码
        @param {payload}: ptc对应命令需要的payload
        @return: 返回内容做解析后的字典final_response
        '''
        PtcSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        PtcSocket.connect((self.host, 9347))
        if cmd_code in [1, 2, 3, 4, 5, 6, 7, 8, 9, '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e',
                        'f']:
            cmd_code = "0" + str(cmd_code)
        if not payload or payload.upper() == "NONE":
            payload_len = 0
            p = '4774' + str(cmd_code) + "00" + \
                struct.pack('>L', payload_len).hex()
        else:
            payload_len = len(bytes.fromhex(payload))
            p = '4774' + str(cmd_code) + "00" + \
                struct.pack('>L', payload_len).hex() + payload
        data = bytes.fromhex(p)
        PtcSocket.send(data)
        response = PtcSocket.recv(8)
        r_cmd = int.from_bytes(response[2:3], 'big')
        r_returnCode = int.from_bytes(response[3:4], 'big')
        r_length = int.from_bytes(response[4:8], 'big')
        if r_length == 0:
            response_payload = ""
        else:
            try:
                response_payload = PtcSocket.recv(r_length)
            except TimeoutError:
                response_payload = ""

        final_response = {
            "response_command": r_cmd,
            "response_return_code": r_returnCode,
            "response_payload_length": r_length,
            "response_payload": response_payload
        }
        PtcSocket.close()
        return final_response

    def read_UDP_data_once(self, new_udp=1):
        if new_udp:
            self.udpsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.udpsock.bind(('', self.port))
            data, addr = self.udpsock.recvfrom(1500)
        else:
            data, addr = self.udpsock.recvfrom(int(self.data_size) + 42)
        # self.udpsock.close()
        return data

    def read_UDP_data_multi_times(self, times=5):
        self.udpsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udpsock.bind(('', self.port))
        datas = []
        for t_idx in range(times):
            data, addr = self.udpsock.recvfrom(int(self.data_size) + 28)
            datas.append(data)
        self.udpsock.close()
        return datas

    def parse_udp_body_general(self, data_all, data_type='all', info_type='dist'):
        if data_type == 'all':
            data_body = data_all[self.header_size:self.header_size + self.body_size]
        elif data_type == 'body':
            data_body = data_all
        else:
            print('wrong data type input!')
            return None

        azmth_list = []
        dist_list = []
        int_list = []
        block_bt = self.laser_num * self.pt_byte_num + 2
        dist_idx = range(2, block_bt, self.pt_byte_num)
        int_idx = range(4, block_bt, self.pt_byte_num)
        if self.conf_flag:
            cnfd_list = []
            cnfd_idx = range(5, block_bt, self.pt_byte_num)
        for block_idx in range(self.block_num):
            start_idx = block_idx * block_bt  # start index of each block
            azmth = struct.unpack('<H', data_body[start_idx:start_idx + 2])[0]
            azmth_list.append(azmth)
            dist_list_i = [round((struct.unpack('<H', data_body[di:di + 2])[0]) * 0.004, 2) for di in dist_idx]
            dist_list.append(dist_list_i)
            int_list_i = [struct.unpack('<B', data_body[ii:ii + 1])[0] for ii in int_idx]
            int_list.append(int_list_i)
            if self.conf_flag:
                cnfd_list_i = [struct.unpack('<B', data_body[ci:ci + 1])[0] for ci in cnfd_idx]
                cnfd_list.append(cnfd_list_i)

        if info_type == 'dist':
            dist_keys = [info_type + "{}".format(temp_i + 1) for temp_i in range(len(dist_list))]
            dist_dict = dict(zip(dist_keys, dist_list))
            return dist_dict
        elif info_type == 'intensity':
            int_keys = [info_type + "{}".format(temp_i + 1) for temp_i in range(len(int_list))]
            int_dict = dict(zip(int_keys, int_list))
            return int_dict
        elif info_type == 'azmth':
            azmth_keys = [info_type + "{}".format(temp_i + 1) for temp_i in range(len(azmth_list))]
            azmth_dict = dict(zip(azmth_keys, azmth_list))
            return azmth_dict
        elif info_type == 'cloudpoint_crc' and self.protocol_version == 1.4:
            return struct.unpack('<I', data_body[-4:])[0]
        elif info_type == 'confidence' and self.conf_flag:
            conf_keys = [info_type + "{}".format(temp_i + 1) for temp_i in range(len(cnfd_list))]
            conf_dict = dict(zip(conf_keys, cnfd_list))
            return conf_dict
        elif info_type == 'confidence' and self.conf_flag == 0:
            print("cloud points of this Lidar have no confidence")
            return None
        else:
            print("wrong info type")
            return None

    def parse_udp_tail_general(self, data_all, data_type='all', return_type="list"):
        if self.protocol_version in [1.3, 3.1]:
            tail_lord = self.__parse_udp_tail_v13_qt__(data_all, return_type=return_type)
        elif self.protocol_version in [6.1]:
            tail_lord = self.__parse_udp_tail_xt__(data_all, return_type=return_type)
        elif self.protocol_version in [1.4]:
            tail_lord = self.__parse_udp_tail_v14__(data_all, data_type=data_type, return_type=return_type)
        elif self.protocol_version in [64.6] or self.laser_num == 40:
            tail_lord = self.__parse_udp_tail_unnmb__(data_all, return_type=return_type)
        else:
            print("this type udp version can not be parsed temporarily")
            tail_lord = None
        return tail_lord

    def login_p128_release_cgi(self, username, passwd):
        if self.protocol_version == 1.4 and self.cs_flag:
            url = self.base_url + 'action=get&object=login'
            bytes_passwd = passwd.encode("utf-8")
            passwdB64 = base64.b64encode(bytes_passwd)
            passwdB64_utf8 = str(passwdB64, encoding="utf8")
            data = {'key': username, 'value': passwdB64_utf8}
            res = requests.post(url, json=data, verify=False)
            data = json.loads(res.text)
            if 'Success' not in data['Head']['Message']:
                print(data)
            name = data.get('Body').get('cookie').get('name')
            uuid = data.get('Body').get('cookie').get('value')
            self.cookies = {name: uuid}
        else:
            self.cookies = None

    def connectWeb_except_error_page(self, driver, t):
        # writer: liyuda
        counter = time.time()
        while time.time() - counter < t:
            try:
                driver.get(self.url)
                break
            except WebDriverException as WDE:
                # print(WDE.msg)
                if "error page" in WDE.msg:
                    print(WDE.msg.split(':')[0])
                    pass

    def set_reset_cgi(self):
        self.udpsock.close()
        set_p = {
            "action": "set",
            "object": "reset"
        }
        self.login_p128_release_cgi(r'admin', r'123456')
        if self.cs_flag and self.cookies:
            response = requests.get(self.base_url, set_p, cookies=self.cookies, verify=False)
        else:
            response = requests.get(self.base_url, set_p)
        r = json.loads(response.text)

        print(r)

    def set_reboot_cgi(self):
        self.udpsock.close()
        set_p = {
            "action": "set",
            "object": "reboot"
        }
        try:
            self.login_p128_release_cgi(r'admin', r'123456')
        except AttributeError:
            print("no login requested, cs_flag is {}".format(self.cs_flag))

        if self.cs_flag and self.cookies:
            response = requests.get(self.base_url, set_p, cookies=self.cookies, verify=False)
        else:
            response = requests.get(self.base_url, set_p)
        r = json.loads(response.text)
        print("reboot starts, responce is {}".format(r))

    def set_spin_rate_cgi(self, spin_spd=600):
        if spin_spd == 600:
            spd_value = "2"
        elif spin_spd == 1200:
            spd_value = "3"
        else:
            print("input spinning speed not defined, set spinning speed as 600rpm")

        set_p = {
            "action": "set",
            "object": "lidar",
            "key": "spin_speed",
            "value": spd_value
        }
        self.login_p128_release_cgi(r'admin', r'123456')
        if self.cs_flag and self.cookies:
            response = requests.get(self.base_url, set_p, cookies=self.cookies, verify=False)
        else:
            response = requests.get(self.base_url, set_p)
        r = json.loads(response.text)
        print('This is response for set motor speed: {}.'.format(r))

    def set_return_mode_cgi(self, return_mode='last_return'):
        mode_value_mapping = {'last_return': '0', 'strongest_return': '1', 'last_and_strongest_return': '2',
                              'first_return': '3', 'last_and_first_return': '4', 'strongest_and_first_return': '5'}
        set_p = {
            "action": "set",
            "object": "lidar_data",
            "key": "lidar_mode",
            "value": mode_value_mapping[return_mode]
        }
        self.login_p128_release_cgi(r'admin', r'123456')
        if self.cs_flag and self.cookies:
            response = requests.get(self.base_url, set_p, cookies=self.cookies, verify=False)
        else:
            response = requests.get(self.base_url, set_p)
        r = json.loads(response.text)
        if r['Head']['ErrorCode'] == '2':
            return_mode_value, return_mode = self.get_return_mode_cgi()
            print("This return mode is not supported in this lidar type, current return mode is {}".format(return_mode))
        elif r['Head']['ErrorCode'] == '0':
            return_mode_value, return_mode = self.get_return_mode_cgi()
            print("return mode setting successful, current return mode is {}".format(return_mode))
        else:
            print("unknown Error, return mode setting failed!")
            return_mode_value, return_mode = self.get_return_mode_cgi()
            print("current return mode is {}".format(return_mode))

    def get_return_mode_cgi(self):
        mode_value_mapping = {'last_return': '0', 'strongest_return': '1', 'last_and_strongest_return': '2',
                              'first_return': '3', 'last_and_first_return': '4', 'strongest_and_first_return': '5'}
        value_mode_mapping = dict(zip(list(mode_value_mapping.values()), list(mode_value_mapping.keys())))
        get_p = {
            "action": "get",
            "object": "lidar_data",
            "key": "lidar_mode"
        }
        self.login_p128_release_cgi(r'admin', r'123456')
        if self.cs_flag and self.cookies:
            response = requests.get(self.base_url, get_p, cookies=self.cookies, verify=False)
        else:
            response = requests.get(self.base_url, get_p)
        r = json.loads(response.text)
        return_mode_value = r["Body"]["lidar_mode"]
        return_mode = value_mode_mapping[return_mode_value]
        return return_mode_value, return_mode

    def set_resolution_cgi(self, resolution_mode='high'):
        if self.protocol_version in [1.3, 1.4]:
            standard_mode_value = '{"mode":' + str(0) + "}'"
            high_mode_value = '{"mode":' + str(1) + "}'"
            mode_value_mapping = {'standard': standard_mode_value, 'high': high_mode_value}
            set_p = {
                "action": "set",
                "object": "laser_control",
                "key": "high_resolution",
                "value": mode_value_mapping[resolution_mode]
            }
            self.login_p128_release_cgi(r'admin', r'123456')
            if self.cs_flag and self.cookies:
                response = requests.get(self.base_url, set_p, cookies=self.cookies, verify=False)
            else:
                response = requests.get(self.base_url, set_p)
            r = json.loads(response.text)
            if r['Head']['ErrorCode'] == '2':
                resolution_mode = self.get_resolution_cgi()
                print("This return mode is not supported in this lidar type, current return mode is {}".format(
                    resolution_mode))
            elif r['Head']['ErrorCode'] == '0':
                resolution_mode = self.get_resolution_cgi()
                print("return mode setting successful, current return mode is {}".format(resolution_mode))
            else:
                print("unknown responce! responce is {}".format(r))
        else:
            print("not supported in this lidar type!")

    def get_resolution_cgi(self):
        if self.protocol_version in [1.3, 1.4]:
            value_mode_mapping = {'0': 'standard', '1': 'high'}
            get_p = {
                "action": "get",
                "object": "high_resolution"
            }
            self.login_p128_release_cgi(r'admin', r'123456')
            if self.cs_flag and self.cookies:
                response = requests.get(self.base_url, get_p, cookies=self.cookies, verify=False)
            else:
                response = requests.get(self.base_url, get_p)
            r = json.loads(response.text)
            if r['Head']['ErrorCode'] == '0':
                resolution_mode = value_mode_mapping[r['Body']['mode']]
                return resolution_mode
            else:
                print("unknown resolution mode! responce is {}".format(r))
                return None
        else:
            print("not supported in this lidar type!")

    def set_sync_angle_cgi(self, enable_flag=1, sync_angle=0):
        if sync_angle > 360 or sync_angle < 0:
            print("wrong synchronization angle")

        syn_value = '{"sync":' + str(enable_flag) + ',"syncAngle":' + str(sync_angle) + "}'"
        set_p = {
            "action": "set",
            "object": "lidar_sync",
            "key": "sync_angle",
            "value": syn_value
        }
        self.login_p128_release_cgi(r'admin', r'123456')
        if self.cs_flag and self.cookies:
            response = requests.get(self.base_url, set_p, cookies=self.cookies, verify=False)
        else:
            response = requests.get(self.base_url, set_p)
        r = json.loads(response.text)
        print('This is response for set sync angle: {}.'.format(r))

    def get_sync_angle_cgi(self):
        # syn_value = '{"sync":' + str(enable_flag) + ',"syncAngle":' + str(sync_angle) + "}'"
        get_p = {
            "action": "get",
            "object": "lidar_sync"
        }
        self.login_p128_release_cgi(r'admin', r'123456')
        if self.cs_flag and self.cookies:
            response = requests.get(self.base_url, get_p, cookies=self.cookies, verify=False)
        else:
            response = requests.get(self.base_url, get_p)
        r = json.loads(response.text)
        syn_value = r["Body"]["syncAngle"]
        print('This is response for set sync angle: {}.'.format(r))
        return syn_value

    def get_lidar_monitor_cgi(self, info_type="float"):
        # info_type = "float" or "str"
        get_p = {
            "action": "get",
            "object": "lidar_monitor"
        }
        self.login_p128_release_cgi(r'admin', r'123456')
        if self.cs_flag and self.cookies:
            response = requests.get(self.base_url, get_p, cookies=self.cookies, verify=False)
        else:
            response = requests.get(self.base_url, get_p)
        r = json.loads(response.text)
        if info_type == "float":
            current = round(float(r["Body"]["lidarInCur"][:-3]) / 1000, 2)
            voltage = round(float(r["Body"]["lidarInVol"][:-2]), 2)
            power = round(float(r["Body"]["lidarInPower"][:-2]), 2)
        elif info_type == "str":
            current = r["Body"]["lidarInCur"]
            voltage = r["Body"]["lidarInVol"]
            power = r["Body"]["lidarInPower"]
        else:
            print("wrong info_type input")
            return None
        monitor_dict = {"current": current, "voltage": voltage, "power": power}
        print('response for get lidar_monitor: {}.'.format(r))
        return monitor_dict

    def set_rotate_direct_cgi(self, dirct):
        # 'clock': clockwise;  'anti-clock': anti-clockwise
        if dirct == 'clockwise':
            dirct_value = 0
        elif dirct == 'counterclockwise':
            dirct_value = 1
        else:
            print("wrong rotate direction input, set direction as clockwise")

        set_p = {
            "action": "set",
            "object": "lidar",
            "key": "rotate_direction",
            "value": dirct_value
        }
        self.login_p128_release_cgi(r'admin', r'123456')
        if self.cs_flag and self.cookies:
            response = requests.get(self.base_url, set_p, cookies=self.cookies, verify=False)
        else:
            response = requests.get(self.base_url, set_p)
        r = json.loads(response.text)
        print('This is response for set rotate direction: {}.'.format(r))

    def set_udp_seq_ena_cgi(self, ena_value=1):
        # only valid for P64 temporarily
        if self.protocol_version in [64.6] or self.laser_num == 40:
            set_p = {
                "action": "set",
                "object": "lidar",
                "key": "udp_sequence",
                "value": ena_value
            }
            self.login_p128_release_cgi(r'admin', r'123456')
            if self.cs_flag and self.cookies:
                response = requests.get(self.base_url, set_p, cookies=self.cookies, verify=False)
            else:
                response = requests.get(self.base_url, set_p)
            r = json.loads(response.text)
            print('This is response for set udp_sequence: {}.'.format(r))
        else:
            print("not supported in this type lidar!")

    def get_time_statistic_cgi(self):
        get_p = {
            "action": "get",
            "object": "TimeStatistic"
        }
        self.login_p128_release_cgi(r'admin', r'123456')
        if self.cs_flag and self.cookies:
            response = requests.get(self.base_url, get_p, cookies=self.cookies, verify=False)
        else:
            response = requests.get(self.base_url, get_p)
        r = json.loads(response.text)
        work_temp = float(r['Body']['CurrentTemp'])
        startup_cnt = r['Body']['StartupTimes']
        tim_stat = [startup_cnt, work_temp]
        return tim_stat

    def get_time_temp_statistics(self):
        get_p = {
            "action": "get",
            "object": "TimeStatistic"
        }
        self.login_p128_release_cgi(r'admin', r'123456')
        if self.cs_flag and self.cookies:
            response = requests.get(self.base_url, get_p, cookies=self.cookies, verify=False)
        else:
            response = requests.get(self.base_url, get_p)
        r = json.loads(response.text)
        startup_cnt = r['Body']['StartupTimes']
        work_temp = float(r['Body']['CurrentTemp'])
        total_work_time = r['Body']['TotalWorkingTime']
        info = [startup_cnt, work_temp, total_work_time]
        templist = np.arange(-40, 121, 20)
        for idx, tp in enumerate(templist):
            info.append(r['Body']['Time{:d}'.format(idx)])

        return info

    def get_dwn_reg_cgi(self, reg_add='43c082d0'):
        get_p = {
            "action": "get",
            "object": "register",
            "key": "down",
            "value": reg_add
        }
        self.login_p128_release_cgi(r'admin', r'123456')
        if self.cs_flag and self.cookies:
            response = requests.get(self.base_url, get_p, cookies=self.cookies, verify=False)
        else:
            response = requests.get(self.base_url, get_p)
        r = json.loads(response.text)
        # print(r)
        if r['Head']['ErrorCode'] == '0':
            reg_value = int(r['Body']['value'], 16)
            return reg_value
        else:
            print("register value not received! Error message is {}".format(r['Head']['Message']))
            return None

    def set_up_reg_cgi(self, reg_add="70000028", value=2):
        # eye protection: 2: shutdown
        # hex_value = hex(value)
        set_p = {
            "action": "set",
            "object": "up_register",
            "key": reg_add,
            "value": value
        }
        self.login_p128_release_cgi(r'admin', r'123456')
        if self.cs_flag and self.cookies:
            response = requests.get(self.base_url, set_p, cookies=self.cookies, verify=False)
        else:
            response = requests.get(self.base_url, set_p)
        r = json.loads(response.text)
        # print(r)
        if r['Head']['ErrorCode'] == '0':
            print("up-register {} set successfully".format(reg_add))
        elif "not support" in r["Head"]["Message"] or '3' in r["Head"]["ErrorCode"]:
            print("set register not support, please check whether fac version")
        else:
            print("unknown error, setting not successful")

    def get_up_reg_cgi(self, reg_add="1000f190"):
        get_p = {
            "action": "get",
            "object": "register",
            "key": "up",
            "value": reg_add
        }
        self.login_p128_release_cgi(r'admin', r'123456')
        if self.cs_flag and self.cookies:
            response = requests.get(self.base_url, get_p, cookies=self.cookies, verify=False)
        else:
            response = requests.get(self.base_url, get_p)
        r = json.loads(response.text)
        # print(r)
        if r['Head']['ErrorCode'] == '0':
            reg_value = int(r['Body']['value'], 16)
            return reg_value
        else:
            print("register value not received! Error message is {}".format(r['Head']['Message']))
            return None

    def get_spin_rate_cgi(self):
        get_p = {
            "action": "get",
            "object": "lidar_config"
        }
        self.login_p128_release_cgi(r'admin', r'123456')
        if self.cs_flag and self.cookies:
            response = requests.get(self.base_url, get_p, cookies=self.cookies, verify=False)
        else:
            response = requests.get(self.base_url, get_p)
        r = json.loads(response.text)
        spd_value = r['Body']['SpinSpeed']
        if spd_value == '2':
            spin_spd = 600
        elif spd_value == '3':
            spin_spd = 1200
        else:
            spin_spd = -1
            print("wrong spinning speed, neither 600rpm nor 1200rpm")
        return spin_spd

    def set_pwd_p128_web(self, WebCtrl):
        # WebCtrl is an instance of WebControl
        if self.cs_flag:
            cs_driver = WebCtrl.driver
            self.connectWeb_except_error_page(cs_driver, 60)
            # cs_driver.get(self.url)
            time.sleep(2)
            try:
                pwd_ele = cs_driver.find_element_by_id("password")
                pwd_ele.clear()
                pwd_ele.send_keys(str(123456))
                time.sleep(1)
                saveButton = cs_driver.find_element_by_id("submit")  ## not sure
                saveButton.click()
            except NoSuchElementException:
                pass
            time.sleep(1)
        if self.release:
            # requests.get(self.base_url[:-12], verify=False)
            try:
                cs_driver.get(self.url)
            except UnexpectedAlertPresentException:
                time.sleep(1)
                cs_driver.get(self.url)
        else:
            w_driver = WebCtrl.driver
            self.connectWeb_except_error_page(w_driver, 60)

    def get_statistic_cgi(self):
        get_p = {
            "action": "get",
            "object": "TimeStatistic"
        }
        self.login_p128_release_cgi(r'admin', r'123456')
        if self.cs_flag and self.cookies:
            response = requests.get(self.base_url, get_p, cookies=self.cookies, verify=False)
        else:
            response = requests.get(self.base_url, get_p)
        r = json.loads(response.text)
        # print(r)
        temp_value = r['Body']['CurrentTemp']
        startup_counter = r['Body']['StartupTimes']
        statisic_dict = {'work_temp': temp_value, 'startup_counter': startup_counter}
        return statisic_dict

    def get_lidar_config_cgi(self, info_type='PTPStatus'):
        get_p = {
            "action": "get",
            "object": "lidar_config"
        }
        self.login_p128_release_cgi(r'admin', r'123456')
        if self.cs_flag and self.cookies:
            response = requests.get(self.base_url, get_p, cookies=self.cookies, verify=False)
        else:
            response = requests.get(self.base_url, get_p)
        r = json.loads(response.text)
        print(r)
        config_dict = r['Body']
        if info_type=='PTPStatus':
            return config_dict['PTPStatus']
        elif info_type=='PTPConfig':
            return config_dict['PTPConfig']
        elif info_type=='NoiseFiltering':
            return int(config_dict['NoiseFiltering'])
        elif info_type=='ReflectivityMapping':
            return int(config_dict['ReflectivityMapping'])
        elif info_type=='gPTPConfig':
            return config_dict['gPTPConfig']
        elif info_type=='PTPProfile':
            return config_dict['PTPProfile']
        else:
            print("not supported yet")
            return None


    def get_rotate_direct_cgi(self):
        get_p = {
            "action": "get",
            "object": "lidar_config"
        }
        self.login_p128_release_cgi(r'admin', r'123456')
        if self.cs_flag and self.cookies:
            response = requests.get(self.base_url, get_p, cookies=self.cookies, verify=False)
        else:
            response = requests.get(self.base_url, get_p)
        r = json.loads(response.text)
        print(r)
        rotdir_value = r['Body']['RotateDirection']
        if rotdir_value == '0':
            rot_dir = 'clockwise'
        elif rotdir_value == '1':
            rot_dir = 'counterclockwise'
        else:
            rot_dir = None
            print("wrong rotate direction, neither clockwise nor anti-clockwise")
        return rot_dir

    def set_code_qt(self, code=484):
        if not isinstance(code, int):
            print("wrong input type, please double check")
        elif code > 511 or code < 0:
            print("invalid code, please")
        else:
            set_p = {
                "action": "set",
                "key": code,
                "object": "anti_interference"
            }
            self.login_p128_release_cgi(r'admin', r'123456')
            if self.cs_flag and self.cookies:
                response = requests.get(self.base_url, set_p, cookies=self.cookies, verify=False)
            else:
                response = requests.get(self.base_url, set_p)
            r = json.loads(response.text)
            if r['Head']['ErrorCode'] == '0':
                get_code = self.get_code_qt()
                print("code setting successful, current code is {}".format(get_code))
            else:
                print("unknown error! response is {}".format(r))
                get_code = self.get_code_qt()
                print("code setting successful, current code is {}".format(get_code))

    def get_code_qt(self):
        get_p = {
            "action": "get",
            "object": "anti_interference",
        }
        self.login_p128_release_cgi(r'admin', r'123456')
        if self.cs_flag and self.cookies:
            response = requests.get(self.base_url, get_p, cookies=self.cookies, verify=False)
        else:
            response = requests.get(self.base_url, get_p)
        r = json.loads(response.text)
        if r['Head']['ErrorCode'] == '0':
            cur_code = r['Body']['anti_interference']
            print("code is {}".format(cur_code))
            return cur_code
        else:
            print("unknown Error, getting code failed")
            return None

    def post_upgrade_cgi(self, file_path):
        timeout = 30
        ufile = {'file': open(file_path, 'rb')}
        post_url = self.url + "/upgrade.cgi"
        if self.cs_flag:
            response = requests.post(post_url, files=ufile, timeout=timeout, cookies=self.cookies, verify=False)
        else:
            response = requests.post(post_url, files=ufile, timeout=timeout)
        res = json.loads(response.text)
        print(res)
        if res['Head']['ErrorCode'] == '0':
            print("upgrade starts")
            return 1
        else:
            print("upgrade request rejected")
            return 0

    def get_status_cgi(self):
        get_p = {
            "action": "get",
            "object": "workmode"
        }
        # self.login_p128_release_cgi(r'admin', r'123456')
        try:
            self.login_p128_release_cgi(r'admin', r'123456')
        except AttributeError:
            print("no login requested, cs_flag is {}".format(self.cs_flag))

        if self.cs_flag and self.cookies:
            response = requests.get(self.base_url, get_p, cookies=self.cookies, verify=False)
        else:
            response = requests.get(self.base_url, get_p)
        res = json.loads(response.text)
        # print(res['Body'])

        if self.protocol_version in [1.3, 1.4]:
            key_list = ['WorkMode', 'Sensor_Process', 'Sensor_Status', 'Controller_Process', 'Controller_Status',
                        'Software_Process', 'Software_Status', 'Parameter_Process', 'Parameter_Status']
            if res['Body']['WorkMode'] == 1:
                upgrade_info = res['Body']['UpdateStatus']
                status_list = [dict_i['Status'] for dict_i in upgrade_info]
                value_list = [res['Body']['WorkMode'], upgrade_info[0]['Process'], upgrade_info[0]['Status'],
                              upgrade_info[1]['Process'], upgrade_info[1]['Status'], upgrade_info[2]['Process'],
                              upgrade_info[2]['Status'], upgrade_info[3]['Process'], upgrade_info[3]['Status']]
            else:
                status_list = None
                value_list = [res['Body']['WorkMode']]
                value_list.extend([None] * 8)
        else:
            key_list = ['WorkMode', 'Sensor_Process', 'Sensor_Status', 'Controller_Process', 'Controller_Status',
                        'Software_Process', 'Software_Status']
            if res['Body']['WorkMode'] == 1:
                upgrade_info = res['Body']['UpdateStatus']
                status_list = [dict_i['Status'] for dict_i in upgrade_info]
                value_list = [res['Body']['WorkMode'], upgrade_info[0]['Process'], upgrade_info[0]['Status'],
                              upgrade_info[1]['Process'], upgrade_info[1]['Status'], upgrade_info[2]['Process'],
                              upgrade_info[2]['Status']]
            else:
                status_list = None
                value_list = [res['Body']['WorkMode']]
                value_list.extend([None] * 6)
        status_dict = dict(zip(key_list, value_list))
        return status_dict, status_list

    def get_device_info_cgi(self, info_type='version'):
        # info_type: None, 'version', 'SN' etc.
        get_p = {
            "action": "get",
            "object": "device_info"
        }
        self.login_p128_release_cgi(r'admin', r'123456')
        if self.cs_flag and self.cookies:
            response = requests.get(self.base_url, get_p, cookies=self.cookies, verify=False)
        else:
            response = requests.get(self.base_url, get_p)
        res = json.loads(response.text)
        # print(res['Body'])
        if info_type == 'version':
            sw_version = res['Body']['SW_Ver'].strip()
            ctller_version = res['Body']['FW_Ver'].strip()
            sensor_version = res['Body']['Up_Fpga_Ver'].strip()
            return [sw_version, sensor_version, ctller_version]
        elif info_type == 'SN':
            return res['Body'][info_type]
        elif info_type == 'all':
            return res['Body']
        elif info_type == 'udp_sequence':
            return int(res['Body']['Udp_Seq'])

    def upgrade_one_file(self, file):
        file_name = os.path.basename(file)
        self.post_upgrade_cgi(file)
        for _ in range(800):
            time.sleep(1)
            status_dict, status_list = self.get_status_cgi()
            if sum(status_list) == 2 * len(status_list):
                print("upgrade version: {} finished".format(file_name))
                break
        # ------------------reboot----------------
        print("power off")
        relayClose(self.relay_host, self.relay_port, self.relay_channel)
        time.sleep(10)
        relayOpen(self.relay_host, self.relay_port, self.relay_channel)
        time.sleep(60)
        print("lidar wakes up")
        # -----------------------------------------
        self.__get_binfo_from_udp__()
        time.sleep(3)
        version = self.get_device_info_cgi(info_type='version')
        print("read version after upgrade from web is {}".format(version))

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
    #     pass
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

def parse_p128_v45_cs_body(data_all, info_type='dist', data_size=861, body_size=776):
    ## info type only 'dist', 'intensity', 'azmth'
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

    if info_type=='dist':
        return dist_list1, dist_list2
    elif info_type=='intensity':
        return int_list1, int_list2
    elif info_type=='azmth':
        return azmth1, azmth2
    else:
        print("wrong info type")

def get_temps_workmode_wcsv_one_row(UDV, savefile="temps_and_workmode_128v45.csv"):
        # writer: LiYuda, date:2020/10/31
        # used for Lidar dynamic character depending on Temperature, main goal of this function is to get temperatures of RFB, CB_3, CB_5 and TMB_FPGA from first 3 bytes of Tail(UDP)
        # udpSerSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # udpSerSock.bind(('', UDV.port))
        csv_row = []

        # initialize parameters
        read_once_flag = 0
        rfb_temp_flag = 0
        cb3_temp_flag = 0
        cb5_temp_flag = 0
        tmb_fpga_temp_flag = 0

        while read_once_flag != 15:
            # print(UDV.data_size)
            data, addr = UDV.udpsock.recvfrom(UDV.data_size + 42)
            # tail_list = parse_p128_v45_cs_tail_with_imu_unit(data)
            tail_dict = UDV.parse_udp_tail_general(data, data_type='all', return_type='dict')

            if tail_dict["temp1_id"] == 0 and rfb_temp_flag == 0:
                rfb_temp = round(tail_dict["temp_1"]*0.1, 1)
                rfb_temp_flag = 1
            elif tail_dict["temp1_id"] == 3 and cb3_temp_flag == 0:
                cb3_temp = round(tail_dict["temp_1"]*0.1, 1)
                cb3_temp_flag = 2
            elif tail_dict["temp1_id"] == 4 and cb5_temp_flag == 0:
                cb5_temp = round(tail_dict["temp_1"] * 0.1, 1)
                cb5_temp_flag = 4
            elif tail_dict["temp1_id"] == 9 and tmb_fpga_temp_flag == 0:
                tmb_fpga_temp = round(tail_dict["temp_1"]*0.1, 1)
                tmb_fpga_temp_flag = 8
            read_once_flag = rfb_temp_flag+cb3_temp_flag+cb5_temp_flag+tmb_fpga_temp_flag
            if read_once_flag == 15:
                work_mode = round(tail_dict["high_t_shutdown"])
                time = tail_dict["utc_time"]
        csv_row.extend([time, rfb_temp, cb3_temp, cb5_temp, tmb_fpga_temp, work_mode])
        print([time, rfb_temp, cb3_temp, cb5_temp, tmb_fpga_temp, work_mode])
        # return csv_row
        with open(savefile, 'a+', encoding="utf8", newline="") as csvfile:
            myWriter = csv.writer(csvfile)
            myWriter.writerow(csv_row)

        # self.udpSerSock.close()
        return savefile

def plot_single_para(UDV, idx, seconds, info_type='tail'):
    starttime = datetime.now()
    endtime = datetime.now()
    datas = []
    para_list = []
    seq_num_list = []
    udpSerSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udpSerSock.bind(('', UDV.port))
    while (endtime - starttime).seconds <= seconds:
        data, addr = udpSerSock.recvfrom(UDV.data_size + 28)
        if len(data) == UDV.data_size:
            datas.append(data)
        else:
            print('abandon one UDP data')
        endtime = datetime.now()
    for data in datas:
        seq_num_list.append(parse_p128_v45_cs_tail_with_imu_unit(data)[13])
        if info_type=='tail':
            para = parse_p128_v45_cs_tail_with_imu_unit(data)[idx]
            para_list.append(para)
        elif info_type=='body':
            para = parse_p128_v45_cs_body(data)[idx]
            para_list.append(para)
        elif info_type=='head':
            para = parse_p128_v45_cs_header(data)[idx]
            para_list.append(para)
        else:
            # todo should consider max_index of tail,body,header
            print('wrong input!')

    return seq_num_list, para_list

def plot_single_para_from_datas(datas, idx, info_type='tail'):
    # index of motor speed is 9 in tail
    para_list = []
    seq_num_list = []
    for data in datas:
        seq_num_list.append(parse_p128_v45_cs_tail_with_imu_unit(data)[13])
        if info_type=='tail':
            para = parse_p128_v45_cs_tail_with_imu_unit(data)[idx]
            para_list.append(para)
        elif info_type=='body':
            para = parse_p128_v45_cs_body(data)[idx]
            para_list.append(para)
        elif info_type=='head':
            para = parse_p128_v45_cs_header(data)[idx]
            para_list.append(para)
        else:
            # todo should consider max_index of tail,body,header
            print('wrong input!')
    return seq_num_list, para_list

def write_csv_header(savefile):
    with open(savefile, "w", encoding="utf8", newline="") as csvfile:
        myWriter = csv.writer(csvfile)
        header = ["Time", "rfb_Temp", "cb3_Temp", "cb5_Temp", "TMB_FPGA_Temp", "work_mode"]
        # 写入header
        myWriter.writerow(header)

def write_to_csv(header, savefile):
    # header and file name in this form
    # todo： parameter list
    savefile = "reboot_motor_spd_128v45.csv"
    header = ["seq_num", "motor_spd"]
    with open(savefile, "w", encoding="utf8", newline="") as csvfile:
        myWriter = csv.writer(csvfile)
        myWriter.writerow(header)
        for i in range(len(seq_num_list)):
            myWriter.writerow([seq_num_list[i], para_list[i]])

def restart_time_web_connection(t0, host="192.168.1.201"):
    url = r"http://" + host
    userAgent = {"user-agent": "Mozilla/5.0 (X11; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0"}  # 添加一个user-agent,访问反爬虫策略严格的网站很有用
    timeOut = 1
    # loop_num = 1
    while True:
        try:
            request = requests.get(url, headers=userAgent, timeout=timeOut)
            t2=datetime.now()
            re_tim = t2-t0
            print("Web connected")
            pword = "time to get reconnection with web is %s s" %re_tim
            print(pword)
            break
        except ConnectTimeout as CT:
            print("waiting restart")
            pass
    print(request.status_code)
    return re_tim

def set_pwd_p128_cgi():
    # todo waiting for feedback of wangxun
    base_url = "http://192.168.1.201/pandar.cgi?"
    value = "123456"
    set_p = {
        "action": "set",
        "object": "login",
        "key": "admin",
        "value": value
    }
    response = requests.get(base_url, set_p)
    r = json.loads(response.text)
    print(response.text)
    if "Success" in r["Head"]["Message"]:
        prText = 'login successfully'
        print(prText)
    elif "Error" in r["Head"]["Message"]:
        print(r["Head"]["Message"])
    else:
        print(r["Head"])
    time.sleep(1)

def set_pwd_p128_web(WebCtrl):
    # WebCtrl is an instance of WebControl
    url = "http://192.168.1.201/login.html"
    cs_driver = WebCtrl.driver
    cs_driver.get(url)
    time.sleep(2)

    pwd_ele = cs_driver.find_element_by_id("password")
    pwd_ele.clear()
    pwd_ele.send_keys(str(123456))
    time.sleep(1)
    saveButton = cs_driver.find_element_by_id("submit")  ## not sure
    saveButton.click()
    time.sleep(1)

    # try:
    #     pwd_ele = cs_driver.find_element_by_id("password")
    #     pwd_ele.clear()
    #     pwd_ele.send_keys(str(123456))
    #     time.sleep(1)
    #     saveButton = cs_driver.find_element_by_id("submit")  ## not sure
    #     saveButton.click()
    #     time.sleep(1)
    # except:
    #     pass

def reboot_time_cal(relay_host, relay_port, relay_channel, UDV, times):
    logs.info("reboot time calculation")
    # RTD = RealTimeData(test_host, udpPort)
    udpSerSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udpSerSock.bind(('', UDV.port))
    relay_rebootTest = WebControl(UDV.host)
    set_pwd_p128_web(relay_rebootTest)   # testing
    relay_rebootTest.connectWeb()
    v = relay_rebootTest.getVersion()
    # logs.info("get current version: %s" % v)
    success_count = 0
    fail_count = 0
    for i in range(times):
        print("start reboot test")
        relayClose(relay_host, relay_port, relay_channel)
        time.sleep(5)
        relayOpen(relay_host, relay_port, relay_channel)
        t0 = datetime.now()
        logs.info("relay %s connected" % relay_channel)
        time.sleep(10)
        data_len=0
        while data_len<UDV.data_size:
            data, addr = udpSerSock.recvfrom(UDV.data_size + 28)
            data_len = len(data)
        motor_spd = parse_p128_v45_cs_tail_with_imu_unit(data)[9]
        reboot_time = datetime.now() - t0
        logs.info("read motor speed from Lidar is %s rpm" % motor_spd)
        logs.info("time to receive first UDP data is %s s" % reboot_time)
        flag = 0
        mspd_list = []
        while flag == 0:
            data, addr = udpSerSock.recvfrom(UDV.data_size + 28)
            motor_spd=parse_p128_v45_cs_tail_with_imu_unit(data)[9]
            dist_list1, dist_list2=parse_p128_v45_cs_body(data)
            vld_dist_num = sum([dist>0.1 for dist in dist_list1])
            mspd_list.append(motor_spd)
            if vld_dist_num > 10:
                flag = 1
        reboot_time2 = datetime.now() - t0
        print(mspd_list)
        logs.info("time to get stable UDP data is %s s" % reboot_time2)
        mspd_flag = 0
        while mspd_flag == 0:
            # datas = UDV.read_UDP_data_multi_times(10)
            datas = []
            for t_idx in range(10):
                data, addr = udpSerSock.recvfrom(int(UDV.data_size) + 28)
                datas.append(data)
            seq_num_list, mspd_list = plot_single_para_from_datas(datas, 9)
            if len([mspd for mspd in mspd_list if mspd>598 and mspd<602]) == 10:
                mspd_flag = 1
        reboot_time_mspd = datetime.now() - t0
        logs.info("time to get stable motor speed is %s s" % reboot_time_mspd)
        # time.sleep(3)
        reboot_time_webcon = restart_time_web_connection(t0)
        logs.info("time to rebuild connection with Control Web is %s s" % reboot_time_webcon)
        set_pwd_p128_web(relay_rebootTest)  # testing
        time.sleep(1)
        r = relay_rebootTest.checkVersion(v[0])
        stat = relay_rebootTest.getStatistics()
        logs.info("current start up counter is %s" %stat[0])
        logs.info("working temperature is %s" %stat[1])
        if r:
            success_count += 1
        else:
            fail_count += 1
        print("reboot device success: %s, fail: %s" % (success_count, fail_count))
        time.sleep(10)
    relay_rebootTest.closeWeb()
    logs.info("reboot device success: %s, fail: %s" % (success_count, fail_count))

def call_dyn_work_mode_func(UDV, test_seconds, sample_time, savefile = "temps_and_workmode_128v45.csv"):
    write_csv_header(savefile)
    starttime = datetime.now()
    while (datetime.now() - starttime).seconds <= test_seconds:
        get_temps_workmode_wcsv_one_row(UDV)
        time.sleep(sample_time)

if __name__ == "__main__":
    relay_host = "192.168.1.210"
    relay_port = 8089
    relay_channel = "1"
    host = '192.168.1.201'
    port = 2368

    UDV = UDP_Data_Parser(host, port, relay_host, relay_port, relay_channel)
    UDV.__get_binfo_from_udp__()
    print('UDV setup successful')
    savefile = "temps_and_workmode_128v45.csv"
    test_seconds = 36

    write_csv_header(savefile)
    starttime = datetime.now()
    while (datetime.now() - starttime).seconds <= test_seconds:
        get_temps_workmode_wcsv_one_row(UDV)
        time.sleep(5)

    # reboot_time_cal(relay_host, relay_port, relay_channel, UDV, reboot_times)
    #
    # seq_num_list, para_list = plot_single_para(UDV, 9, 60)



