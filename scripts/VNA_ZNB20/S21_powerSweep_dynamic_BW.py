import qt
import numpy as np
import os
import shutil
import sys
######### METAgen for spyview; careful with Y-axis flip and abort();

def generate_meta_file():
    metafile = open('%s.meta.txt' % data.get_filepath()[:-4], 'w')
    metafile.write('#inner loop\n%s\n%s\n%s\n%s\n'%
            (num_points, start_freq, stop_freq, 'Frequency(Hz)'))
    metafile.write('#outer loop\n%s\n%s\n%s\n%s\n'%
            (20001, 0, 0.02, 'Current(A)'))
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
        return 1
    elif power<=-40 and power>-50:
        return 5
    elif power<=-30 and power>-40:
        return 10
    elif power<=-20 and power>-30:
        return 30
    elif power<=-10 and power>-20:
        return 100
    elif power<=0 and power>-10:
        return 1*kHz
    elif power<=10 and power>0:
        return 10*kHz



def bandwidth2(power):
    if power<=-50 and power>=-60:
        return 30
    elif power<=-40 and power>-50:
        return 50
    elif power<=-30 and power>-40:
        return 100
    elif power<=-20 and power>-30:
        return 300
    elif power<=-10 and power>-20:
        return 1000
    elif power<=0 and power>-10:
        return 3*kHz
    elif power<=10 and power>0:
        return 10*kHz



########## USER INPUTS FOR SETTING THE MEASUREMENT ##########

center =6.16575*GHz
span= 20*MHz
num_points = 1001
start_power = -60 #dBm
end_power = -20 #dBm
power_points = 21
if_bw= 150
filename='sudhir_power_sweep_vna_al_drum'

start_freq=center-span/2
stop_freq=center+span/2

#############################################################

#create the instrument
znb = qt.instruments.create('ZNB20', 'RhodeSchwartz_ZNB20', address='TCPIP0::192.168.1.3::INSTR')
qs = qt.instruments.create('GS200', 'Yokogawa_GS200', address='USB0::0x0B21::0x0039::91T416206::INSTR')
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
data.add_coordinate('Current', units='A')
data.add_coordinate('Frequency', units='Hz')
#data.add_value('S21 real')
#data.add_value('S21 imag')
data.add_value('S21 abs')
#data.add_value('S21 phase')
## WE should also add copy of script to the data folder
curr_list=np.linspace(0,0.02,20001)
#power_list = np.linspace(start_power, end_power, power_points)
freq_array = np.linspace(start_freq, stop_freq, num=num_points)
znb.rf_on()
#raw_input()

qt.mstart()
znb.add_trace('S21')
znb.set_source_power(-33)
znb.set_if_bandwidth(if_bw)


# Outer loop : Power sweep
for cr in curr_list:
    #print 'Current: %.2f A %.2f %% left                                            \r'%(power,(end_power-power)*100/(end_power-start_power)),
    #qt.msleep(0.1)
    qs.set_current(cr)
    znb.send_trigger(wait=True)
    trace= znb.get_data('S21')
    znb.autoscale()
    curr_array = np.linspace(cr, cr, num=num_points)
    data.add_data_point(curr_array, freq_array,np.absolute(trace))
    generate_meta_file()
    shutil.copy2('%s'%sys.argv[0],'%s/%s'%(data.get_filepath()[:-(len(filename)+11)],os.path.basename(sys.argv[0])))

data.close_file()
