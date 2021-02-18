import qt
import numpy as np
import os
import shutil
import sys
import progressbar
from constants import *

def copy_script(once):
  if once:
    shutil.copy2('%s'%sys.argv[0],'%s/%s'%(data.get_filepath()[:-(len(data.get_filename())+1)],os.path.basename(sys.argv[0])))


fsv = qt.instruments.create('FSV', 'RhodeSchwartz_FSV', address = FSV_ADDRESS)

fsv.reset()
qt.msleep(3.0)
## FSV parameters
center_frequency = 5.993242*GHz
span = 100*kHz
RBW = 5*Hz
numpoints = 32001
ref_level = -50 #dBm

# Prepare FSV
fsv.set_centerfrequency(center_frequency)
fsv.set_span(span)
fsv.set_referencelevel(ref_level)
fsv.set_bandwidth(RBW)
fsv.set_sweep_points(numpoints)

fsv.set_sweep_mode_avg()
fsv.set_sweep_count(100)



freq = raw_input('enter search start (MHz):   ')
data=qt.Data(name=freq+'_MHz')
data.add_coordinate('counter', units='nothing')
data.add_coordinate('Frequency', units='Hz')
data.add_value('PSD_red', units = 'dBm')


wm_start = float(freq)*MHz
# wm_array = np.linspace(wm_start, wm_start, 1)
wm_array = np.linspace(wm_start, wm_start+0.5*MHz, 6)
# wm_array = [10.1528*MHz,10.5221*MHz,10.749*MHz,11.6151*MHz,11.4535*MHz,12.0626*MHz,11.9523*MHz,12.7207*MHz,12.8869*MHz]


in_meta = [center_frequency - span/2, center_frequency + span/2, numpoints, 'Frequency (Hz)']
out_meta = [wm_start, wm_start+1*MHz, 11,'wm']
once = True

for val in wm_array:
	fsv.set_centerfrequency(center_frequency - val)
	print('setting : ', round(val/MHz, ndigits=4))
	val_array = np.linspace(val, val, numpoints)
	qt.msleep(2.0)
	fsv.run_single()
	qt.msleep(39.0)
	trace = fsv.get_data()
	data.add_data_point(val_array, trace[0], trace[1])
	if once:
		copy_script(once)
		data.metagen2D(in_meta, out_meta)
	once = False

data.close_file()