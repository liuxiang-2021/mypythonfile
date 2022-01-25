# -*- coding: utf-8 -*-
# @Time    : 2020/11/12 11:02
# @Author  : liuxiang
# @FileName: plot_study.py
# @Software: PyCharm
# @email    ：liuxiang@hesaitech.com

import matplotlib.pyplot as plt
import numpy as np

# fig, ax = plt.subplots()
# print(fig)
# print(ax)

# sc = ax.scatter([1, 2], [1, 2], c=[1, 2])
# ax.set_ylabel('YLabel')
#
# ax.set_xlabel('XLabel')
# cbar = fig.colorbar(sc)
# cbar.set_label("ZLabel")
#
# plt.show()

# Fixing random state for reproducibility
np.random.seed(19680801)
fig, ax = plt.subplots()

x = np.arange(0.0, 50.0, 2.0)
y = x ** 1.3 + np.random.rand(*x.shape) * 30.0
s = np.random.rand(*x.shape) * 800 + 500
# s = 30

# plt.scatter(x, y, s, c="g", alpha=0.5, marker=r'$\clubsuit$',
#             label="Luck")
# plt.xlabel("Leprechauns")
# plt.ylabel("Gold")
# plt.legend(loc='upper left')
# plt.show()

ax.scatter(x, y, s, c="g", alpha=0.5, marker=r'$\clubsuit$',
            label="Luck")

plt.xlabel("Leprechauns")
plt.ylabel("Gold")
plt.legend(loc='upper left')
plt.show()