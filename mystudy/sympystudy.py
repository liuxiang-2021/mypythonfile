# -*- coding: utf-8 -*-
# @Time    : 2020/10/29 16:09
# @Author  : liuxiang
# @FileName: sympystudy.py
# @Software: PyCharm
# @email    ：liuxiang@hesaitech.com

#解方程无穷多解
#定义变量
# import sympy
# x=sympy.Symbol('x')
# y=sympy.Symbol('y')
# fx=x*3+y**2
# #得到是x与y的关系式，
# print(sympy.solve(fx,x,y))

from sympy import *
import time
x, y, z = symbols("x y z")
# expr = cos(x) + 1
# a = expr.subs(x, y)
# print(a)
# expr1 = sin(2*x) + cos(2*x)
# print(expand_trig(expr1))
#
# expr2 = x**4 - 4*x**3 + 4*x**2 - 2*x + 3
# replacements = [(x**i, y**i) for i in range(5) if i % 2 == 0]
# print(expr2.subs(replacements))
#
# expr3 = sqrt(8)
# print(expr3.evalf())
expr = cos(2*x)
start = time.time()
a = expr.evalf(subs={x:2.4})
end =time.time()
elaped_time = end -start
print("使用的时间为%f" %elaped_time) #从测试结果来看，这个耗时更小；

start1 = time.time()
b = expr.subs(x,2.4)
end1 =time.time()
elaped_time1 = end1 -start1
print("使用的时间为%f" %elaped_time1)
print(a)
print(b)

from sympy.abc import x
from sympy.plotting import plot

plot(1/x)