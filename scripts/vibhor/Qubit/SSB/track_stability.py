import numpy as np
import progressbar
from constants import *

fsv = qt.instruments.create('FSV', 'RhodeSchwartz_FSV', address = FSV_ADDRESS)
f = open(r'D:\data\20210125\sg396_tracking1.txt', 'w+')

for i in np.arange(3000):
	ls = fsv.get_max_freqs(3)
	print(i, ls[1][0],ls[1][1],ls[1][2])
	f.write('%f\t%f\t%f\t%f\n'%(i, ls[1][0], ls[1][1], ls[1][2]))
	qt.msleep(30)


f.close()




