import qt
import numpy as np
import sys

######### METAgen for spyview

def generate_meta_file():
    metafile = open('%s.meta.txt' % data.get_filepath()[:-4], 'w')
    metafile.write('#inner loop\n%s\n%s\n%s\n%s\n'%
            (num_points, start_freq, stop_freq, 'Frequency(Hz)'))
    metafile.write('#outer loop\n%s\n%s\n%s\n%s\n'%
            (power_points,  end_power, start_power, 'Power(dBm)'))
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

start_freq = 7.0234*GHz
stop_freq = 7.0334*GHz
num_points = 1001
start_power = -30 #dBm
end_power = -30 #dBm
power_points = 1
if_bw= 0.1*kHz

#############################################################

#create the instrument
znb = qt.instruments.create('ZNB20', 'RhodeSchwartz_ZNB20', address='TCPIP0::192.168.1.3::INSTR')
znb.reset()
#znb.delete_all_traces()
znb.set_start_frequency(start_freq)
znb.set_stop_frequency(stop_freq)
znb.set_source_power(start_power)
znb.set_numpoints(num_points)
znb.set_if_bandwidth(if_bw)
znb.set_sweep_mode('single')

dataname='S21,S11,S12,S22'

if len(sys.argv)==1:
    s_list = ['S21', 'S11', 'S12', 'S22']
else:
    s_list=[]
    i=1
    while i<len(sys.argv):
        if 'name' in sys.argv[i]:
            dataname=sys.argv[i][5:]
        else:
            znb.add_trace('Trckw'+str(i),1,sys.argv[i].upper())
            s_list.append(str.upper(sys.argv[i]))
        i+=1
s_data = {}

### SETTING UP DATA FILE
data=qt.Data(name=dataname)
data.add_coordinate('Power', units='dBm')
data.add_coordinate('Frequency', units='Hz')

for s in s_list:
    data.add_value(s+' mag')
    data.add_value(s+' phase')
    data.add_value(s+' real')
    data.add_value(s+' imag')

power_list = np.linspace(start_power, end_power, power_points)
freq_array = np.linspace(start_freq, stop_freq, num=num_points)
qt.mstart()

# Outer loop : Power sweep
for power in power_list:
    print 'Power: %.2f dBm %.2f %% left                                            \r'%(power,(end_power-power)*100/(end_power-start_power)),
    #qt.msleep(0.1)
    znb.set_source_power(power)
    znb.send_trigger(wait=True)
    power_array = np.linspace(power, power, num=num_points)
    list_to_pass=[power_array, freq_array]
    #trace= znb.get_data('S21')
    for s in s_list:
        s_data[s]=znb.get_data(s)
        list_to_pass.append(np.absolute(s_data[s]))
        list_to_pass.append(np.angle(s_data[s]))
        list_to_pass.append(np.real(s_data[s]))
        list_to_pass.append(np.imag(s_data[s]))
    #data.add_data_point(power_array, freq_array, np.real(trace), np.imag(trace))
    data.add_data_point(*list_to_pass)
    
data.close_file()
generate_meta_file()
