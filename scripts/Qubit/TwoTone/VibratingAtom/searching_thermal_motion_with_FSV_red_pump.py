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
smf = qt.instruments.create('SMF100', 'RhodeSchwartz_SMF100', address = SMF100_ADDRESS)

fsv.reset()
qt.msleep(3.0)
## FSV parameters
center_frequency = 5.9903*GHz
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

smf.rf_on()

freq = raw_input('enter search start (MHz):   ')
data=qt.Data(name=freq+'_MHz')
data.add_coordinate('counter', units='nothing')
data.add_coordinate('Frequency', units='Hz')
data.add_value('PSD_red', units = 'dBm')


wm_start = float(freq)*MHz
# wm_array = np.linspace(wm_start, wm_start, 1)
wm_array = np.linspace(wm_start, wm_start+0.5*MHz, 6)


in_meta = [center_frequency - span/2, center_frequency + span/2, numpoints, 'Frequency (Hz)']
out_meta = [wm_array[0], wm_array[-1], len(wm_array),'wm']
once = True

for val in wm_array:
	smf.set_frequency(center_frequency - val)
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
smf.rf_off()