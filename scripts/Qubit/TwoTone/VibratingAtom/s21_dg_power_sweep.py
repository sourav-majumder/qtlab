from constants import *
import sys
import os
import shutil
import qt
import progressbar
import numpy as np
import time
import visa


rm = visa.ResourceManager()
##############################################

us = 1e-6

##############################################
#smf = qt.instruments.create('SMF100', 'RhodeSchwartz_SMF100', address = SMF100_ADDRESS)
#rig = qt.instruments.create('DP832A', 'Rigol_DP832A', address='TCPIP0::192.168.1.5::INSTR')
znb = qt.instruments.create('ZNB20', 'RhodeSchwartz_ZNB20', address='TCPIP0::192.168.1.3::INSTR')
dg = rm.open_resource('USB0::0x1AB1::0x0642::DG1ZA194405642::INSTR')

##############################################

def generate_meta_file(outer_index,outer_value, outermost_index,outermost_value):
    metafile = open('%s.meta.txt' % data.get_filepath()[:-4], 'w')
    metafile.write('#inner loop\n%s\n%s\n%s\n%s\n'%
            (len_innerloop,  inner_start/us, inner_stop/us, inner_meta_info))
    metafile.write('#outer loop\n%s\n%s\n%s\n%s\n'%
            (outer_index, outer_value, outerloop[0], outer_meta_info))
    metafile.write('#outermost loop\n%s\n%s\n%s\n%s\n'%
            (outermost_index, outermostloop[0], outermost_value, outermost_meta_info))

    metafile.write('#for each of the values\n')
    values = data.get_values()
    i=0
    while i<len(values):
        metafile.write('%d\n%s\n'% (i+4, values[i]['name']))
        i+=1
    metafile.close()
##################################################
def copy_script():
    shutil.copy2('%s'%sys.argv[0],'%s/%s'%(data.get_filepath()[:-(len(data_file_name)+11)],os.path.basename(sys.argv[0])))

##################################################

data_file_name = raw_input('Enter name of data file: ')

data=qt.Data(name=data_file_name)
data.add_coordinate('DG Power', units = 'Volt')
data.add_coordinate('VNA freq', units = 'Hz')

data.add_value('S21 Real')
data.add_value('S21 Imag')
data.add_value('S21 Absolute')

# OuterMost loop 
outermost_meta_info = "Nothing" 
outermost_start = 0
outermost_stop  = 1  # One more than the end point you 
outermost_len  =  1




# SMF frequency = 5801.6 MHz
# SMF Power = 6 dBm

# See logbook for detailed setup

#Outerloop
outer_meta_info = "DG Power"
outer_start = 5.0 #Volt
outer_stop  = 1.0 #Volt
outer_resolution = 0.2 #volt
outer_len = int(abs(outer_stop - outer_start)/outer_resolution + 1)
DG_drive_freq= 6.5838245*MHz

# Inner most loop
inner_meta_info = "VNA` freq" 
inner_start = 5.98832*GHz
inner_stop = 6.02837*GHz #center + span/2.
inner_resolution = 0.2*MHz
len_innerloop = int(abs(inner_stop - inner_start)/inner_resolution + 1)
innerloop = np.linspace(inner_start,inner_stop,len_innerloop)
### Other drive variables:
if_bw = 10
vna_power = -36


#####################
outermostloop = np.linspace(outermost_start,outermost_stop,outermost_len) 
outerloop = np.linspace(outer_start,outer_stop,outer_len) 
len_outermostloop=len(outermostloop) 
len_outerloop=len(outerloop) 
data_info=["X","Y","R"] 

####### Preparing instruments

## DG READY
dg.write(':SOUR1:VOLT %f'%outer_start) 
dg.write(':SOUR1:FREQ %f'%DG_drive_freq)
dg.write(':OUTP1:LOAD 50')
dg.write(':OUTP1 ON')
qt.msleep(1)

znb.reset()
#znb.set_external_reference(True)
znb.set_start_frequency(inner_start)
znb.set_stop_frequency(inner_stop)
znb.set_source_power(vna_power)
znb.set_numpoints(len_innerloop)
znb.set_if_bandwidth(if_bw)
znb.set_sweep_mode('single')

znb.rf_on()
znb.add_trace('S21')
#smf.rf_on()

qt.mstart()

first_time = True

###########################################
delay_progress_bar = progressbar.ProgressBar(maxval=outer_len, \
    widgets=['Total: ', progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage(), ' (', progressbar.ETA(), ') '])
delay_progress_bar.start()
#outermost_value_array = np.linspace(outermost_value, outermost_value, record_length)
#########################################################################################################



for outer_index, outer_value in enumerate(outerloop):
    # sweep_gate(outer_value)
    dg.write(':SOUR1:VOLT %f'%outer_value)
    qt.msleep(0.25)
    outer_value_array = np.linspace(outer_value,outer_value,len_innerloop)
    znb.send_trigger(wait=True)
    trace= znb.get_data('S21')
    znb.autoscale()
    data.add_data_point(outer_value_array, innerloop, np.real(trace),np.imag(trace),np.absolute(trace))
    if first_time:
        generate_meta_file(outer_len, outer_stop, outermost_len,outermost_stop)
        copy_script()
    first_time = False
    delay_progress_bar.update(outer_index+1)

delay_progress_bar.finish()
data.close_file()
dg.write(':OUTP1 OFF')
#rig.all_outputs_off()
#smf.rf_off()
#znb.rf_off()
#execfile('hook.py')
