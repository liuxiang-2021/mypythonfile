# -*- coding: utf-8 -*-
# @Time    : 2020/11/24 16:59
# @Author  : liuxiang
# @FileName: nearaccuracy_PDF.py
# @Software: PyCharm
# @email    ：liuxiang@hesaitech.com
import pdfplumber
import pandas as pd
import numpy as np
import os
from matplotlib import pyplot as plt
import glob
from matplotlib.pyplot import MultipleLocator


class nearaccuracy_datacollect(object):

    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False

    def __init__(self, folder_path):

        self.folder = folder_path
        self.path = os.path.join(folder_path, '*.pdf')
        self.frame = glob.glob(self.path)

        for frame in self.frame:
            try:
                data = self.collect_PDFdata(frame)
                name = frame.split('\\')[-1]
                self.lidarname = name.split('_')[0]
                self.detect_maxmin(data)
                self.new_plot_data(data,self.lidarname)
            except:
                pass


    def collect_PDFdata(self,path):
        pdf = pdfplumber.open(path)
        head_page = 0
        pdf_head = pdf.pages[head_page].extract_table()
        print(pdf_head)
        next_page = head_page + 1
        try:
            while pdf.pages[next_page].extract_table():  # 只要有就提取出来
                pdf_head = pdf_head + pdf.pages[next_page].extract_table()
                next_page = next_page + 1
        except:
            pass
        table_info = pd.DataFrame(pdf_head, columns=['laserID', 'Accuracy', 'RMSE', 'POD'], index=None)
        table_new = table_info.drop(labels=[0, 1], axis=0)
        table_new.reset_index(drop=True, inplace=True) #索引重构
        print(table_new)
        for var in table_new.columns:
            table_new[var] = table_new.apply(lambda v: float(v[var]), axis=1) #dataframe中数据结构变成数值型，否则报错；
        table_new['POD'] = table_new.apply(lambda x:x['POD']/100,axis=1)
        table_new.to_csv(r'C:\Users\Administrator\Desktop\table_info.csv')
        return table_new

    def detect_maxmin(self,data):
        accuracy_test = list(data['Accuracy'])
        max_acc = max(accuracy_test)
        min_acc = min(accuracy_test)
        ind_max = data["Accuracy"].idxmax()  # 找到最大的ID
        ind_min = data["Accuracy"].idxmin()
        print('所有通道中准度最大的通道是%d,数值是%f' % (ind_max + 1, max_acc))
        print('所有通道中准度最小的通道是%d,数值是%f' % (ind_min + 1, min_acc))
        # print(max_acc)
        # print(min_acc)
        rmse_test = list(data['RMSE'])
        max_rmse = max(rmse_test)
        min_rmse = min(rmse_test)
        rmseID_max = data["RMSE"].idxmax()  # 找到最大的ID
        rmseID_min = data["RMSE"].idxmin()
        print('所有通道中精度最大的通道是%d,数值是%f' % (rmseID_max + 1, max_rmse))
        print('所有通道中精度最小的通道是%d,数值是%f' % (rmseID_min + 1, min_rmse))
        pod_test = list(data['POD'])
        max_pod = max(pod_test)
        min_pod = min(pod_test)
        podID_max = data['POD'].idxmax()
        podID_min = data['POD'].idxmin()
        print('所有通道中POD最大的通道是%d,数值是%f' % (podID_max + 1, max_pod))
        print('所有通道中POD最小的通道是%d,数值是%f' % (podID_min + 1, min_pod))



    def plot_data(self,data,name):
        fig = plt.figure(figsize=(20,8))
        lx1 = data['laserID']
        for k in ['Accuracy', 'RMSE', 'POD']:
            plt.clf()
            ax = fig.add_subplot()
            if k == 'Accuracy':
                ax.set_ylim(-8, 8)
                ax.set_yticks(np.arange(-8, 8, 0.5))
                fontsize = 20
                ax.set_xlabel('LaserID', fontsize=fontsize)
                ax.set_ylabel('准度值[cm]', fontsize=fontsize)
                ax.set_title('{:s}-{:s}\n'.format(name, k), fontsize=fontsize)
            elif k == 'RMSE':
                ax.set_ylim(0, 6)
                ax.set_yticks(np.arange(0, 6, 0.5))
                fontsize = 20
                ax.set_xlabel('LaserID', fontsize=fontsize)
                ax.set_ylabel('RMSE[cm]', fontsize=fontsize)
                ax.set_title('{:s}-{:s}\n'.format(name, k), fontsize=fontsize)
            else:
                ax.set_ylim(0.5, 1)
                ax.set_yticks(np.arange(0.5, 1, 0.1))
                fontsize = 20
                ax.set_xlabel('LaserID', fontsize=fontsize)
                ax.set_ylabel('POD', fontsize=fontsize)
                ax.set_title('{:s}-{:s}\n'.format(name, k), fontsize=fontsize)
            ly1 = data[k]
            ax.scatter(lx1, ly1, alpha=0.5)
            path = os.path.join('highshort_range', '{:s}-{:s}.png'.format(name,k))
            plt.savefig(path, facecolor='white', dpi=200)

    def new_plot_data(self,data,name):
        fig = plt.figure(figsize=(20,8))
        size = 50
        fontsize = 20
        plt.clf()
        for k in ['Accuracy', 'RMSE', 'POD']:
            if k == 'Accuracy' or k=='RMSE':
                ax = fig.add_subplot()
                ax.scatter(data['laserID'], data['Accuracy'], s=size, marker='o',
                           label='Accuracy[cm]')
                ax.scatter(data['laserID'], data['RMSE'], s=size, marker='o',
                           label='Precision[cm]')
                ax.set_xlabel('Channel ID', fontsize=fontsize)
                ax.set_ylabel('Accuracy/Precision[cm]', fontsize=fontsize)
                ax.set_title('{:s}-accuracy and precision\n'.format(name), fontsize=fontsize * 1.5)
                ax.set_xlim(0, len(data['laserID']) + 2)
                ax.set_xticks(np.arange(0, len(data['laserID']) + 2, 8))
                ax.set_ylim(-5, 5)
                ax.set_yticks(np.arange(-5, 5.1, 1))
                ax.tick_params(axis='both', labelsize=fontsize)
                ax.grid(True)
                ax.legend(fontsize=fontsize)
                pic_path = os.path.join('highshort_range', '{:s}-accuracy and precision.png'.format(name))
                plt.savefig(pic_path, facecolor='white', dpi=200)
                plt.clf() #保存完成后清除图形，
            else:
                ax = fig.add_subplot()
                ax.scatter(data['laserID'], data['POD'], s=size, marker='o',
                           label='POD')
                ax.set_xlabel('Channel ID', fontsize=fontsize)
                ax.set_ylabel('POD', fontsize=fontsize)
                ax.set_title('{:s}-POD\n'.format(name), fontsize=fontsize * 1.5)
                ax.set_xlim(0, len(data['laserID']) + 2)
                ax.set_xticks(np.arange(0, len(data['laserID']) + 2, 8))
                ax.set_ylim(0, 1)
                ax.set_yticks(np.arange(0, 1.2, 0.2))
                ax.tick_params(axis='both', labelsize=fontsize)
                ax.grid(True)
                ax.legend(fontsize=fontsize)
                pic_path = os.path.join('highshort_range', '{:s}-POD.png'.format(name))
                plt.savefig(pic_path, facecolor='white', dpi=200)


if __name__ == '__main__':
    folder_path = r'C:\Users\Administrator\Desktop\111'
    abc = nearaccuracy_datacollect(folder_path)