import numpy as np
import matplotlib.pyplot as plt

i = np.linspace(0,50,501)

def fr(i,f0, i0):
	return f0*np.sqrt(np.abs(np.cos(np.pi*i/i0)))

fq = 6.7;
f_jpa = 6.5;

i_q = 2.2;
i_j = 8.7;


fq_list = fr(i,fq,i_q)
jpa_list = fr(i, f_jpa, i_j)
fc_list = 6.011*np.ones(501)

plt.plot(i,fq_list,'-r',i,jpa_list,'-g')
plt.plot(i, fc_list,'-c')
plt.ylim(5.5,6.5)
plt.show()