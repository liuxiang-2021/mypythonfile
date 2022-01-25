# -*- coding: utf-8 -*-
# @Time    : 2021/3/4 20:47
# @Author  : liuxiang
# @FileName: email_test1.py
# @Software: PyCharm
# @email    ：liuxiang@hesaitech.com

import smtplib
from email.mime.text import MIMEText
#设置服务器所需信息
#163邮箱服务器地址
'''用163邮箱给QQ发邮件相对来说很容易，而用QQ发邮件需要在QQ邮箱里面设置一下授权码，
   然后QQ 邮箱需要SSL认证，可以模拟给自己发一个邮件,公司邮件
'''
mail_host = 'smtp.qq.com'
#163用户名
mail_user = '1332868528'
#密码(部分邮箱为授权码)
mail_pass = 'mpiptoviwplfiafe' #注意，如果发件箱是QQ邮箱的话，那么密码就是授权码
#邮件发送方邮箱地址
sender = '1332868528@qq.com'  #sender 需要和账号密码进行匹配
#邮件接受方邮箱地址，注意需要[]包裹，这意味着你可以写多个邮件地址群发
receivers = ['liuxiang@hesaitech.com']

#设置email信息
#邮件内容设置
message = MIMEText('Hello，World','plain','utf-8')
#邮件主题
message['Subject'] = '这是一个自动发送邮件的脚本试验'
#发送方信息
message['From'] = sender
#接受方信息
message['To'] = receivers[0]

#登录并发送邮件
try:
    smtpObj = smtplib.SMTP()
    #连接到服务器
    smtpObj.connect(mail_host,25)
    #更换SSL认证
    smtpObj = smtplib.SMTP_SSL(mail_host)
    #登录到服务器
    smtpObj.login(mail_user,mail_pass)
    #发送
    smtpObj.sendmail(
        sender,receivers,message.as_string())
    #退出
    smtpObj.quit()
    print('success')
except smtplib.SMTPException as e:
    print('error',e) #打印错误