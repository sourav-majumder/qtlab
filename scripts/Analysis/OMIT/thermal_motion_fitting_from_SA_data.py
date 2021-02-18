import numpy as np
import matplotlib.pyplot as plt 
from lmfit import Model
import glob



def thermal(f, f0, a, gammaM):
	return baseline + a / ((2*(f-f0)/gammaM)**2 + 1)




pth = 'D:\\data\\2018-09-10\\thermal motion\\1500_avg\\150mK_down1500avg.dat'

freq, powerdB = np.loadtxt(pth, delimiter=';', skiprows=29, usecols=(0,1), unpack=True)
power_lin_Watt = 10.**(powerdB/10.)

#cut = 200

x = freq[:]
y = power_lin_Watt[:]

#plt.plot(x,y);plt.show()

lor = Model(thermal)

f0_guess = freq[np.argmax(power_lin_Watt)]
a_guess = np.max(power_lin_Watt)
#baseline_guess = np.min(power_lin_Watt)

baseline = np.mean(y[:50])

gam_guess = 4262

result = lor.fit(y, f = x, f0 =f0_guess, a = a_guess, gammaM = gam_guess)#, baseline = baseline_guess)
fitR = result.best_values['gammaM']
fita = result.best_values['a']
amp = (result.best_values['a']) 
gammaM = (result.best_values['gammaM'])
area = (amp )*(gammaM)

errfitR = result.params['gammaM'].stderr
errfita = result.params['a'].stderr
errarea = amp*errfitR + gammaM*errfita

print(result.fit_report())
print(area)
print(errarea)
plt.plot(x, y,'bo', label = r'$\gamma_m = $'+str(fitR))
plt.plot(x, result.best_fit,'-r', label = r'Error on $\gamma_m = $'+str(errfitR))

plt.title('a = '+str(fita)+'  Err on a = '+str(errfita))

plt.legend()
plt.tight_layout()

#plt.plot(x, y,'bo')
plt.show()

