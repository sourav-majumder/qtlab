import numpy as np
from lmfit import Model
import matplotlib.pyplot as plt


#######################################################
path1 = r'D:\data\20191011\233510_pw_sweep_at_70mk_-30dc'

data_name1 = path1+path1[16:]+r'.dat'

data1 = np.loadtxt(data_name1, unpack=True,skiprows= 26)

n1=16
power1 = np.split(data1[0],n1)
freq1 = np.split(data1[1],n1)
absol1 = np.split(data1[4],n1)

pow_arr = np.linspace(-10,5,n1)

#######################################################
freq_max=[]
#pow_arr = []
#######################################################

#######################################################


def inv(f, f0, base, amp, k):
	return base + amp*np.abs(1./(1j*(f-f0)*(2./k) - 1. ) )

m = Model(inv)

k_list = []
f0_list = []

for i in np.arange(n1):
	fguess = freq1[i][np.argmax(absol1[i])]
	kguess = 6.1e6
	base_guess=np.min(absol1[i])
	print(i)
	data2fit = absol1[i]
	f2fit = freq1[i]
	result = m.fit(data2fit, f= f2fit, f0 = fguess, k = kguess, base = base_guess,amp=0.00015)
	plt.plot(f2fit, data2fit,'-ro', f2fit, result.best_fit, '-g')
	plt.title(str(power1[i][0]))
    
	plt.savefig(r'D:\data\20191010\214846_pw_sweep_at_-30dc\figs\%f.png'%i, transparent = True)
	plt.clf()
   #plt.tight_layout()
	k_list = np.append(k_list, result.best_values['k'])
	f0_list = np.append(f0_list, result.best_values['f0'])



#######################################################
pow_mw=10.**(pow_arr/10)
# print(pow_arr)
plt.plot(pow_arr-8, k_list,'-ro')
plt.grid()
plt.ylabel('K (Hz)')
plt.xlabel('Eq_SMF_Power(dBm)')
plt.title('75mk and -30volt DC bias')
# plt.colorbar()
plt.show()

# f=open(r'D:\data\20191011\233510_pw_sweep_at_70mk_-30dc\k_vs_f_list.dat','w+')
 
# for idx, val in enumerate(k_list):
#     f.write(str(pow_arr[idx])+'\t'+str(val)+'\n')


# f.close()
