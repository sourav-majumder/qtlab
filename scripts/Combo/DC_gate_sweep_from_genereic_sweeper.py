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

# smf = qt.instruments.create('SMF100', 'RhodeSchwartz_SMF100', address = SMF100_ADDRESS)
# rig = qt.instruments.create('DP832A', 'Rigol_DP832A', address='TCPIP0::192.168.1.5::INSTR')
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

##################################################

data_file_name = raw_input('Enter name of data file: ')

data=qt.Data(name=data_file_name)
#data.add_coordinate('Frequency', units = 'Hz')
data.add_coordinate('Time', units = 'V')
data.add_coordinate('Probe Freq', units = 'Hz')

data.add_value('S21 Real')
data.add_value('S21 Imag')
data.add_value('S21 Absolute')
data.add_value('S21 Phase')

# OuterMost loop 
outermost_meta_info = "Nothing" 
outermost_start = 0
outermost_stop  = 1  # One more than the end point you 
outermost_len  =  1


center = 7.5*GHz
span = 4*GHz
if_bw = 100
vna_power = -30

# SMF frequency = 6.56132 GHz
# SMF Power = 21.91 dBm


#Outerloop
outer_meta_info = "Time"
outer_start = 5
outer_stop  = 0
outer_len = 501

# Inner most loop

inner_meta_info = "Probe freq" 
inner_start = center - span/2.
inner_stop = center + span/2.
len_innerloop = 1001
innerloop = np.linspace(inner_start,inner_stop,len_innerloop)



### Other drive variables:



#####################
outermostloop = np.linspace(outermost_start,outermost_stop,outermost_len) 
outerloop = np.linspace(outer_start,outer_stop,outer_len) 
len_outermostloop=len(outermostloop) 
len_outerloop=len(outerloop) 
data_info=["X","Y","R","Phi"] 

####### Preparing instruments
znb.reset()
znb.set_external_reference(True)
znb.set_start_frequency(inner_start)
znb.set_stop_frequency(inner_stop)
znb.set_source_power(vna_power)
znb.set_numpoints(len_innerloop)
znb.set_if_bandwidth(if_bw)
znb.set_sweep_mode('single')

znb.rf_on()
znb.add_trace('S21')
qt.mstart()

first_time = True

###########################################
delay_progress_bar = progressbar.ProgressBar(maxval=outer_len, \
    widgets=['Total: ', progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage(), ' (', progressbar.ETA(), ') '])
delay_progress_bar.start()
#outermost_value_array = np.linspace(outermost_value, outermost_value, record_length)
#for outer_index, outer_value in enumerate(outerloop):
while True:
    # rig.set_voltage3(outer_value)
    time_now = time.time()
    outer_value_array = np.linspace(time_now,time_now,len_innerloop)
    znb.send_trigger(wait=True)
    trace= znb.get_data('S21')
    znb.autoscale()
    data.add_data_point(outer_value_array, innerloop, np.real(trace),np.imag(trace),np.absolute(trace),np.angle(trace))
    if first_time:
        generate_meta_file(outer_len, outer_stop, outermost_len,outermost_stop)
        copy_script()
    first_time = False
    # delay_progress_bar.update(outer_index+1)

delay_progress_bar.finish()
data.close_file()
#print(time.time()-start)

 #for i in np.linspace(5,0,501):
 #    rig.set_voltage3(i)
 #    qt.msleep(0.1)