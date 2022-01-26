# -*- coding: utf-8 -*-
# @Time    : 2021/2/24 20:12
# @Author  : liuxiang
# @FileName: plot_workmode.py
# @Software: PyCharm
# @email    ：liuxiang@hesaitech.com
#

#just test here
from matplotlib import pyplot as plt
import pandas as pd
import glob
import os
import warnings
from matplotlib.pyplot import MultipleLocator

warnings.filterwarnings('ignore')

class range_detect(object):

    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False

    def __init__(self,folder_path):
        self.folder = folder_path
        self.path = os.path.join(self.folder,'*csv')
        self.frame = glob.glob(self.path)
        for frame in self.frame:
            name = frame.split('\\')[-1]
            self.name = name.split('.')[0]
            df = pd.read_csv(frame)
            self.plot_data(df)


    def plot_data(self,data):
         data['times(s)'] = data['Time'] - data['Time'][0] #增加新的一列
         l1 = data['times(s)']
         l2 = data['rfb_Temp']
         l3 = data['cb3_Temp']
         l4 = data['cb5_Temp']
         l5 = data['TMB_FPGA_Temp']
         l6 = data['work_mode']
         l1_value = max(l1)
         fig = plt.figure()
         plt.clf()
         ax = fig.add_subplot()
         ax.plot(l1,l2,'b-',label = 'rfb')
         ax.plot(l1,l3,'g-', label='cb3')
         ax.plot(l1,l4,'r-',label ='cb5')
         ax.plot(l1,l5,'k--',label ='FPGA')
         fontsize = 10
         ax.set_xlabel('持续加热时间(S)', fontsize=fontsize)
         ax.set_ylabel('温度[°C]', fontsize=fontsize)
         ax.set_title('{:s}-动态性能模式与时间、温度关系\n'.format(self.name), fontsize=fontsize)
         x_major_locator = MultipleLocator(50)
         ax.xaxis.set_major_locator(x_major_locator)
         # plt.xlim(0,l1_value)
         ax.set_xlim(0,l1_value) #都用ax来表示
         ax.text(300, 130, r'$\mu=100,\ \sigma=15$')
         ax2 = ax.twinx()
         ax2.plot(l1,l6,'y-',label = 'shutdown flag')
         ax2.set_ylim(0, 4)
         ax2.set_ylabel('shutdown flag')
         ax.legend()
         ax2.legend()
         ax2.text(300, 3.5, r'$\mu=100,\ \sigma=15$') #利用ax对象可以在ax与ax2设置提示文本
         ax2.annotate('local max', xy=(600, 3), xytext=(700, 3.5),    #用ax对象设置注释，注释名称，注释点位置，文档的位置，箭头颜色和大小等
                     arrowprops=dict(facecolor='black', shrink=0.05))
         path = os.path.join('workmode_plot', '{:s}-动态性能.png'.format(self.name))
         plt.savefig(path, facecolor='white', dpi=200)
         plt.show()


if __name__ == '__main__':
    folder_path = r'C:\Users\Administrator\Desktop\111'
    abc = range_detect(folder_path)
