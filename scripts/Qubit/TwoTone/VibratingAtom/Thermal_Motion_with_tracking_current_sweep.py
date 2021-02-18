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


fsv = qt.instruments.create('FSV', 'RhodeSchwartz_FSV', address = FSV_ADDRESS, reset= True)
znb = qt.instruments.create('ZNB20', 'RhodeSchwartz_ZNB20', address=ZNB20_ADDRESS, reset= True)
smf = qt.instruments.create('SMF100', 'RhodeSchwartz_SMF100', address = SMF100_ADDRESS)
qs = qt.instruments.create('GS200', 'Yokogawa_GS200', address='USB0::0x0B21::0x0039::91T416206::INSTR')


# How many traces
no_of_traces = 200
target_value = -75.8 - 1.0
# ibias = 134.615*mA   # This is varied during the flux search

#current sweep
start_curr=30*mA
stop_curr=180*mA
curr_points=5
fixed_curr=0*mA
curr_list=np.linspace(start_curr,stop_curr,curr_points)

## FSV parameters
center_frequency = 6025.*MHz
span = 200*Hz
RBW = 2*Hz
numpoints = 401
ref_level = -70 #dBm

# wm = 6.583815*MHz #-19 Volt
#wm = 6.584205*MHz #-15 Volt
wm=6.582210*MHz #-30 Volt

#### SMF parameters
smf_freq = 6025*MHz
smf_power_start = -10
smf_power_stop = -10
smf_power_pts = 1
repeat = 1
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
smf.set_source_power(smf_power_start)
smf.rf_on()


# Setup VNA
znb.add_trace('S21')
znb.set_external_reference(True)
znb.set_source_power(probe_power)
znb.rf_on()
znb.set_sweep_mode('single')


def check_cavity():
    smf.rf_off()
    znb.set_source_power(probe_power)
    znb.set_center_frequency(probe_center)
    znb.set_numpoints(probe_numpoints)
    znb.set_span(probe_span)
    znb.set_if_bandwidth(if_bw_0)
    znb.send_trigger(wait=True)
    znb.autoscale()


def cw_setup():
    smf.rf_off()
    znb.rf_on()
    znb.set_source_power(two_probe_power)
    znb.set_numpoints(two_probe_numpoints)
    znb.set_center_frequency(probe_center)
    znb.set_if_bandwidth(two_if_bw_1)
    
def thermal():
    smf.rf_on()
    qt.msleep(0.1)
    znb.set_source_power(-60)
    znb.rf_off()

def get_peak():
    znb.send_trigger(wait=True)
    znb.autoscale()
    dummy = znb.get_data('S21')
    return 20*np.log10(np.abs(dummy[0]))

def flux_adjust_finest(ibias):
    # ibias = qs.get_level()
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
        print('*locked*')
        qs.sweep_current(ib)
    else:
        flux_adjust_finer(ib)

def flux_adjust_finer(ibias):
    print('Adjusting Finer ... ')
    i_list = np.linspace(-30*uA, 30*uA, 16)
    ls = []
    for curr in i_list:
        qs.sweep_current(ibias + curr)
        val = get_peak()
        print(str(val) + '  '+ str((ibias + curr)*1e3))
        ls = np.append(ls, val)

    max_pos = np.max(ls)
    ib = ibias + i_list[np.argmax(ls)]
    if (max_pos > target_value - 3.0):
        qs.sweep_current(ib)
        flux_adjust_finest(ib)
    else:
        flux_adjust_coarse(ib)


def flux_adjust_coarse(ibias):
    i_list = np.linspace(-500*uA, 500*uA, 101)
    ls = []
    print('Adjusting Coarse ... ')
    for curr in i_list:
        qs.sweep_current(ibias + curr)
        val = get_peak()
        print(str(val) + '  '+ str((ibias + curr)*1e3))
        ls = np.append(ls, val)

    max_pos = np.max(ls)
    ib = ibias + i_list[np.argmax(ls)]
    if (max_pos > target_value - 10):
        qs.sweep_current(ib)
        flux_adjust_finer(ib)

    else:
        manual_adjust()


def manual_adjust():
    znb.set_sweep_mode('cont')
    check_cavity()
    print('*******  ADJUST FLUX  ********')
    raw_input('then press enter to continue')
    znb.set_sweep_mode('single')



def data_file(pw):
    data=qt.Data(name=str(pw) +str( amp+fixed_curr)+'curr(mA)'+'test')
    data.add_coordinate('counter', units='nothing')
    data.add_coordinate('Frequency', units='Hz')
    data.add_value('PSD_red', units = 'dBm')
    data.add_value('PSD_blue', units = 'dBm')
    return data



incr = np.arange(no_of_traces)

in_meta = [center_frequency - span/2, center_frequency + span/2, numpoints, 'Frequency (Hz)']
out_meta = [no_of_traces, 1.0, no_of_traces,'Counter']
once = True

smf_power_array = np.linspace(smf_power_start, smf_power_stop, smf_power_pts)

pw_list = []
for pw in smf_power_array:
    pw_list = np.append(pw_list, np.linspace(pw, pw, repeat))
for amp in curr_list:
    qs.sweep_current(amp)
    for pw in pw_list:
        smf.set_source_power(pw)
        data = data_file(pw)
        value = 0
        mp = []
        curr_array = []
        check_cavity()

        while value < no_of_traces:
            print(value)
            value_array = np.linspace(value, value, numpoints)
            thermal()
            fsv.set_centerfrequency(smf_freq - wm)
            qt.msleep(1.0)
            fsv.run_single()
            trace1= fsv.get_data()
            fsv.set_centerfrequency(smf_freq + wm)
            qt.msleep(1.0)
            fsv.run_single()
            trace2= fsv.get_data()
            cw_setup()
            measure_peak = get_peak()
            measure_curr = qs.get_level()*1e3
            print(str(measure_peak)+'  '+str(measure_curr))
            mp = np.append(mp, measure_peak)
            curr_array = np.append(curr_array, measure_curr)
            if measure_peak > target_value:
                data.add_data_point(value_array, smf_freq - trace1[0], trace1[1], trace2[1])
                value = value + 1
            else:
                it = qs.get_level()
                flux_adjust_finest(it)

            print('got a trace')
            if value == 1:
                copy_script(True)
                data.metagen2D(in_meta, out_meta)

        file = open(data.get_filepath()[:-4]+'_peak_curr_list.dat', 'w+')
        for index, val in enumerate(mp):
            file.write(str(val)+'\t'+str(curr_array[index])+'\n')

        file.close()
        data.close_file()


smf.rf_off()