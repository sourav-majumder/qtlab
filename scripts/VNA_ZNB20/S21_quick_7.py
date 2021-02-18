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



########## USER INPUTS FOR SETTING THE MEASUREMENT ##########

center =6*GHz
span= 2000*MHz
num_points = 50001
start_power = 8 #dBm
end_power = -48 #dBm
power_points = 11
if_bw= 3

start_freq=center-span/2
stop_freq=center+span/2

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
data.add_coordinate('Power', units='dBm')
data.add_value('S11 real')
data.add_value('S11 imag')
data.add_value('S11 abs')
data.add_value('S11 phase')
## WE should also add copy of script to the data folder

power_list = np.linspace(start_power, end_power, power_points)
freq_array = np.linspace(start_freq, stop_freq, num=num_points)
qt.mstart()

# Outer loop : Power sweep
for power in power_list:
    #print 'Power: %.2f dBm %.2f %% left                                            \r'%(power,(end_power-power)*100/(end_power-start_power)),
    #qt.msleep(0.1)
    znb.set_source_power(bandwidth(power))
    znb.set_if_bandwidth(if_bw)
    znb.send_trigger(wait=True)
    trace= znb.get_data('S21')
    power_array = np.linspace(power, power, num=num_points)
    data.add_data_point(power_array, freq_array, np.real(trace), np.imag(trace),np.absolute(trace), np.angle(trace))

data.close_file()
generate_meta_file()
