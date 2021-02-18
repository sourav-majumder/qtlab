import numpy as np
import lmfit as lm

t = np.linspace(0,5,100)
ydata = np.exp(-t/1.)*np.sin(2*np.pi*0.3*t)# + np.random.uniform(low=-0.5,high=0.5, size=len(t))
def sine(freq, tau):
	return np.exp(-t/tau)*np.sin(2*np.pi*freq*t)

def residual(params):
	p=[]
	for key,value in params.valuesdict().items():
		p.append(value)
	return sine(*p)-ydata

lmfit_params = lm.Parameters()
lmfit_params.add('Frequency', value=0, min=-1, max=1)
lmfit_params.add('Tau', value=0.1, min=0.1, max=3)
# print lmfit_params
mi = lm.minimize(residual,lmfit_params,method='leastsq')
print lm.fit_report(mi)