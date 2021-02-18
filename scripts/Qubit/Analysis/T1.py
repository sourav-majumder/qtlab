import numpy as np
import matplotlib.pyplot as plt

def volt(dBm):
	return np.sqrt(50*1e-3*(10**(dBm/10)))

data = np.loadtxt(r'D:\data\20201201\160058_t1_1\160058_t1_1.dat', unpack=True)

no = 11
test = 1

delay= np.array_split(data[0],no)
time = np.array_split(data[1],no)[0]/1e-6
X = np.array_split(data[2],no)
Y = np.array_split(data[3],no)
R = np.array_split(data[4],no)

plt.plot(X[test], label="X")
plt.plot(Y[test], label="Y")
plt.grid()
plt.legend()
plt.show()

for i in range(no):
	X_cal = X[i]-np.average(X[i][900:999])
	Y_cal = Y[i]-np.average(Y[i][900:999])
	steady_X= np.average(X_cal[520:560])
	steady_Y= np.average(Y_cal[520:560])
	rot = np.arctan2(steady_Y,steady_X)
	# print(rot)
	X[i] = X_cal*np.cos(rot) + Y_cal*np.sin(rot)
	X[i] = X[i]/np.average(X[i][520:560])
	Y[i] = -1*X_cal*np.sin(rot) + Y_cal*np.cos(rot)


plt.plot(X[15])
plt.plot(Y[15])
plt.show()

# plt.plot(X2[0]-X2[-1])
# plt.show()
# plt.imshow([((s-X2[-1])/(X2[0]-X2[-1])) for s in X2], aspect='auto' )
# plt.plot(Y[test], label="Y")
# plt.grid()
# plt.legend()
# plt.show()

# for x in X: 


# plt.plot((X[0][210:500]-X[-1][210:500]))
# plt.show()



# area = np.sum([s[240:400] for s in X],1)
delay = np.array([s[0]*4.4*1e-9 for s in delay])
# print(area[np.argmax(area)])
# plt.plot(delay/1e-6,area)
# plt.xlabel('Pulse length (us)')
# plt.ylabel('Area')
# plt.grid()


def tau_fit(left,right, plot=False):
	X2 = [s[left:right] for s in X]
	print len(X2[0])
	ground = X2[-1]
	exited = X2[0]

	Population = np.zeros(no-30)

	for i in range(no-30):
		for j in range(len(X2[0])):
			Population[i] = Population[i]+((1/float(len(X2[0])))*((X2[i][j]-ground[j])/(exited[j]-ground[j])))
	# return Population
	import lmfit as lm
	t = delay[:-30]
	ydata = Population# + np.random.uniform(low=-0.5,high=0.5, size=len(t))
	def expo(tau, norm):
		return norm*np.exp(-t/tau)

	def residual(params):
		p=[]
		for key,value in params.valuesdict().items():
			p.append(value)
		return expo(*p)-ydata

	lmfit_params = lm.Parameters()
	# lmfit_params.add('Frequency', value=0, min=-1, max=1)
	lmfit_params.add('Tau', value=3.6e-6)
	lmfit_params.add('Norm', value=0.9)
	# print lmfit_params
	mi = lm.minimize(residual,lmfit_params,method='leastsq')
	if plot:
		plt.plot(t, ydata, '.')
		plt.plot(t, mi.residual+ydata)
		plt.show()
	return Population, mi.residual+ydata, mi.params['Tau'].value, mi.params['Norm'].value
	
X = X[:-30]
fit_p = tau_fit(210,240,True)
print fit_p[-1], fit_p[-2]
pops = []
fits = []
taus = []
raw = open('raw.dat','w')
fitf = open('fit.dat','w')
for left in range(100, 250):
	pop, fit, tau, _ = tau_fit(left, 300)
	taus.append(tau)
	for popi, fiti in zip(pop, fit):
		raw.write('%f\n'%popi)
		fitf.write('%f\n'%fiti)
fitf.close()
raw.close()
taus = np.array(taus)
plt.plot(range(100,250),taus/1e-6)
plt.show()
	# pops.append(pop)
	# taus.append(tau)
	# for right in range(360, 700, 10):
	# 	taus[-1].append(tau_fit(left, right))
# plt.imshow(pops, aspect='auto', extent=(0, 22, 350, 240))
# plt.figure(2)
# plt.imshow(taus, aspect='auto', extent=(0, 22, 350, 240))
# plt.show()

# plt.title('Two tone spectroscopy ( Measurement power -75dBm at the cable)')
# plt.imshow(R, aspect='auto',extent=[time[0], time[-1], delay[-1][0], delay[0][0]], cmap = 'jet')
# plt.xlabel('Drive Frequency (GHz)')
# plt.ylabel('Drive Power(dBm)')
# plt.colorbar()
plt.show()