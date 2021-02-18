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
znb = qt.instruments.create('ZNB20', 'RhodeSchwartz_ZNB20', address=ZNB20_ADDRESS, reset= True)
smf = qt.instruments.create('SMF100', 'RhodeSchwartz_SMF100', address = SMF100_ADDRESS)


target_value = -79.1-1
# How many traces
no_of_traces = 200



## FSV parameters
center_frequency = 6025.*MHz
span = 200*Hz
RBW = 1*Hz
numpoints = 501
ref_level = -70 #dBm


#### SMF parameters
smf_freq = 6025*MHz - 6.583815*MHz
smf_power = -0.5

#  VNA

probe_center = center_frequency
probe_span = 80*MHz
probe_numpoints = 201
if_bw_0 = 100*Hz
probe_power = 0

# two_probe_span = 2*Hz
two_probe_numpoints = 1
two_if_bw_1 = 2*Hz
two_probe_power = 0

# Prepare FSV
fsv.set_centerfrequency(center_frequency)
fsv.set_span(span)
fsv.set_bandwidth(RBW)
fsv.set_sweep_points(numpoints)
fsv.set_referencelevel(ref_level)

# Prepare SMF
smf.set_frequency(smf_freq)
smf.set_source_power(smf_power)
smf.rf_on()


# Setup VNA
znb.add_trace('S21')
znb.set_external_reference(True)
znb.set_source_power(probe_power)
znb.rf_on()
znb.set_sweep_mode('single')


def check_cavity():
    znb.set_source_power(probe_power)
    znb.set_center_frequency(probe_center)
    znb.set_numpoints(probe_numpoints)
    znb.set_span(probe_span)
    znb.set_if_bandwidth(if_bw_0)
    znb.send_trigger(wait=True)
    znb.autoscale()


def cw_setup():
    znb.rf_on()
    znb.set_source_power(two_probe_power)
    znb.set_numpoints(two_probe_numpoints)
    znb.set_center_frequency(probe_center)
    # znb.set_span(two_probe_span)
    znb.set_if_bandwidth(two_if_bw_1)
    znb.send_trigger(wait=True)
    znb.autoscale()
    dummy = znb.get_data('S21')
    return 20*np.log10(np.abs(dummy[0]))

def thermal():
    znb.set_source_power(-60)
    znb.rf_off()


### SETTING UP DATA FILE
data_file_name = raw_input('Enter name of data file: ')
data=qt.Data(name=data_file_name)
data.add_coordinate('counter', units='nothing')
data.add_coordinate('Frequency', units='Hz')
data.add_value('PSD', units = 'dBm')
data.add_value('MP', units = 'dBm')

incr = np.arange(no_of_traces)

in_meta = [center_frequency - span/2, center_frequency + span/2, numpoints, 'Frequency (Hz)']
out_meta = [no_of_traces, 1.0, no_of_traces,'Counter']
once = True

value = 0

check_cavity()

while 1<2:
    print(value)
    value_array = np.linspace(value, value, numpoints)
    thermal()
    fsv.run_single()
    trace= fsv.get_data()
    measure_peak = cw_setup()
    print(measure_peak)
    if measure_peak > target_value:
        mp = np.linspace(measure_peak, measure_peak, numpoints)
        data.add_data_point(value_array, trace[0], trace[1], mp)
        value = value + 1
    else:
        znb.set_sweep_mode('cont')
        check_cavity()
        print('*******  ADJUST FLUX  ********')
        raw_input('then press enter to continue')
        znb.set_sweep_mode('single')

    data.metagen2D(in_meta, out_meta)
    # progress_bar.update(idx+1)
    if value > no_of_traces:
        break
    else:
        print('got a trace')

    if value == 1:
        copy_script(True)


data.close_file()
smf.rf_off()