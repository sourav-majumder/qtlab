from __future__ import print_function

import qt
import shutil
import sys
import os
import time

from constants import *

def copy_script(once):
  if once:
    shutil.copy2('%s'%sys.argv[0],'%s/%s'%(data.get_filepath()[:-(len(data.get_filename())+1)],os.path.basename(sys.argv[0])))


#############################
# Measurement Parameters
#############################
# VNA sweep parameters
probe_center = 7.414*GHz
probe_span = 1*Hz
probe_start_freq = probe_center-probe_span/2
probe_stop_freq = probe_center+probe_span/2
probe_numpoints = 1
if_bw = 5*Hz
probe_power = -30 #dBm 26dB attenuation at VNA
s_params = ['S21']
filename = raw_input('Filename : ')
avg_point = 1

# APSYN sweep parameters  TOTAL Att ~ 23 - 40 -3 - 20 (till blue cable input)
drive_start_freq = 4.694*GHz
drive_stop_freq = 4.7*GHz
resolution = 0.1*MHz
drive_numpoints = int(abs(drive_stop_freq - drive_start_freq)/resolution + 1)

# Sideband Pump using SMF 
sideband_start_freq = 4.69062*GHz - 6*MHz
sideband_stop_freq = 4.69062*GHz - 3*MHz
sideband_resolution =  3*MHz
sideband_freq_numpoint = int(abs(sideband_stop_freq - sideband_start_freq)/sideband_resolution + 1) - 1
sideband_power = 0

#############################
# Initialize Instruments
#############################
znb = qt.instruments.create('ZNB20', 'RhodeSchwartz_ZNB20', address=ZNB20_ADDRESS, reset=True)
smf = qt.instruments.create('SMF100', 'RhodeSchwartz_SMF100', address = SMF100_ADDRESS, reset=True)
aps = qt.instruments.create('APSYN420',   'AnaPico_APSYN420', address = APSYN420_ADDRESS)

# setup SMF100 as source
smf.set_frequency(sideband_start_freq)
smf.set_source_power(sideband_power)

# Setup VNA as source
znb.set_external_reference(True)
znb.set_external_reference_frequency(10)
znb.set_source_power(probe_power)
znb.set_start_frequency(probe_start_freq)
znb.set_stop_frequency(probe_stop_freq)
znb.set_numpoints(probe_numpoints)
znb.set_if_bandwidth(if_bw)
znb.add_trace('S21')

# Turn on sources
# smf.rf_on()
znb.rf_on()
aps.rf_on()
# Test trigger
znb.send_trigger(wait=True)
znb.autoscale()
go_on = raw_input('Continue? [y/n] ')

assert go_on.strip().upper() != 'N'


### SETTING UP DATA FILE
data=qt.Data(name=filename)
# data.add_comment('No. of repeated measurements for average is 60')
data.add_coordinate('Pump Freq', units='Hz')
data.add_coordinate('Spec Freq', units='Hz')
data.add_value('S21 real')
data.add_value('S21 imag')
data.add_value('S21 abs')
data.add_value('S21 phase')

drive_freq_array = np.linspace(drive_start_freq, drive_stop_freq, drive_numpoints)
sideband_freq_array = np.linspace(sideband_start_freq, sideband_stop_freq, sideband_freq_numpoint)

in_meta = [drive_start_freq, drive_stop_freq, drive_numpoints, 'Pump Freq (Hz)']
out_meta = [sideband_start_freq, sideband_stop_freq, sideband_freq_numpoint,'Spec Freq (Hz)']

qt.mstart()
once = True

for side_freq in sideband_freq_array:
    start_time = time.time()
    smf.set_frequency(side_freq)
    smf_list = np.linspace(side_freq, side_freq, num=drive_numpoints)
    traces=[[],[],[],[]]
    for index, drive_freq in enumerate(drive_freq_array):
        print('%d/%d'%(index+1,len(drive_freq_array)), end='\r')
        traces_sum=[0,0,0,0]
        aps.set_frequency(drive_freq)
        for i in range(avg_point):
            znb.send_trigger(wait=True)
            trace = znb.get_data('S21')
            traces_sum[0]+=np.real(trace)
            traces_sum[1]+=np.imag(trace)
            traces_sum[2]+=np.absolute(trace)
            traces_sum[3]+=np.angle(trace)    
        traces[0].append(traces_sum[0][0]/avg_point)
        traces[1].append(traces_sum[1][0]/avg_point)
        traces[2].append(traces_sum[2][0]/avg_point)
        traces[3].append(traces_sum[3][0]/avg_point)
    end_time = time.time()
    data.add_data_point(smf_list, drive_freq_array, traces[0], traces[1], traces[2], traces[3])
    copy_script(once);once = False
    data.metagen2D(in_meta, out_meta)
    copy_script(once);once = False
    print(end_time - start_time)

data.close_file()
znb.rf_off()
aps.rf_off()
smf.rf_off()

