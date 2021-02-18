import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.colors import LogNorm
from scipy.constants import hbar
from matplotlib import cm

cons_w = 2*3.14*6.84e9
cons_ke = 2*3.14*1.5e6
cons_k = 2*3.14*2.8e6
cons_delta = 0

def Plin(p):
	return 10.**(p/10.-3.)

def photons(power):
	return Plin(power)/(hbar*cons_w)*(cons_ke/((cons_k/2)**2+cons_delta**2))




path = r'D:\data\20200130\155116_high_power_meas_pulse_len_sweep'

data_name = path+path[16:]+r'.dat'

data = np.loadtxt(data_name, unpack=True)
n=41
length = np.array_split(data[0],n)
X = np.array(np.array_split(data[3],n))[:,:]
Y = np.array(np.array_split(data[4],n))[:,:]

for i in range(n)[::4]:
	plt.plot(Y[i], X[i], label= r'{} $\mu m$'.format(length[i][0]))

plt.legend()
plt.show()


# # xedges = np.linspace(-0.7,0.1,100)
# # yedges = np.linspace(-0.02,0.15,100)
# # H, xedges, yedges = np.histogram2d(X,Y,bins= 100, range = [[-0.7,0.1],[-0.02,0.15]])
# # H = H.T
# pow_list = np.array([-1,0,1])

# def plot_func():
# 	fig = plt.figure(figsize=(12, 5)) 
	
# 	no = 1000
# 	# X = np.array_split(data[0],no)
# 	# Y = np.array_split(data[1],no)
	
# 	# X = np.loadtxt("D:\\data\\20190805\\X%soncable.txt"%power, skiprows = 5)
# 	# Y = np.loadtxt("D:\\data\\20190805\\Y%soncable.txt"%power, skiprows = 5)
# 	# R = np.zeros((len(X),len(X[0])))
# 	prob = np.zeros(len(X[0]))
# 	print(len(prob))
# 	for i in range(len(X)):
# 		for j in range(len(X[0])):
# 			R[i][j] = np.sqrt(X[i][j]**2 + Y[i][j]**2)
# 			if R[i][j] >= 0.09:
# 				prob[j] = prob[j] + 1
# 		# plt.plot(np.array(range(len(X[0])))/32.0,R[i])
# 	plt.plot(np.array(range(len(X[0])))/33.0, prob)
# 	plt.xlabel(r'$\mu s$')
# 	# plt.ylabel('Voltage(V)')
# 	plt.ylabel('Counts')
# 	# plt.ylim([-0.05,0.72])
	
# 	# plt.imshow(R,aspect = 'auto',extent=[0, 10, 0, 1000])
# 	# plt.plot(np.array(range(len(X[0]))),X[0],'o-')
# 	# plt.xlabel(r'$\mu s$')
# 	# plt.ylabel('counts')
# 	# plt.plot(R)
	
	
# 	plt.hexbin(X,Y, gridsize=1000, bins = 'log', cmap = plt.cm.BuGn_r)#, vmax = 100, vmin = 0, alpha = 0.5, cmap = 'Blues')
# 	# plt.plot(X, Y, '.')
# 	plt.xlabel('X-quadrature (V)')
# 	plt.ylabel('Y-quadrature (V)')
# 	plt.tight_layout()
# 	plt.xlim([min(X), max(X)])
# 	plt.ylim([min(Y), max(Y)])

# for k in range(len(pow_list)):
# 	plot_func(pow_list[k])
# plt.show()