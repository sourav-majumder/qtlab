# import scipy.signal as sig
import scipy as sp
import numpy as np

# tc = 30e-9
# caviy_tc = 10e-9
# n=1
# wc = 1/tc
fac = sp.math.factorial

# def filter_func(tc, order, t):
# 	wc=1/float(tc)
# 	return (wc*t)**(order-1)/fac(order-1)*wc*np.exp(-wc*t)

# filt = filter_func(tc, 7, np.arange(tc,20*tc, 0.1*tc))
# print filt
# # signal = np.repeat([0.,1.,0.], 10*len(filt))
# t = np.linspace(0,30e-9, 10*len(filt))
# rise_arr = 1-np.exp(-t/caviy_tc)
# fall_arr = rise_arr[-1]*np.exp(-t/caviy_tc)
# signal = np.concatenate((np.zeros(len(filt)), rise_arr, np.repeat(rise_arr[-1], 10*len(filt)), fall_arr, np.repeat(fall_arr[-1], 2*len(filt))))
# filt = filt/filt.max()
# print filt.min()

# convoluted = np.convolve(signal,filt,mode='same')
# deconv,  _ = sig.deconvolve( convoluted, filt )
# # #the deconvolution has n = len(signal) - len(gauss) + 1 points
# # n = len(signal)-len(filt)+1
# # # so we need to expand it by 
# # s = (len(signal)-n)/2
# # #on both sides.
# # deconv_res = np.zeros(len(signal))
# # deconv_res[s:len(signal)-s-1] = deconv
# # deconv = deconv_res
# # # now deconv contains the deconvolution 
# # # expanded to the original shape (filled with zeros)

def filter_func(tc, order, t):
		wc=1/float(tc)
		return (wc*t)**(order-1)/fac(order-1)*wc*np.exp(-wc*t)

def deconvolve(data, tc, order):
	'''
	Returns deconvoluted data.
	'''
	t = data[0] # time values
	y = data[1] # recorded signal

	time = t[-1]-t[0]
	resolution = t[1]-t[0]

	if time <= 0:
		raise UHFLIException('Time must run forwards.')
	elif time < 10*tc:
		raise UHFLIException('Data must be longer than 10 time constants of the filter.')
	else:
		filt = filter_func(tc, order, np.arange(0, 10*tc, resolution))
		if filt.min() < 0e-5:
			raise UHFLIException('Filter error.')
		from scipy.signal import deconvolve
		return deconvolve(y,filt)

# d = np.loadtxt(r'D:\data\20170612\130605_2port_30ns_isolator\130605_2port_30ns_isolator.dat').swapaxes(0,1)