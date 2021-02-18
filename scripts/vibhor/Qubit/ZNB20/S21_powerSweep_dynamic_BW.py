import qt
import numpy as np
import os
import shutil
import sys
from constants import *

def copy_script(once):
	if once:
		shutil.copy2('%s'%sys.argv[0],'%s/%s'%(data.get_filepath()[:-(len(filename)+11)],os.path.basename(sys.argv[0])))



def bandwidth(power):
    if power<=-50 and power>=-60:
        return 20
    elif power<=-40 and power>-50:
        return 30
    elif power<=-30 and power>-40:
        return 50
    elif power<=-20 and power>-30:
        return 100
    elif power<=-10 and power>-20:
        return 300
    elif power<=0 and power>-10:
        return 1*kHz
    elif power<=10 and power>0:
        return 3*kHz


########## USER INPUTS FOR SETTING THE MEASUREMENT ##########

center =6.16575*GHz
span= 20*MHz
num_points = 601
start_power = -10 #dBm
stop_power = -50 #dBm
power_points = 21
if_bw= 150
filename='pw_sweep'

start_freq=center-span/2
stop_freq=center+span/2

#############################################################

#create the instrument
znb = qt.instruments.create('ZNB20', 'RhodeSchwartz_ZNB20', address='TCPIP0::192.168.1.3::INSTR')

znb.reset()
#znb.set_default_channel_config()
znb.set_start_frequency(start_freq)
znb.set_stop_frequency(stop_freq)
znb.set_source_power(start_power)
znb.set_numpoints(num_points)
znb.set_if_bandwidth(if_bw)
znb.set_sweep_mode('single')

### SETTING UP DATA FILE
data=qt.Data(name=filename)
data.add_coordinate('Power', units='dBm')
data.add_coordinate('Frequency', units='Hz')
#data.add_value('S21 real')
#data.add_value('S21 imag')
data.add_value('S21 abs')
# data.add_value('S21 phase')


## WE should also add copy of script to the data folder

power_list = np.linspace(start_power, stop_power, power_points)
freq_array = np.linspace(start_freq, stop_freq, num=num_points)

##########
# Take care of Meta

in_meta = [start_freq, stop_freq, num_points, 'Frequency (Hz)']
out_meta = [start_power, stop_power, power_points,'Power (dBm)']


qt.mstart()


znb.rf_on()
znb.add_trace('S21')
znb.set_source_power(-60)
znb.set_if_bandwidth(if_bw)

once = True

for pw in power_list:
    znb.set_source_power(pw)
    znb.set_if_bandwidth(bandwidth(pw))
    qt.msleep(0.1)
    znb.send_trigger(wait=True)
    trace= znb.get_data('S21')
    znb.autoscale()
    pw_array = np.linspace(pw, pw, num=num_points)
    data.add_data_point(pw_array, freq_array, np.absolute(trace))

    copy_script(once);once = False
    data.metagen2D(in_meta, out_meta)


data.close_file()
