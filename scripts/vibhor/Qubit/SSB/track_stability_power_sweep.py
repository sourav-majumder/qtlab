import numpy as np
import progressbar
from constants import *

fsv = qt.instruments.create('FSV', 'RhodeSchwartz_FSV', address = FSV_ADDRESS)
sgs = qt.instruments.create('sgs', 'RS_SGS100A', address = SGS100A_ADDRESS)

pw_list = np.linspace(-10,-60,51)

for pw in pw_list:
	sgs.set_power(pw)
	qt.msleep(5)
	f = open(r'D:\data\20200118\sgs_tracking_dc_blockr_pw_sweep.txt', 'a+')
	ls = fsv.get_max_freqs(3)
	print(pw, ls[1][0],ls[1][1],ls[1][2])
	f.write('%f\t%f\t%f\t%f\n'%(pw, ls[1][0], ls[1][1], ls[1][2]))
	f.close()




