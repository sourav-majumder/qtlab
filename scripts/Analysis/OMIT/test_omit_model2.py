import numpy as np
import matplotlib.pyplot as plt
from fitter import *
from lmfit import Model


# def omit_trans(f, f0, base, gamma, Cp):
#     return base * np.abs( 1 / (1 + Cp / (-1j*(2*(f-f0) /gamma) + 1  ) ) )


def omit_complete(f, f0, base, kappa, gamma, Cp):
    return base * np.abs( 1 / ( ( (-1j*(2*(f-f0) /kappa) + 1  ) ) + (Cp / ((-1j*(2*(f-f0) /gamma) + 1  )) )  )   )

#gm = Model(omit_trans)
gm_c = Model(omit_complete)

frn ,realn, imagn, abn ,phasen = np.loadtxt(r'D:\\data\\20180909\\120645_narrow\\120645_narrow.dat', usecols=(0,1,2,3,4), unpack=True)

frw ,realw, imagw, abw ,phasew = np.loadtxt(r'D:\\data\\20180909\\120829_widespan\\120829_widespan.dat', usecols=(0,1,2,3,4), unpack=True)

#powers = powers[::1001]
#freqs = np.array_split(fr,11)
#amps = np.array_split(am,11)
#phs = np.array_split(ph,11)


#Coo = []

#idx = 0

#x0 = freqs[idx]
#y0 = amps[idx]

#x1 = freqs2[idx]


x2fit = np.concatenate((frn,frw),axis = 0)

y2fit = np.concatenate((abn,abw),axis = 0)


base_guess = np.mean(abn[:5])
f0_guess = x2fit[np.argmin(abn)]
gamma_guess = 300
kappa_guess = 400*1000
Cp_guess = np.max(abn)  / np.min(abn) - 1.0


result = gm_c.fit(y2fit, f = x2fit, f0 = f0_guess, base = base_guess,kappa=kappa_guess, gamma = gamma_guess, Cp = Cp_guess)
print(result.fit_report())
plt.plot(x2fit,y2fit,'bo');	plt.plot(x2fit, result.best_fit, 'r*');	plt.show()


# for idx, pw in enumerate(powers):
# 	x = freqs[idx]
# 	y = amps[idx]

# 	base_guess = np.mean(y[:5])
# 	f0_guess = x[np.argmin(y)]
# 	gamma_guess = 200
# 	Cp_guess = np.max(y)  / np.min(y) - 1.0
# 	result = gm.fit(y, f = x, f0 = f0_guess, base = base_guess, gamma = gamma_guess, Cp = Cp_guess)
# 	#plt.plot(x,y,'bo');	plt.plot(x, result.best_fit, 'r-');	plt.show()
# 	print(result.fit_report())
# 	Coo.append(result.best_values['Cp'])

# plt.plot(powers,Coo);plt.show()