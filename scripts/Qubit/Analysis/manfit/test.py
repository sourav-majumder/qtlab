import numpy as np
import lmfit as lm



def residual(params):
	p=[]
	for key,value in params.valuesdict().items():
		p.append(value)
	return custom(*p)-absol[0]

lmfit_params = lm.Parameters()
lmfit_params.add('Frequency', value=0, min=-1, max=1)
lmfit_params.add('ke', value=1e6, min=1e3, max=5e6)
# print lmfit_params
mi = lm.minimize(residual,lmfit_params,method='leastsq')
print lm.fit_report(mi)