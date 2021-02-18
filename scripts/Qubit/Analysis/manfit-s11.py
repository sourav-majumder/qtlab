import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons
from lmfit import *
import glob
import manfit as mf
lig = 3e8/2.1**0.5


# files = glob.glob('*.dat')

data = np.loadtxt('D:/data/20180302/172657_cavity/172657_cavity.dat', unpack = True, usecols=(0,1,2,3,4))

freq = data[0]
real = data[1]
imag = data[2]
absol = data[3]
phase = data[4]
# s11data = real[-1] + 1j*imag[-1]






###############
#Fitting
###############

# def s11(f, ki,ke,f0,norm,c,b,z):
#     return (norm*(1-ke/((ki+ke)/2 + 1j*(f-f0)))-(c+1j*b))**np.exp(1j*2*np.pi*freq*z/lig)

def s11(f,ki,ke,f0):
    return (1-ke/((ki+ke)/2 + 1j*(f-f0)))

def residual(params):
    p=[]
    for key,value in params.valuesdict().items():
        p.append(value)
    return np.real(s11(*p))-y

def s11real(f,ki,ke,f0,norm,c,b,z=0):
	return np.real(s11(f,ki,ke,f0,norm,c,b,z))

def s11imag(f,ki,ke,f0,norm,c,b,z=0):
	return np.imag(s11(f,ki,ke,f0,norm,c,b,z))

def s11abs(f,ki,ke,f0,norm,c=0):
	return norm*np.abs(s11(f,ki,ke,f0)) + c

t = freq
ydata = real



# Initialize Parameters
params = [mf.Parameter(100,1e6, name='ki'),
		  mf.Parameter(100,1e5, name='ke'),
		  mf.Parameter(freq[0],freq[-10], name='f0'),
		  mf.Parameter(0.01,1, name='norm')]
''',
		  mf.Parameter(0.01,1, name='norm'),
		  mf.Parameter(0,1, name='c')]'''


figure, axes = plt.subplots(1,1,figsize=(6,4), dpi=96)
line1, = axes.plot(t,s11abs(t, *[param.val for param in params]))
line2, = axes.plot(t,absol,'.',color='#33000033')


# setup plot
# figure, (axes1,axes2) = plt.subplots(1,2,figsize=(6,4), dpi=96)
# line1, = axes1.plot(t,s11real(t, *[param.val for param in params]))
# line2, = axes1.plot(t,real)
# line3, = axes2.plot(t,s11imag(t, *[param.val for param in params]))
# line4, = axes2.plot(t,imag)

# start ManFit
# mf.manfit(figure, parameter_list, lines_to_update, xdata, ydata, fit_func)
mf.manfit(figure, params, {line1:s11abs}, t, absol, s11abs)