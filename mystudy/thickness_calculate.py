# -*- coding: utf-8 -*-
# @Time    : 2020/11/30 14:17
# @Author  : liuxiang
# @FileName: thickness_calculate.py
# @Software: PyCharm
# @email    ：liuxiang@hesaitech.com

import pandas as pd
from scipy.optimize import leastsq
import numpy as np
import math as mt
import os
import glob
import warnings
import csv
import time

warnings.filterwarnings('ignore')


class thickness_cal(object):
    def __init__(self,path_folder):

        self.folder = path_folder
        self.lidarname = self.folder.split('\\')[-1]
        self.path = os.path.join(folder_path, '*.csv')
        self.frame = glob.glob(self.path)
        data_list = []
        for frame in self.frame:
            name = frame.split('\\')[-1]
            k = os.path.splitext(name)
            self.name = k[0]
            # print(self.name)
            # self.name = name.split('.')[0]
            m = pd.read_csv(frame)
            self.data = m[["Points:0","Points:1","Points:2"]]
            m = self.change_data()
            k = [1,1,1] #初始值
            tparap = leastsq(self.planeerrors,k,m)
            para = tparap[0]
            error = self.thickness_cal(para,m)
            error_new = np.sort(error)
            # long = len(error_new)
            # long_idex = mt.floor(long * 0.995)
            # new_errordata = error_new[mt.floor((long - long_idex) / 2):(mt.floor((long - long_idex) / 2) + long_idex - 1)]
            # print(new_errordata)
            max_err = np.percentile(error_new,99.75)
            min_err = np.percentile(error_new,0.25)
            thick_result = max_err-min_err
            print(self.name + ' 距离下最大的板厚数据是%f' %(thick_result))
            # self.name = bytes(self.name, encoding="utf8") #实际上这个是不需要的
            data_element = (self.name, thick_result)
            data_list.append(data_element)
        time.sleep(2)
        save_file = self.lidarname + '_' + 'thickness'
        self.mkdir(save_file)
        data_path = os.path.join(save_file,'thickness.csv')
        with open(data_path, 'a+', encoding="utf8", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(data_list)

    @staticmethod #静态方法，不需要访问其他方法和属性；
    def mkdir(path):
        folder = os.path.exists(path)
        if not folder:
            os.makedirs(path)



    def change_data(self):
        for var in self.data.columns:
            self.data[var] = self.data.apply(lambda v:float(v[var]),axis=1)
        k = self.data.values #可以将dataframe数据结构转化为Matrix
        #对Matrix 处理去除第一行数据；
        k1 = k[1:,:]
        return k1


    def planeerrors(self,para, points):
        """平面误差"""
        a0, a1, a2 = para
        return a0 * points[:, 0] + a1 * points[:, 2] + a2 - points[:, 1]

    def thickness_cal(self,para,points):
        a0, a1, a2 = para
        n = np.sqrt(a0**2 + a1**2 + 1)
        return (a0 * points[:, 0] + a1 * points[:, 2] + a2 - points[:, 1])/n

if __name__ == '__main__':
    folder_path = r'C:\Users\Administrator\Desktop\HEBE-0009'
    abc = thickness_cal(folder_path)

