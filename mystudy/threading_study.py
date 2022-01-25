# -*- coding: utf-8 -*-
# @Time    : 2020/11/19 11:24
# @Author  : liuxiang
# @FileName: threading_study.py
# @Software: PyCharm
# @email    ：liuxiang@hesaitech.com

# import threading, time


# def run(n):
#     # 获得信号量，信号量减一
#     semaphore.acquire()
#     time.sleep(1)
#     print("run the thread: %s" % n)
#
#     # 释放信号量，信号量加一
#     semaphore.release()
#     #semaphore.release()    # 可以多次释放信号量，每次释放计数器+1
#     #semaphore.release()    # 可以多次释放信号量，每次释放计数器+1
#
#
# if __name__ == '__main__':
#
#     num = 0
#     semaphore = threading.Semaphore(2)  # 最多允许2个线程同时运行(即计数器值)；在多次释放信号量后，计数器值增加后每次可以运行的线程数也会增加
#     for i in range(20):
#         t = threading.Thread(target=run, args=(i,))
#         t.start()
#
# while threading.active_count() != 1:
#     pass  # print threading.active_count()
# else:
#     print('----all threads done---')
#     print(num)

import threading
import time

def run():
    print(threading.current_thread().getName(), "开始工作")
    time.sleep(2)       # 子线程停2s
    print("子线程工作完毕")

for i in range(3):
    t = threading.Thread(target=run,)
    t.setDaemon(True)   # 把子线程设置为守护线程，必须在start()之前设置
    t.start()

time.sleep(1)     # 主线程停1秒
print("主线程结束了！")
print(threading.active_count())  # 输出活跃的线程数