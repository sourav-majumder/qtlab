from numpy.polynomial.polynomial import polyfit, polyval
import matplotlib.pyplot as plt
import numpy as np

def population(data, ground, saturated=None, excited=None):
	if saturated is not None:
		pop = 0.0
		for j in range(len(data)):
			pop += ((data[j]-ground[j])/(2*(saturated[j]-ground[j])))
		pop /= float(len(data))
		return pop

	if excited is not None:
		pop = 0.0
		for j in range(len(data)):
			pop += ((data[j]-ground[j])/(excited[j]-ground[j]))
		pop /= float(len(data))
		return pop

def full_pop(t, X, left, right, ground, saturated=None, excited=None, order=12):
	if saturated is not None:
		saturated = saturated[left:right]
		pop = np.zeros(len(X))
		t = t[left:right]
		for i,x in enumerate(X):
			x = x[left:right]
			# x = pfit(t, x[left:right], order=order)
			pop[i] = population(x, ground[left:right], saturated=saturated)
		return pop

	if excited is not None:
		excited = excited[left:right]
		pop = np.zeros(len(X))
		t = t[left:right]
		for i,x in enumerate(X):
			x = x[left:right]
			# x = pfit(t, x[left:right], order=order)
			pop[i] = population(x, ground[left:right], excited=excited)
		return pop

def pfit(t, data, order=12):
	return polyval(t, polyfit(t, data, order))

def rotate(X, Y, zeros = (900,999), steady = (520,570)):
	for i in range(len(X)):
		X_cal = X[i]-np.average(X[i][zeros[0]:zeros[1]])
		Y_cal = Y[i]-np.average(Y[i][zeros[0]:zeros[1]])
		steady_X= np.average(X_cal[steady[0]:steady[1]])
		steady_Y= np.average(Y_cal[steady[0]:steady[1]])
		rot = np.arctan2(steady_Y,steady_X)
		# print(rot)
		X[i] = X_cal*np.cos(rot) + Y_cal*np.sin(rot)
		X[i] = X[i]/np.average(X[i][steady[0]:steady[1]])
		Y[i] = -1*X_cal*np.sin(rot) + Y_cal*np.cos(rot)

	return X, Y