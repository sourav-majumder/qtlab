import numpy as np
import matplotlib.pyplot as plt
from fitter import *


power = np.linspace(10,-60,num=10)

fr, am = np.loadtxt(r'C:\Users\Vibhor\Desktop\SMF_power_set_S21_frequency_set.dat', usecols=(1,2), unpack=True)

freqs = np.array_split(fr,10)
amps = np.array_split(am,10)


#plt.plot(freqs[0],amps[0]);plt.show()

x = freqs[0]
y = amps[7]

# def omit_transmission(f,f0,amp, gamma,Cp):
    # return np.abs( amp * (1. -  Cp / (-1j*(2*(f-f0)/gamma) + 1 + Cp )) )


# gm = Model(omit_transmission)

omit = Fitter(omit_transmission)

res = omit.fit(x, y, print_report = True,gamma = 200)
omit.plot()

# f0_guess = x[np.argmin(y)]
# Cp_guess = (np.max(y) - np.min(y)) /np.min(y)
# gamma_guess = 190
# amp_guess = np.max(y)  

# result = gm.fit(y, f = x, f0 = f0_guess, amp = amp_guess, gamma = gamma_guess, Cp = Cp_guess)

# plt.plot(x, y, 'b',label = 'Power dBm')
# plt.plot(x, result.best_fit, 'r-')

# print(result.best_values)