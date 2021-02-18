import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons
from mpmath import *
from lmfit import *
import manfit as mf

GHz = 1e9
MHz = 1e6
kHz = 1e3
Hz = 1
Pi = np.pi

bare_freq = 7.3740*GHz
dressed_freq = 6.68073*GHz
f01 = 5.732*GHz
f12 = 5.4181*GHz
Ec = 313.9*MHz
kappa = 2*Pi*836.86*kHz
mearurement_freq = dressed_freq
Delta_r = 0#2*Pi*(bare_freq - mearurement_freq)
gamma_2 = 2 #in MHz and 2*Pi

################
#Spectroscopy Detail
################
start_freq = 5.7*GHz
stop_freq = 5.76*GHz
resolution = 1*MHz
numpoints = int(abs(stop_freq - start_freq)/resolution + 1)
# freq = np.linspace(start_freq, stop_freq, numpoints)

################
#Analysis File
################
file_name = 'D:/data/20180201-CooldownDataWithQubitInTwoPortCavity/20180203/234240_stark-shift/234240_stark-shift.dat'
data = np.loadtxt(file_name, unpack=True)
power= np.array_split(data[0],11)
freq = np.array_split(data[1],11)[0]
real = np.array_split(data[2],11)
absol = np.array_split(data[4],11)


def detuning(w_ij,wr = bare_freq):
	return w_ij - wr

def g(w_ij, chi_ij):
	return np.sqrt(chi_ij*detuning(w_ij))

chi01 = bare_freq - dressed_freq #without 2*pi
delta0 = detuning(f01)
g01 = g(f01,chi01)
chi_reduce = -pow(g01,2)*(Ec/(delta0*(delta0-Ec))) #without 2*pi

chi = 2*Pi*chi_reduce
Delta_r = chi
print(chi_reduce)

def D_s(nph,kappa):
	return (2*nph*pow(chi,2))/(pow(kappa,2)/4+pow(chi,2)+pow(Delta_r,2))
def A(nph,kappa):
	return (D_s(nph,kappa)*(kappa/2-1j*chi-1j*Delta_r))/(kappa/2+1j*chi+1j*Delta_r)
def B(nph,kappa):
	return chi*(nph-D_s(nph,kappa))
def w(j,nph,fa,kappa):
	return 2*Pi*fa+chi+B(nph,kappa)+j*(chi+Delta_r)
def Gamma_m(nph,kappa):
	return (nph*kappa*pow(chi,2))/(pow(kappa,2)/4+pow(chi,2)+pow(Delta_r,2))
def Gamma(j,nph,gamma,kappa):
	return 2*(2*Pi*gamma*MHz+Gamma_m(nph,kappa))+j*kappa
def S_absol(f,nph,fa,gamma,kappa):
	return nsum(lambda n: (1/math.factorial(n))*np.abs((pow(-1*A(nph,kappa),n)*np.exp(A(nph,kappa)))/(Gamma(n,nph,gamma,kappa)/2-1j*(f-w(n,nph,fa,kappa)))),[0,inf])/Pi
def S_real(f,nph,fa,gamma,kappa):
    return nsum(lambda n: (1/math.factorial(n))*np.real((pow(-1*A(nph,kappa),n)*np.exp(A(nph,kappa)))/(Gamma(n,nph,gamma,kappa)/2-1j*(f-w(n,nph,fa,kappa)))),[0,inf])/Pi
def spectroscope(f,fa,nph,norm,c,gamma,kappa=kappa):
	SW = np.zeros(len(freq))
	for i in range(len(freq)):
		SW[i]= norm*S_real(2*Pi*freq[i],nph,fa,gamma,kappa)+c
	return SW

def residual(params):
    p=[]
    for key,value in params.valuesdict().items():
        p.append(value)
    return spectroscope(*p)-real[index]

index=8
plt.title('Stark Shift')
for i in range(len(real)):
    plt.plot(freq/1e9,absol[i]-i*0.001)
plt.ylabel(r'$S(w)$')
plt.xlabel('Frequency (GHz)')
plt.show()

f = range(len(freq))
# ydata = np.exp(-t/1.)*np.sin(2*np.pi*0.7*t) + np.random.uniform(low=-0.5,high=0.5, size=len(t))
# def sine(t, freq, tau):
#     return np.exp(-t/tau)*np.sin(2*np.pi*freq*t)

# def cosine(t, freq, phi):
#     return np.cos(2*np.pi*freq*t + phi)

# Initialize Parameters
params = [mf.Parameter(freq[0],freq[-1], name='Frequency'),
          mf.Parameter(0,20, name='photon'),
          mf.Parameter(19800,1e7, name='norm'),
          mf.Parameter(-0.007,0.01, name='c'),
          mf.Parameter(gamma_2,20, name='gamma')]


# setup plot
figure, axes = plt.subplots(1,1,figsize=(6,4), dpi=96)
line1, = axes.plot(freq,spectroscope(f,*[param.val for param in params]))
line2, = axes.plot(freq,real[index])

# start ManFit
# mf.manfit(figure, parameter_list, lines_to_update, xdata, ydata, fit_func)
mf.manfit(figure, params, {line1:spectroscope}, f, real[index], spectroscope)

































# fig = plt.figure()
# ax = fig.add_subplot(111)
# fig.subplots_adjust(left=0.25, bottom=0.25)
# fa0 = freq[30]
# nph0 = 11.9
# norm0 = 2e8
# c0 = 0.0056
# gamma0= gamma_2
# kappa0 = kappa


# im, = ax.plot(freq, spectroscope(fa0,nph0,norm0,c0,gamma0,kappa0), label= 'Theory')
# ax.plot(freq,absol[index],label= 'Data')
# ax.legend()

# axcolor = 'lightgoldenrodyellow'

# axc = fig.add_axes([0.25, 0.01, 0.65, 0.03], facecolor=axcolor)
# axnorm = fig.add_axes([0.25, 0.05, 0.65, 0.03], facecolor=axcolor)
# axnph = fig.add_axes([0.25, 0.09, 0.65, 0.03], facecolor=axcolor)
# axfa = fig.add_axes([0.25, 0.13, 0.65, 0.03], facecolor=axcolor)
# axgamma = fig.add_axes([0.25, 0.17, 0.65, 0.03], facecolor=axcolor)
# axkappa = fig.add_axes([0.25, 0.21, 0.65, 0.03], facecolor=axcolor)


# sc = Slider(axc, 'Constant', 0, 0.093, valinit=c0, valfmt='%0.3f')
# snorm = Slider(axnorm, 'norm', 1e7, 1e10, valinit=norm0, valfmt='%d')
# snph = Slider(axnph, 'Photon',4, 14, valinit=nph0, valfmt='%0.3f')
# sfa = Slider(axfa, 'Qubit freq', freq[0], freq[-1], valinit=fa0, valfmt='%d')
# sgamma = Slider(axgamma, 'Gamma',1, 40, valinit=gamma0, valfmt='%0.3f')
# skappa = Slider(axkappa, 'Kappa',2*Pi*100*kHz, 2*Pi*2000*kHz, valinit=kappa0, valfmt='%0.3f')


# def update(val):
#     im.set_ydata(spectroscope(sfa.val, snph.val, snorm.val, sc.val, sgamma.val, skappa.val))
#     fig.canvas.draw()

# snph.on_changed(update)
# snorm.on_changed(update)
# sc.on_changed(update)
# sfa.on_changed(update)
# sgamma.on_changed(update)
# skappa.on_changed(update)

# resetax = plt.axes([0.05, 0.025, 0.1, 0.04])
# button = Button(resetax, 'Reset', color=axcolor, hovercolor='0.975')


# def reset(event):
#     snph.reset()
#     snorm.reset()
#     sc.reset()
#     sfa.reset()
#     sgamma.reset()
#     skappa.reset()

# button.on_clicked(reset)
# # plt.plot(freq,spectroscope(10,0))
# # plt.plot(freq,absol[0],'.')
# plt.show()

# paramsa=Parameters()
# #               (Name,      Value,      Vary,     Min,      Max,    Expr)
# paramsa.add_many(('fa',      sfa.val,   True,     freq[0],    freq[-1],   None),
# 				('nph',       snph.val,      True,     4,        14,   None),
#                 ('norm',    snorm.val,    True,     1e5,     1e9,   None),
#                 ('c',       sc.val,          True,     0,        0.004,   None),
#                 ('gamma',    sgamma.val,      True,     1,        40,   None),
#                 ('kappa',    skappa.val,      True,     2*Pi*100*kHz,        2*Pi*2000*kHz,   None))

# mi = minimize(residual,paramsa,method='leastsq')
# print fit_report(mi)

# gamma = mi.params['gamma'].value
# nph = mi.params['nph'].value
# fa = mi.params['fa'].value
# norm = mi.params['norm'].value
# c = mi.params['c'].value
# kappa = mi.params['kappa'].value

# plt.plot(freq,absol[index], 'ro', label='data')
# plt.plot(freq,spectroscope(fa, nph, norm, c, gamma,kappa), 'b', label='fit')
# plt.legend()
# plt.show()







