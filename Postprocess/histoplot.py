# -*- coding: utf-8 -*-
"""
Created on Mon Dec 23 13:37:33 2019

@author: vr_lab
"""
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import pdb


#names = ['0-2.8', '2.8-5.6', '5.6-8.4','8.4-11.2','11.2-14']
#values = [49.11721, 11.10192, 16.81643, 15.89028, 7.07417]
#names = ['0-1', '1-2', '2-3','3-4','4-5']
#values = [51.35966, 13.58477, 19.63033, 7.590447, 7.834792]
#names = ['0-0.003', '0.003-0.006', '0.006-0.009','0.009-0.012','0.012-0.016']
#values = [49.64531, 19.86679, 19.9732, 7.37369, 3.14101]
names = ['0-0.016', '0.016-0.032', '0.032-0.048','0.048-0.064','0.064-0.08']
values = [45.82644, 19.56727, 21.19098, 7.937259, 5.478048]
plt.bar(names, values)
plt.bar(range(len(values)), values)
plt.grid(axis='y', alpha=0.75)
#plt.suptitle('node percentage vs displacement (mm)')
#plt.xlabel('displacement (mm)')
#plt.ylabel('number of node (%)')
plt.suptitle('node percentage vs error')
plt.xlabel('error (mm)')
plt.ylabel('node percentage (%)')
plt.show()