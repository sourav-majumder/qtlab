import qt
import numpy as np

######### METAgen for spyview; careful with Y-axis flip and abort();

def generate_meta_file():
    metafile = open('%s.meta.txt' % data.get_filepath()[:-4], 'w')
    metafile.write('#inner loop\n%s\n%s\n%s\n%s\n'%
            (num_points, start_freq, stop_freq, 'Frequency(Hz)'))
    metafile.write('#outer loop\n%s\n%s\n%s\n%s\n'%
            (power_points, start_power, end_power, 'Power(dBm)'))
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

########## USER INPUTS FOR SETTING THE MEASUREMENT ##########

start_freq = 4*GHz
stop_freq = 8*GHz
num_points = 5001
start_power = -10 #dBm
if_bw= 1*kHz

#############################################################

#create the instrument
znb = qt.instruments.create('ZNB20', 'RhodeSchwartz_ZNB20', address='TCPIP0::10.1.1.20::INSTR')
znb.reset()
#znb.set_default_channel_config()
znb.set_start_frequency(start_freq)
znb.set_stop_frequency(stop_freq)
znb.set_source_power(start_power)
znb.set_numpoints(num_points)
znb.set_if_bandwidth(if_bw)
znb.set_sweep_mode('single')

### SETTING UP DATA FILE
data=qt.Data(name='test')
data.add_coordinate('Frequency', units='Hz')
########data.add_coordinate('Power', units='dBm')
data.add_value('S21 mag')
data.add_value('S21 phase')
data.add_value('S21 real')
data.add_value('S21 imag')
## WE should also add copy of script to the data folder

power_list = np.linspace(start_power, end_power, power_points)
freq_array = np.linspace(start_freq, stop_freq, num=num_points)
qt.mstart()

try:

    # Outer loop : Power sweep
    #qt.msleep(0.1)
    #znb.set_source_power(start_power)
    znb.send_trigger()
    znb.wait_till_complete()
    trace= znb.get_data('S21')
    data.add_data_point(freq_array,np.absolute(trace),np.angle(trace), np.real(trace), np.imag(trace))

except KeyboardInterrupt:
    print '\nInterrupted'

data.close_file()
generate_meta_file()
