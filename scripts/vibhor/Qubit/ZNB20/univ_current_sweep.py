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
num_points = 601
power = -34 #dBm
if_bw= 10

start_current = 0e-3
stop_current = 3e-3
current_points = 76

#############################################################

start_freq= 7.157*GHz#center-span/2
stop_freq=  7.757*GHz#center+span/2

IF = 77*MHz


#create the instrument
znb = qt.instruments.create('ZNB20', 'RhodeSchwartz_ZNB20', address='TCPIP0::192.168.1.3::INSTR')
qs = qt.instruments.create('GS200', 'Yokogawa_GS200', address='USB0::0x0B21::0x0039::91T416206::INSTR')
uhf = ZurichInstruments_UHFLI('dev2232')
smf = qt.instruments.create('SMF100', 'RhodeSchwartz_SMF100', address = SMF100_ADDRESS)



# znb.reset()
# znb.set_default_channel_config()
# znb.add_trace('S21')

def get_trace(flist):
    tr = []
    for f in flist:
        smf.set_frequency(f)
        znb.LO_mode_frequency(f+IF)
        



znb.set_start_frequency(start_freq)
znb.set_stop_frequency(stop_freq)
znb.set_source_power(power)
znb.set_numpoints(num_points)
znb.set_if_bandwidth(if_bw)
znb.set_sweep_mode('single')



### SETTING UP DATA FILE
data_file_name = raw_input('Enter name of data file: ')

data=qt.Data(name=data_file_name)
data.add_coordinate('Current', units='A')
data.add_coordinate('Frequency', units='Hz')
data.add_value('S21 abs')
data.add_value('S21 phase')


curr_list = np.linspace(start_current, stop_current, current_points)
freq_array = np.linspace(start_freq, stop_freq, num=num_points)

##########
# Take care of Meta

in_meta = [start_freq, stop_freq, num_points, 'Frequency (Hz)']
out_meta = [stop_current, start_current, current_points,'Current (mA)']

qt.mstart()


znb.LO_mode()
qs.set_output(True)
smf.rf_on()
once = True

progress_bar = progressbar.ProgressBar(maxval=len(curr_list), \
        widgets=['Progress: ', progressbar.Bar('.', '', ''), ' ', progressbar.Percentage(), ' (', progressbar.ETA(), ') '])
progress_bar.start()



for idx, curr in enumerate(curr_list):
    qs.sweep_current(curr, delay = 0.05)
    # print(idx)
    qt.msleep(0.1)

    znb.send_trigger(wait=True)
    trace= get_trace(freq_array)
    znb.autoscale()
    


    curr_array = np.linspace(curr, curr, num_points)
    data.add_data_point(curr_array, freq_array, np.absolute(trace),np.angle(trace))
    copy_script(once);once = False
    data.metagen2D(in_meta, out_meta)
    progress_bar.update(idx+1)

data.close_file()
qs.sweep_current(0)
qs.set_output(False)
progress_bar.finish()
