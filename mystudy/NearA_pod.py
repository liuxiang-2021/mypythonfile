# -*- coding: utf-8 -*-
# @Time    : 2021/2/25 13:25
# @Author  : liuxiang
# @FileName: NearA_pod.py
# @Software: PyCharm
# @email    ：liuxiang@hesaitech.com

'''当前的目标是集成POD csv表的生成以及根据csv生成对应的图'''

import pandas as pd
import os
import csv
import math
from datetime import datetime

import numpy as np
import matplotlib.pyplot as plt
import copy
import warnings
warnings.filterwarnings('ignore')

def gen_near_pod(file, realdis, laser_num):
    # file_df = pd.read_csv(file)
    # file_df = pd.DataFrame(columns=["distance", "laser_id", "azimuth"])
    file_data = pd.DataFrame(columns=["laser_id","theory_points","real_points"])
    final_list = []
    # filename = os.path.basename(file).split(".csv")[0]
    with open(file, newline="", encoding='utf8') as csvfile:
        try:
            print("start  file: %s" % file)
            lines = csv.reader(csvfile)
            count = 0
            for line in lines:
                count += 1
                if line[0] == "distance":
                    d = line
                    laserId = int(line[1])
                elif line[0] == "azimuth":
                    c = line
                    df = pd.DataFrame({"distance": d[5:],"azimuth": c[5:]}, dtype=float)  #把一行的数据整体提取出来
                    if df.empty:
                        continue
                    else:
                        df["laser_id"] = laserId
                        az_max = max(list(df["azimuth"]))
                        az_min = min(list(df["azimuth"]))
                        th_points = int((az_max-az_min)/0.4+1)*2
                        temp_df = df[(df["distance"] < realdis + 1.0) & (df["distance"] >0)]
                        re_points = len(list(temp_df["distance"]))
                        file_data = file_data.append({"laser_id":laserId,"theory_points": th_points,"real_points": re_points},ignore_index=True)
                        #把每一行数据提取出来，统计每一行的理论点数和实际点数，后续操作是根据laserID来计算
                else:
                    continue
            # file_df.to_csv(filename+"_frame.csv", index=False)
            for j in range(0, int(laser_num)):
                # temp_df = file_df[file_df["laser_id"]==i]
                temp_df = file_data[file_data["laser_id"] == j]
                if temp_df.empty:
                    continue
                else:
                    theory_all = sum(list(temp_df["theory_points"]))
                    point_all = sum(list(temp_df["real_points"]))
                    pod = round(point_all/theory_all, 4)
                    if pod > 1:
                        pod = 1
                    else:
                        pass
                    final_list.append((realdis, j, pod))
        except Exception:
            print("fail at %s" % file)
    return final_list

def pod_main():
    final_df = pd.DataFrame(columns=["real_dis", "laser_id", "pod", "lidar_name"])
    laser_num = 128
    for root, dirs, files in os.walk(r".\data"):
        for file in files:
            if "_d" in file and "csv" in file and "frame" not in file:
                print("start file deal at %s" % datetime.now())
                lidar_name = file.split("_")[0]
                '''创建一个文件夹存放文件'''
                save_path = r"./near_accuracy_pod_data_%s" % lidar_name
                mkdir(save_path)
                dis = round(float(file.split("_")[2]), 3)
                save_file = os.path.join(save_path, '{:s}_{:s}_pod.csv'.format(lidar_name, str(dis)))
                csvfile = os.path.join(root, file)
                file_attr = gen_near_pod(csvfile, dis, laser_num)
                df = pd.DataFrame(file_attr, columns=["real_dis", "laser_id", "pod"])
                df["lidar_name"] = lidar_name
                # df["real_dis"] = dis
                df.to_csv(save_file, index=False)
                final_df = final_df.append(df)
                print("finish file deal at %s" % datetime.now())
    final_df.to_csv("lidar_near_pod_final.csv", index=False)

def mkdir(path):
    folder = os.path.exists(path)
    if not folder:
        os.makedirs(path)

'''不在需要合并csv,而是通过对lidar_near_pod_final.csv此文件直接处理'''

def plot_all_lidar_pod(file):
    df = pd.read_csv(file)
    cm = plt.cm.get_cmap('jet')
    fig = plt.figure(figsize=(20, 12))
    size = 30
    fontsize = 20
    lidar_list = df["lidar_name"].unique().tolist()
    lidar_count = len(lidar_list)
    dis_list = df["real_dis"].unique()
    df["lidar_index"] = df["lidar_name"]
    df["lidar_index"] = df["lidar_index"].apply(lambda x:lidar_list.index(x))

    for dis in dis_list:
        tdf = df[(df["real_dis"]==dis)]
        plt.clf()
        ax = fig.add_subplot(111)
        lx1 = tdf["lidar_index"]
        # lx1 = lx1.map(lambda x: math.log(x))
        lx1_label = lx1.unique()
        lx1 = lx1.map(lambda x: x + np.random.normal(0, 0.1, 1)[0])
        ly1 = tdf["pod"] * 100
        ll1 = tdf["laser_id"]
        pic = ax.scatter(lx1, ly1, c=ll1, s=size, vmin=min(ll1),
                            vmax=max(ll1), cmap=cm, marker='o')
        # pic = ax.scatter(lx1, ly1, s=size, cmap=cm, marker='o')
        cb = plt.colorbar(pic)
        cb.set_label("Laser_id", size=fontsize)
        cbx = cb.ax
        ticks = np.arange(min(ll1), max(ll1), 4)
        cb.set_ticks(ticks)
        cbx.tick_params(labelsize=fontsize)
        ax.set_xlabel('Lidar_Sample', fontsize=fontsize)
        ax.set_ylabel('{:s}[%]'.format("POD"), fontsize=fontsize)
        ax.set_title('{:d}-Lidar_POD-{:s}\n'.format(lidar_count, str(dis)), fontsize=fontsize * 1.5)
        ax.set_xlim(min(lx1)-0.2, max(lx1) + 0.2)
        ax.set_xticks(lx1_label)
        ax.set_xticklabels(range(0, lidar_count), rotation=45)
        ax.set_ylim(min(ly1)-10, max(ly1)+10)
        # ax.set_yticks(np.arange(int(min(ly1)), int(max(ly1))))
        # ax.set_ylim(-8, 8)
        # ax.set_yticks(np.arange(-8, 8), 1)
        ax.tick_params(axis='both', labelsize=fontsize)
        pic_path = os.path.join('plot', '{:d}-Lidar_POD-{:s}.png'.format(lidar_count, str(dis)))
        plt.hlines(70, 0, 4, colors = "b", linestyles = "dashed")
        '''获取雷达的个数'''
        for i in range(0, lidar_count):
            temp_df1 = tdf[tdf["lidar_index"]==i]
            pod_rate = round(temp_df1[temp_df1["pod"]>=0.7]["pod"].size/temp_df1["pod"].size * 100, 2)
            plt.text(i-0.2, 80+i/2, str(pod_rate)+"%", size = 10, alpha = 0.9, color = "k")
        plt.savefig(pic_path, facecolor='white', dpi=200)

def plot_one_part_POD(file):
    df = pd.read_csv(file)
    tdf = copy.deepcopy(df)
    cm = plt.cm.get_cmap('jet')
    fig = plt.figure(figsize=(20, 12))
    size = 30
    fontsize = 20
    lidar_list = df["lidar_name"].unique().tolist()
    dis_list = df["real_dis"].unique()
    # df["lidar_index"] = df["lidar_name"]
    # df["lidar_index"] = df["lidar_index"].apply(lambda x:lidar_list.index(x))
    # far_laser_list = [i for i in range(9,38)] + [7, 39, 41]
    # far_laser_list = sorted(far_laser_list)
    # far_laser_data = []
    # nfar_laser_data = []
    for i in lidar_list:
        df1 = df.loc[df['lidar_name']==i]
        lidar_name = i
        plt.clf()
        ax = fig.add_subplot(111)
        df1["real_dis"] = df1["real_dis"].map(lambda x: x + np.random.normal(0, 0.01, 1)[0])
        df1["pod"] = df1["pod"].map(lambda x: x * 100)
        pic = ax.scatter(df1["real_dis"], df1["pod"], c=df1['laser_id'], s=size, vmin=int(min(df1['laser_id'])),
                         vmax=int(max(df1['laser_id']))+2, cmap=cm, marker='o')
        # pic = ax.scatter(lx1, ly1, s=size, cmap=cm, marker='o')
        cb = plt.colorbar(pic)
        cb.set_label("Laser_id", size=fontsize)
        cbx = cb.ax
        cbx.tick_params(labelsize=fontsize)
        ax.set_xlabel('Distance[m]', fontsize=fontsize)
        ax.set_ylabel('{:s}{:s}'.format("POD", '[%]'), fontsize=fontsize)
        ax.set_title('{:s}-{:s}\n'.format(lidar_name, "POD"), fontsize=fontsize * 1.5)
        ax.set_xlim(0, (max(dis_list)) + 0.2)
        ax.set_xticks(dis_list)
        # ax.set_xticklabels(range(0, 5), rotation=45)
        ax.set_ylim(0, 101)
        ax.set_yticks(np.arange(0, 101, 10))
        ax.tick_params(axis='both', labelsize=fontsize)
        pic_path = os.path.join('plot', '{:s}-{:s}.png'.format(lidar_name, "POD"))
        # plt.hlines(70, 0, 4, colors = "b", linestyles = "dashed")
        # 显示每个距离下POD的占比
        # for i in dis_list:
        #     temp_df1 = tdf[tdf["real_dis"]==i]
        #     pod_rate = round(temp_df1[temp_df1["pod"]>=0.7]["pod"].size/temp_df1["pod"].size * 100, 2)
        #     plt.text(i-0.2, 80+i/2, str(pod_rate)+"%", size = 10, alpha = 0.9, color = "k")
        plt.savefig(pic_path, facecolor='white', dpi=200)



if __name__ == "__main__":
    # file = r"C:\Users\Administrator\PycharmProjects\mytest\Pointcloud"
    # gen_near_accuracy(file, 0.3)
    # pod_main() #统计POD数值
    file = r"lidar_near_pod_final.csv"
    plot_all_lidar_pod(file) #画所有雷达在一起的图
    plot_one_part_POD(file) #依次画每一个雷达的图