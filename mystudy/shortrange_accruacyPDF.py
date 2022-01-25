# -*- coding: utf-8 -*-
# @Time    : 2020/11/16 19:18
# @Author  : liuxiang
# @FileName: shortrange_accruacyPDF.py
# @Software: PyCharm
# @email    ：liuxiang@hesaitech.com

import pdfplumber
import pandas as pd
import numpy as np
import os
from matplotlib import pyplot as plt
from matplotlib.pyplot import MultipleLocator

path = r'C:\Users\Administrator\Desktop\431_Short_Range_Accuracy_Test_Report.pdf'

pdf = pdfplumber.open(path)
head_page = 0
pdf_head = pdf.pages[head_page].extract_table()
# del pdf_head[head_page] #删除字符串的那一行数据
print(pdf_head)
# pdf_head[0][0] = 'Laser ID'

'''将表头信息替换掉'''
# for i in range(1,len(pdf_head[0])):
#     if (i % 2 != 0):
#         k = pdf_head[0][i] #将表头的信息先保存起来，老卜通过取指定的字符来实现
#         pdf_head[0][i] = pdf_head[0][i] + '-accuracy'
#     else:
#
#         pdf_head[0][i] = k
#         pdf_head[0][i] = pdf_head[0][i] + '-Precision'
#
# '''将所有的信息提取出来'''
next_page = head_page + 1
# while pdf.pages[next_page].extract_table(): #只要有就提取出来
#     pdf_head = pdf_head + pdf.pages[next_page].extract_table()
#     next_page = next_page+1
try:
    while pdf.pages[next_page].extract_table():  # 只要有就提取出来
        pdf_head = pdf_head + pdf.pages[next_page].extract_table()
        next_page = next_page + 1
except:
    pass

'''更换column的信息并删除第一行
'''
table_info = pd.DataFrame(pdf_head, columns=['laserID', 'Accuracy', 'RMSE', 'POD'], index=None)
table_new = table_info.drop(labels=[0, 1], axis=0)
table_new.reset_index(drop=True, inplace=True) #索引重构
print(table_new)
for var in table_new.columns:
    table_new[var] = table_new.apply(lambda v: float(v[var]), axis=1) #dataframe中数据结构变成数值型，否则报错；
table_new['POD'] = table_new.apply(lambda x:x['POD']/100,axis=1)
print(table_new)
accuracy_test = list(table_new['Accuracy'])
max_acc = max(accuracy_test)
min_acc = min(accuracy_test)
ind_max = table_new["Accuracy"].idxmax() #找到最大的ID
ind_min = table_new["Accuracy"].idxmin()
print('所有通道中准度最大的通道是%d,数值是%f'%(ind_max+1,max_acc))
print('所有通道中准度最小的通道是%d,数值是%f'%(ind_min+1,min_acc))
# print(max_acc)
# print(min_acc)
rmse_test = list(table_new['RMSE'])
max_rmse = max(rmse_test)
min_rmse = min(rmse_test)
rmseID_max = table_new["RMSE"].idxmax() #找到最大的ID
rmseID_min = table_new["RMSE"].idxmin()
# print(max_rmse)
# print(min_rmse)
print('所有通道中精度最大的通道是%d,数值是%f'%(rmseID_max+1,max_rmse))
print('所有通道中精度最小的通道是%d,数值是%f'%(rmseID_min+1,min_rmse))
fig = plt.figure()
lx1 = table_new['laserID']
for k in ['Accuracy','RMSE','POD']:
    plt.clf()
    ax = fig.add_subplot()
    if k =='Accuracy':
        ax.set_ylim(-6,6)
        ax.set_yticks(np.arange(-6, 6, 0.5))
    elif k == 'RMSE':
        ax.set_ylim(-4, 4)
        ax.set_yticks(np.arange(-4, 4, 0.5))
    else:
        ax.set_ylim(0.5,1)
        ax.set_yticks(np.arange(0.5, 1, 0.1))
    ly1 = table_new[k]
    ax.scatter(lx1, ly1, alpha=0.5)
    path = os.path.join('highshort_range', '{:s}.png'.format(k))
    plt.savefig(path,facecolor='white', dpi=200)


# plt.title("pod of laserID", fontsize=22)
# plt.xlabel("LaserID", fontsize=22)
# plt.ylabel("POD", fontsize=22)
# x_major_locator = MultipleLocator(2)
# # 把x轴的刻度间隔设置为1，并存在变量里
# y_major_locator = MultipleLocator(1)
# # 把y轴的刻度间隔设置为10，并存在变量里
# ax = plt.gca()
# # ax为两条坐标轴的实例
# ax.xaxis.set_major_locator(x_major_locator)
# # 把x轴的主刻度设置为1的倍数
# ax.yaxis.set_major_locator(y_major_locator)
# plt.savefig('testpic')


# table_column = table_info.loc[[0]]
# print(type(table_column))
# table_columnlist = np.array(table_column).tolist()
# table_columnlist = table_columnlist[0]
# table_info.columns = table_columnlist
# table_info.drop(index = 0,inplace = True)

#
'''替换掉换行符'''
# table_info['Laser ID'] = table_info['Laser ID'].apply(lambda x:x.replace('\n', '').replace('\r', '')) #列索引如果是字符串，用'',数值的话直接写就可以

'''保存成csv'''
# table_info.to_csv(r'C:\Users\Administrator\Desktop\table_info.csv')
#
# print(table_info)
