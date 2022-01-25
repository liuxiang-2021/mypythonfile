# -*- coding: utf-8 -*-
# @Time    : 2021/2/7 13:21
# @Author  : liuxiang
# @FileName: codesettting.py
# @Software: PyCharm
# @email    ：liuxiang@hesaitech.com

import os
import csv
import time
import win32gui
import win32com.client
from WebUpgrade.Upgrade import WebControl
from PIL import ImageGrab

def code_setting(code_file, col_num, code_tot_num, test_host="192.168.1.201"):

    url="http://192.168.1.201/special_setting.html"
    f = open(code_file, 'r', encoding='utf-8')
    code_reader = csv.reader((f))
    codes = [code for code in code_reader]
    code_num = codes[col_num][0]

    if col_num<0 or col_num>code_tot_num:
        print("code number exceeds maximum, exit")
        exit()
    else:
        ist_code=codes[col_num]
        print("code ", code_num, "will be set:", ist_code)

    cs_webctrl = WebControl(test_host)
    cs_driver = cs_webctrl.driver
    cs_driver.get(url)
    time.sleep(2)
    # after comformation of security code, one prompt dialog with "successfully saved" as message will be raised. error: UnexpectedAlertPresentException
    try:
        SCode = cs_driver.find_element_by_id("security-code")
        SCode.clear()
        SCode.send_keys(str(921223))
        time.sleep(1)
        saveButton = cs_driver.find_element_by_id("save_code_range")  ## not sure
        saveButton.click()
        time.sleep(1)
    except:
        pass

    Code1 = cs_driver.find_element_by_id("constant_value_box_1")
    Code1.clear()
    Code1.send_keys(str(ist_code[1]))
    for i in range(8):
        Code2 = cs_driver.find_element_by_id("constant_value_box_2_manual_"+str(i+1))
        Code2.clear()
        Code2.send_keys(str(ist_code[i+2]))


    cs_driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    saveButton = cs_driver.find_element_by_id("save_code_range_detail")
    saveButton.click()
    flag = 1
    try:
        al_text = cs_driver.switch_to.alert.text
        print(al_text+": code "+str(code_num))
        cs_driver.switch_to.alert.accept()
        flag = 0
    except:
        pass
    # cs_driver.close()
    cs_driver.quit()
    return flag, code_num

def save_screenshot(folder_path, num):
    im = ImageGrab.grab()
    image_name = "code%s.png" % num
    image_path = os.path.join(folder_path, image_name)
    im.save(image_path)

if __name__ == '__main__':
    # Before upgrade, please confirm sensor version is not "xxxxx"
    relay_host = "192.168.1.210"
    relay_port = 8089
    relay_channel = "1"
    test_host = "192.168.1.201"
    # IP已经写死，不能修改
    udpPort = 2368

    code_file = r"Z:\TempTestCases\liyuda\p128_encoding\p128V42code_version2.csv"
    code_tot_num = 176
    sleeptime = 9
    #
    for col_num in range(167, code_tot_num):
        flag, code_num = code_setting(code_file, col_num+1, code_tot_num, test_host="192.168.1.201")

        pandarview = win32gui.FindWindow('Qwidget', 'Pandar')
        # win32gui.BringWindowToTop(pandarview)
        pshell = win32com.client.Dispatch("Wscript.Shell")
        pshell.SendKeys('%')
        win32gui.SetForegroundWindow(pandarview)
        if flag==1:
            time.sleep(sleeptime)

            folder_path = r"Z:\TempTestCases\liyuda\p128_encoding\screenshots"
            save_screenshot(folder_path, code_num)
            time.sleep(1)
            folder_path2 = r"Z:\TempTestCases\liyuda\p128_encoding\screenshots_backup"
            save_screenshot(folder_path2, code_num)
