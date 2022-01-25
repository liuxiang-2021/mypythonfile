# -*- coding: utf-8 -*-
# @Time    : 2020/11/19 14:15
# @Author  : liuxiang
# @FileName: tkinter_study.py
# @Software: PyCharm
# @email    ：liuxiang@hesaitech.com
import tkinter as tk  # 使用Tkinter前需要先导入

# # 第1步，实例化object，建立窗口window
# window = tk.Tk()
#
# # 第2步，给窗口的可视化起名字
# window.title('My Window')
#
# # 第3步，设定窗口的大小(长 * 宽)
# window.geometry('500x300')  # 这里的乘是小x
#
# # 第4步，在图形界面上设定标签
# var = tk.StringVar()  # 将label标签的内容设置为字符类型，用var来接收hit_me函数的传出内容用以显示在标签上
# l = tk.Label(window, textvariable=var, bg='green', fg='white', font=('Arial', 12), width=30, height=2)
# # 说明： bg为背景，fg为字体颜色，font为字体，width为长，height为高，这里的长和高是字符的长和高，比如height=2,就是标签有2个字符这么高
# l.pack()
#
# # 定义一个函数功能（内容自己自由编写），供点击Button按键时调用，调用命令参数command=函数名
# on_hit = False
#
#
# def hit_me():
#     global on_hit
#     if on_hit == False:
#         on_hit = True
#         var.set('you hit me')
#     else:
#         on_hit = False
#         var.set('')
#
# def unlike_me():
#     global on_hit
#     if on_hit == False:
#         on_hit = True
#         var.set('you unlike me')
#     else:
#         on_hit = False
#         var.set('')
#
# # 第5步，在窗口界面设置放置Button按键
# b = tk.Button(window, text='hit me', font=('Arial', 12), width=10, height=1, command=hit_me)
# b.pack(padx= 10,pady= 10)
#
# c = tk.Button(window, text='unlike me', font=('Arial', 12), width=10, height=1, padx=1,pady=1,command=unlike_me)
# c.pack(padx= 100,pady= 10)
#
# # 第6步，主窗口循环显示
# window.mainloop()

import tkinter as tk  # 使用Tkinter前需要先导入

# 第1步，实例化object，建立窗口window
window = tk.Tk()

# 第2步，给窗口的可视化起名字
window.title('My Window')

# 第3步，设定窗口的大小(长 * 宽)
window.geometry('500x300')  # 这里的乘是小x

# 第4步，在图形界面上设定输入框控件entry框并放置
e = tk.Entry(window, show=None)  # 显示成明文形式
e.pack()


# 第5步，定义两个触发事件时的函数insert_point和insert_end（注意：因为Python的执行顺序是从上往下，所以函数一定要放在按钮的上面）
def insert_point():  # 在鼠标焦点处插入输入内容
    var = e.get()
    t.insert('insert', var)


def insert_end():  # 在文本框内容最后接着插入输入内容
    var = e.get()
    t.insert('end', var)


# 第6步，创建并放置两个按钮分别触发两种情况
b1 = tk.Button(window, text='insert point', width=10,
               height=2, command=insert_point)
b1.pack()
b2 = tk.Button(window, text='insert end', width=10,
               height=2, command=insert_end)
b2.pack()

# 第7步，创建并放置一个多行文本框text用以显示，指定height=3为文本框是三个字符高度
t = tk.Text(window, height=3)
t.pack()

# 第8步，主窗口循环显示
window.mainloop()