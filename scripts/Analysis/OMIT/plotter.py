import numpy as np
import matplotlib.pyplot as plt 
from lmfit import Model
import glob

def thermal(f, f0, a, gammaM,baseline):
	return baseline + a / ((2*(f-f0)/gammaM)**2 + 1)

flist = [67]

init_guess= 55.0
cut = 200
files = glob.glob('**mK.dat')
print(files)
for index, name in enumerate(flist):
	freq, powerdB = np.loadtxt(str(name)+'mk.DAT', delimiter=';', skiprows=29, usecols=(0,1), unpack=True)
	power_lin_Watt = 10.**(powerdB/10.)
	gmodel = Model(thermal)
	
	a0 = np.max(power_lin_Watt)
	f00 = freq[np.argmax(power_lin_Watt)]
	gammaM0 = init_guess
	baseline0 = np.min(power_lin_Watt)

	result = gmodel.fit(power_lin_Watt[cut:-cut],f = freq[cut:-cut], f0 = f00, a = a0, gammaM = gammaM0, baseline = baseline0 )

	plt.plot(freq[cut:-cut],power_lin_Watt[cut:-cut],'bo',label = str(name)+' dBm') 
	plt.plot(freq[cut:-cut],result.best_fit,'r-')
	plt.legend()
	tlstr = str(result.best_values['a'])+" "+str(result.best_values['gammaM'])+" "+str(result.best_values['gammaM']*result.best_values['a'])
	plt.title(tlstr)
	plt.savefig(str(name)+'mK'+'.png')
	plt.clf()
	fit = [name, result.best_values['f0'], result.best_values['gammaM'],result.best_values['a'],result.best_values['baseline']]
	print(fit)
