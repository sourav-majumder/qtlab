import numpy as np
import matplotlib.pyplot as plt
import lmfit as lm
from helpers import *


#path_gr = r'D:\data\20201219\193651_dimon_ground\193651_dimon_ground'
# print path+path[16:]+r'.dat'

#

#path = r'D:\data\20201219\185435_rabi_dimon_long\185435_rabi_dimon_long'
# print path+path[16:]+r'.dat'
data = np.loadtxt(r'D:\data\20201223\173113_Bright_driven_dark_pi_cal3\173113_Bright_driven_dark_pi_cal3.dat', unpack=True, skiprows = 23)

no = 81

delay1 = np.array_split(data[0],no)
time = np.array_split(data[1],no)[0]/1e-6
X = np.array_split(data[2],no)
Y = np.array_split(data[3],no)
R = np.array_split(data[4],no)

# plt.plot(R[0])
# plt.show()

