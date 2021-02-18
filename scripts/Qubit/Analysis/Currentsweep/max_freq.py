import numpy as np
import matplotlib.pyplot as plt
from matplotlib.pyplot import gca
import matplotlib as mb


def resonance_fit(n,curr,freq,absol):
	fc=[]
	I=[]
	l = len(freq)

	for i in range(1,n):
		x=np.argmax(absol[i-1])
		fc=np.append(fc,freq[x])
		I=np.append(I,1e3*curr[i-1][0])
	return fc,I


path = r'D:\data\20190827\214400_current_sweep_around_0mA'

data_name = path+path[16:]+r'.dat'
data = np.loadtxt(data_name, unpack=True)

n = 51

curr = np.array_split(data[0],n)
freq = np.array_split(data[1],n)[0]*1e-9
absol = np.array_split(data[2],n)

fc,I= resonance_fit(n,curr,freq,absol)

I=I-0.2



plt.plot(I,fc)
plt.show()

fit= np.poly1d(np.polyfit(I,fc,7))
I_new = np.linspace(I[0], I[-1], 1001)
fit_new = fit(I_new)

deriv = np.diff(fit_new)/np.diff(I_new)

print(len(deriv))
print(len(I_new))
Id = I_new[:-1]

plt.plot(I,fc,'-r',I,fit(I),'b')
plt.xlabel('mA')
plt.ylabel('GHz')
plt.grid()

plt.show()

f= open(path+"\\out_0.txt","w+")

for i in np.arange(1001):
	f.write(str(I_new[i])+'\t'+str(fit_new[i])+'\n')


f.close()