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


def predict_fm(vg):
    return int(1e6*(-3.057341113977019e-06*vg**2 + 1.0912028617869325e-06*vg + 6.5849223950571885))

znb = qt.instruments.create('ZNB20', 'RhodeSchwartz_ZNB20', address=ZNB20_ADDRESS, reset= True)
smf = qt.instruments.create('SMF100', 'RhodeSchwartz_SMF100', address = SMF100_ADDRESS, reset = True)
qs = qt.instruments.create('GS200', 'Yokogawa_GS200', address='USB0::0x0B21::0x0039::91T416206::INSTR')
qs2 = qt.instruments.create('GS200_3', 'Yokogawa_GS200', address='USB0::0x0B21::0x0039::91U620248::INSTR')
qsV = qt.instruments.create('GS200_2', 'Yokogawa_GS200', address='USB0::0x0B21::0x0039::91NA21403::INSTR')


target_value = -69.3 - 1.0
# ibias = 134.615*mA   # This is varied during the flux search


# wm = 6.583815*MHz #-19 Volt
#wm = 6.584205*MHz #-15 Volt
# wm=6.582210*MHz-70 #-30 Volt

#### SMF parameters
smf_freq = 5966*MHz
smf_power= 8


### VNA check cavity param

probe_center = smf_freq
probe_span = 80*MHz
probe_numpoints = 201
if_bw_0 = 100*Hz
probe_power = -12

# VNA CW mode
two_probe_numpoints = 1
two_if_bw_1 = 2*Hz

# VNA Mech mode

fm_center = 6.583815*MHz
fm_span = 200*Hz
fm_bw = 2*Hz
fm_numpoints = 201
fm_power = -10

#  Gate parameters
vg_start = -20
vg_stop = -16
vg_numpoints = 41


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

 # Prepare Gate
qsV.sweep_gate(vg_start)


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
    znb.set_source_power(probe_power)
    znb.set_numpoints(two_probe_numpoints)
    znb.set_center_frequency(probe_center)
    znb.set_if_bandwidth(two_if_bw_1)
    
def mechanical(fm_c):
    smf.rf_on()
    qt.msleep(0.1)
    znb.set_center_frequency(fm_c)
    znb.set_numpoints(fm_numpoints)
    znb.set_span(fm_span)
    znb.set_if_bandwidth(fm_bw)
    znb.set_source_power(fm_power)
    znb.rf_on()
    znb.send_trigger(wait = True)
    znb.autoscale()
    return znb.get_data('S21')

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
    data.add_coordinate('Vg', units='V')
    data.add_coordinate('Frequency', units='Hz')
    data.add_value('Amplitude', units = 'abs')
    data.add_value('Phase', units = 'radian')
    return data


in_meta = [fm_center -fm_span/2, fm_center + fm_span/2, fm_numpoints, 'Frequency (Hz)']
out_meta = [vg_stop, vg_start, vg_numpoints, 'Gate (V)']
once = True

vg_array = np.linspace(vg_start, vg_stop, vg_numpoints)

filename = raw_input('Filename : ')

data = data_file(filename)
value = 0
flag = True
mp = []
curr_array = []
fm_l = []
check_cavity()

for vv in vg_array:
    qsV.sweep_gate(vv)
    trace = []
    cw_setup()
    measure_peak = get_peak()
    if measure_peak > target_value:
        print('got a trace')
    else:
        it = qs.get_level()
        flux_adjust_finest(it)
    fm_c = predict_fm(vv)
    trace = mechanical(fm_c)
    vg_dummy = np.linspace(vv, vv, fm_numpoints)
    fm_array = np.linspace(fm_c-fm_span/2, fm_c+fm_span/2, fm_numpoints)
    data.add_data_point(vg_dummy, fm_array, np.abs(trace), np.angle(trace))
    mp = np.append(mp, measure_peak)
    measure_curr = qs.get_level()*1e3
    fm_l = np.append(fm_l, fm_c)
    curr_array = np.append(curr_array, measure_curr)
    print(str(measure_peak)+'  '+str(measure_curr) + '  '+ str(fm_c) )
    copy_script(flag)
    if flag == True:
        data.metagen2D(in_meta, out_meta)
    flag = False


file = open(data.get_filepath()[:-4]+'_peak_curr_list.dat', 'w+')
for index, val in enumerate(mp):
    file.write(str(val)+'\t'+str(curr_array[index])+'\t'+str(fm_l[index])+'\n')

file.close()
data.close_file()

smf.rf_off()
qs.sweep_current(0)
qs2.sweep_current(0)
qsV.sweep_gate(0)