import numpy as np
import matplotlib.pyplot as plt
from helpers import *
import lmfit as lm
from lmfit import Model

path = r'D:\data\20190902\154301_t1_mechanical_test'
# print path+path[16:]+r'.dat'
data = np.loadtxt(path+path[16:]+r'.dat', unpack=True)

n=21

wm_drive= np.array_split(data[0],n)
time = np.array_split(data[1],n)[0]/1e-3
X = np.array_split(data[2],n)
Y = np.array_split(data[3],n)
R = np.array_split(data[4],n)

t= time-time[0]
print(t[-1])
t=t[150:-60]
R1=R[12][150:-60]

def expo(t,tau, norm):
	return norm*np.exp(-t/(2*tau))

m=Model(expo)
norm_guess=max(R1)
result=m.fit(R1,t=t,tau=t[250],norm=1)

print(result.best_values['tau'])
plt.plot(t,R1,'-ro',t,result.best_fit,'g')
plt.xlabel('Time(ms)')
plt.ylabel('Output signal(V)')
plt.show()

