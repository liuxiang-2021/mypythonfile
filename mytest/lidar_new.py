# -*- coding: utf-8 -*-
import numpy as np
import Queue as Q
from matplotlib import pyplot as plt
import matplotlib.animation as animation
from pandas import Series,DataFrame
import pandas as pd
from scipy.interpolate import interp1d

# define caldate format
GATEIDMAP = {'100':0, '400':1, '1500':2  }
GATEVLMAP = {4:0  ,14:1   ,92:2  }
GATELEVEL = (4    ,14     ,92    )
        

class Wave_packet_info(object):
    """docstring for Wave_packet_info"""
    def __init__(self, lidar_type, lidarID, top_version, bot_version, sw_version,
     top_version_sha , top_para_sha, record_date, size, recorder, catch_method, description ):
        super(Wave_packet_info, self).__init__()
        self.lidar_type         = lidar_type
        self.lidarID            = lidarID
        self.top_version        = top_version
        self.bot_version        = bot_version
        self.sw_version         = sw_version
        self.top_version_sha    = top_version_sha
        self.top_para_sha       = top_para_sha
        self.record_date        = record_date
        self.size               = size
        self.recorder           = recorder
        self.catch_method       = catch_method
        self.description        = description
        


class Wave(object):
    """docstring for Wave"""
    def __init__(self, NO, waveform, channel=0, tspace=0, gate=0, gain=0, front=0, width=0,
        peak=0, strength=0, hv_apd=0, hv_out=0, Temp_RT4=0, Temp_RT2=0, Temp_L_MON=0, 
        Temp_R_MON=0, angle=0, birthday=0):
        super(Wave, self).__init__()
        self.NO                 = NO
        self.waveform           = waveform
        self.channel            = channel
        self.tspace             = tspace
        self.gate               = gate
        self.gain               = gain
        self.front              = front
        self.width              = width
        self.peak               = peak
        self.strength           = strength
        self.hv_apd             = hv_apd
        self.hv_out             = hv_out
        self.Temp_RT4           = Temp_RT4
        self.Temp_RT2           = Temp_RT2
        self.Temp_L_MON         = Temp_L_MON
        self.Temp_R_MON         = Temp_R_MON
        self.angle              = angle
        self.birthday           = birthday

class Pulse(object):
    """docstring for Pulse"""
    def __init__(self, front=0, width=0, peak=0, area=0, threshold=0):
        super(Pulse, self).__init__()
        self.front      = front
        self.width      = width
        self.peak       = peak
        self.area       = area
        self.threshold  = threshold

class Lidar(object):
    """docstring for Lidar:
    simulate the top board function
    """
    def __init__(self, lidar_type, lidar_id):
        super(Lidar, self).__init__()
        self.lidar_type = lidar_type
        self.lidar_id   = lidar_id
        cal_file_name = 'Lidar-'+str(lidar_id)
        self.calmap = self.load_cal_data(cal_file_name)
        gateTune_file_name = 'lidar_config/'+'gate_vs_width_5.5ns.csv' #gate_vs_width_5.5ns  # gate_vs_area_5.5ns
        self.gateTune_map = self.load_gateTune_map(gateTune_file_name)
        gateTune_file_name2 = 'lidar_config/'+'gate_vs_area_1000bit.csv' #gate_vs_width_5.5ns  # gate_vs_area_5.5ns
        self.gateTune_map2 = self.load_gateTune_map(gateTune_file_name2)
        gateTune_file_name3 = 'lidar_config/'+'gate_vs_width_avg_12ns.csv' #gate_vs_width_5.5ns  # gate_vs_area_5.5ns
        self.gateTune_map3 = self.load_gateTune_map(gateTune_file_name3)
        lidar_config_file_name = 'lidar_config/'+str(lidar_type)+'.csv'
        self.lidar_config = self.load_config_file(lidar_config_file_name)
        self.laserID2calID_map = dict(zip(self.lidar_config['laserID'],self.lidar_config['logicChannel_a']))

    def load_cal_data(self,file_name):
        channel_num_total = 64
        gate_num_total = 3
        cal_data = DataFrame([[0]*3*channel_num_total*3]*9,dtype=np.float)   
        try:
            for g,gate in enumerate(['100','400','1500']):
                gate_bias = g*channel_num_total*3
                for b,bank in enumerate(['A','B']):
                    bank_bias = b*32*3
                    txt_name = 'cal_xyk_'+bank+gate+'.txt'
                    name = file_name+'/'+txt_name
                    with open(name, 'r') as f:
                        head1 = f.readline()
                        head2 = f.readline()
                        for i,line in enumerate(f.readlines()):
                            for j in range(9):
                                cal_data[gate_bias+bank_bias+i*3+0][j] = int(line[j*14+0 :j*14+5 ],16)*0.15/256.0
                                cal_data[gate_bias+bank_bias+i*3+1][j] = int(line[j*14+5 :j*14+10],16)*0.15/256
                                cal_data[gate_bias+bank_bias+i*3+2][j] = int(line[j*14+10:j*14+14],16)/256.0
            print ("load",file_name," calibration file success!")
        except:
            print (file_name," calibration file doesn't exist!")
        return cal_data

    def load_gateTune_map(self,filename):
        try:
            try:
                df = pd.read_csv(filename)
            except:
                df = pd.read_csv('../common/'+filename)
            df.index = range(288)
            df.columns = range(3,101)
        except:
            print ("gateTune_map dosen't exist!")
            df = DataFrame([[0]*(101-3)]*288,index=range(288),columns=range(3,101))
        return df

    def load_gateTune_plot_map(self,filename):
        try:
            try:
                gate_map,factor_map = np.load(filename)
            except:
                gate_map,factor_map = np.load('../common/'+filename)
        except:
            print ("load_gateTune_plot_map dosen't exist!")
            gate_map,factor_map = range(4,101),[0]*97
        return gate_map,factor_map

    def load_config_file(self,filename):
        try:
            try:
                df = pd.read_csv(filename)
            except:
                df = pd.read_csv('../common/'+filename)
        except:
            print ("lidar_config file dosen't exist!")
            df = DataFrame([[0]*(101-3)]*288,index=range(288),columns=range(3,101))
        return df

    def moving_average(self,waveform,window):
        waveform_avg = []
        for i in range(len(waveform)-window):
            waveform_avg.append(sum(waveform[i:i+window])/window)
        return waveform_avg

    def corr(self,waveform,tspace,baseline=85):
        waveform_corr = []
        waveform_delay = waveform[int(tspace):]
        for i in range(len(waveform_delay)):
            waveform_corr.append((waveform[i]-baseline)*(waveform_delay[i]-baseline))
        return waveform_corr

    def acc(self,waveform,tspace,baseline=85):
        waveform_corr = []
        waveform_delay = waveform[int(tspace):]
        for i in range(len(waveform_delay)):
            waveform_corr.append((waveform[i]-baseline)+(waveform_delay[i]-baseline))
        return waveform_corr

    def baseoff(self,waveform,baseline=85):
        return [x - baseline for x in waveform]

    def conv(self,waveform,conv_wave):
        return np.convolve(waveform, conv_wave, 'same')


    def pulse_timing_old(self,waveform,threshold=150,baseline=85,start=0,end=800):
        # print 'waveform:',waveform
        offset = 37
        i = start
        find_rise_edge = 0
        rise = 0
        fall = 0
        area = 0
        peak = threshold
        pulse_array = []
        while i<(len(waveform)-1) and i<end: 
            if waveform[i]<threshold and waveform[i+1]>=threshold:
                rise = (i + (threshold-waveform[i])*1.0/(waveform[i+1]-waveform[i]))
                find_rise_edge = 1
            if waveform[i]>peak and find_rise_edge:
                peak = waveform[i]
            if waveform[i]>threshold and find_rise_edge:
                area = area + waveform[i] - baseline
            if waveform[i]>=threshold and waveform[i+1]<threshold and find_rise_edge:
                fall = (i + (threshold-waveform[i])*1.0/(waveform[i+1]-waveform[i]))
                width = fall - rise
                pulse_array.append(Pulse(rise-offset,width,area))
                area = 0
                find_rise_edge = 0
                peak = threshold
                # print rise
            i = i+1
        return pulse_array

    def pulse_timing(self,waveform,threshold=150,baseline=85,start=0,end=800):
        # print 'waveform:',waveform
        offset = 50
        i = start
        find_rise_edge = 0
        rise = 0
        fall = 0
        area = 0
        peak = threshold
        pulse_array = []
        while i<(len(waveform)-1) and i<end: 
            if waveform[i]<threshold and waveform[i+1]>=threshold:
                rise = (i + (threshold-waveform[i])*1.0/(waveform[i+1]-waveform[i]))
                find_rise_edge = 1
            if waveform[i]>peak and find_rise_edge:
                peak = waveform[i]
            if waveform[i]>threshold and find_rise_edge:
                area = area + waveform[i] - baseline
            if waveform[i]>=threshold and waveform[i+1]<threshold and find_rise_edge:
                fall = (i + (threshold-waveform[i])*1.0/(waveform[i+1]-waveform[i]))
                width = fall - rise
                pulse_array.append(Pulse(rise-offset,width,peak,area,threshold))
                area = 0
                find_rise_edge = 0
                peak = threshold
                # print rise
            i = i+1
        return pulse_array

    def pulse_timing2(self,waveform,high_threshold=150,low_threshold=95,baseline=85,start=0,end=800):
        # print 'waveform:',waveform
        offset = 37
        i = start
        find_lth_rise_edge = 0
        find_hth_rise_edge = 0
        rise_lth = 0
        rise_hth = 0
        fall_lth = 0
        fall_hth = 0
        area_lth = 0
        area_hth = 0
        front = 0
        peak = 95
        pulse_array = []
        while i<(len(waveform)-1) and i<end: 
            if waveform[i]<low_threshold and waveform[i+1]>=low_threshold:
                rise_lth = (i + (low_threshold-waveform[i])*1.0/(waveform[i+1]-waveform[i]))
                find_lth_rise_edge = 1
            if waveform[i]<high_threshold and waveform[i+1]>=high_threshold:
                rise_hth = (i + (high_threshold-waveform[i])*1.0/(waveform[i+1]-waveform[i]))
                find_hth_rise_edge = 1 
            if waveform[i]>peak and find_lth_rise_edge :
                peak = waveform[i]
            if waveform[i]>low_threshold and find_lth_rise_edge:
                area_lth = area_lth + waveform[i] - baseline
            if waveform[i]>high_threshold and find_hth_rise_edge:
                area_hth = area_hth + waveform[i] - baseline
            if waveform[i]>=high_threshold and waveform[i+1]<high_threshold:
                fall_hth = (i + (high_threshold-waveform[i])*1.0/(waveform[i+1]-waveform[i]))
                width = fall_hth - rise_hth
                if find_hth_rise_edge:
                    pulse_array.append(Pulse((rise_hth-offset),width,peak,area_lth,high_threshold))
                area_hth = 0
                peak = 95
                find_lth_rise_edge = 0
                find_hth_rise_edge = 0

            if waveform[i]>=low_threshold and waveform[i+1]<low_threshold:
                fall_lth = (i + (low_threshold-waveform[i])*1.0/(waveform[i+1]-waveform[i]))
                width = fall_lth - rise_lth
                if find_lth_rise_edge:
                    pulse_array.append(Pulse((rise_lth-offset),width,peak,area_hth,low_threshold))
                area_lth = 0
                peak = 95
                find_lth_rise_edge = 0
                find_hth_rise_edge = 0
            i = i+1
        return pulse_array

    def pulse_timing3(self,waveform,high_threshold=150,low_threshold=95,baseline=85,start=0,end=2000,offset=37):
        # print 'waveform:',waveform
        i = start
        find_lth_rise_edge = 0
        find_hth_rise_edge = 0
        find_hth_fall_edge = 0
        rise_lth = 0
        rise_hth = 0
        fall_lth = 0
        fall_hth = 0
        area_lth = 0
        area_hth = 0
        width_lth = 0
        width_hth = 0 
        front_lth = 0
        front_hth = 0
        peak = 95
        pulse_array = []
        while i<(len(waveform)-1) and i<end: 
            if waveform[i]<low_threshold and waveform[i+1]>=low_threshold:
                rise_lth = (i + (low_threshold-waveform[i])*1.0/(waveform[i+1]-waveform[i]))
                find_lth_rise_edge = 1
            if waveform[i]<high_threshold and waveform[i+1]>=high_threshold:
                rise_hth = (i + (high_threshold-waveform[i])*1.0/(waveform[i+1]-waveform[i]))
                find_hth_rise_edge = 1 
            if waveform[i]>peak and find_lth_rise_edge :
                peak = waveform[i]
            if waveform[i]>low_threshold and find_lth_rise_edge:
                area_lth = area_lth + waveform[i] - baseline
            if waveform[i]>high_threshold and find_hth_rise_edge:
                area_hth = area_hth + waveform[i] - baseline
            if waveform[i]>=high_threshold and waveform[i+1]<high_threshold:
                fall_hth = (i + (high_threshold-waveform[i])*1.0/(waveform[i+1]-waveform[i]))
                width_hth = fall_hth - rise_hth
                front_hth = rise_hth - offset
                area_hth = 0
                find_hth_rise_edge = 0
                find_hth_fall_edge = 1

            if waveform[i]>=low_threshold and waveform[i+1]<low_threshold:
                fall_lth = (i + (low_threshold-waveform[i])*1.0/(waveform[i+1]-waveform[i]))
                width_lth = fall_lth - rise_lth
                front_lth = rise_lth - offset
                if find_hth_fall_edge:
                    pulse_array.append(Pulse(front_hth,width_hth,peak,area_lth,high_threshold))
                elif find_lth_rise_edge:
                    pulse_array.append(Pulse(front_lth,width_lth,peak,area_lth,low_threshold))
                area_lth = 0
                peak = 95
                find_lth_rise_edge = 0
                find_hth_rise_edge = 0
                find_hth_fall_edge = 0
            i = i+1
        return pulse_array

    def pulse_timing4(self,waveform,high_threshold=150,low_threshold=95,baseline=85,start=0,end=800,offset = 37):
        # print 'waveform:',waveform
        i = start
        find_lth_rise_edge = 0
        find_hth_rise_edge = 0
        find_hth_fall_edge = 0
        rise_lth = 0
        rise_hth = 0
        fall_lth = 0
        fall_hth = 0
        area_lth = 0
        area_hth = 0
        width_lth = 0
        width_hth = 0 
        front_lth = 0
        front_hth = 0
        peak = 95
        pulse_array = []
        while i<(len(waveform)-1) and i<end: 
            if waveform[i]<low_threshold and waveform[i+1]>=low_threshold:
                rise_lth = (i + (low_threshold-waveform[i])*1.0/(waveform[i+1]-waveform[i]))
                find_lth_rise_edge = 1
            if waveform[i]<high_threshold and waveform[i+1]>=high_threshold:
                rise_hth = (i + (high_threshold-waveform[i])*1.0/(waveform[i+1]-waveform[i]))
                find_hth_rise_edge = 1 
            if waveform[i]>peak and find_lth_rise_edge :
                peak = waveform[i]
            if waveform[i]>low_threshold and find_lth_rise_edge:
                area_lth = area_lth + waveform[i] - baseline
            if waveform[i]>high_threshold and find_hth_rise_edge:
                area_hth = area_hth + waveform[i] - baseline
            if waveform[i]>=high_threshold and waveform[i+1]<high_threshold:
                fall_hth = (i + (high_threshold-waveform[i])*1.0/(waveform[i+1]-waveform[i]))
                width_hth = fall_hth - rise_hth
                front_hth = rise_hth - offset
                area_hth = 0
                find_hth_rise_edge = 0
                find_hth_fall_edge = 1

            if waveform[i]>=low_threshold and waveform[i+1]<low_threshold:
                fall_lth = (i + (low_threshold-waveform[i])*1.0/(waveform[i+1]-waveform[i]))
                width_lth = fall_lth - rise_lth
                front_lth = rise_lth - offset
                if find_hth_fall_edge:
                    peak = width_lth/(width_lth-width_hth)*(150-85)+85
                    pulse_array.append(Pulse(front_hth,width_hth,peak,area_lth,high_threshold))
                elif find_lth_rise_edge:
                    pulse_array.append(Pulse(front_lth,width_lth,peak,area_lth,low_threshold))
                area_lth = 0
                peak = 95
                find_lth_rise_edge = 0
                find_hth_rise_edge = 0
                find_hth_fall_edge = 0
            i = i+1
        return pulse_array

    def pulse_timing_auto_th(self,waveform,threshold=95,baseline=85,start=0,end=800,offset=37):
        i = start
        find_rise_edge = 0
        rise = 0
        fall = 0
        area = 0
        peak = threshold
        find_rise_edge_FWHM = 0
        rise_FWHM = 0
        fall_FWHM = 0
        area_FWHM = 0   
        pulse_array = []
        while i<(len(waveform)-1) and i<end: 
            if waveform[i]<threshold and waveform[i+1]>=threshold:
                rise = (i + (threshold-waveform[i])*1.0/(waveform[i+1]-waveform[i]))
                find_rise_edge = 1
                rise_id = i
            if waveform[i]>peak and find_rise_edge:
                peak = waveform[i]
            if waveform[i]>threshold and find_rise_edge:
                area = area + waveform[i] - baseline
            if waveform[i]>threshold and waveform[i+1]<=threshold and find_rise_edge:
                fall = (i + (threshold-waveform[i])*1.0/(waveform[i+1]-waveform[i]))
                fall_id = i
                threshold_FWHM = max(np.floor((peak+baseline)/2.),threshold)
                threshold_FWHM = max(peak-15,threshold)
                threshold_FWHM = min(150, threshold_FWHM)
                j = rise_id
                while j < fall_id + 1: 
                    if waveform[j]<threshold_FWHM and waveform[j+1]>=threshold_FWHM:
                        rise_FWHM = (j + (threshold_FWHM-waveform[j])*1.0/(waveform[j+1]-waveform[j]))
                        find_rise_edge_FWHM = 1
                    # if waveform[j]>peak and find_rise_edge_FWHM:
                    #     peak = waveform[j]
                    # if waveform[j]>threshold_FWHM and find_rise_edge_FWHM:
                    #     area_FWHM = area_FWHM + waveform[j] - baseline
                    if waveform[j]>threshold_FWHM and waveform[j+1]<=threshold_FWHM and find_rise_edge_FWHM:
                        fall_FWHM = (j + (threshold_FWHM-waveform[j])*1.0/(waveform[j+1]-waveform[j]))
                        width = fall_FWHM - rise_FWHM
                        pulse_array.append(Pulse(rise_FWHM-offset,width,peak,area,threshold))
                        area_FWHM = 0
                        find_rise_edge_FWHM = 0
                    j = j+1
                area = 0
                find_rise_edge = 0
                peak = threshold
            i = i+1
        return pulse_array

    def pulse_timing_extremum(self,waveform,threshold=40,baseline=23,start=0,end=1800,offset=0):
        i = start+1
        peak = threshold
        find_rise_edge_FWHM = 0
        rise_FWHM = 0
        fall_FWHM = 0
        top_index = i
        pulse_array = []
        rise_list = [85]
        fall_list = [85]
        pulse_start = i
        pulse_end   = i
        while i<(len(waveform)-1) and i<end: 
            if waveform[i] > waveform[i-1] :
                rise_list.append(waveform[i])
            if waveform[i] < waveform[i-1] :
                fall_list.append(waveform[i])
            if waveform[i-1] <= waveform[i] and waveform[i] > waveform[i+1]: #find top
                fall_list = []
                fall_list.append(waveform[i])
                top_index = i
            if waveform[i-1] > waveform[i] and waveform[i] <= waveform[i+1]: #find bottom
                pulse_end = i
                rise_peak = max(rise_list)
                rise_bottom = min(rise_list)
                fall_peak = max(fall_list)
                fall_bottom = min(fall_list)
                if rise_peak >= threshold and max(rise_bottom,fall_bottom) < threshold:
                    threshold_FWHM = max(np.floor((rise_peak+baseline)/2.),threshold)
                    threshold_FWHM = max(threshold_FWHM,threshold)
                    threshold_FWHM = min(150, threshold_FWHM)

                    # print max(rise_int1),max(fall_int1)

                    if waveform[top_index-1]>waveform[top_index+1]:
                        x1 = top_index - 2
                        x2 = top_index - 1
                        x3 = top_index + 1
                        x4 = top_index + 2
                        y1 = waveform[x1]
                        y2 = waveform[x2]
                        y3 = waveform[x3]
                        y4 = waveform[x4]
                    else:
                        x1 = top_index - 2
                        x2 = top_index -1
                        x3 = top_index + 1
                        x4 = top_index + 2
                        y1 = waveform[x1]
                        y2 = waveform[x2]
                        y3 = waveform[x3]
                        y4 = waveform[x4]
                    k1 = float((y2-y1)/(x2-x1))
                    k2 = float((y3-y4)/(x3-x4))
                    # print k1,k2                    
                    x0 = (k1*x2 - k2*x3 + y3 - y2)/(k1-k2)
                    y0 = k1*x0 -k1*x2 +y2
                    pulse_array.append(Pulse(x0-offset,1,y0,rise_slope_factor,threshold))
                rise_list = []
                rise_list.append(waveform[i])
                pulse_start = i
            i = i+1
        return pulse_array

    def pulse_timing_extremum2(self,waveform,threshold=90,baseline=85,start=0,end=800,offset=37):
        i = start+1
        peak = threshold
        find_rise_edge_FWHM = 0
        rise_FWHM = 0
        fall_FWHM = 0
        top_index = i
        pulse_array = []
        rise_list = [85]
        fall_list = [85]
        pulse_start = i
        pulse_end   = i
        while i<(len(waveform)-1) and i<end : 
            if waveform[i] > threshold and waveform[i-1] <= threshold : #find top
                rise_list = []
                fall_list = []
                pulse_start = i - 1
            if waveform[i] > waveform[i-1] and waveform[i]>=threshold :
                rise_list.append(waveform[i])
            if waveform[i] < waveform[i-1] and waveform[i]>=threshold :
                fall_list.append(waveform[i])
            if waveform[i] < threshold and waveform[i-1] >= threshold : #find bottom
                pulse_end = i
                rise_peak = max(rise_list)
                rise_bottom = min(rise_list)
                fall_peak = max(fall_list)
                fall_bottom = min(fall_list)
                if rise_peak >= threshold:
                    threshold_FWHM = max(np.floor((rise_peak+baseline)/2.),threshold)
                    threshold_FWHM = max(threshold_FWHM,threshold)
                    threshold_FWHM = min(150, threshold_FWHM)
                    # rise_slope_factor = float((rise_peak - rise_bottom)*(len(rise_list)))/(sum(rise_list) - rise_bottom*len(rise_list))
                    # fall_slope_factor = float((fall_peak - fall_bottom)*(len(fall_list)))/(sum(fall_list) - fall_bottom*len(fall_list))
                    # rise_slope_factor = rise_slope_factor/fall_slope_factor
                    rise_int = [rise_list[x+1] - rise_list[x] for x in range(len(rise_list)-1)]
                    rise_int1 = [rise_int[y+1] - rise_int[y] for y in range(len(rise_int)-1)]
                    fall_int = [fall_list[z+1] - fall_list[z] for z in range(len(fall_list)-1) if fall_list[z]>baseline]
                    fall_int1 = [fall_int[t+1] - fall_int[t] for t in range(len(fall_int)-1)]

                    rise_slope_factor = float(max(rise_int1))


                    if waveform[top_index-1]>waveform[top_index+1]:
                        x1 = top_index - 2
                        x2 = top_index - 1
                        x3 = top_index + 1
                        x4 = top_index + 2
                        y1 = waveform[x1]
                        y2 = waveform[x2]
                        y3 = waveform[x3]
                        y4 = waveform[x4]
                    else:
                        x1 = top_index - 2
                        x2 = top_index -1
                        x3 = top_index + 1
                        x4 = top_index + 2
                        y1 = waveform[x1]
                        y2 = waveform[x2]
                        y3 = waveform[x3]
                        y4 = waveform[x4]
                    k1 = float((y2-y1)/(x2-x1))
                    k2 = float((y3-y4)/(x3-x4))
                    # print k1,k2                    
                    x0 = (k1*x2 - k2*x3 + y3 - y2)/(k1-k2)
                    y0 = k1*x0 -k1*x2 +y2
                    # pulse_array.append(Pulse(x0-offset,1,y0,rise_slope_factor,threshold))
                    # rise_slope_factor = (x0 - pulse_start)/(pulse_end - pulse_start)

                    # print 'threshold_FWHM',threshold_FWHM
                    j = pulse_start
                    while j < pulse_end + 1:
                        if waveform[j]<threshold_FWHM and waveform[j+1]>=threshold_FWHM:
                            rise_FWHM = (j + (threshold_FWHM-waveform[j])*1.0/(waveform[j+1]-waveform[j]))
                            find_rise_edge_FWHM = 1
                        if waveform[j]>threshold_FWHM and waveform[j+1]<=threshold_FWHM and find_rise_edge_FWHM:
                            fall_FWHM = (j + (threshold_FWHM-waveform[j])*1.0/(waveform[j+1]-waveform[j]))
                            width = fall_FWHM - rise_FWHM
                            # print 'rise_FWHM',rise_FWHM
                            pulse_array.append(Pulse(rise_FWHM-offset,width,rise_peak,rise_slope_factor,threshold_FWHM))
                            find_rise_edge_FWHM = 0
                        j = j+1
            i = i+1
        return pulse_array


    def pulse_timing_FWHM(self,waveform,threshold=95,baseline=85,start=0,end=2000):
        offset = 37
        i = start
        find_rise_edge = 0
        rise = 0
        fall = 0
        area = 0
        peak = threshold
        find_rise_edge_FWHM = 0
        rise_FWHM = 0
        fall_FWHM = 0
        area_FWHM = 0   
        pulse_array = []
        while i<(len(waveform)-1) and i<end: 
            if waveform[i]<threshold and waveform[i+1]>=threshold:
                rise = (i + (threshold-waveform[i])*1.0/(waveform[i+1]-waveform[i]))
                find_rise_edge = 1
                rise_id = i
            if waveform[i]>peak and find_rise_edge:
                peak = waveform[i]
            if waveform[i]>threshold and find_rise_edge:
                area = area + waveform[i] - baseline
            if waveform[i]>threshold and waveform[i+1]<=threshold and find_rise_edge:
                fall = (i + (threshold-waveform[i])*1.0/(waveform[i+1]-waveform[i]))
                fall_id = i
                threshold_FWHM = max(np.floor((peak+baseline)/2.),threshold)
                j = rise_id
                while j < fall_id + 1: 
                    if waveform[j]<threshold_FWHM and waveform[j+1]>=threshold_FWHM:
                        rise_FWHM = (j + (threshold_FWHM-waveform[j])*1.0/(waveform[j+1]-waveform[j]))
                        find_rise_edge_FWHM = 1
                    # if waveform[j]>peak and find_rise_edge_FWHM:
                    #     peak = waveform[j]
                    # if waveform[j]>threshold_FWHM and find_rise_edge_FWHM:
                    #     area_FWHM = area_FWHM + waveform[j] - baseline
                    if waveform[j]>threshold_FWHM and waveform[j+1]<=threshold_FWHM and find_rise_edge_FWHM:
                        fall_FWHM = (j + (threshold_FWHM-waveform[j])*1.0/(waveform[j+1]-waveform[j]))
                        width = fall_FWHM - rise_FWHM
                        pulse_array.append(Pulse(rise_FWHM-offset,width,peak,area,threshold))
                        area_FWHM = 0
                        find_rise_edge_FWHM = 0
                    j = j+1
                area = 0
                find_rise_edge = 0
                peak = threshold
            i = i+1
        return pulse_array

    def pulse_timing_peak(self,waveform,high_threshold=150,low_threshold=95,baseline=85,start=0,end=800):
        # print 'waveform:',waveform
        offset = 37
        i = start
        find_lth_rise_edge = 0
        find_hth_rise_edge = 0
        find_hth_fall_edge = 0
        rise_lth = 0
        rise_hth = 0
        fall_lth = 0
        fall_hth = 0
        area_lth = 0
        area_hth = 0
        width_lth = 0
        width_hth = 0 
        front_lth = 0
        front_hth = 0
        peak = 95
        pulse_array = []
        while i<(len(waveform)-1) and i<end: 
            if waveform[i]<low_threshold and waveform[i+1]>=low_threshold:
                rise_lth = (i + (low_threshold-waveform[i])*1.0/(waveform[i+1]-waveform[i]))
                find_lth_rise_edge = 1
            if waveform[i]<high_threshold and waveform[i+1]>=high_threshold:
                rise_hth = (i + (high_threshold-waveform[i])*1.0/(waveform[i+1]-waveform[i]))
                find_hth_rise_edge = 1 
            if waveform[i]>peak and find_lth_rise_edge :
                peak = waveform[i]
            if waveform[i]>low_threshold and find_lth_rise_edge:
                area_lth = area_lth + waveform[i] - baseline
            if waveform[i]>high_threshold and find_hth_rise_edge:
                area_hth = area_hth + waveform[i] - baseline

            if waveform[i]>=low_threshold and waveform[i+1]<low_threshold:
                fall_lth = (i + (low_threshold-waveform[i])*1.0/(waveform[i+1]-waveform[i]))
                width_lth = fall_lth - rise_lth
                front_lth = rise_lth - offset
                if find_hth_fall_edge:
                    peak = width_lth/(width_lth-width_hth)*(150-85)+85
                    pulse_array.append(Pulse(front_hth,width_hth,peak,area_lth,high_threshold))
                elif find_lth_rise_edge:
                    pulse_array.append(Pulse(front_lth,width_lth,peak,area_lth,low_threshold))
                area_lth = 0
                peak = 95
                find_lth_rise_edge = 0
                find_hth_rise_edge = 0
                find_hth_fall_edge = 0
            i = i+1
        return pulse_array

    def pulse_timing_weight(self,waveform,threshold=90,baseline=85,start=0,end=2000,offset=37):
        # offset = 37
        i = start
        find_rise_edge = 0
        rise = 0
        fall = 0
        area = 0
        peak = threshold
        pulse_array = []
        while i<(len(waveform)-1) and i<end: 
            if waveform[i]<threshold and waveform[i+1]>=threshold:
                rise = (i + (threshold-waveform[i])*1.0/(waveform[i+1]-waveform[i]))
                find_rise_edge = 1
                rise_id = i
            if waveform[i]>peak and find_rise_edge:
                peak = waveform[i]
            if waveform[i]>threshold and find_rise_edge:
                area = area + waveform[i] - baseline
            if waveform[i]>threshold and waveform[i+1]<=threshold and find_rise_edge:
                fall = (i + (threshold-waveform[i])*1.0/(waveform[i+1]-waveform[i]))
                fall_id = i
                j = rise_id+1
                weight = 0
                height = 0
                while j < fall_id + 1: 
                    weight = weight + j*(waveform[j]-baseline)
                    height = height + waveform[j]-baseline
                    j = j+1
                front_weight = float(weight)/height
                if peak > 90 :
                    pulse_array.append(Pulse(front_weight-offset,area/peak,peak,area,threshold))
                area = 0
                find_rise_edge = 0
                peak = threshold
            i = i+1
        return pulse_array

    def pulse_timing_weight2(self,waveform,threshold=90,baseline=85,start=0,end=2000,offset=37):
        # offset = 37
        i = start
        find_rise_edge = 0
        rise = 0
        fall = 0
        area = 0
        peak = threshold
        pulse_array = []
        while i<(len(waveform)-1) and i<end: 
            if waveform[i]<threshold and waveform[i+1]>=threshold:
                rise = (i + (threshold-waveform[i])*1.0/(waveform[i+1]-waveform[i]))
                find_rise_edge = 1
                rise_id = i
            if waveform[i]>peak and find_rise_edge:
                peak = waveform[i]
            if waveform[i]>threshold and find_rise_edge:
                area = area + waveform[i] - baseline
            if waveform[i]>threshold and waveform[i+1]<=threshold and find_rise_edge:
                fall = (i + (threshold-waveform[i])*1.0/(waveform[i+1]-waveform[i]))
                fall_id = i
                j = rise_id+1
                weight = 0
                height = 0
                while j < fall_id + 1: 
                    weight = weight + j*(waveform[j]-baseline)
                    height = height + waveform[j]-baseline
                    j = j+1
                front_weight = float(weight)/height
                if peak > 90 :
                    pulse_array.append(Pulse(front_weight-offset,area/peak,peak,area,threshold))
                area = 0
                find_rise_edge = 0
                peak = threshold
            i = i+1
        return pulse_array

    def laserID2physicID(self,laserID='0'):
        return self.lidar_config[self.lidar_config['laserID']==int(laserID)]['physicalChannel']

    def physicID2laserID(self,physicID='A0'):
        return self.lidar_config[self.lidar_config['physicalChannel']==physicID]['laserID']

    def get_calID(self,laserID):
        # BANKMAP  = { 'A':0, 'B':32}
        # print physicID[0]
        # return BANKMAP[physicID[0]]+int(physicID[1:])
        return self.laserID2calID_map[laserID]

    def get_cal_curve(self,calID,gate):
        channel_num_total = 64
        gate_level = GATEVLMAP[gate]
        xlist = list(self.calmap[gate_level*channel_num_total*3+calID*3+0])
        ylist = list(self.calmap[gate_level*channel_num_total*3+calID*3+1])
        klist = list(self.calmap[gate_level*channel_num_total*3+calID*3+2])
        xlist_ns = [x/0.15 for x in xlist]
        ylist_ns = [y/0.15 for y in ylist]
        # klist_ns = [k/0.15 for k in klist]
        return xlist_ns,ylist_ns,klist

    def distance_calibration(self,width,xlist,ylist,klist):
        f=interp1d(xlist,ylist,kind='linear')
        # print width
        # print xlist,ylist
        if width<xlist[0]:
            dist_erro = (width-xlist[0])*(ylist[1]-ylist[0])/(xlist[1]-xlist[0])+ylist[0] if (xlist[1]-xlist[0])!=0 else 0
        elif width>xlist[-1]:
            dist_erro = (width-xlist[-1])*(ylist[-2]-ylist[-1])/(xlist[-2]-xlist[-1])+ylist[-1] if (xlist[-2]-xlist[-1])!=0 else 0
        else:
            dist_erro = f(width)
        return dist_erro

    def dist_correction(self,width,calID,gate):
        # print 'calID',calID
        # width = width*0.35
        if gate<GATELEVEL[0]:
            gate_low = GATELEVEL[0]
            gate_high= GATELEVEL[0]
        elif gate<GATELEVEL[1]:
            gate_low = GATELEVEL[0]
            gate_high= GATELEVEL[1]
        elif gate<GATELEVEL[2]:
            gate_low = GATELEVEL[1]
            gate_high= GATELEVEL[2]
        else:
            gate_low = GATELEVEL[2]
            gate_high= GATELEVEL[2]
        lx,ly,lk = self.get_cal_curve(calID,gate_low )
        hx,hy,hk = self.get_cal_curve(calID,gate_high)
        dist_erro_low  = self.distance_calibration(width,lx,ly,lk)
        dist_erro_high = self.distance_calibration(width,hx,hy,hk)
        f=interp1d([gate_low,gate_high],[dist_erro_low,dist_erro_high],kind='linear')
        if gate<gate_low:
            dist_erro = dist_erro_low
        elif gate>gate_high:
            dist_erro = dist_erro_high
        else:
            dist_erro = f(gate)
        return dist_erro

    def calibration(self,pulse_array,wave_info,calID):
        # print 'pulse_array_pt: ',pulse_array
        pulse_array_cal = []
        if pulse_array != []:
            for pulse in pulse_array:
                front_cal = pulse.front - self.dist_correction(pulse.width,calID,wave_info.gate)
                pulse_array_cal.append(Pulse(front_cal,pulse.width,pulse.peak,pulse.area,pulse.threshold))
        return pulse_array_cal

    def difference(self,subtractor,subtracted_arry):
        pulse_diff_array = []
        for subtracted in subtracted_arry:
            front_diff = subtracted.front - subtractor.front 
            width_diff = subtracted.width - subtractor.width 
            peak_diff  = subtracted.peak  - subtractor.peak 
            pulse_diff_array.append(Pulse(front_diff,width_diff,peak_diff,subtracted.area,subtracted.threshold))
        return pulse_diff_array

    def find_proper_pulse(self,pulse_diff_array,wave_info):
        min_index = 1000
        min_indexx= 1000
        if pulse_diff_array != [[]]:
            min_erro = 10000
            min_index = 0
            min_indexx= 0
            for i,v in enumerate(pulse_diff_array):
                for ii,vv in enumerate(v):
                    if abs(vv.front-wave_info.tspace) < min_erro:
                        min_erro  = abs(vv.front-wave_info.tspace)
                        min_index = i 
                        min_indexx= ii
        # print min_index,min_indexx
        return min_index,min_indexx

    def compare(self,pulse,pulse_diff,wave_info):
        RWH_ERROR_base = [175,1024,300]
        
        if wave_info.gate>10:
            RWH_ERROR_gt = [0,0,0]
        elif wave_info.gate>8:
            RWH_ERROR_gt = [64,128,150]
        else:
            RWH_ERROR_gt = [128,256,300]

        if pulse.front>140:
            RWH_ERROR_tm = [128,128,0]
        elif pulse.front>70:
            RWH_ERROR_tm = [64,64,0]
        else:
            RWH_ERROR_tm = [0,0,0]

        if pulse.width>25:
            RWH_ERROR_wd = [256,pulse.width*256/2.,0]
        elif pulse.width>0:
            RWH_ERROR_wd = [0,0,0]
        else:
            RWH_ERROR_wd = [256,1024,0]

        if pulse.peak>210:
            RWH_ERROR_hg = [0,0,300]
        elif pulse.peak>170:
            RWH_ERROR_hg = [0,0,150]
        else:
            RWH_ERROR_hg = [0,0,0]

        RWH_ERROR = [0,0,0]
        for i in range(len(RWH_ERROR)):
            RWH_ERROR[i] = RWH_ERROR_base[i]+RWH_ERROR_gt[i]+RWH_ERROR_tm[i]+RWH_ERROR_wd[i]+RWH_ERROR_hg[i]
        # print 'decoding:',(abs(pulse_diff.front-wave_info.tspace)<RWH_ERROR[0]/256.,abs(pulse_diff.width)<RWH_ERROR[1]/256.,abs(pulse_diff[2])<RWH_ERROR[2]/8.)
        if abs(pulse_diff.front-wave_info.tspace)<RWH_ERROR[0]/256. and abs(pulse_diff.width)<RWH_ERROR[1]/256. and abs(pulse_diff[2])<RWH_ERROR[2]/8.:
            pulse_valid = 1
        else:
            pulse_valid = 0
        return pulse_valid   

    def decoding(self,pulse_array,wave_info):
        pulse_array_decoding = [] 
        valid_decoding = 0
        # print 'pulse_array_cal:',pulse_array
        if len(pulse_array)>=2:
            for i in range(len(pulse_array)-1):
                pulse_diff_array = self.difference(pulse_array[i],pulse_array[i+1:])
                for k,v in enumerate(pulse_diff_array):
                    if self.compare(pulse_array[i],v,wave_info):
                        pulse_array_decoding.append(pulse_array[i])
                        valid_decoding = 1
        return pulse_array_decoding,valid_decoding

    def intensity_cal(self,):
        pass    

    def distProcessing(self,pulse_array):
        last_return = [0,0,0,0,0]#front,width,intensity,factor1,facctor2
        strongest_return = [0,0,0,0,0]#front,width,intensity,factor1,facctor2
        if pulse_array != []:
            for pulse in pulse_array:
                factor = 10 if pulse.threshold==95 else 1
                if pulse.front > last_return[0]:
                    last_return = [pulse.front*0.15,pulse.width*0.15,pulse.peak,pulse.area,0]
                if pulse.width/factor > strongest_return[1]:
                    strongest_return = [pulse.front*0.15,pulse.width*0.15,pulse.peak,pulse.area,0]
        return last_return,strongest_return

    def get_gateTune_info(self,pulse_array,pulse_array_decoding,valid_decoding,wave_info):
        gateTune_info = [wave_info.gate,0,95,0]#gate,width,peak,area
        pulse_array_gateTune = pulse_array_decoding if valid_decoding else pulse_array        
        if pulse_array_gateTune != []:
            for pulse in pulse_array_gateTune:
                if pulse.width>gateTune_info[1] and pulse.threshold==150:
                    gateTune_info[1] = pulse.width
                    gateTune_info[2] = pulse.peak
                    gateTune_info[3] = pulse.area
        # print gateTune_info[1]
        return gateTune_info

    def get_gateTune_info2(self,pulse_array,pulse_array_decoding,valid_decoding,wave_info):
        gateTune_info = [wave_info.gate,0,95,0]#gate,width,peak,area
        pulse_array_gateTune = pulse_array_decoding if valid_decoding else pulse_array        
        if pulse_array_gateTune != []:
            for pulse in pulse_array_gateTune:
                # print (pulse.threshold,pulse.width)
                width_factor = 10 if pulse.threshold==150 else 1
                if pulse.width/width_factor>gateTune_info[1]:
                    gateTune_info[1] = pulse.width
                    gateTune_info[2] = pulse.peak
                    gateTune_info[3] = pulse.area
        # print gateTune_info[1]
        return gateTune_info

    def get_gateTune_info3(self,pulse_array,pulse_array_decoding,valid_decoding,wave_info):
        gateTune_info = [wave_info.gate,0,95,0]#gate,width,peak,area
        pulse_array_gateTune = pulse_array_decoding if valid_decoding else pulse_array
        if pulse_array_gateTune != []:
            for pulse in pulse_array_gateTune:
                # print (pulse.threshold,pulse.width)
                if pulse.area>gateTune_info[3]:
                    gateTune_info[1] = pulse.width
                    gateTune_info[2] = pulse.peak
                    gateTune_info[3] = pulse.area
        # print gateTune_info[1]
        return gateTune_info

    def get_gateTune_info4(self,pulse_array,wave_info):
        gateTune_info = [wave_info.gate,0,95,0]#gate,width,peak,area
        pulse_array_gateTune = pulse_array        
        if pulse_array_gateTune != []:
            for pulse in pulse_array_gateTune:
                if pulse.width>gateTune_info[1] :
                    gateTune_info[1] = pulse.width
                    gateTune_info[2] = pulse.peak
                    gateTune_info[3] = pulse.area
        # print gateTune_info[1]
        return gateTune_info

    def gateTune(self,gateTune_info):
        gate,width,peak,area = gateTune_info
        width_x8 = np.floor(width*8) # accuracy = 0.125ns
        width_x8 = min(287,width_x8)
        gate_next = self.gateTune_map[int(gate)][int(width_x8)]
        if gate_next>46:
            gate_next = 46
        elif gate_next<4:
            gate_next = 4
        return int(gate_next)
        
    def gateTune2(self,gateTune_info,target_peak=85+150):
        gate,width,peak,area = gateTune_info
        # print gateTune_info
        # target_peak = 85+150
        # print peak
        gate_next = np.ceil((target_peak-85.)/(peak-85.)*gate)
        if gate_next>46:
            gate_next = 46
        elif gate_next<4:
            gate_next = 4
        return gate_next

    def gateTune3(self,gateTune_info):
        gate,width,peak,area = gateTune_info
        width_x8 = np.floor(area/16) # accuracy = 0.125ns
        # print 'width_x8',width_x8
        width_x8 = min(287,width_x8)
        gate_next = self.gateTune_map2[int(gate)][int(width_x8)]
        if gate_next>46:
            gate_next = 46
        elif gate_next<4:
            gate_next = 4
        return int(gate_next)

    def gateTune4(self,gateTune_info):
        gate,width,peak,area = gateTune_info
        width_x8 = np.floor(width*8) # accuracy = 0.125ns
        # print 'width_x8',width_x8
        width_x8 = min(287,width_x8)
        gate_next = self.gateTune_map3[int(gate)][int(width_x8)]
        if gate_next>46:
            gate_next = 46
        elif gate_next<4:
            gate_next = 4
        return int(gate_next)