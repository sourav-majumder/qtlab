import numpy as np
import matplotlib.pyplot as plt
from lmfit import *

def s11(ki,ke,f0,norm,m,c):
	return norm*(1-ke/((ki+ke)/2 + 1j*(f-f0)))+m*f+c

def residual(params):
	p=[]
	for key,value in params.valuesdict().items():
		p.append(value)
	return np.abs(s11(*p))-y

# format is power,freq,amp,pha,real,imag
data = np.loadtxt('D:\\data\\20171004\\181600_test s11\\181600_test s11.dat', skiprows=22, usecols=(0,3)).swapaxes(0,1)

freq = data[0]
abso = data[1]

# First fit absolute

f = freq
y = abso
paramsa=Parameters()
#         	    (Name,		Value,  	Vary,     Min,	    Max,    Expr)
paramsa.add_many(('ki',		2e6,  	    True,	  0,	    1e9,	None),
				('ke',		2e6,  	    True,	  0,	    1e9,	None),
           		('f0',		7.95e9, 	True,	  None, 	None,	None),
           		('norm',	0.625,   	True,	  0,		50, 	None),
                ('m',	    0.5, 	    True,	  None,		None,	None),
                ('c',	    1e5, 	    True,     None,		None,	None))

mi = minimize(residual,paramsa,method='leastsq')
print fit_report(mi)
plt.plot(f,abso, 'ro', label='data')
plt.plot(f,mi.residual+y, 'b', label='fit')
plt.show()

ki = mi.params['ki'].value
ke = mi.params['ke'].value
f0 = mi.params['f0'].value
norm = mi.params['norm'].value

# paramsb = Parameters()
# paramsb.add_many(('z',	6,  True,	None,	None,	None),
# 				('phi', 0.344, False, -np.pi, np.pi, None))

# y = (real + 1j*imag).view(np.double)

# def new_res(params):
# 	p=[]
# 	for key,value in params.valuesdict().items():
# 		p.append(value)
# 	print p
# 	complex_s11 = s11(ki,ke,f0,norm)*np.exp(1j*2*np.pi*f*p[0])*np.exp(1j*p[1])
# 	flat_s11 = complex_s11.view(np.double)
# 	# plt.plot(flat_s11-y)
# 	# plt.show()
# 	return flat_s11-y

# mi2 = minimize(new_res,paramsb,method='leastsq')
# print fit_report(mi2)
# yfit = (mi2.residual+y).view(np.complex128)
# plt.subplot(231)
# plt.plot(real,imag, 'ro')
# plt.plot(np.real(yfit), np.imag(yfit), 'b')
# plt.subplot(232)
# plt.plot(f,real, 'ro')
# plt.plot(f, np.real(yfit),'b')
# plt.subplot(233)
# plt.plot(f,imag,'ro')
# plt.plot(f,np.imag(yfit), 'b')
# plt.subplot(234)
# plt.plot(f,phase, 'ro')
# plt.plot(f,np.angle(yfit),'b')
# plt.subplot(235)
# plt.plot(f,abso, 'ro')
# plt.plot(f,np.abs(yfit),'b')
# plt.tight_layout()
# plt.show()