import manfit.manfit as mf

import numpy as np
import matplotlib.pyplot as plt

data = np.loadtxt('D:/data/20180605/110628_t1/110628_t1.dat', unpack=True)

no = 21
test = 15

delay= np.array_split(data[0],no)
time = np.array_split(data[1],no)[0]/1e-6
X = np.array_split(data[2],no)
Y = np.array_split(data[3],no)
R = np.array_split(data[4],no)

for i in range(no):
	X_cal = X[i]-np.average(X[i][900:999])
	Y_cal = Y[i]-np.average(Y[i][900:999])
	steady_X= np.average(X_cal[525:560])
	steady_Y= np.average(Y_cal[525:560])
	rot = np.arctan2(steady_Y,steady_X)
	# print(rot)
	X[i] = X_cal*np.cos(rot) + Y_cal*np.sin(rot)
	X[i] = X[i]/np.average(X[i][525:560])
	Y[i] = -1*X_cal*np.sin(rot) + Y_cal*np.cos(rot)

# plt.plot(X[test], label="X")
# plt.plot(Y[test], label="Y")
# plt.grid()
# plt.legend()
# plt.show()

# write function with parameters as parameters
t = time[100:500]
ydata = X[10][100:500]
plt.plot(t,ydata)
plt.show()
def exp(t, t0, ts, tau1, tau2):
	result=[]
	for time in t:
		if time<t0:
			result.append(0)
		elif ts>time>t0:
			result.append(1-np.exp(-(time-t0)/tau1))
		else:
			result.append(np.exp(-(time-ts)/tau2))
	return np.array(result)

# Initialize Parameters
params = [mf.Parameter(0,20, name='t0'),
		  mf.Parameter(1,20, name='ts'),
		  mf.Parameter(1,20, name='tau1'),
		  mf.Parameter(1,20, name='tau2')]

# setup plot
figure, axes = plt.subplots(1,1,figsize=(6,4), dpi=96)
line1, = axes.plot(t,exp(t, *[param.val for param in params]))
line2, = axes.plot(t,ydata)

# start ManFit
# mf.manfit(figure, parameter_list, lines_to_update, xdata, ydata, fit_func)
mf.manfit(figure, params, {line1:exp}, t, ydata, exp)