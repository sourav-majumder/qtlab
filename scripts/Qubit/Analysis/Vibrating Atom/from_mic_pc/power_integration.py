import numpy as np
import matplotlib.pyplot as plt
from lmfit import Model
from glob import glob




path  = r'D:\data\20191009\205618_-12.5repeat3'
path1 = glob(path+'\*red*')


# wm = 6.583815*1e6
wm = 6.584205*1e6

freq1, psd1 = np.loadtxt(path1[0], unpack = True)


cen1=np.argmax(psd1)

bl1 =(np.mean(psd1[:cen1-50])+np.mean(psd1[cen1+50:]))/2


area1=np.sum(psd1[cen1-50:cen1+50]-bl1)


# area1 = np.sum(pd - baseline)
# area2 = np.sum(p - baseline) * 200./501
	
area_nor1=area1*(200/501)

plt.plot(freq1 - wm, psd1, '-r')
plt.xlabel('freq')
plt.ylabel('psd (fW)')
plt.grid()
plt.title('A = '+str(area_nor1))
plt.tight_layout()
plt.show()
