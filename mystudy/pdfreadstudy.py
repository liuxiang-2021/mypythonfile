# -*- coding: utf-8 -*-
# @Time    : 2020/10/13 15:12
# @Author  : liuxiang
# @FileName: pdfreadstudy.py
# @Software: PyCharm
# @email    ：liuxiang@hesaitech.com

import pdfplumber
import pandas as pd
import numpy as np
import os

path = r'C:\Users\Administrator\Desktop\431_Short_Range_Accuracy_Test_Report.pdf'

pdf = pdfplumber.open(path)
head_page = 1
pdf_head = pdf.pages[head_page].extract_table()
del pdf_head[head_page] #删除字符串的那一行数据
print(pdf_head)
pdf_head[0][0] = 'Laser ID'

'''将表头信息替换掉'''
for i in range(1,len(pdf_head[0])):
    if (i % 2 != 0):
        k = pdf_head[0][i] #将表头的信息先保存起来，老卜通过取指定的字符来实现
        pdf_head[0][i] = pdf_head[0][i] + '-accuracy'
    else:

        pdf_head[0][i] = k
        pdf_head[0][i] = pdf_head[0][i] + '-Precision'

'''将所有的信息提取出来'''
next_page = head_page + 1
# while pdf.pages[next_page].extract_table(): #只要有就提取出来
#     pdf_head = pdf_head + pdf.pages[next_page].extract_table()
#     next_page = next_page+1

try:
    while pdf.pages[next_page].extract_table(): #只要有就提取出来
        pdf_head = pdf_head + pdf.pages[next_page].extract_table()
        next_page = next_page+1
except:
    pass

'''更换column的信息并删除第一行
'''
table_info = pd.DataFrame(pdf_head)
table_column = table_info.loc[[0]]
print(type(table_column))
table_columnlist = np.array(table_column).tolist()
table_columnlist = table_columnlist[0]
table_info.columns = table_columnlist
table_info.drop(index = 0,inplace = True)

'''替换掉换行符'''
table_info['Laser ID'] = table_info['Laser ID'].apply(lambda x:x.replace('\n', '').replace('\r', '')) #列索引如果是字符串，用'',数值的话直接写就可以

'''保存成csv'''
table_info.to_csv(r'C:\Users\Administrator\Desktop\table_info.csv')

print(table_info)





