import matplotlib.pyplot as plt
import numpy as np

_, freq, _, _, amp, _  = np.loadtxt(r'D:\data\20190401\113524_tcavityomitred(3-5MHz)\113524_tcavityomitred(3-5MHz).dat', unpack = True)

plt.plot(freq,20*np.log10(amp), '-ro', markersize =1)
plt.show()