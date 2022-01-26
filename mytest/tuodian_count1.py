# -*- coding: utf-8 -*-
# @Time    : 2021/3/4 20:53
# @Author  : liuxiang
# @FileName: tuodian_count1.py
# @Software: PyCharm
# @email    ：liuxiang@hesaitech.com

#from kui branch and try to use it.
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import random
import openpyxl
import math
from copy import deepcopy

BUFFER_BOUNDARY=0.08        # 统计拖点时的缓冲带距离：m
POINTS_CUT_RAT=0.06         # 拖点占比预测，决定找中心点收敛速度

# 按行的方式计算两个坐标点之间的距离
def dist(a, b):
    return np.linalg.norm(a - b)


filename = 111              # 文件名随便起0
# 主模块
if __name__ == "__main__":

    # 读文件
    df = pd.read_csv(r'C:\Users\Administrator\Desktop\11.csv')
    distanceList = list(df["distance_m"])
    aziList = list(df["azimuth_calib"])
    eleList = list(df["elevation"])

    # 找到最近的点当作基准点
    minDistance = min(distanceList)
    for i in range(len(distanceList)):
        if distanceList[i] == minDistance:
            minIndex = i
            break

   # benchMarkAzi = aziList[i]
   # benchMarkEle = eleList[i]

   # print("基准点：",benchMarkAzi,benchMarkEle)
   print('for git test')

    for i in range(len(distanceList)):
        a = math.pi
        distanceList[i] = distanceList[i]*math.cos((aziList[i]-benchMarkAzi)/180.0*math.pi)*math.cos((eleList[i]-benchMarkEle)/180.0*math.pi)

    # 设定分区数
    k = 2
    # 随机获得k个中心点
    CC=[]
    for i in range(k):
        CC.append(distanceList[np.random.randint(0, len(distanceList)-1)])

    # 列表转数组
    C = np.array(CC)
    print("随机起始点：",C)

    # 用于保存中心点更新前的坐标
    C_old = np.zeros(C.shape)
    # 迭代标识位，通过计算新旧中心点的距离
    iteration_flag = dist(C,C_old)#math.sqrt(pow(math.fabs(C[0]-C_old[0]),2) + pow(math.fabs(C[1]-C_old[1]),2))

    tmp = 1
    distances0 = []         # 近处点云
    distances1 = []         # 远处点云
    std0List = []           # 用于保留数据，计算均方差
    std1List = []           # 用于保留数据，计算均方差
    # 若中心点不再变化或循环次数不超过n次(此限制可取消)，则退出循环
    while iteration_flag.any() != 0 and tmp < 100:
        # 循环计算出每个点对应的最近中心点
        for i in range(len(distanceList)):
            if(math.fabs(distanceList[i]- C[0])<math.fabs(distanceList[i]- C[1])):
                distances0.append(distanceList[i])
            else:
                distances1.append(distanceList[i])

        # 采用深拷贝将当前的中心点保存下来
        #print("the distinct of clusters: ", set(clusters))
        C_old = deepcopy(C)
        # 从属于中心点放到一个数组中，然后按照列的方向取平均值
        C[0] = np.mean(distances0)
        C[1] = np.mean(distances1)
        distances0.sort()
        distances1.sort()
        tmpMin = min(C)
        tmpMax = max(C)
        C[0] = tmpMin
        C[1] = tmpMax
        # 去除POINTS_CUT_RAT%的拖点 找中心更快更准  前板中心拖点比重大  后板中心拖点比重小
        #if(C[0]<C[1]):
        lenCuted = int(len(distances0)*POINTS_CUT_RAT)
        del distances0[0:lenCuted]
        lenCuted = int(len(distances1) * POINTS_CUT_RAT)
        del distances1[len(distances1)-lenCuted-1:len(distances1)-1]

        std0List.clear()
        std1List.clear()
        std0List = deepcopy(distances0)
        std1List = deepcopy(distances1)
        distances0.clear()
        distances1.clear()
        tmp = tmp + 1

    #std0 = np.std(std0List, ddof=1)
    #std1 = np.std(std1List, ddof=1)
    print("前板距离：", min(C),"\n后板距离：", max(C))
    #print("前板均方差：", std0,"\n后板均方差：", std1)

    # 以下是找拖点个数  方法1  标准差+固定缓冲(经验加权)
    iPointsCounts = 0
    iPointsCountsFilter = 0
    iPointsIndexList = []   # 拖点标记
    for i in range(len(distanceList)):
        if((distanceList[i]-min(C))>BUFFER_BOUNDARY/5*2):
            if((max(C)-distanceList[i])>BUFFER_BOUNDARY/3*2):
                iPointsCounts += 1
                a = math.fabs(distanceList[i] - min(C))
                b = math.fabs(distanceList[i]- max(C))
                maxRat = max(a,b)
                minRat = min(a,b) + 0.0001
                rate = maxRat / minRat
                #if (rate < 10):
                iPointsCountsFilter += 1
                iPointsIndexList.append(i)      # 获得哪些是拖点的index列表
#                    iPointsListX.append(1+random.normalvariate(0,0.01))
#                    iPointsListY.append(distanceList[i])

    print("拖点的个数为：", iPointsCountsFilter)

    # 开始画图
    allPointsListX = list(df["Points:0"])
    allPointsListY = list(df["Points:1"])
    allPointsListXFilter = []
    allPointsListYFilter = []
    iPointsListXFilter = []
    iPointsListYFilter = []
    cPointsX = []
    cPointsY = []

    for i in range(len(distanceList)):
        if i not in iPointsIndexList:
            allPointsListXFilter.append(allPointsListX[i]*(-1))     # 画图时翻转失败  不知为何
            allPointsListYFilter.append(allPointsListY[i])
        else:
            iPointsListXFilter.append(allPointsListX[i]*(-1))       # 画图时翻转失败  不知为何
            iPointsListYFilter.append(allPointsListY[i])

    cPointsXList = deepcopy(allPointsListXFilter)
    cPointsXList.sort()
    cPointsXListMin = cPointsXList[:int(len(cPointsXList)/2)]
    cPointsXListMax = cPointsXList[int(len(cPointsXList)/2):]
    cPointsX.append(np.mean(cPointsXListMin))
    cPointsX.append(np.mean(cPointsXListMax))
    cPointsY.append(min(C)/math.cos((180-benchMarkAzi)/180.0*math.pi)*math.cos((0-benchMarkEle)/180.0*math.pi)*(-1))      # 修正正负号
    cPointsY.append(max(C)/math.cos((180-benchMarkAzi)/180.0*math.pi)*math.cos((0-benchMarkEle)/180.0*math.pi)*(-1))      # 修正正负号

    # 画图
    # 创建画图窗口
    fig = plt.figure()
    # 将画图窗口分成1行1列，选择第一块区域作子图
    ax1 = fig.add_subplot(1, 1, 1)
    # 设置标题
    ax1.set_title('Intensity Analysis')
    # 设置横坐标名称
    ax1.set_xlabel('X-axis(m)')
    ax1.xaxis.set_ticks_position('top')
    # 设置纵坐标名称
    ax1.set_ylabel('Y-axis(m)')
    # ax1.invert_xaxis() 翻转失败  不知为何
    ax1.invert_yaxis()

    # 画拖点散点图
    ax1.scatter(iPointsListXFilter, iPointsListYFilter, s=3, c='red', marker='.')
    # 画除了拖点以外的其他点
    ax1.scatter(allPointsListXFilter, allPointsListYFilter, s=3, c='blue', marker='.')
    # 画两个中心点
    ax1.scatter(cPointsX, cPointsY, s=50, c='red', marker='^')

    #plt.text(1, 1, iPointsCounts)

    # 调整横坐标的上下界
    plt.xlim(xmax=max(allPointsListXFilter)+0.5, xmin=min(allPointsListXFilter)-0.5)
    #plt.ylim(ymax=30, ymin=0)

    # 显示
    plt.show()

