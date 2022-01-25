# -*- coding: utf-8 -*-
import socket
import struct
import random
from mystudy.CommonFunc import *
import time

class PTC:
    def __init__(self, host="192.168.1.201", port=9347):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        lp = random.randint(10000, 30000)
        self.s.bind(('0.0.0.0', lp))
        self.s.settimeout(30)
        self.s.connect((host, port))

    def closeSocket(self):
        self.s.shutdown(1)
        # self.s.close()

    def ByteToHex(self, h):
        return ''.join(["%02x" % x for x in h]).strip()

    def read_bytes(self, payload_size):
        chunks = []
        bytes_received = 0
        while bytes_received < payload_size:
            chunk = self.s.recv(payload_size - bytes_received)
            if chunk == b"":
                raise RuntimeError("Socket has been unexpectedly closed")
            chunks.append(chunk)
            bytes_received = bytes_received + len(chunk)

        return b"".join(chunks)

    def sender(self, cmd_code, payload):
        """
        :param cmd_code:
        :param payload: payload should input like '015d010207'
        :return:
        """
        if cmd_code in [1, 2, 3, 4, 5, 6, 7, 8, 9, '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e',
                        'f']:
            cmd_code = "0" + str(cmd_code)
        print("payload :")
        print(payload)
        if not payload or payload.upper() == "NONE":
            payload_len = 0
            p = '4774' + str(cmd_code) + "00" + struct.pack('>L', payload_len).hex()
        else:
            payload_len = len(bytes.fromhex(payload))
            p = '4774' + str(cmd_code) + "00" + struct.pack('>L', payload_len).hex() + payload
        print("p :")
        print(p)
        print(type(p))
        data = bytes.fromhex(p)
        print("data :")
        print(data)
        print(type(data))
        # data = struct.pack('8B', int('47', 16), int('74', 16), int(cmd_code, 16), int('00', 16), int("00", 16),
        #                    int('00', 16), int('00', 16), int('00', 16))
        self.start_time1 = time.time()
        # print(self.start_time1)
        self.s.send(data)
        response = self.s.recv(8)
        self.end_time1 = time.time()
        # print(self.end_time1 )
        cost_time_real = round(self.end_time1 - self.start_time1, 3) * 1000
        print("cost time real: %s ms" % cost_time_real)
        print("response: ")
        print(response)
        r_header = response[0:2]
        # r_cmd = '{:x}'.format(response[2:3])
        r_cmd = bytes.hex(response[2:3])
        r_returnCode = bytes.hex(response[3:4])
        if bytes.hex(response[4:8]) == "\x00\x00\x00\x00":
            r_length = 0
            response_payload = ""
        else:
            r_length = int(bytes.hex(response[4:8]), 16)
            response_payload = self.read_bytes(r_length)
        print("command is: %s, get return code: %s, return length: %s, \nreturn string:\n%s" % (
            r_cmd, r_returnCode, r_length, response_payload))
        final_response = {
            "response_command": r_cmd,
            "response_return_code": r_returnCode,
            "response_payload_length": r_length,
            "response_payload": response_payload
        }
        return final_response


if __name__ == '__main__':
    ptc_test = PTC(host="192.168.1.201")
    model_list = {"0": ['Pandar40P', 40], "1": ['Pandar20P', 20], "2": ['Pandar64P', 64],
                  "3": ['Pandar160', 160], "4": ['Pandar20AC', 20], "5": ['Pandar40AC', 40],
                  "6": ['Pandar20P_A', 20], "7": ['Pandar20P_B', 20], "8": ['Pandar20P_F', 20],
                  "9": ['Pandar40P_LARA', 40], "10": ['Pandar40P_AC', 40], "11": ['Pandar40P_T', 40],
                  "12": ['Pandar64_M', 64], "13": ['Pandar64_A', 64], "14": ['Pandar64_B', 64],
                  "15": ['PandarQT-64', 64],"17": ['Pandar128', 128]}

    '''Fov设置'''
    # for i in range(1):
    #         cmd_code = '22'
    #         method = 0
    #         method_string = int_to_hex_string(method, 1)
    #         start_string = int_to_hex_string(0, 2)
    #         end_string = int_to_hex_string(3600, 2)
    #         payload = method_string + start_string + end_string
    #         try:
    #             r = ptc_test.sender(cmd_code, payload)
    #         except Exception:
    #             raise
    '''设置二倍鬼像滤除'''
    # for i in range(1):
    #         cmd_code = '47'
    #         method = 0
    #         method_string = int_to_hex_string(method, 1)
    #         payload = method_string
    #         try:
    #             r = ptc_test.sender(cmd_code, payload)
    #         except Exception:
    #             raise
    '''转速设置'''
    # for i in range(1):
    #     cmd_code = '17'
    #     method = '0258'
    #     # method_string = int_to_hex_string(method, 2)
    #     # payload = method_string
    #     try:
    #         r = ptc_test.sender(cmd_code, method)
    #     except Exception:
    #         raise
    '''trigger模式设置'''
    # for i in range(1):
    #     cmd_code = '1b'
    #     method = '01'
    #     # method_string = int_to_hex_string(method, 1)
    #     # payload = method_string
    #     try:
    #         r = ptc_test.sender(cmd_code, method)
    #     except Exception:
    #         raise

    '''高分辨率模式设置'''
    # for i in range(1):
    #     cmd_code = '1a'
    #     method = '00'
    #     # method_string = int_to_hex_string(method, 1)
    #     # payload = method_string
    #     try:
    #         r = ptc_test.sender(cmd_code, method)
    #     except Exception:
    #         raise

    '''获取回波模式，PTC_COMMAND_GET_CONFIG_INFO在这个里面'''

    # for i in range(1):
    #     cmd_code = '08'
    #     method = 'None'
    #     # method_string = int_to_hex_string(method, 1)
    #     # payload = method_string
    #     try:
    #         r = ptc_test.sender(cmd_code, method)
    #     except Exception:
    #         raise


    '''设置回波模式'''
    for i in range(1):
        cmd_code = '1e'
        method = '05'
        # method_string = int_to_hex_string(method, 1)
        # payload = method_string
        try:
            r = ptc_test.sender(cmd_code, method)
        except Exception:
            raise

    '''get code range'''
    # for i in range(1):
    #         cmd_code = 'f'
    #         sm_string = int_to_hex_string(0, 1)
    #         security_code = '393231323233'
    #         payload = security_code
    #
    #         try:
    #             r = ptc_test.sender(cmd_code, payload)
    #         except Exception:
    #             raise

    '''set code range'''
    # for i in range(1):
    #     cmd_code = 'e'
    #     security_code = '393231323233'
    #     code1 = int_to_hex_string(131, 2)
    #     code2 = int_to_hex_string(130, 2)
    #
    #     constant = int_to_hex_string(2, 1)
    #     step =  int_to_hex_string(10, 1)
    #     code2sp = int_to_hex_string(132, 2)+int_to_hex_string(148, 2)+int_to_hex_string(164, 2)+int_to_hex_string(180, 2)+int_to_hex_string(140, 2)+int_to_hex_string(156, 2)+int_to_hex_string(172, 2)+int_to_hex_string(188, 2)
    #     payload = security_code + code1 + code2 + constant + step +code2sp
    #
    #     try:
    #         r = ptc_test.sender(cmd_code, payload)
    #     except Exception:
    #         raise

    '''802.1AS协议设置'''
    # for i in range(1):
    #     cmd_code = '24'
    # 802.1     AS
    #     sm_string = int_to_hex_string(1, 1)+int_to_hex_string(122, 1)+int_to_hex_string(1, 1)
    #     payload = sm_string
    #     try:
    #         r = ptc_test.sender(cmd_code, payload)
    #     except Exception:
    #         raise
    #
    # 1588v2

    # for i in range(1):
    #     cmd_code = '24'
    #     sm_string = int_to_hex_string(0, 1)+int_to_hex_string(33, 1)+int_to_hex_string(1, 1)+int_to_hex_string(1, 1)+int_to_hex_string(1, 1)+int_to_hex_string(1, 1)
    #     payload = sm_string
    #     try:
    #         r = ptc_test.sender(cmd_code, payload)
    #     except Exception:
    #         raise

    # while 1 ==1:
    #     cmd_code = '1f'
    #     sm_string = int_to_hex_string(1, 1)
    #     payload = 'None'
    #     try:
    #         r = ptc_test.sender(cmd_code, payload)
    #     except Exception:
    #         raise
    #     time.sleep(5)

    #get code range
    # for i in range(1):
    #         cmd_code = 'f'
    #         sm_string = int_to_hex_string(0, 1)
    #         security_code = '393231323233'
    #         payload = security_code
    #
    #         try:
    #             r = ptc_test.sender(cmd_code, payload)
    #         except Exception:
    #             raise

    #
    # for i in range(1):
    #         cmd_code = 'a'
    #         sm_string = int_to_hex_string(0, 1)
    #         payload = sm_string
    #         try:
    #             r = ptc_test.sender(cmd_code, payload)
    #         except Exception:
    #             raise
    #
    # for i in range(1):
    #         cmd_code = '12'
    #         sm_string = int_to_hex_string(1, 1)
    #         payload = sm_string
    #         try:
    #             r = ptc_test.sender(cmd_code, payload)
    #         except Exception:
    #             raise
    # #34设置冻结帧mode
    # for i in range(1):
    #     cmd_code = '18'
    #     sm_string = int_to_hex_string(1, 1)+int_to_hex_string(15, 2)
    #     payload = sm_string
    #     try:
    #         r = ptc_test.sender(cmd_code, payload)
    #     except Exception:
    #         raise


    # 30查info   35查status，31clear ，
    # for i in range(1):
    #     cmd_code = '05'
    #     payload = None
    #     try:
    #         r = ptc_test.sender(cmd_code, payload)
    #
    #     except Exception:
    #         raise

    # for i in range(1):
    #         cmd_code = '06'
    #         sm_string = int_to_hex_string(2, 1)
    #         payload = sm_string
    #         try:
    #             r = ptc_test.sender(cmd_code, payload)
    #         except Exception:
    #             raise

    # for i in range(1):
    #     cmd_code = '24'
    #     payload = '0063000101FF'
    #     try:
    #         r = ptc_test.sender(cmd_code, payload)
    #
    #     except Exception:
    #         raise
    # 0c GET_REGISTER
    # for i in range(1):
    #     cmd_code = '0c'
    #     sm_string = int_to_hex_string(108, 2)
    #     payload =sm_string
    #     try:
    #         r = ptc_test.sender(cmd_code, payload)
    #     except Exception:
    #         raise

    # FOV_3
    # for i in range(1):
    #         cmd_code = '22'
    #         sm_string = int_to_hex_string(3, 1) +int_to_hex_string(1, 1)
    #         payload1 = gen_fov_range_ptc_3(119, 906,906)
    #         payload = sm_string + payload1
    #         try:
    #             r = ptc_test.sender(cmd_code, payload)
    #         except Exception:
    #             raise



    # # #



    #
    # 百度分段阈值PTC测试
    # for i in range(1):
    #     cmd_code = '11'
    #
    #     seg = 10
    #     payload = '' + int_to_hex_string(10, 1)
    #
    #     for x in range(0, 40):
    #         payload = payload + int_to_hex_string(1, 1)
    #
    #     for x in range(0, 40):
    #         for y in range(0, 1):
    #             payload = payload + int_to_hex_string(120, 2) + int_to_hex_string(240, 2) + int_to_hex_string(165, 1)
    #         for y in range(1, 2):
    #             payload = payload + int_to_hex_string(240, 2) + int_to_hex_string(360, 2) + int_to_hex_string(5, 1)
    #         for y in range(2, 3):
    #             payload = payload + int_to_hex_string(360, 2) + int_to_hex_string(480, 2) + int_to_hex_string(165, 1)
    #         for y in range(3, 4):
    #             payload = payload + int_to_hex_string(480, 2) + int_to_hex_string(600, 2) + int_to_hex_string(5, 1)
    #         for y in range(4, 5):
    #             payload = payload + int_to_hex_string(2000, 2) + int_to_hex_string(2200, 2) + int_to_hex_string(165, 1)
    #         for y in range(5, 6):
    #             payload = payload + int_to_hex_string(2600, 2) + int_to_hex_string(2800, 2) + int_to_hex_string(5, 1)
    #         for y in range(6, 7):
    #             payload = payload + int_to_hex_string(720, 2) + int_to_hex_string(840, 2) + int_to_hex_string(165, 1)
    #         for y in range(7, 8):
    #             payload = payload + int_to_hex_string(840, 2) + int_to_hex_string(960, 2) + int_to_hex_string(5, 1)
    #         for y in range(8, 9):
    #             payload = payload + int_to_hex_string(960, 2) + int_to_hex_string(1800, 2) + int_to_hex_string(165, 1)
    #         for y in range(9, 10):
    #             payload = payload + int_to_hex_string(1800, 2) + int_to_hex_string(1920, 2) + int_to_hex_string(5, 1)
    #
    #     try:
    #         r = ptc_test.sender(cmd_code, payload)
    #     except Exception:
    #         raise

    #
    # for i in range(1):
    #     cmd_code = '11'
    #
    #     seg = 1
    #     payload = '' + int_to_hex_string(1, 1)
    #
    #     for x in range(0, 39):
    #         payload = payload + int_to_hex_string(1, 1)
    #     for x in range(39, 40):
    #         payload = payload + int_to_hex_string(1, 1)
    #
    #     for x in range(0, 39):
    #         for y in range(0, 1):
    #             payload = payload + int_to_hex_string(0, 2) + int_to_hex_string(1000, 2) + int_to_hex_string(5, 1)
    #         for y in range(1, 10):
    #             payload = payload + int_to_hex_string(0, 2) + int_to_hex_string(0, 2) + int_to_hex_string(0, 1)
    #     for x in range(39, 40):
    #         for y in range(0, 1):
    #             payload = payload + int_to_hex_string(0, 2) + int_to_hex_string(1000, 2) + int_to_hex_string(165, 1)
    #         for y in range(1, 10):
    #             payload = payload + int_to_hex_string(0, 2) + int_to_hex_string(0, 2) + int_to_hex_string(0, 1)
    #
    #     try:
    #         r = ptc_test.sender(cmd_code, payload)
    #     except Exception:
    #         raise
    # #
    # for i in range(1):
    #     cmd_code = '11'
    #
    #     seg = 1
    #     payload = '' + int_to_hex_string(1, 1)
    #
    #     for x in range(0, 40):
    #         payload = payload + int_to_hex_string(1, 1)
    #
    #
    #     for x in range(0, 40):
    #         for y in range(0, 1):
    #             payload = payload + int_to_hex_string(0, 2) + int_to_hex_string(2000, 2) + int_to_hex_string(165, 1)
    #         for y in range(1, 10):
    #             payload = payload + int_to_hex_string(0, 2) + int_to_hex_string(0, 2) + int_to_hex_string(0, 1)
    #
    #
    #     try:
    #         r = ptc_test.sender(cmd_code, payload)
    #     except Exception:
    #         raise


    # for i in range(1):
    #     cmd_code = '21'
    #     ipv4 = "192.168.1.252"
    #     mask = "255.255.255.0"
    #     gateway = "192.168.1.1"
    #     code1_string = int_to_hex_string(int(ipv4.split(".")[0]), 1) + int_to_hex_string(int(ipv4.split(".")[1]),
    #                                                                                      1) + int_to_hex_string(
    #         int(ipv4.split(".")[2]), 1) + int_to_hex_string(int(ipv4.split(".")[3]), 1)
    #     code2_string = int_to_hex_string(int(mask.split(".")[0]), 1) + int_to_hex_string(int(mask.split(".")[1]),
    #                                                                                      1) + int_to_hex_string(
    #         int(mask.split(".")[2]), 1) + int_to_hex_string(int(mask.split(".")[3]), 1)
    #     code3_string = int_to_hex_string(int(gateway.split(".")[0]), 1) + int_to_hex_string(int(gateway.split(".")[1]),
    #                                                                                    1) + int_to_hex_string(
    #         int(gateway.split(".")[2]), 1) + int_to_hex_string(int(gateway.split(".")[3]), 1)
    #
    #     payload = code1_string + code2_string + code3_string
    #     try:
    #         r = ptc_test.sender(cmd_code, payload)
    #     except Exception:
    #         raise
    #

    # for i in range(1):
    #     cmd_code = '21'
    #     # ipv4 = "192.168.1.252"
    #     # mask = "255.255.255.0"
    #     # gateway = "192.168.1.1"
    #     code1_string =  '' + int_to_hex_string(192, 1)+  int_to_hex_string(168, 1) + int_to_hex_string(1, 1) + int_to_hex_string(201, 1)
    #     code2_string = '' + int_to_hex_string(255, 1)+ int_to_hex_string(255, 1)+ int_to_hex_string(255, 1)+ int_to_hex_string(0, 1)
    #     code3_string =  '' + int_to_hex_string(192, 1)+  int_to_hex_string(168, 1) + int_to_hex_string(1, 1) + int_to_hex_string(1, 1)
    #     code4_string =  '' + int_to_hex_string(0, 1)
    #     code5_string =  '' + int_to_hex_string(1, 2)
    #     # payload = code1_string + code2_string + code3_string
    #     payload = code1_string + code2_string + code3_string+ code4_string+ code5_string
    #     try:
    #         r = ptc_test.sender(cmd_code, payload)
    #     except Exception:
    #         raise
 #
    # for i in range(1):
    #        cmd_code = 'e'
    #        security_code = '393231323233'
    #        # low_range_string = '0073'
    #        low_range_string = int_to_hex_string_reverse_2bytes(115)
    #        # high_range_string = '0190'
    #        high_range_string = int_to_hex_string_reverse_2bytes(400)
    #        laser_code = gen_code_range_ptc_old(115, 400, 40)
    #        payload = security_code + low_range_string + high_range_string + laser_code
    #        # payload1 = "01" + "28010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010109d70b0107c80b4f00c20347028e083d0c820ce302b8056c086f08b90a710b1804670d4d002f03d708420c5f0c5a0c890ded0dfe0df70e090ba50d48001b045e0a000cbd04df05d7038d0bae0308049d09730c06088f0ccd0aab0de70a7f0aca0a010ab0032e0add0a650b15057e07580b280b6e0cd60d4300b908250ab70d2a07260a330909093b05080caa045007fa02d10df00dc90dee01fb049108010af80a120a3309260c280ddf0ded009706f8054b0a9909910d6b0a2d0a60002e025d063306b50d3b0d9b0447060a07cc09da09200b270a5a0dec0cdc0d8a0ae60b2f043606bb03be0a9a0d680d6805fc08320c460deb0b210c5a0b900e0b0daa0ddc"
    #        try:
    #            r = ptc_test.sender(cmd_code, payload)
    #        except Exception:
    #            raise