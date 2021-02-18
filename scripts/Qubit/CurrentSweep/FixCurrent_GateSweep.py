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


########## USER INPUTS FOR SETTING THE MEASUREMENT ##########

# center =2.25*GHz
# span= 2000*MHz
num_points = 201
power = -12 #0dBm attenuation#Low frequency
if_bw = 50

current = 135e-3 + 195e-3


voltage_start = -30 #in Volt
voltage_stop = +30 #in Volt
voltage_point = 301
#############################################################

start_freq = 5.940425*GHz#center-span/2
stop_freq = 5.940425*GHz + 60*MHz #center+span/2

# SMF 6.0378GHz  # 7 dBm  # driving at Wc

#create the instrument
znb = qt.instruments.create('ZNB20', 'RhodeSchwartz_ZNB20', address='TCPIP0::192.168.1.3::INSTR')
# qs = qt.instruments.create('GS200', 'Yokogawa_GS200', address='USB0::0x0B21::0x0039::91T416206::INSTR')
qsV = qt.instruments.create('GS200_2', 'Yokogawa_GS200', address='USB0::0x0B21::0x0039::91NA21403::INSTR')

# rigol = qt.instruments.create('DP832A', 'Rigol_DP832A', address='TCPIP0::192.168.1.5::INSTR')
# smf = qt.instruments.create('SMF100', 'RhodeSchwartz_SMF100', address = SMF100_ADDRESS)


znb.reset()
znb.set_external_reference(True)
# znb.set_default_channel_config()
znb.add_trace('S21')
znb.set_start_frequency(start_freq)
znb.set_stop_frequency(stop_freq)
znb.set_source_power(power)
znb.set_numpoints(num_points)
znb.set_if_bandwidth(if_bw)
znb.set_sweep_mode('single')


### SETTING UP DATA FILE
data_file_name = raw_input('Enter name of data file: ')

data=qt.Data(name=data_file_name)
data.add_coordinate('Gate', units='V')
data.add_coordinate('Frequency', units='Hz')
data.add_value('S21 real')
data.add_value('S21 imag')
data.add_value('S21 abs')
data.add_value('S21 phase')


volt_list = np.linspace(voltage_start, voltage_stop, voltage_point)
freq_array = np.linspace(start_freq, stop_freq, num=num_points)

##########
# Take care of Meta

in_meta = [start_freq, stop_freq, num_points, 'Frequency (Hz)']
out_meta = [voltage_stop, voltage_start, voltage_point,'Gate (V)']

qt.mstart()
znb.rf_on()
# qs.set_output(True)
qsV.sweep_gate(voltage_start, delay = 0.05)
# rigol.output_on(2)
once = True

progress_bar = progressbar.ProgressBar(maxval=len(volt_list), \
        widgets=['Progress: ', progressbar.Bar('.', '', ''), ' ', progressbar.Percentage(), ' (', progressbar.ETA(), ') '])
progress_bar.start()


for idx, volt in enumerate(volt_list):
    qsV.sweep_gate(volt, delay = 0.05)
    # print(idx)
    qt.msleep(0.1)
    znb.send_trigger(wait=True)
    trace= znb.get_data('S21')
    znb.autoscale()
    volt_array = np.linspace(volt, volt, num_points)
    data.add_data_point(volt_array, freq_array, np.real(trace),np.imag(trace), np.abs(trace),np.angle(trace))
    copy_script(once);once = False
    data.metagen2D(in_meta, out_meta)
    progress_bar.update(idx+1)

data.close_file()
# qs.sweep_current(0)
# qs.set_output(False)
progress_bar.finish()
qsV.sweep_gate(0.0, delay = 0.05)
# znb.rf_off()
# rigol.output_off(2)
