# -*- coding: utf-8 -*-
# @Time    : 2021/3/4 20:50
# @Author  : liuxiang
# @FileName: open_pandarviewer.py
# @Software: PyCharm
# @email    ：liuxiang@hesaitech.com

import win32api as wp
import os
import time

#控制应用程序的开启和关闭
wp.ShellExecute(0, 'open', r'C:\Program Files\PandarViewX64\PandarView\bin\Pandar.exe', '','',1)
time.sleep(5)
os.system("taskkill /F /IM Pandar.exe")