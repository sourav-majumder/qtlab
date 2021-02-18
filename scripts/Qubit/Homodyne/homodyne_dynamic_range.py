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


# def predict_fm(vg):
#     return int(1e6*(-3.057341113977019e-06*vg**2 + 1.0912028617869325e-06*vg + 6.5849223950571885))

znb = qt.instruments.create('ZNB20', 'RhodeSchwartz_ZNB20', address=ZNB20_ADDRESS, reset= True)
smf = qt.instruments.create('SMF100', 'RhodeSchwartz_SMF100', address = SMF100_ADDRESS, reset = True)
qs = qt.instruments.create('GS200', 'Yokogawa_GS200', address='USB0::0x0B21::0x0039::91T416206::INSTR')
# qs2 = qt.instruments.create('GS200_3', 'Yokogawa_GS200', address='USB0::0x0B21::0x0039::91U620248::INSTR')
# qsV = qt.instruments.create('GS200_2', 'Yokogawa_GS200', address='USB0::0x0B21::0x0039::91NA21403::INSTR')
fsv = qt.instruments.create('FSV', 'RhodeSchwartz_FSV', address = FSV_ADDRESS, reset = True)

path = r'D:\data\20191104\190209_thermal_peak_detection100avg'

target_value = -89 - 1.0
# ibias = 134.615*mA   # This is varied during the flux search


# wm = 6.583815*MHz #-19 Volt
#wm = 6.584205*MHz #-15 Volt
# wm=6.582210*MHz-70 #-30 Volt

#### SMF parameters
smf_freq = 6025*MHz
smf_power= 7


### VNA check cavity param

probe_center = smf_freq
probe_span = 30*MHz
probe_numpoints = 201
if_bw_0 = 10*Hz
probe_power = -5
# VNA CW mode
two_probe_numpoints = 1
two_if_bw_1 = 2*Hz


center_frequency = 6025*MHz


avg = 100
RBW = 2*Hz
numpoints = 5001
ref_level = -57 #dBm

start_offset = 6.00*MHz
stop_offset = 7.03*MHz
resolution = 10*kHz
offset_points = int(abs(stop_offset - start_offset)/resolution + 1)

# Prepare SMF
smf.set_frequency(smf_freq)
smf.set_source_power(smf_power)
smf.rf_on()


# Setup VNA
znb.add_trace('S21')
znb.set_external_reference(True)
znb.set_source_power(probe_power)
#znb.rf_on()

znb.set_sweep_mode('single')


def fsv_setup():
    fsv.set_centerfrequency(center_frequency)
    fsv.set_span(resolution)
    fsv.set_bandwidth(RBW)
    fsv.set_sweep_points(numpoints)
    fsv.set_referencelevel(ref_level)
    fsv.set_sweep_mode_avg()
    fsv.set_sweep_count(avg)

def check_cavity():
    smf.rf_off()
    znb.rf_on()
    znb.set_source_power(probe_power)
    znb.set_center_frequency(probe_center)
    znb.set_numpoints(probe_numpoints)
    znb.set_span(probe_span)
    znb.set_if_bandwidth(if_bw_0)
    znb.send_trigger(wait=True)
    znb.autoscale()
    znb.rf_off()

def cw_setup():
    smf.rf_off()
    znb.rf_on()
    znb.set_source_power(probe_power)
    znb.set_numpoints(two_probe_numpoints)
    znb.set_center_frequency(probe_center)
    znb.set_if_bandwidth(two_if_bw_1)
    znb.rf_off()

def get_peak():
    znb.rf_on()
    znb.send_trigger(wait=True)
    znb.autoscale()
    dummy = znb.get_data('S21')
    znb.rf_off()
    return 20*np.log10(np.abs(dummy[0]))

def flux_adjust_finest(ibias):
    # ibias = qs.get_level()
    i_list = np.linspace(-3*21*uA, 3*21*uA, 7)
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
    i_list = np.linspace(-30*16*uA, 30*16*uA, 16)
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
    i_list = np.linspace(-500*20*uA, 500*20*uA, 101)
    ls = []
    print('Adjusting Coarse ... ')
    for curr in i_list:
        qs.sweep_current(ibias + curr)
        val = get_peak()
        print(str(val) + '  '+ str((ibias + curr)*1e3))
        ls = np.append(ls, val)

    max_pos = np.max(ls)
    ib = ibias + i_list[np.argmax(ls)]
    if (max_pos > target_value - 13):
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
    data.add_coordinate('offset', units='Hz')
    data.add_value('frequency', units = 'Hz')
    data.add_value('PSD')
    return data



value = 0
flag = True
mp = []
curr_array = []
fm_l = []
check_cavity()
fsv_setup()
filename = raw_input('Filename : ')

data = data_file(filename)

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
    cw_setup()
    measure_peak = get_peak()
    if measure_peak > target_value:
        print('got a trace')
    else:
        it = qs.get_level()
        flux_adjust_finest(it)
    fsv.set_centerfrequency(center_frequency + offs)
    smf.rf_on()
    fsv.run_single()
    qt.msleep(100)
    trace = fsv.get_data()
    offs_array = np.linspace(offs, offs, numpoints)
    data.add_data_point(offs_array, trace[0]-center_frequency, trace[1])
    copy_script(once);once = False
    data.metagen2D(in_meta, out_meta)
    progress_bar.update(idx+1)


file.close()
data.close_file()

smf.rf_off()
qs.sweep_current(0)
