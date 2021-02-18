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


fsv = qt.instruments.create('FSV', 'RhodeSchwartz_FSV', address = FSV_ADDRESS, reset = True)


center_frequency = 7.417630*GHz


avg = 500
RBW = 10*Hz
numpoints = 10001
ref_level = -40 #dBm

start_offset = 3*MHz
stop_offset = 7*MHz
resolution = 0.1*MHz
offset_points = int(abs(stop_offset - start_offset)/resolution + 1)


### SETTING UP DATA FILE
data_file_name = raw_input('Enter name of data file: ')
data=qt.Data(name=data_file_name)
data.add_coordinate('offset', units='Hz')
data.add_value('Frequency', units='Hz')
data.add_value('PSD')



fsv.set_centerfrequency(center_frequency)
fsv.set_span(resolution)
fsv.set_bandwidth(RBW)
fsv.set_sweep_points(numpoints)
fsv.set_referencelevel(ref_level)
fsv.set_sweep_mode_avg()
fsv.set_sweep_count(avg)



offset_list = np.linspace(start_offset, stop_offset, offset_points)


in_meta = [0, resolution, numpoints, 'Frequency (Hz)']
out_meta = [stop_offset, start_offset, offset_points,'offset (Hz)']

once = True

progress_bar = progressbar.ProgressBar(maxval=len(offset_list), \
        widgets=['Progress: ', progressbar.Bar('.', '', ''), ' ', progressbar.Percentage(), ' (', progressbar.ETA(), ') '])
progress_bar.start()


for idx, offs in enumerate(offset_list):
    # qs.sweep_current(offs, delay = 0.05)
    # print(idx)
    fsv.set_centerfrequency(center_frequency + offs)
    fsv.run_single()
    trace= fsv.get_data()
    offs_array = np.linspace(offs, offs, numpoints)
    data.add_data_point(offs_array, trace[0]-center_frequency, trace[1]) #,np.angle(trace))
    copy_script(once);once = False
    data.metagen2D(in_meta, out_meta)
    progress_bar.update(idx+1)

data.close_file()
progress_bar.finish()
