# Temperature = 10 mK

import qt
import numpy as np
import shutil
import sys
import os

######### METAgen for spyview; careful with Y-axis flip and abort();

def generate_meta_file():
    metafile = open('%s.meta.txt' % data.get_filepath()[:-4], 'w')
    metafile.write('#inner loop\n%s\n%s\n%s\n%s\n'%
            (num_points, start_freq, stop_freq, 'Frequency(Hz)'))
    metafile.write('#outer loop\n%s\n%s\n%s\n%s\n'%
            (power_points, end_power, start_power, 'Power(dBm)'))
    metafile.write('#outermost loop (unused)\n1\n0\n1\nNothing\n')

    metafile.write('#for each of the values\n')
    values = data.get_values()
    i=0
    while i<len(values):
        metafile.write('%d\n%s\n'% (i+3, values[i]['name']))
        i+=1
    metafile.close()

################## END Metagen
# def bandwidth(power):
#     if power<=-50 and power>=-60:
#         return 1
#     elif power<=-40 and power>-50:
#         return 3
#     elif power<=-30 and power>-40:
#         return 5
#     elif power<=-20 and power>-30:
#         return 10
#     elif power<=-10 and power>-20:
#         return 100
#     elif power<=0 and power>-10:
#         return 1*KHz
#     elif power<=10 and power>0:
#         return 10*KHz
    

##file_name = os.path.basename(sys.argv[0])



kHz=1e3;
MHz=1e6;
GHz=1e9;



########## USER INPUTS FOR SETTING THE MEASUREMENT ##########

center =6*GHz
span= 4*GHz
num_points = 5001
start_power = -10 #dBm
end_power = -10 #dBm
power_points = 1
if_bw= 1*kHz
average_count = 20

start_freq=center-span/2
stop_freq=center+span/2

#############################################################

#create the instrument
znb = qt.instruments.create('ZNB20', 'RhodeSchwartz_ZNB20', address='TCPIP0::192.168.1.3::INSTR')
znb.reset()
#znb.set_default_channel_config()
# znb.set_start_frequency(start_freq)
# znb.set_stop_frequency(stop_freq)
znb.set_center_frequency(center)
znb.set_span(span)
# znb.set_source_power(start_power)
znb.set_numpoints(num_points)
znb.set_if_bandwidth(if_bw)
znb.set_sweep_mode('single')
znb.set_averages(average_count)
znb.sweep_number(average_count)
znb.rf_on()

#To avoid timeout error
#qt.msleep(15)

print 'this'
### SETTING UP DATA FILE
filename='Cavity_with_drum_temperature_sweep'
data=qt.Data(name=filename)
data.add_coordinate('Temperature', units='K')
data.add_coordinate('Frequency', units='Hz')
data.add_value('S21 real')
data.add_value('S21 imag')
data.add_value('S21 abs')
data.add_value('S21 phase')

## WE should also add copy of script to the data folder

# power_list = np.linspace(start_power, end_power, power_points)
freq_array = np.linspace(start_freq, stop_freq, num=num_points)
qt.mstart()
power = -30
# Outer loop : Power sweep
temp = raw_input('Temperature : ')
while temp != 'd':
    #print 'Power: %.2f dBm %.2f %% left                                            \r'%(power,(end_power-power)*100/(end_power-start_power)),
    #qt.msleep(0.1)
    znb.set_source_power(power)
    # if_bw=bandwidth(power)
    # znb.set_if_bandwidth(if_bw)
    znb.send_trigger(wait=True)
    trace= znb.get_data('S21')
    temp_array = np.linspace(float(temp), float(temp), num=num_points)
    data.add_data_point(temp_array, freq_array, np.real(trace), np.imag(trace),np.absolute(trace), np.angle(trace))
    temp = raw_input('Temperature : ')

#create script in data directory
shutil.copy2('%s'%sys.argv[0],'%s/%s'%(data.get_filepath()[:-(len(filename)+11)],os.path.basename(sys.argv[0])))

#close data file
data.close_file()
generate_meta_file()