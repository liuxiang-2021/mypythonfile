#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
=================================================
@IDE    ：PyCharm
@Author ：Bu Yujun
@Date   ：2020/9/20 13:37
@Desc   ：
==================================================
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
import pdfplumber
import re
import copy


class PDFReadPlot(object):

    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False

    def __init__(self, pdf_path, header_page=1):
        pdf = pdfplumber.open(pdf_path)
        self.pdf = pdf_path
        self.distance_type = []
        self.pdf_table = []
        self.pdf_df = []
        self.pdf_df_oneline = []
        self.cm = plt.cm.get_cmap('jet')

        # 找到有表头的那一页
        header_table = pdf.pages[header_page].extract_table()
        del header_table[1]
        header_table[0][0] = 'LaserID'

        # 修改表头为可容易理解
        def header_(string):
            return int(round(float(string[:-1]), 0))

        for i in range(1, len(header_table[0])):
            if i % 2 != 0:
                self.distance_type.append(header_(header_table[0][i]))
                header_table[0][i] = str(header_(header_table[0][i])) + 'm-Accuracy'
            else:
                header_table[0][i] = header_table[0][i - 1][:-9] + '-Precision'

        # 获取其余的数据
        self.pdf_table = self.pdf_table + header_table
        content_page = header_page + 1
        while pdf.pages[content_page].extract_table():
            self.pdf_table += pdf.pages[content_page].extract_table()
            content_page += 1

        # 修改成可以画图的数据格式
        pdf_df = pd.DataFrame(self.pdf_table[1:], columns=header_table[0])
        for columns_name in pdf_df.columns:
            if columns_name == 'LaserID':
                pdf_df[columns_name] = pdf_df[columns_name].map\
                    (lambda x: int(re.findall(r'\d+\.?\d*', x)[0]))
            else:
                pdf_df[columns_name] = pdf_df[columns_name].map\
                    (lambda x: float(x))
        self.pdf_df = pdf_df

        # 所有距离的数据放在一起
        pdf_df_oneline = {}
        pdf_df_oneline['LaserID'] = list(self.pdf_df['LaserID'])*len(self.distance_type)
        pdf_df_oneline['Distance'], pdf_df_oneline['Accuracy'], pdf_df_oneline['Precision'] = [], [], []
        for distance in self.distance_type:
            pdf_df_oneline['Distance'] += [distance]*len(self.pdf_df)
            pdf_df_oneline['Accuracy'] += list(self.pdf_df[str(distance)+'m-Accuracy'])
            pdf_df_oneline['Precision'] += list(self.pdf_df[str(distance) + 'm-Precision'])
        self.pdf_df_oneline = pd.DataFrame.from_dict(pdf_df_oneline)

    @staticmethod #静态方法，不需要访问其他方法和属性；
    def mkdir(path):
        folder = os.path.exists(path)
        if not folder:
            os.makedirs(path)

    def plotbydistance(self, folder: str = 'ByDistance'):
        folder = self.pdf[:-4] + '_' + folder
        self.mkdir(folder)
        fig = plt.figure(figsize=(20, 8))
        size = 50
        fontsize = 20
        data = self.pdf_df
        for distance in self.distance_type:
            plt.clf()
            ax = fig.add_subplot(111)
            ax.scatter(data['LaserID'], data['{:d}m-Accuracy'.format(distance)], s=size, marker='o',
                       label='Accuracy[cm]')
            ax.scatter(data['LaserID'], data['{:d}m-Precision'.format(distance)], s=size, marker='o',
                       label='Precision[cm]')
            ax.set_xlabel('Channel ID', fontsize=fontsize)
            ax.set_ylabel('Accuracy/Precision[cm]', fontsize=fontsize)
            ax.set_title('{:s}-{:d}m\n'.format(self.pdf[:-4], distance), fontsize=fontsize * 1.5)
            ax.set_xlim(0, len(self.pdf_df)+2)
            ax.set_xticks(np.arange(0, len(self.pdf_df)+2, 8))
            ax.set_ylim(-5, 5)
            ax.set_yticks(np.arange(-5, 5.1, 1))
            ax.tick_params(axis='both', labelsize=fontsize)
            ax.grid(True)
            ax.legend(fontsize=fontsize)
            pic_path = os.path.join(folder, '{:s}-{:d}m.png'.format(self.pdf[:-4], distance))
            plt.savefig(pic_path, facecolor='white', dpi=200)

    def plotbychannel(self, folder: str = 'ByChannel'):
        folder = self.pdf[:-4] + '_' + folder
        self.mkdir(folder)

        # 增加水平随机偏移，以增加水平区分度
        np.random.seed(128)
        data = copy.deepcopy(self.pdf_df_oneline)
        data['Distance'] = data['Distance'].map(lambda x: x + np.random.normal(0, 0.6, 1)[0])

        fig = plt.figure(figsize=(12, 12))
        size = 30
        fontsize = 20
        for k in ['Accuracy', 'Precision']:
            plt.clf()
            ax = fig.add_subplot(111)
            pic = ax.scatter(data['Distance'], data[k], c=data['LaserID'], s=size, vmin=1, vmax=len(self.pdf_df),
                             cmap=self.cm, marker='o')
            cb = plt.colorbar(pic)
            cb.set_label('Channel ID', size=fontsize)
            cbx = cb.ax
            cbx.tick_params(labelsize=fontsize)
            ax.set_xlabel('Distance[m]', fontsize=fontsize)
            ax.set_ylabel('{:s}[cm]'.format(k), fontsize=fontsize)
            ax.set_title('{:s}-{:s}\n'.format(self.pdf[:-4], k), fontsize=fontsize * 1.5)
            ax.set_xlim(0, max(self.distance_type)+5)
            ax.set_xticks(self.distance_type)
            if k != 'Accuracy':
                ax.set_ylim(0, 4)
                ax.set_yticks(np.arange(0, 4.1, 0.5))
            else:
                ax.set_ylim(-5, 5)
                ax.set_yticks(np.arange(-5, 5.1, 1))
            ax.tick_params(axis='both', labelsize=fontsize)
            pic_path = os.path.join(folder, '{:s}-{:s}.png'.format(self.pdf[:-4], k))
            plt.savefig(pic_path, facecolor='white', dpi=200)

    def plotbybank(self, folder: str = 'ByBank'):
        folder = self.pdf[:-4] + '_' + folder
        self.mkdir(folder)

        # 读取bank信息
        bank = pd.read_excel('Channel Bank.xlsx', index_col=None).to_dict('list')
        data_bank = {}
        for i in range(0, 8):
            np.random.seed(i)
            bankname = 'Bank' + str(i)
            data_bank[bankname] = {}
            data_bank[bankname]['LaserID'] = [ID for ID in self.pdf_df_oneline['LaserID'] if ID in bank[bankname]]
            data_bank[bankname]['Distance'] = [self.pdf_df_oneline['Distance'][k] + np.random.normal(0, 0.6, 1)[0]
                                               for k in range(len(self.pdf_df_oneline['LaserID'])) if
                                               self.pdf_df_oneline['LaserID'][k] in bank[bankname]]
            data_bank[bankname]['Accuracy'] = [self.pdf_df_oneline['Accuracy'][k] for k in range(len(self.pdf_df_oneline['LaserID'])) if
                                               self.pdf_df_oneline['LaserID'][k] in bank[bankname]]
            data_bank[bankname]['Precision'] = [self.pdf_df_oneline['Precision'][k] for k in range(len(self.pdf_df_oneline['LaserID'])) if
                                                self.pdf_df_oneline['LaserID'][k] in bank[bankname]]

        fig = plt.figure(figsize=(12, 12))
        size = 30
        fontsize = 20
        for bankname in bank.keys():
            for k in ['Accuracy', 'Precision']:
                plt.clf()
                ax = fig.add_subplot(1, 1, 1)
                pic = ax.scatter(data_bank[bankname]['Distance'], data_bank[bankname][k],
                                 c=data_bank[bankname]['LaserID'], s=size, vmin=1, vmax=128, cmap=self.cm, marker='o')
                cb = plt.colorbar(pic)
                cb.set_label('Channel ID', size=fontsize)
                cbx = cb.ax
                cbx.tick_params(labelsize=fontsize)
                ax.set_xlabel('Distance[m]', fontsize=fontsize)
                ax.set_ylabel('{:s}[cm]'.format(k), fontsize=fontsize)
                ax.set_title('{:s}-{:s}-{:s}\n'.format(self.pdf[-4], bankname, k), fontsize=fontsize * 1.5)
                ax.set_xlim(0, max(self.distance_type)+5)
                ax.set_xticks(self.distance_type)
                if k != 'Accuracy':
                    ax.set_ylim(0, 4)
                    ax.set_yticks(np.arange(0, 4, 0.5))
                else:
                    ax.set_ylim(-5, 5)
                    ax.set_yticks(np.arange(-5, 5.1, 1))
                ax.tick_params(axis='both', labelsize=fontsize)
                pic_path = os.path.join(folder, '{:s}-{:s}-{:s}.png'.format(self.pdf[-4], bankname, k))
                plt.savefig(pic_path, facecolor='white', dpi=200)

if __name__ == '__main__':
    data = PDFReadPlot(r'ZEUS-T1-0837_Fail.pdf')
    data.plotbydistance()
    data.plotbychannel()
    # data.plotbybank()