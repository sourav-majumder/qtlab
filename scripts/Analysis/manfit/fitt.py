import manfit as mf

import numpy as np
import matplotlib.pyplot as plt

# write function with parameters as parameters
import manfit as mf

import numpy as np
import matplotlib.pyplot as plt

# write function with parameters as parameters
file = 'D:/data/20180408/125124_sudhir_without_bscco_drum/125124_sudhir_without_bscco_drum.dat'
data = np.loadtxt(file, unpack = True, usecols=(0,1,2,3,4))

freq = data[0]
real = data[1]
imag = data[2]
absol = data[3]
phase = data[4]

# t = np.linspace(0,5,100)
# ydata = np.exp(-t/3)*np.sin(2*np.pi*0.7*t) + np.random.uniform(low=-0.5,high=0.5, size=len(t))
# def sine(t, freq, tau):
# 	return np.exp(-t/tau)*np.sin(2*np.pi*freq*t)

# def cosine(t, freq, phi):
# 	return np.cos(2*np.pi*freq*t + phi)

f= freq
ydata = absol
def s11(f,ki,ke,f0):
    return (1-ke/((ki+ke)/2 + 1j*(f-f0)))
def abs11(f,ki,ke,f0,norm,c,b):
	return norm*np.abs(s11(f,ki,ke,f0)+(c+1j*b))

# Initialize Parameters
params = [mf.Parameter(1e3,1e6, name='ki'),
		  mf.Parameter(1e3,1e6, name='ke'),
		  mf.Parameter(freq[0],freq[-1], name='f0'),
		  mf.Parameter(0.1,1, name='norm'),
		  mf.Parameter(0,1, name='c'),
		  mf.Parameter(0,3, name='b')]

# setup plot
figure, axes = plt.subplots(1,1,figsize=(6,4), dpi=96)
line1, = axes.plot(f,abs11(f, *[param.val for param in params]))
line2, = axes.plot(f,ydata)

# start ManFit
# mf.manfit(figure, parameter_list, lines_to_update, xdata, ydata, fit_func)
mf.manfit(figure, params, {line1:abs11}, f, ydata, abs11)
