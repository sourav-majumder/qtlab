from __future__ import print_function

import qt
import numpy as np
import os
import shutil
import sys
import progressbar
from constants import *
import visa

################################
rm = visa.ResourceManager()
################################


def copy_script(once):
  if once:
    shutil.copy2('%s'%sys.argv[0],'%s/%s'%(data.get_filepath()[:-(len(data.get_filename())+1)],os.path.basename(sys.argv[0])))

znb = qt.instruments.create('ZNB20', 'RhodeSchwartz_ZNB20', address=ZNB20_ADDRESS, reset= True)
smf = qt.instruments.create('SMF100', 'RhodeSchwartz_SMF100', address = SMF100_ADDRESS)
qs = qt.instruments.create('GS200', 'Yokogawa_GS200', address='USB0::0x0B21::0x0039::91T416206::INSTR')
dg = rm.open_resource('USB0::0x1AB1::0x0642::DG1ZA194405642::INSTR')

# How many traces
target_value = -64.6 - 1
# ibias = 134.615*mA   # This is varied during the flux search


# wm = 6.583815*MHz #-19 Volt
#wm = 6.584205*MHz #-15 Volt

wm=6.582210*MHz #-30 Volt


# DG sweep parameters
DG_drive_start_freq = wm - 25*Hz
DG_drive_stop_freq = wm + 35*Hz
DG_resolution = 0.4*Hz
DG_drive_numpoints = int(abs(DG_drive_stop_freq - DG_drive_start_freq)/DG_resolution + 1)
DG_drive_power =  1.0 #Volt

# SMF sweep parameters
drive_start_freq = 6.85*GHz
drive_stop_freq = 7.15*GHz
resolution = 1*MHz
drive_numpoints = int(abs(drive_stop_freq - drive_start_freq)/resolution + 1)
drive_power = -5

# VNA sweep parameters
probe_center = 5.9857*GHz
probe_numpoints = 1
if_bw = 5*Hz
probe_power = -5
s_params = ['S21']
filename = raw_input('Filename : ')
avg_point = 1

probe_numpoints_2 = 201
span_2 = 80*MHz
if_bw_2 = 100*Hz

## DG READY
dg.write(':ROSC:SOUR EXT')
dg.write(':SOUR1:FREQ %f'%DG_drive_start_freq)
dg.write(':SOUR1:VOLT %f'%DG_drive_power)
dg.write(':OUTP1:LOAD 50')
dg.write(':OUTP1 ON')
qt.msleep(1)



# Prepare SMF
smf.set_frequency(drive_start_freq)
smf.set_source_power(drive_power)
smf.rf_on()


# Setup VNA as source
znb.add_trace('S21')
znb.set_external_reference(True)
znb.set_external_reference_frequency(10)
znb.set_numpoints(probe_numpoints)
znb.set_center_frequency(probe_center)
znb.set_if_bandwidth(if_bw)
znb.set_source_power(probe_power)
znb.rf_on()
znb.send_trigger(wait=True)


def check_cavity():
    smf.rf_off()
    dg.write(':OUTP1 OFF')
    znb.set_source_power(probe_power)
    znb.set_center_frequency(probe_center)
    znb.set_numpoints(probe_numpoints_2)
    znb.set_span(span_2)  
    znb.set_if_bandwidth(if_bw_2)
    znb.send_trigger(wait=True)
    znb.autoscale()


def cw_setup():
    smf.rf_off()
    dg.write(':OUTP1 OFF')
    znb.set_source_power(probe_power)
    znb.set_center_frequency(probe_center)
    znb.set_numpoints(1)
    znb.set_if_bandwidth(if_bw)
    
def thermal():
    smf.rf_on()
    dg.write(':OUTP1 ON')
    qt.msleep(1)

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



def data_file(filename):
    data=qt.Data(name=filename)
    data.add_coordinate('DG Freq', units='Hz')
    data.add_coordinate('Drive Frequency', units='Hz')
    data.add_value('S21 real')
    data.add_value('S21 imag')
    data.add_value('S21 abs')
    data.add_value('S21 phase')
    return data



def two_tone_loop(drive_freq_array):
    traces=[[],[],[],[]]
    for index, drive_freq in enumerate(drive_freq_array):
        print('%d/%d'%(index+1,len(drive_freq_array)), end='\r')
        traces_sum=[0,0,0,0]
        smf.set_frequency(drive_freq)
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
    return traces



in_meta = [drive_start_freq, drive_stop_freq, drive_numpoints, 'Drive Frequency (Hz)']
out_meta = [DG_drive_start_freq, DG_drive_stop_freq, DG_drive_numpoints,'DG Freq (Hz)']

DG_freq_array = np.linspace(DG_drive_start_freq, DG_drive_stop_freq, DG_drive_numpoints)
drive_freq_array = np.linspace(drive_start_freq, drive_stop_freq, drive_numpoints)

mp = []
curr_array = []
flag = True
data = data_file(filename)


for fr in DG_freq_array:
    dg.write(':SOUR1:FREQ %f'%fr)
    qt.msleep(0.25)    
    cw_setup()
    measure_peak = get_peak()
    if measure_peak > target_value:
        thermal()
        trace1= two_tone_loop(drive_freq_array)
        fr_array = np.linspace(fr, fr, drive_numpoints)
        data.add_data_point(fr_array, drive_freq_array, trace1[0], trace1[1], trace1[2], trace1[3])
        mp = np.append(mp, measure_peak)
        measure_curr = qs.get_level()*1e3
        curr_array = np.append(curr_array, measure_curr)
        print(str(measure_peak)+'  '+str(measure_curr))
        print('got a trace')
        copy_script(flag)
        if flag == True:
            data.metagen2D(in_meta, out_meta)
        flag = False
    else:
        it = qs.get_level()
        flux_adjust_finest(it)



file = open(data.get_filepath()[:-4]+'_peak_curr_list.dat', 'w+')

for index, val in enumerate(mp):
    file.write(str(val)+'\t'+str(curr_array[index])+'\n')

file.close()
data.close_file()
smf.rf_off()
dg.write(':OUTP1 OFF')
qs.sweep_current(0)
