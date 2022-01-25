# -*- coding: utf-8 -*-
# @Time    : 2021/1/4 17:03
# @Author  : liuxiang
# @FileName: muti_process_study.py
# @Software: PyCharm
# @email    ：liuxiang@hesaitech.com

from multiprocessing import Process
import os

def info(title):
    print(title)
    print('module name:', __name__)
    print('parent process:', os.getppid())
    print('process id:', os.getpid())

def f(name):
    info('function f')
    print('hello', name)

if __name__ == '__main__':
    info('main line')
    p = Process(target=f, args=('bob',))
    p.start()
    p.join()