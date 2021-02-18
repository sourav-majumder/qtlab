import numpy as np
import matplotlib.pyplot as plt
from helpers import *

path = r'D:\data\20180611\041252_t2'
data = np.loadtxt(path+path[16:]+r'.dat', unpack=True)

no = 176

delay= np.array_split(data[0],no)
time = np.array_split(data[1],no)[0]/1e-6
X = np.array_split(data[2],no)
Y = np.array_split(data[3],no)
R = np.array_split(data[4],no)

# plt.plot(X[0])
# plt.plot(Y[0])
# plt.show()
X, _ = rotate(X, Y, zeros = (900,999), steady = (520,620))
delay = np.array([s[0]*4.4*1e-9 for s in delay])

#
# np.save(path+r'\rt_norm_X',X)
# plt.imshow(X, aspect='auto',extent=[time[0], time[-1], delay[-1], delay[0]], cmap = 'jet')
# plt.show()


left = 260
right = 300

X = [pfit(time[left:right],s[left:right]) for s in X]

for i in range(10):
	plt.plot(X[i],label = str(i))
plt.legend()
plt.show()
# plt.plot(time[left:right], X[0][left:right], 'bo')
# plt.plot(time[left:right], pfit(time[left:right], X[0][left:right]))
# plt.show()

def tau_fit(plot=False):
	ground = X[4]
	excited = X[0]

	pop = []

	for x in X:
		pop.append(population(x, ground=ground, excited=excited))
	
	pop = np.array(pop)
	# plt.plot(pop)
	# plt.show()
	import lmfit as lm
	t = delay
	ydata = pop# + np.random.uniform(low=-0.5,high=0.5, size=len(t))
	def expo(freq, tau, norm ,pha,m):
		return norm*np.exp(-t/tau)*np.sin(freq*t+pha)+0.5 +t*m

	def residual(params):
		p=[]
		for key,value in params.valuesdict().items():
			p.append(value)
		return expo(*p)-ydata

	lmfit_params = lm.Parameters()
	lmfit_params.add('Frequency', value=1e9)
	lmfit_params.add('Tau', value=3.6e-6)
	lmfit_params.add('Norm', value=0.9)
	lmfit_params.add('Phase', value=0.5)
	lmfit_params.add('m', value=0.9)
	# print lmfit_params
	mi = lm.minimize(residual,lmfit_params,method='leastsq')
	if plot:
		fig = plt.figure(figsize= (12,2))
		plt.plot(t, ydata, '.')
		plt.plot(t, mi.residual+ydata)
		plt.tight_layout()
		plt.show()
	return pop, mi.residual+ydata, mi.params['Tau'].value, mi.params['Norm'].value
	
# X = X[:-30]
fit_p = tau_fit(True)
print fit_p[-1], fit_p[-2]