# -*- coding: utf-8 -*-
# @Time    : 2021/3/4 20:52
# @Author  : liuxiang
# @FileName: photogettext1.py
# @Software: PyCharm
# @email    ：liuxiang@hesaitech.com

# 用于识别出屏幕特定位置的数字，满足一定的温度条件后录制特定时长的点云
# https://www.cnblogs.com/BackingStar/p/11254120.html 识别图片上数字教程，
# 需要下载识别引擎


import pyautogui
import pytesseract
from PIL import Image


import win32api
import win32con
from ctypes import *
import time


def screenshot():
    img = pyautogui.screenshot()
    img.save('screenshot.png')

def image2str(img):
    text = pytesseract.image_to_string(Image.open(img), lang="eng")
    return text


if __name__ == '__main__':
       # img = screenshot()   # 截取图片的位置
        #time.sleep(1)
        temp_str = image2str('123.png')
        #temp_str = temp_str[0:4]
        print(temp_str)