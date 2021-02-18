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



path = r'D:\data\20190827\135554_current_sweep_around_70mA'

data_name = path+path[16:]+r'.dat'
data = np.loadtxt(data_name, unpack=True)

n = 51

curr = np.array_split(data[0],n)
freq = np.array_split(data[1],n)[0]*1e-9
absol = np.array_split(data[2],n)

fc,I= resonance_fit(n,curr,freq,absol)
# fc=fc[] 
I=I-69.6

plt.plot(I,fc)
plt.show()

fit= np.poly1d(np.polyfit(I,fc,7))
I_new = np.linspace(I[0], I[-1], 1001)
fit_new = fit(I_new)
deriv = np.diff(fit_new)/np.diff(I_new)
print(len(deriv))
print(len(I_new))
Id = I_new[:-1]







path = r'D:\data\20190827\144827_current_sweep_around_135mA_again'

data_name = path+path[16:]+r'.dat'
data = np.loadtxt(data_name, unpack=True)

n = 51

curr = np.array_split(data[0],n)
freq = np.array_split(data[1],n)[0]*1e-9
absol = np.array_split(data[2],n)

fc_1,I_1= resonance_fit(n,curr,freq,absol)


fit_1= np.poly1d(np.polyfit(I_1,fc_1,7))
I_new_1 = np.linspace(I_1[0], I_1[-1], 1101)
I_new_1=I_new_1[0;1000]
fit_new_1= fit(I_new_1)
deriv_1 = np.diff(fit_new_1)/np.diff(I_new_1)
print(len(deriv_1))
print(len(I_new))
Id_1= I_new_1[:-1]



f=plt.figure(figsize=(4,6))

f1=f.add_subplot(2,1,1)
plt.plot(I,fc,)


# f = plt.figure(figsize = (4,6))

# f1 = f.add_subplot(3,1,1)
# plt.plot(I,fc,'-r',I,fit(I),'b')
# plt.xlabel('mA')
# plt.ylabel('GHz')
# plt.grid()


# f2 = f.add_subplot(3,1,2)

# plt.plot(Id, deriv, 'r')
# plt.xlabel('mA')
# plt.ylabel('GHz/mA')


# f2 = f.add_subplot(3,1,3)

# plt.plot(fit(Id), deriv, 'r')
# plt.xlabel('GHz')
# plt.ylabel('GHz/mA')
# plt.grid()




# plt.tight_layout(True)
# plt.show()

# plt.plot(fc_1,d)
# plt.show()


# Use this part of the code when their is another peak(might be of qubit) whose hight is more than Cavity

# freq=freq[136:300]
# l=len(freq)
# print(l)
# absol_1=np.zeros(shape=(151,164))
# for i in range(1,n):
# 	a=absol[i-1]
# 	absol_1[i-1]=a[136:300]
