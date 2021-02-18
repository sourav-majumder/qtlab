# Example running ManFit
import manfit as mf

import numpy as np
import matplotlib.pyplot as plt

# write function with parameters as parameters
t = np.linspace(0,5,100)
ydata = np.exp(-t/3)*np.sin(2*np.pi*0.7*t) + np.random.uniform(low=-0.5,high=0.5, size=len(t))
def sine(t, freq, tau):
	return np.exp(-t/tau)*np.sin(2*np.pi*freq*t)

def cosine(t, freq, phi):
	return np.cos(2*np.pi*freq*t + phi)

# Initialize Parameters
params = [mf.Parameter(-1,1, name='Frequency'),
		  mf.Parameter(0.1,3, name='Tau')]

# setup plot
figure, axes = plt.subplots(1,1,figsize=(6,4), dpi=96)
line1, = axes.plot(t,sine(t, *[param.val for param in params]))
line2, = axes.plot(t,ydata)

# start ManFit
# mf.manfit(figure, parameter_list, lines_to_update, xdata, ydata, fit_func)
mf.manfit(figure, params, {line1:sine}, t, ydata, sine)