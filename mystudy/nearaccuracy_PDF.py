# -*- coding: utf-8 -*-
# @Time    : 2020/11/24 19:48
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
import copy
from matplotlib.pyplot import MultipleLocator


class nearaccuracy_datacollect(object):

    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False

    def __init__(self, folder_path):

        self.folder = folder_path
        self.path = os.path.join(folder_path, '*.pdf')
        self.frame = glob.glob(self.path)
        self.distance_type = [0.3, 0.5, 0.8, 1.2]

        for frame in self.frame:
            try:  #增加try会让报错不显示，当有些Bug不显示的时候
                data = self.collect_PDFdata(frame)
                name = frame.split('\\')[-1]
                self.lidarname = name.split('_')[0]
                self.detect_maxmin(data)
                self.plotbydistance(data, self.lidarname)
                new_data = self.data_tochange(data)
                self.plotbychannel(new_data,self.lidarname)
            except:
                pass


    def collect_PDFdata(self,path):
        pdf = pdfplumber.open(path)
        head_page = 0
        pdf_head = pdf.pages[head_page].extract_table()
        # print(pdf_head)
        next_page = head_page + 1
        try:
            while pdf.pages[next_page].extract_table():  # 只要有就提取出来
                pdf_head = pdf_head + pdf.pages[next_page].extract_table()
                next_page = next_page + 1
        except:
            pass
        table_info = pd.DataFrame(pdf_head, columns=['laserID', '0.3m-Accuracy', '0.3m-RMSE','0.5m-Accuracy', '0.5m-RMSE','0.8m-Accuracy', '0.8m-RMSE','1.2m-Accuracy', '1.2m-RMSE'], index=None)
        table_new = table_info.drop(labels=[0, 1], axis=0)
        table_new.reset_index(drop=True, inplace=True) #索引重构
        # print(type(list(table_new['0.3m-Accuracy'])[1]))
        table_new.replace(to_replace=r'^\s*$', value=np.nan, regex=True, inplace=True) #此DataFrame中有空格，空格并不是为空，所以需要先把空格替换掉之后，然后把带有空格行去掉
        table_new.dropna(axis=0, how='any', inplace=True)
        print(table_new)
        for var in table_new.columns:
            table_new[var] = table_new.apply(lambda v: float(v[var]), axis=1) #dataframe中数据结构变成数值型，否则报错；
        return table_new

    def detect_maxmin(self,data):
        for k in data.columns:
            if k == 'laserID':
                pass
            else:
                accuracy_test = list(data[k])
                max_acc = max(accuracy_test)
                min_acc = min(accuracy_test)
                ind_max = data[k].idxmax()  # 找到最大的ID
                ind_min = data[k].idxmin()
                print('所有通道中'+ k + '最大为%d,数值为%f'% (ind_max + 1, max_acc))
                print('所有通道中' + k + '最小为%d,数值为%f' % (ind_min + 1, min_acc))

    def data_tochange(self,data):
        pdf_df_oneline = {}
        pdf_df_oneline['LaserID'] = list(data['laserID']) * len(self.distance_type)
        pdf_df_oneline['Distance'], pdf_df_oneline['Accuracy'], pdf_df_oneline['Precision'] = [], [], []
        for distance in self.distance_type:
            pdf_df_oneline['Distance'] += [distance] * len(data)
            pdf_df_oneline['Accuracy'] += list(data[str(distance) + 'm-Accuracy'])
            pdf_df_oneline['Precision'] += list(data[str(distance) + 'm-RMSE'])
        pdf_df_oneline = pd.DataFrame.from_dict(pdf_df_oneline)
        return pdf_df_oneline

    def plotbychannel(self, data, name):

        # 增加水平随机偏移，以增加水平区分度
        np.random.seed(128)
        data = copy.deepcopy(data)
        data['Distance'] = data['Distance'].map(lambda x: x + np.random.normal(0, 0.01, 1)[0])
        fig = plt.figure(figsize=(12, 12))
        size = 30
        fontsize = 20
        for k in ['Accuracy', 'Precision']:
            plt.clf()
            ax = fig.add_subplot(111)
            pic = ax.scatter(data['Distance'], data[k], c=data['LaserID'], s=size, vmin=1, vmax=len(data),marker='o')
            cb = plt.colorbar(pic)
            cb.set_label('Channel ID', size=fontsize)
            cbx = cb.ax
            cbx.tick_params(labelsize=fontsize)
            ax.set_xlabel('Distance[m]', fontsize=fontsize)
            ax.set_ylabel('{:s}[cm]'.format(k), fontsize=fontsize)
            ax.set_title('{:s}-{:s}\n'.format(name, k), fontsize=fontsize * 1.5)
            ax.set_xlim(0, max(self.distance_type)+0.2)
            ax.set_xticks(self.distance_type)
            if k == 'Accuracy':
                ax.set_ylim(-10, 10)
                ax.set_yticks(np.arange(-10, 10, 2))
            else:
                ax.set_ylim(0, 5)
                ax.set_yticks(np.arange(0, 5.1, 1))
            ax.tick_params(axis='both', labelsize=fontsize)
            path = os.path.join('nearshort_range', '{:s}-{:s}.png'.format(name,k))
            plt.savefig(path, facecolor='white', dpi=200)

    def plotbydistance(self, data, name):
        fig = plt.figure(figsize=(20, 8))
        size = 50
        fontsize = 20
        for distance in self.distance_type:
            plt.clf()
            ax = fig.add_subplot(111)
            ax.scatter(data['laserID'], data['{:.1f}m-Accuracy'.format(distance)], s=size, marker='o',
                       label='Accuracy[cm]')
            ax.scatter(data['laserID'], data['{:.1f}m-RMSE'.format(distance)], s=size, marker='o',
                       label='Precision[cm]')
            ax.set_xlabel('Channel ID', fontsize=fontsize)
            ax.set_ylabel('Accuracy/Precision[cm]', fontsize=fontsize)
            ax.set_title('{:s}-{:.1f}m\n'.format(name, distance), fontsize=fontsize * 1.5)
            ax.set_xlim(0, max(data['laserID']) + 2)
            ax.set_xticks(np.arange(0, max(data['laserID']) + 2, 8))
            ax.set_ylim(-5, 5)
            ax.set_yticks(np.arange(-5, 5.1, 1))
            ax.tick_params(axis='both', labelsize=fontsize)
            ax.grid(True)
            ax.legend(fontsize=fontsize)
            pic_path = os.path.join('nearshort_range', '{:s}-{:.1f}m.png'.format(name, distance))
            plt.savefig(pic_path, facecolor='white', dpi=200)

    # def plot_data(self,data,name):
    #     fig = plt.figure()
    #     lx1 = data['laserID']
    #     for k in ['Accuracy', 'RMSE', 'POD']:
    #         plt.clf()
    #         ax = fig.add_subplot()
    #         if k == 'Accuracy':
    #             ax.set_ylim(-6, 6)
    #             ax.set_yticks(np.arange(-6, 6, 0.5))
    #         elif k == 'RMSE':
    #             ax.set_ylim(-4, 4)
    #             ax.set_yticks(np.arange(-4, 4, 0.5))
    #         else:
    #             ax.set_ylim(0.5, 1)
    #             ax.set_yticks(np.arange(0.5, 1, 0.1))
    #         ly1 = data[k]
    #         ax.scatter(lx1, ly1, alpha=0.5)
    #         path = os.path.join('nearshort_range', '{:s}-{:s}.png'.format(name,k))
    #         plt.savefig(path, facecolor='white', dpi=200)


if __name__ == '__main__':
    folder_path = r'C:\Users\Administrator\Desktop\1'
    abc = nearaccuracy_datacollect(folder_path)