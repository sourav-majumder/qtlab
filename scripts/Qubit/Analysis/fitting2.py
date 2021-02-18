import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons
from lmfit import *
import glob
lig = 3e8/2.1**0.5


files = glob.glob('*.dat')

data = np.loadtxt(files[0], unpack = True, usecols=(0,1,2,3,4))

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

def s11(ki,ke,f0,norm,c,b,z):
    return norm*(1-ke/((ki+ke)/2 + 1j*(f-f0)))*np.exp(-1j*2*np.pi*f*z/lig) - (c+1j*b)

def residual(params):
    p=[]
    for key,value in params.valuesdict().items():
        p.append(value)
    return np.real(s11(*p))-y

def residual_img(params):
    p=[]
    for key,value in params.valuesdict().items():
        p.append(value)
    return np.imag(s11(*p))-yim

# z0 = 9.819

f= freq
y= real
yim = imag
s11data = real + 1j*imag
# plt.plot(freq,np.abs(s11data))
# plt.show()
paramsa=Parameters()
#               (Name,      Value,      Vary,     Min,      Max,    Expr)
paramsa.add_many(('ki',     5528,      True,     5520,        5540,    None),
                ('ke',      40937,     True,     40000,        42000,    None),
                ('f0',      7666580609,   True,     freq[0],    freq[-1],   None),
                ('norm',    5.281e-2,    True,     5e-2,     5.5e-2,   None),
                ('c',       -0.0056,      True,     -0.005,        -0.006,   None),
                ('b',       0.0044,          None,     0.004,        0.005,   None),
                ('z',       8.8762,      True,     0,        20,   None))


mi = minimize(residual,paramsa,method='leastsq')
print fit_report(mi)
# plt.plot(f,real[-1], 'ro', label='data')
# plt.plot(f,mi.residual+y, 'b', label='fit')
# plt.show()

ki = mi.params['ki'].value
ke = mi.params['ke'].value
f0 = mi.params['f0'].value
norm = mi.params['norm'].value
c = mi.params['c'].value
z = mi.params['z'].value
b = mi.params['b'].value



paramsa_im=Parameters()
#               (Name,      Value,      Vary,     Min,      Max,    Expr)
paramsa_im.add_many(('ki',     ki,      True,     0,        1e5,    None),
                ('ke',      ke,     True,     1e4,        1e6,    None),
                ('f0',      f0,   True,     freq[0],    freq[-1],   None),
                ('norm',    norm,    True,     0.01,     0.07,   None),
                ('c',       c,          None,     0,        0.1,   None),
                ('b',       b,          True,    -0.01,        0.01,   None),
                ('z',       z,      True,     0,        1,   None))

mi_img = minimize(residual_img,paramsa_im,method='leastsq')
print fit_report(mi_img)



ki = mi_img.params['ki'].value
ke = mi_img.params['ke'].value
f0 = mi_img.params['f0'].value
norm = mi_img.params['norm'].value
c = mi_img.params['c'].value
z = mi_img.params['z'].value
b =mi_img.params['b'].value

# s11(ki,ke,f0,norm,c,b,z)
plt.subplot(121)
plt.plot(f,imag, 'ro', label='imag_data')
plt.plot(f,np.imag(s11(ki,ke,f0,norm,c,b,z)), 'b', label='imag_fit')
plt.legend()
plt.subplot(122)
plt.plot(f,real, 'ro', label='real_data')
plt.plot(f,np.real(s11(ki,ke,f0,norm,c,b,z)), 'b', label='real_fit')


plt.legend()
plt.show()
































#################
#Slider Manipulation
#################

fig = plt.figure()
ax = fig.add_subplot(121)
bx = fig.add_subplot(122)
fig.subplots_adjust(left=0.25, bottom=0.25)
z0 = z
ki0 = ki
ke0 = ke
f00 = f0
norm0 = norm
c0 = c
b0 = b

lig = 3e8/2.1**0.5
files = glob.glob('*.dat')



s11data = real + 1j*imag







# print(func(1)-func(0))
im, = ax.plot(freq, imag, label= 'img')
re, = ax.plot(freq, real, label= 'real')
sreal, = ax.plot(freq, np.real(s11(ki0,ke0,f00,norm0,c0,b0,z0)), label= 'ideal real')
simag, = ax.plot(freq, np.imag(s11(ki0,ke0,f00,norm0,c0,b0,z0)), label= 'ideal imag')
ax.legend()
# ax.plot(freq, np.zeros(len(freq)))
po, = bx.plot(real,imag, label= 'data')
s11po, = bx.plot(np.real(s11(ki0,ke0,f00,norm0,c0,b0,z0)),np.imag(s11(ki0,ke0,f00,norm0,c0,b0,z0)), label= 'ideal')
# bx.yrange(-1,1)
# bx.yrange(-1,1)

bx.legend()
axcolor = 'lightgoldenrodyellow'

axz = fig.add_axes([0.25, 0.01, 0.65, 0.02], facecolor=axcolor)
axki = fig.add_axes([0.25, 0.04, 0.65, 0.02], facecolor=axcolor)
axke = fig.add_axes([0.25, 0.07, 0.65, 0.02], facecolor=axcolor)
axf0 = fig.add_axes([0.25, 0.10, 0.65, 0.02], facecolor=axcolor)
axnorm = fig.add_axes([0.25, 0.13, 0.65, 0.02], facecolor=axcolor)
axc = fig.add_axes([0.25, 0.16, 0.65, 0.02], facecolor=axcolor)
axb = fig.add_axes([0.25, 0.19, 0.65, 0.02], facecolor=axcolor)


sz = Slider(axz, 'Z',8, 12, valinit=z0, valfmt='%.4e')
ski = Slider(axki, 'Ki', 0, 1e5, valinit=ki0, valfmt='%d')
ske = Slider(axke, 'Ke', 1e4, 1e6, valinit=ke0, valfmt='%d')
sf0 = Slider(axf0, 'f0', freq[0], freq[-1], valinit=f00, valfmt='%d')
snorm = Slider(axnorm, 'norm', 0.01, 0.07, valinit=norm0, valfmt='%.3e')
sc = Slider(axc, 'consc', -0.2, 0.2, valinit=c0, valfmt='%.4f')
sb = Slider(axb, 'consb', -0.1, 0.1, valinit=b0, valfmt='%.4f')
# spixel = Slider(axpixel,'Value', 3, 71, valinit=pixel0, valfmt='%d')

def update(val):
    sreal.set_ydata(np.real(s11(ski.val, ske.val, sf0.val, snorm.val, sc.val, sb.val, sz.val)))
    simag.set_ydata(np.imag(s11(ski.val, ske.val, sf0.val, snorm.val, sc.val, sb.val, sz.val)))
    s11po.set_ydata(np.imag(s11(ski.val, ske.val, sf0.val, snorm.val, sc.val, sb.val, sz.val)))
    s11po.set_xdata(np.real(s11(ski.val, ske.val, sf0.val, snorm.val, sc.val, sb.val, sz.val)))
    fig.canvas.draw()



sz.on_changed(update)
ski.on_changed(update)
ske.on_changed(update)
sf0.on_changed(update)
snorm.on_changed(update)
sc.on_changed(update)
sb.on_changed(update)

resetax = plt.axes([0.1, 0.025, 0.1, 0.04])
button = Button(resetax, 'Reset', color=axcolor, hovercolor='0.975')


def reset(event):
    sz.reset()
    ski.reset()
    ske.reset()
    sf0.reset()
    snorm.reset()
    sc.reset()
    sb.reset()

button.on_clicked(reset)

plt.show()