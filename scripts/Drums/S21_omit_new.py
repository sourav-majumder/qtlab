import qt
import numpy as np
import shutil
import sys
import os
import time
import progressbar
from constants import *


def copy_script(once):
  if once:
    shutil.copy2('%s'%sys.argv[0],'%s/%s'%(data.get_filepath()[:-(len(data.get_filename())+1)],os.path.basename(sys.argv[0])))

## 
center = 3.583144*GHz
span = 50*kHz

start_freq = center - span/2.0 # 6.148908*GHz
stop_freq = center + span/2.0 # 6.153908*GHz
power = -40 #with -20db attenuation
num_points=501
if_bw = 300
 
# pump
pump_start = center - 17*MHz
pump_stop = center - 29*MHz
pump_points = 481
pump_power = 14


znb = qt.instruments.create('ZNB20', 'RhodeSchwartz_ZNB20', address='TCPIP0::192.168.1.3::INSTR')
smf = qt.instruments.create('SMF100', 'RhodeSchwartz_SMF100', address = 'TCPIP0::192.168.1.4::INSTR', reset=False)
rigol = qt.instruments.create('DP832A', 'Rigol_DP832A', address='TCPIP0::192.168.1.5::INSTR')
# rigol.output_on(1)



znb.reset()
znb.add_trace('S21')
znb.set_external_reference(True)
znb.set_start_frequency(start_freq)
znb.set_stop_frequency(stop_freq)
znb.set_source_power(power)
znb.set_sweep_mode('single')
znb.set_if_bandwidth(if_bw)
znb.set_numpoints(num_points)
znb.rf_on()

qt.mstart()

data_file_name = raw_input('Enter name of data file: ')
data=qt.Data(name=data_file_name)
data.add_coordinate('pump', units='Hz')
data.add_coordinate('frequency', units='Hz')
data.add_value('S21 abs')
# data.add_value('S21 phase')


pump_list = np.linspace(pump_start, pump_stop, pump_points)
freq_array = np.linspace(start_freq, stop_freq, num=num_points)

##########
# Take care of Meta

in_meta = [start_freq, stop_freq, num_points, 'Probe (Hz)']
out_meta = [pump_start, pump_stop, pump_points,'Pump (Hz)']

once = True
smf.rf_on()
smf.set_source_power(pump_power)


progress_bar = progressbar.ProgressBar(maxval=len(pump_list), \
        widgets=['Progress: ', progressbar.Bar('.', '', ''), ' ', progressbar.Percentage(), ' (', progressbar.ETA(), ') '])
progress_bar.start()

for index, pump in enumerate(pump_list):
    smf.set_frequency(pump)
    znb.send_trigger(wait=True)
    trace= znb.get_data('S21')
    znb.autoscale()
    pump_array = np.linspace(pump, pump, num_points)
    data.add_data_point(pump_array, freq_array, np.absolute(trace))
    data.metagen2D(in_meta, out_meta)
    progress_bar.update(index+1)

    copy_script(once); once = False
    # qt.msleep(60)
progress_bar.finish()


data.close_file()
smf.rf_off()
znb.rf_off()
rigol.output_off(2)

