from scipy.constants import hbar, pi
import numpy as np
DeltaS = 1.764*1.38064852e-23*1.1
e = 1.60217662e-19
GHz = 1e9
MHz = 1e6
kHz = 1e3
Hz = 1


bare_cavity_freq = 7.35*GHz
dressed_cavity_freq_ground = 7.24426*GHz
dressed_cavity_freq_exited = 7.21762*GHz #None
f01 = 6.63387*GHz
f12 = 5.79571*GHz
Ec = 250*MHz#f01-f12
# print Ec

def photons(power):
	p = 1e-3*10**(power/10.)
	return (p*ke)/(hbar*w*((k/2)**2+(w-w0)**2))

def CriticalCurrent(Resis):
	return pi*DeltaS/(2*e*Resis)

def CriticalCurrentDensity(Resis, length, width):
	return CriticalCurrent(Resis)/((length*1e-9*width*1e-9-10454*1e-18)*1e4)# unit A*cm-2 
	#length and width is in nm
	#resistance is in ohm

def detuning(w_ij,wr = bare_cavity_freq):
	return w_ij - wr

def g(w_ij, chi_ij):
	return np.sqrt(chi_ij*detuning(w_ij))

def chi12(exited, ground, c01):
	if exited == None:
		return None
	else:
		return 2*c01-(exited-ground)

def chiKoch(exited, ground, c01):
	if exited == None:
		return None
	else:
		return c01-chi12(exited, ground, c01)/2



# chi01 = bare_cavity_freq - dressed_cavity_freq_ground #without 2*pi
# delta0 = detuning(f01)
# g01 = g(f01,chi01)
# chi_reduce = -pow(g01,2)*(Ec/(delta0*(delta0-Ec))) #without 2*pi
# # chi12 = chi12(dressed_cavity_freq_exited,dressed_cavity_freq_ground,chi01)
# chi = 2*pi*chi_reduce
# # print g(f01,chi_reduce)



k = 2*pi*2.6e6
ke = 2*pi*1.1e6
w0 = 2*pi*7.35*GHz
w = 2*pi*6.9*GHz #2*pi*6.40275e9#w0-(2*pi*15e6)#2*pi*4.721e9
attenuation = 52 #dB

p1 =  photons(-30-attenuation)
print p1
# # k = 2*pi*17e6
# # ke = (2./9)*k
# # w0 = 2*pi*8.9772e9
# # w = 2*pi*8e9

# # p2 = photons(-attenuation)
# # print p1/1e6
# # print CriticalCurrent(118000)
# print CriticalCurrentDensity(10000,250,400)