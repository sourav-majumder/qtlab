# To be run in scripts folder

import numpy as np
import matplotlib.pyplot as plt

datadir = r'D:\data\20170609\162009_2port_copper_50ns'

datfilename = datadir.split('\\')[-1]
filestr = '%s\%s' % (datadir, datfilename)

timearr_full = np.load(filestr+'_timearr.npy')[:-15]
deconvx_res = np.load(filestr+'_deconvoluted_x.npy')[:,:-15]
deconvy_res = np.load(filestr+'_deconvoluted_y.npy')[:,15:]
deconvx_res = deconvx_res-np.average(deconvx_res[:,20:200])
deconvy_res = deconvy_res-np.average(deconvy_res[:,20:200])

freq_arr = np.load(filestr+'_freq_arr.npy')
freq_start = freq_arr[0]
freq_stop = freq_arr[-1]
del freq_arr

plt.plot(deconvx_res[500])
plt.plot(deconvy_res[500])
plt.show()

def IandQ(phi):
	I = np.cos(phi)*deconvx_res - np.sin(phi)*deconvy_res
	Q = np.sin(phi)*deconvx_res + np.cos(phi)*deconvy_res
	return I,Q

I,Q = IandQ(5.428)
# Iresarr = []
# Qresarr = []

# for phi in np.arange(0,2*np.pi, 0.01):
# 	I,Q = IandQ(phi)
# 	Iresarr.append(I)
# 	Qresarr.append(Q)
# 	del I,Q

np.save(filestr+'_corrected_I', I)
np.save(filestr+'_corrected_Q', Q)

# plt.subplot(211)
# plt.imshow(I, aspect='auto', extent=(timearr_full[0], timearr_full[-1], freq_start, freq_stop))
# plt.colorbar()
# plt.subplot(212)
# plt.imshow(Q, aspect='auto', extent=(timearr_full[0], timearr_full[-1], freq_start, freq_stop))
# plt.colorbar()
# plt.show()
# Iresarr = np.array(Iresarr)
# Qresarr = np.array(Qresarr)

# plt.subplot(211)
# plt.imshow(Iresarr, aspect='auto', extent=(timearr_full[0], timearr_full[-1], 0, 2*np.pi))
# plt.colorbar()
# plt.subplot(212)
# plt.imshow(Qresarr, aspect='auto', extent=(timearr_full[0], timearr_full[-1], 0, 2*np.pi))
# plt.colorbar()
# plt.show()