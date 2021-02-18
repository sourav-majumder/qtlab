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
qs = qt.instruments.create('GS200', 'Yokogawa_GS200', address='USB0::0x0B21::0x0039::91T416206::INSTR')


# How many traces
no_of_traces = 50
target_value = -76.9-1.5
# ibias = 134.615*mA   # This is varied during the flux search

## FSV parameters
center_frequency = 6025.*MHz
span = 200*Hz
RBW = 1*Hz
numpoints = 501
ref_level = -70 #dBm


#### SMF parameters
smf_freq = 6025*MHz - 6.583815*MHz
smf_power_start = -3.5
smf_power_stop = -6.5
smf_power_pts = 2

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
    znb.set_if_bandwidth(two_if_bw_1)
    
def thermal():
    znb.set_source_power(-60)
    znb.rf_off()


def get_peak():
    znb.send_trigger(wait=True)
    znb.autoscale()
    dummy = znb.get_data('S21')
    return 20*np.log10(np.abs(dummy[0]))

def flux_adjust_finest():
    ibias = qs.get_level()
    i_list = np.linspace(-3*uA, 3*uA, 7)
    ls = []
    print('Adjusting Finest ... ')
    for curr in i_list:
        qs.sweep_current(ibias + curr)
        val = get_peak()
        print(str(val) + '  '+ str((ibias + curr)*1e3))
        ls = np.append(ls, val)

    max_pos = np.max(ls)
    ib = ibias + i_list[np.argmax(ls)]
    if (max_pos > target_value):
        qs.sweep_current(ib)
    else:
        flux_adjust_finer(ib)

def flux_adjust_finer(ibias):
    print('Adjusting Finer ... ')
    i_list = np.linspace(-30*uA, 30*uA, 61)
    ls = []
    for curr in i_list:
        qs.sweep_current(ibias + curr)
        val = get_peak()
        print(str(val) + '  '+ str((ibias + curr)*1e3))
        ls = np.append(ls, val)

    max_pos = np.max(ls)
    ib = ibias + i_list[np.argmax(ls)]
    if (max_pos > target_value):
        qs.sweep_current(ib)
    else:
        flux_adjust_coarse(ib)

def flux_adjust_coarse(ibias):
    i_list = np.linspace(-250*uA, 250*uA, 501)
    ls = []
    print('Adjusting Coarse ... ')
    for curr in i_list:
        qs.sweep_current(ibias + curr)
        val = get_peak()
        print(str(val) + '  '+ str((ibias + curr)*1e3))
        ls = np.append(ls, val)

    max_pos = np.max(ls)
    ib = ibias + i_list[np.argmax(ls)]
    if (max_pos > target_value):
        qs.sweep_current(ib)
    else:
        manual_adjust()


def manual_adjust():
    znb.set_sweep_mode('cont')
    check_cavity()
    print('*******  ADJUST FLUX  ********')
    raw_input('then press enter to continue')
    znb.set_sweep_mode('single')



### SETTING UP DATA FILE
data_file_name = raw_input('Enter name of data file: ')
data=qt.Data(name=data_file_name)
data.add_coordinate('counter', units='nothing')
data.add_coordinate('Frequency', units='Hz')
data.add_value('PSD', units = 'dBm')
data.add_value('MP', units = 'dBm')
data.add_value('Bias current', units = 'mA')

incr = np.arange(no_of_traces)

in_meta = [center_frequency - span/2, center_frequency + span/2, numpoints, 'Frequency (Hz)']
out_meta = [no_of_traces, 1.0, no_of_traces,'Counter']
once = True

value = 0

check_cavity()

while value < no_of_traces:
    print(value)
    value_array = np.linspace(value, value, numpoints)
    thermal()
    fsv.run_single()
    trace= fsv.get_data()
    cw_setup()
    measure_peak = get_peak()
    measure_curr = qs.get_level()*1e3
    print(str(measure_peak)+'  '+str(measure_curr))
    if measure_peak > target_value:
        mp = np.linspace(measure_peak, measure_peak, numpoints)
        curr_array = np.linspace(measure_curr, measure_curr, numpoints)
        data.add_data_point(value_array, trace[0], trace[1], mp, curr_array)
        value = value + 1
    else:
        flux_adjust_finest()

    print('got a trace')
    if value == 1:
        copy_script(True)
        data.metagen2D(in_meta, out_meta)


data.close_file()
smf.rf_off()