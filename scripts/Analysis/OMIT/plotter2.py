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
for index, name in enumerate(files[:]):
	freq, powerdB = np.loadtxt(str(name), delimiter=';', skiprows=29, usecols=(0,1), unpack=True)
	power_lin_Watt = 10.**(powerdB/10.)
	if 10>=index>=6:
		plt.plot(freq,power_lin_Watt,'+',label=files[index])
	elif index>10:
		plt.plot(freq,power_lin_Watt,'*',label=files[index],)
	else:
		plt.plot(freq,power_lin_Watt,label=files[index])
plt.legend()
plt.show()
	
	# plt.plot(freq[cut:-cut],power_lin_Watt[cut:-cut],'bo',label = str(name)+' dBm') 
	# plt.plot(freq[cut:-cut],result.best_fit,'r-')
	# plt.legend()
	# tlstr = str(result.best_values['a'])+" "+str(result.best_values['gammaM'])+" "+str(result.best_values['gammaM']*result.best_values['a'])
	# plt.title(tlstr)
	# plt.savefig(str(name)+'mK'+'.png')
	# plt.clf()
	# fitt = [name, result.best_values['f0'], result.best_values['gammaM'],result.best_values['a'],result.best_values['baseline']]
	# print(fitt)

