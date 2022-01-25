# -*- coding: utf-8 -*-
# @Time    : 2020/11/30 19:44
# @Author  : liuxiang
# @FileName: range_detect.py
# @Software: PyCharm
# @email    ：liuxiang@hesaitech.com

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
         data.columns = ['laserID','range_ability','2','spec_range','4','5','6','7']
         l1 = data['laserID']
         l2 = data['range_ability']
         l3 = data['spec_range']
         fig = plt.figure()
         plt.clf()
         ax = fig.add_subplot()
         ax.plot(l1,l2,'b-',label ='Range detect ability')
         ax.plot(l1,l3,'g-',label ='Spec value')
         fontsize = 10
         ax.set_xlabel('LaserID', fontsize=fontsize)
         ax.set_ylabel('测远能力[m]', fontsize=fontsize)
         ax.set_title('{:s}-测远能力\n'.format(self.name), fontsize=fontsize)
         x_major_locator = MultipleLocator(5)
         ax.xaxis.set_major_locator(x_major_locator)
         ax.set_xlim(0, 128)
         ax.legend()
         path = os.path.join('distance_range', '{:s}-测远能力.png'.format(self.name))
         plt.savefig(path, facecolor='white', dpi=200)
         plt.show()


if __name__ == '__main__':
    folder_path = r'C:\Users\Administrator\Desktop\111'
    abc = range_detect(folder_path)