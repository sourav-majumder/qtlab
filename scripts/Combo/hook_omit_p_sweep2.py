from constants import *
import sys
import os
import shutil
import qt
import progressbar
import numpy as np
import time

##############################################

us = 1e-6

##############################################
rig = qt.instruments.create('DP832A', 'Rigol_DP832A', address='TCPIP0::192.168.1.5::INSTR')
smf = qt.instruments.create('SMF100', 'RhodeSchwartz_SMF100', address = SMF100_ADDRESS)
znb = qt.instruments.create('ZNB20', 'RhodeSchwartz_ZNB20', address='TCPIP0::192.168.1.3::INSTR')
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


data_file_name = 'redsideband_2ndpeak'

data=qt.Data(name = data_file_name)
data.add_coordinate('Drive power', units = 'dBm')
data.add_coordinate('Probe Freq', units = 'Hz')

data.add_value('X-Quadrature')
data.add_value('Y-Quadrature')
data.add_value('R-Quadrature')

# OuterMost loop 
outermost_meta_info = "SMF_Power_Sweep" 
outermost_start = 0
outermost_stop  = 1  # One more than the end point you need 
outermost_len  =  1

center = 6413289024.0
span = 40*kHz
if_bw = 100
vna_power = -45 # Dir coupler 6 dB


#Outerloop
outer_meta_info = "Drive power"
outer_start = 5
outer_stop  = 30
outer_len = 26

drive_freq=6402034866.7

# Inner most loop

inner_meta_info = "Probe freq" 
inner_start = center-span/2
inner_stop = center+span/2
len_innerloop = 2001
innerloop = np.linspace(inner_start,inner_stop,len_innerloop)



### Other drive variables:



#####################
outermostloop = np.linspace(outermost_start,outermost_stop,outermost_len) 
outerloop = np.linspace(outer_start,outer_stop,outer_len) 
len_outermostloop=len(outermostloop) 
len_outerloop=len(outerloop) 
data_info=["X","Y","R"] 

####### Preparing instruments
znb.reset()
znb.set_external_reference(True)
znb.set_start_frequency(inner_start)
znb.set_stop_frequency(inner_stop)
znb.set_source_power(vna_power)
znb.set_numpoints(len_innerloop)
znb.set_if_bandwidth(if_bw)
znb.set_sweep_mode('single')
znb.add_trace('S21')
znb.rf_on()

qt.mstart()

first_time = True

###########################################


#smf.set_source_power(SMF_power)
smf.set_frequency(drive_freq)
smf.rf_on()
#outermost_value_array = np.linspace(outermost_value, outermost_value, record_length)
for outer_index, outer_value in enumerate(outerloop):
    smf.set_source_power(outer_value)
    print(outer_index)
    outer_value_array = np.linspace(outer_value,outer_value,len_innerloop)
    znb.send_trigger(wait=True)
    trace= znb.get_data('S21')
    znb.autoscale()
    data.add_data_point(outer_value_array, innerloop, np.real(trace),np.real(trace),np.absolute(trace))
    if first_time:
        generate_meta_file(outer_len, outer_stop, outermost_len,outermost_stop)
        copy_script()
    first_time = False
    #delay_progress_bar.update(outer_index+1)

data.close_file()
rig.all_outputs_off()
smf.rf_off()
