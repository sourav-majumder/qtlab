import matplotlib.pyplot as plt
import numpy as np
from scipy.constants import hbar

def nd(omega_c, P_in, kappa, delta=None, omega=None, eta=None, kappa_e=None):
	# try:
	# 	if delta is None:
	# 		delta = omega-omega_c
	# 	elif omega is None:
	# 		delta = 0
	# 	if eta is None:
	# 		eta = 0.5
	# 	elif kappa_e is None:
	# 		kappa_e = eta*kappa
	# except ValueError:
	# 	print 'Provide either delta or omega, and eta or kappa_e'
	P = 1e-3*10**(P_in/10.)
	return P*eta*kappa**2/(hbar*2*np.pi*(omega_c+delta)*((kappa/2.)**2+(delta)**2))

def pow(omega_c, nd, kappa, delta=None, omega=None, eta=None, kappa_e=None):
	P = nd/(eta*kappa**2/(hbar*2*np.pi*(omega_c+delta)*((kappa/2.)**2+(delta)**2)))
	return 10*np.log10(P/1e-3)

kappas = [100e3, 1e6, 10e6]
nds = [1]
delta = 10**np.linspace(4, np.log10(3e9), 1000)
fig,ax1 = plt.subplots()
# ax2 = ax1.twinx()
# ax2.plot([nd(6e9, -200, 100e3, delta=0, eta=0.5), nd(6e9, -10, 100e3, delta=0, eta=0.5)], color='#00000000')
# ax2.set_yscale('log')
for ndt in nds:
	for kappa in kappas:
		yvals=pow(6e9, ndt, kappa, delta=delta, eta=0.5)
		ax1.plot(delta/1e6, yvals , label=r'$\kappa = %.1f$ MHz, n_d = %d'%(kappa/1e6, ndt))
# plt.yscale('log')
ax1.set_xscale('log')
ax1.set_xlabel(r'$\Delta$ (MHz)')
ax1.set_ylabel(r'$P_in$ (dBm)')
plt.title(r'$\eta=0.5, f_c=6 GHz$')
ax1.grid()
ax1.legend()

plt.show()