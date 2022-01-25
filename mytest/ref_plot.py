# -*- coding: utf-8 -*-
# @Time    : 2021/3/4 20:52
# @Author  : liuxiang
# @FileName: ref_plot.py
# @Software: PyCharm
# @email    ：liuxiang@hesaitech.com

# coding=utf-8
import pandas as pd
import glob
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
import numpy as np

TESTFILE_PATH = 'C:/Users/Administrator/Desktop/ZEUS-0150/ZEUS-0150_rawData/'
CORR_FAC = {
    1: 1,
    1.7: 1,
    3: 1,
    4: 1,
    5: 1,
    6: 1,
    9: 1,
    10: 1,
}
REF = 50

FILENAME_STARTER = {
    10: 'LSB',
    54: 'HSB',
    94: 'USB'
}

LINE_COLOR = {
    10: 'b',
    54: 'g',
    94: 'r'
}

DOT_COLOR = {
    10: 'cornflowerblue',
    54: 'limegreen',
    94: 'tomato'
}


def concatFiles(dist, target_ref):
    # print('Distance: ', dist)
    filelist = glob.glob(TESTFILE_PATH + ''.join(
        [FILENAME_STARTER[target_ref], '-%d' % dist, '-', '%d' % int(10 * (dist - int(dist))), 'M-ZEUS-0150*']))
    # print(filelist)
    data = pd.DataFrame()
    for filename in filelist:
        single_file = pd.read_csv(filename)
        # single_file = single_file[['laser_id', 'intensity']]
        data = pd.concat([data, single_file], sort=False)
    return data


def calRefMean():
    ref_mean_df = pd.DataFrame()
    for dist in CORR_FAC.keys():
        if dist in [1, 10]:
            continue
        col_name = str(dist) + 'm'
        data = concatFiles(dist)
        ref_mean_list = []
        for laserID in range(128):
            ref_cal = data.loc[data.laser_id == laserID]['intensity'].mean()
            ref_mean_list.append(ref_cal)

        ref_mean_df[col_name] = ref_mean_list
    ref_mean_df = ref_mean_df.interpolate(method='linear', axis=0)
    return ref_mean_df


def plotIntensity(dist_list, intensity_list, laserID):
    fig, ax = plt.subplots()
    ax.plot(dist_list, intensity_list)
    # plt.show()
    plt.savefig(''.join(TESTFILE_PATH, 'laser', str(laserID), '.png'))


def plotResult(fig, ax, data, target_ref):
    data = data[['laser_id', 'intensity']]
    for laserID in range(128):
        ref_list = data.loc[data.laser_id == laserID]['intensity']
        ax.scatter([laserID] * len(ref_list), ref_list,
                   s=2,
                   color=DOT_COLOR[target_ref])
    ax.plot([0, 128], [target_ref, target_ref],
            linestyle='dashed',
            linewidth=2,
            color=LINE_COLOR[target_ref],
            label=''.join(['standard board ', str(target_ref), '%']))


if __name__ == "__main__":

    DIST_LIST = [1.7, 3, 4, 5, 6, 9, 13, 18, 24, 30]
    '''
    # 拼接文件
    for dist in DIST_LIST:
        print(dist)
        for target_ref in [10, 54, 94]:
            data = concatFiles(dist, target_ref)
            data.to_csv(''.join([TESTFILE_PATH, 'ZEUS-0150-concat/', FILENAME_STARTER[target_ref], '-%d'%dist, '-', '%d'%int(10 *(dist-int(dist))), 'M-ZEUS-0150']), index=None)


    # 画图 - 每个距离
    for dist in DIST_LIST:
        print(dist)
        fig, ax = plt.subplots()
        for target_ref in [10, 54, 94]:
            data = pd.read_csv(''.join([TESTFILE_PATH, 'ZEUS-0150-concat/', FILENAME_STARTER[target_ref], '-%d'%dist, '-', '%d'%int(10 *(dist-int(dist))), 'M-ZEUS-0150']))
            plotResult(fig, ax, data, target_ref)
        ax.set_xlabel('laserid')
        ax.set_ylabel('intensity /%')
        ax.set_xlim(-8, 135)
        ax.set_ylim(0, 140)
        ax.set_title(''.join([str(dist), 'm']))
        ax.legend()
        ax.grid()
        plt.savefig(''.join([TESTFILE_PATH, 'ZEUS-0150-concat/', str(dist), 'm.png']))
        # plt.show()
    '''

    # 画图 - 所有距离
    fig, ax = plt.subplots(figsize=(10, 6))
    for target_ref in [10, 54]:
        all_intensity = []
        for dist in DIST_LIST:
            data = pd.read_csv(''.join(
                [TESTFILE_PATH, 'ZEUS-0150-concat/', FILENAME_STARTER[target_ref], '-%d' % dist, '-',
                 '%d' % int(10 * (dist - int(dist))), 'M-ZEUS-0150']))
            data = data[['laser_id', 'intensity', 'distance_m']]
            data = data.loc[data.laser_id < 100]
            all_intensity += list(data['intensity'])
            # data = data.loc[data.intensity <= 110]
            # ax.scatter([dist] * len(data), data['intensity'],
            #            s = 2,
            #            color = DOT_COLOR[target_ref])
            ax.scatter([distance + np.random.normal() for distance in data['distance_m']], data['intensity'],
                       s=2,
                       color=DOT_COLOR[target_ref])
        mean_intensity = np.mean(np.array(all_intensity))
        rmse = np.sqrt(np.mean(np.array([(intensity - target_ref) ** 2 for intensity in all_intensity])))
        ax.plot(DIST_LIST, [target_ref] * len(DIST_LIST),
                linestyle='dashed',
                linewidth=2,
                color=LINE_COLOR[target_ref],
                label=''.join(['standard board ', str(target_ref),
                               '%%,  average intensity: %.1f%%, RMSE: %.1f%%' % (mean_intensity, rmse)]))
    ax.set_xlabel('distance /m')
    ax.set_ylabel('intensity /%')
    ax.set_xlim(-3, 32)
    ax.set_ylim(0, 140)
    ax.set_title('intensity - distance (laser ID 0 - 99)')
    ax.legend()
    ax.grid()
    plt.savefig(''.join([TESTFILE_PATH, 'ZEUS-0150-concat/all_distance_0-99.png']))
    # plt.show()
    '''

    ref_mean_df = calRefMean()
    print(ref_mean_df)

    WORKPATH = 'D:/P128V4/3-reflectivity/ZDH-ZEUS-0150/'

    intensity_cof = pd.read_csv(''.join([WORKPATH, 'intensity_cof.csv']))
    intensity_cof.columns = ['laser_id', 'dist', 'cof'] 

    intensity_cof_new = pd.DataFrame()
    for index, row in ref_mean_df.iterrows():
        print(index)
        CORR_FAC[1.7] = row['1.7m'] / REF
        CORR_FAC[3] = row['3m'] / REF
        CORR_FAC[4] = row['4m'] / REF
        CORR_FAC[5] = row['5m'] / REF
        CORR_FAC[6] = row['6m'] / REF
        CORR_FAC[9] = row['9m'] / REF

        CORR_FAC[1] = CORR_FAC[1.7]
        CORR_FAC[10] = CORR_FAC[9]

        # plotIntensity([1.7, 3, 4, 5, 6, 9], [row['1.7m'], row['3m'], row['4m'], row['5m'], row['6m'], row['9m']], index)
        # print(CORR_FAC.keys())
        # print(CORR_FAC.values())

        f = interp1d(list(CORR_FAC.keys()), list(CORR_FAC.values()), bounds_error=False, fill_value='extrapolate')

        intensity_cof_1chan = intensity_cof.loc[intensity_cof.laser_id == index]
        intensity_cof_1chan['cof'] = intensity_cof_1chan.apply(lambda x: x['cof'] * f(x['dist']), axis=1)
        # print(intensity_cof_1chan)

        intensity_cof_new = pd.concat([intensity_cof_new, intensity_cof_1chan], sort=False)
    intensity_cof_new.to_csv(WORKPATH + 'intensity_cof_new.csv', index=None, header=None)
    '''
