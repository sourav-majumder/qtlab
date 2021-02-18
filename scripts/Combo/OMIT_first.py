# To be run in qtlab
import qt
import numpy as np
import sys
import shutil
import os
#from constants import *

GHz=10**9;
MHz=10**6;
kHz=1000;
Hz=1;

#############################
# Parameters
#############################
# probe
probe_center_freq = 6.9366*GHz
probe_span = 1000*kHz
probe_points = 1001
if_bw = 1000*Hz
VNA_power = 0
average_count = 1

# pump
pump_start = cavity_freq+2*MHz
pump_stop = cavity_freq+37*MHz
pump_points = 1501
pump_power = 16

def generate_meta_file(points):
    metafile = open('%s.meta.txt' % data.get_filepath()[:-4], 'w')
    metafile.write('#inner loop\n%s\n%s\n%s\n%s\n'%
            (vna_points, cavity_freq-vna_span, cavity_freq+vna_span, 'Frequency(Hz)'))
    metafile.write('#outer loop\n%s\n%s\n%s\n%s\n'%
            (points, pump_start, pump_stop, 'Detuning(Hz)'))
    metafile.write('#outermost loop (unused)\n1\n0\n1\nNothing\n')

    metafile.write('#for each of the values\n')
    values = data.get_values()
    i=0
    while i<len(values):
        metafile.write('%d\n%s\n'% (i+3, values[i]['name']))
        i+=1
    metafile.close()

#############################
# Initialize Instruments
#############################

print 'part 1 over '

znb = qt.instruments.create('ZNB20', 'RhodeSchwartz_ZNB20', address='TCPIP0::192.168.1.3::INSTR', reset=True)
smf = qt.instruments.create('SMF100', 'RhodeSchwartz_SMF100', address = 'TCPIP0::192.168.1.4::INSTR', reset=True)

smf.set_frequency(cavity_freq)
znb.set_external_reference(True)
znb.set_external_reference_frequency(10)
znb.set_average_mode('AUTO')
znb.set_averages(average_count)
znb.sweep_number(average_count)
znb.set_center_frequency(cavity_freq)
znb.set_span(vna_span)
znb.set_numpoints(vna_points)
znb.set_if_bandwidth(if_bw)
znb.set_source_power(VNA_power)
smf.set_source_power(SMF_power)

print 'instrument intialized'


filename='cavity_with_drum_pump_test'
data=qt.Data(name=filename)
data.add_coordinate('Pump Detuning', units='Hz')
data.add_coordinate('Probe Frequency', units='Hz')
#data.add_value('S21 real')
#data.add_value('S21 imag')
data.add_value('S21 abs')
data.add_value('S21 phase')

smf.rf_on()
znb.rf_on()
#raw_input()
qt.mstart()

pump_array = np.linspace(pump_start, pump_stop, pump_points)
freq_array = np.linspace(cavity_freq-vna_span, cavity_freq+vna_span, vna_points)

i = 0

print 'preparing loop'

for pump in pump_array:
    smf.set_frequency(pump)
    znb.send_trigger(wait=True)
    znb.autoscale()
    trace = znb.get_data('S21')
    pump_detuning = np.linspace(pump-cavity_freq, pump-cavity_freq, vna_points)
    data.add_data_point(pump_detuning, freq_array, np.absolute(trace), np.angle(trace))
    #data.add_data_point(pump_detuning, freq_array, np.real(trace), np.imag(trace),np.absolute(trace), np.angle(trace))
    i+=1
    generate_meta_file(i)
    

#create script in data directory
data.close_file()