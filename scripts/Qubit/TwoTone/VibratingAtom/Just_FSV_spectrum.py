import qt
import numpy as np
import os
import shutil
import sys
import progressbar
from constants import *

fsv = qt.instruments.create('FSV', 'RhodeSchwartz_FSV', address = FSV_ADDRESS)


## FSV parameters
center_frequency = 6018.416185*MHz
span = 2000*Hz
RBW = 10*Hz
numpoints = 501
ref_level = -70 #dBm

trs = 10

# Prepare FSV
fsv.set_centerfrequency(center_frequency)
fsv.set_span(span)
fsv.set_bandwidth(RBW)
fsv.set_sweep_points(numpoints)
fsv.set_referencelevel(ref_level)

### SETTING UP DATA FILE
data_file_name = raw_input('Enter name of data file: ')
data=qt.Data(name=data_file_name)
data.add_coordinate('counter', units=' ')
data.add_coordinate('Frequency', units='Hz')
data.add_value('PSD', units = 'dBm')


in_meta = [center_frequency - span/2, center_frequency + span/2, numpoints, 'Frequency (Hz)']
out_meta = [1, 0, trs,'Counter']

for i in np.arange(trs):
	fsv.run_single()
	trace= fsv.get_data()
	dummy = np.linspace(i, i, numpoints)
	data.add_data_point(dummy, trace[0], trace[1])

data.metagen2D(in_meta, out_meta)
data.close_file()

