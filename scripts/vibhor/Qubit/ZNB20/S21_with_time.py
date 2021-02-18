import qt
import numpy as np
import shutil
import sys
import os
import time
from constants import *

## 
start_freq = 6.148908*GHz
stop_freq = 6.153908*GHz
power = -20
num_points=1001
if_bw = 10*kHz 


znb = qt.instruments.create('ZNB20', 'RhodeSchwartz_ZNB20', address='TCPIP0::192.168.1.3::INSTR')
znb.reset()
znb.add_trace('S21')
znb.set_start_frequency(start_freq)
znb.set_stop_frequency(stop_freq)
znb.set_source_power(power)
znb.set_sweep_mode('single')
znb.set_if_bandwidth(if_bw)
znb.set_numpoints(num_points)
znb.rf_on()

dataname='stability'
data=qt.Data(name=dataname)
data.add_coordinate('Time', units='s')
data.add_coordinate('frequency', units='Hz')
data.add_value('S21 abs')

start_t = 0
stop_t = 1000
t_points = 1001

t_list = np.linspace(start_t, stop_t, t_points)
freq_array = np.linspace(start_freq, stop_freq, num=num_points)

##########
# Take care of Meta

in_meta = [start_freq, stop_freq, num_points, 'Frequency (Hz)']
out_meta = [start_t, stop_t, t_points,'Time (min)']


for t in t_list:
    znb.send_trigger(wait=True)
    trace= znb.get_data('S21')
    znb.autoscale()
    t_array = np.linspace(t, t, num_points)
    data.add_data_point(t_array, freq_array, np.absolute(trace))
    # copy_script(once);once = False
    data.metagen2D(in_meta, out_meta)
    qt.msleep(60)

data.close_file()

