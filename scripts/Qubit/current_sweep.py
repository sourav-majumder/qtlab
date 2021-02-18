import qt
import numpy as np
import os
import shutil
import sys
import progressbar
######### METAgen for spyview; careful with Y-axis flip and abort();

def generate_meta_file(current,index):
    metafile = open('%s.meta.txt' % data.get_filepath()[:-4], 'w')
    metafile.write('#inner loop\n%s\n%s\n%s\n%s\n'%
            (num_points, freq_array[0], freq_array[-1], 'Frequency(Hz)'))
    metafile.write('#outer loop\n%s\n%s\n%s\n%s\n'%
            (index, current, start_current, 'Current(A)'))
    metafile.write('#outermost loop (unused)\n1\n0\n1\nNothing\n')

    metafile.write('#for each of the values\n')
    values = data.get_values()
    i=0
    while i<len(values):
        metafile.write('%d\n%s\n'% (i+3, values[i]['name']))
        i+=1
    metafile.close()



################## END Metagen

kHz=1e3;
MHz=1e6;
GHz=1e9;



def bandwidth(power):
    if power<=-50 and power>=-60:
        return 100
    elif power<=-40 and power>-50:
        return 100
    elif power<=-30 and power>-40:
        return 100
    elif power<=-20 and power>-30:
        return 100
    elif power<=-10 and power>-20:
        return 100
    elif power<=0 and power>-10:
        return 100
    elif power<=10 and power>0:
        return 100



########## USER INPUTS FOR SETTING THE MEASUREMENT ##########

center =5.954*GHz
span= 200*MHz
# num_points = 601
power = -30 #dBm
if_bw= 100
filename=raw_input('Filename: ')

start_freq=center-span/2
stop_freq=center+span/2

#############################################################

#create the instrument
znb = qt.instruments.create('ZNB20', 'RhodeSchwartz_ZNB20', address='TCPIP0::192.168.1.3::INSTR')
qs = qt.instruments.create('GS200', 'Yokogawa_GS200', address='USB0::0x0B21::0x0039::91T416206::INSTR')
# znb.reset()
#znb.set_default_channel_config()
# znb.set_start_frequency(start_freq)
# znb.set_stop_frequency(stop_freq)
# znb.set_source_power(start_power)
# znb.set_numpoints(num_points)
# znb.set_if_bandwidth(if_bw)
# znb.set_sweep_mode('single')

### SETTING UP DATA FILE
data=qt.Data(name=filename)
data.add_coordinate('Current', units='A')
data.add_coordinate('Frequency', units='Hz')
data.add_value('S21 real')
data.add_value('S21 imag')
data.add_value('S21 abs')
data.add_value('S21 phase')
## WE should also add copy of script to the data folder
start_current = 15e-3
stop_current = -15e-3
curr_numpoints = 301
curr_list=np.linspace(start_current,stop_current,curr_numpoints)
#power_list = np.linspace(start_power, end_power, power_points)
freq_array = znb.get_frequency_data()
num_points = znb.get_numpoints()
# znb.rf_on()
#raw_input()

qt.mstart()
# znb.add_trace('S21')
# znb.set_source_power(-33)
# znb.set_if_bandwidth(if_bw)

current_progress_bar = progressbar.ProgressBar(maxval=len(curr_list), \
    widgets=['Total: ', progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage(), ' (', progressbar.ETA(), ') '])
current_progress_bar.start()

qs.set_function('CURR')
for i in np.arange(qs.get_level(), start_current, 0.1e-3):
    qs.set_level(i)
    qt.msleep(0.2)
# Outer loop : Power sweep
for index,cr in enumerate(curr_list):
    #print 'Current: %.2f A %.2f %% left                                            \r'%(power,(end_power-power)*100/(end_power-start_power)),
    #qt.msleep(0.1)
    qs.set_current(cr)
    qt.msleep(0.1)
    znb.send_trigger(wait=True)
    trace= znb.get_data('S21')
    # znb.autoscale()
    curr_array = np.linspace(cr, cr, num=num_points)
    data.add_data_point(curr_array, freq_array, np.real(trace), np.imag(trace),np.absolute(trace), np.angle(trace))
    current_progress_bar.update(index+1)
    generate_meta_file(cr,index+1)
    
qs.set_function('CURR')
for i in np.arange(qs.get_level(), 0, 0.1e-3):
    qs.set_level(i)
    qt.msleep(0.2)

current_progress_bar.finish()
shutil.copy2('%s'%sys.argv[0],'%s/%s'%(data.get_filepath()[:-(len(filename)+11)],os.path.basename(sys.argv[0])))
data.close_file()
