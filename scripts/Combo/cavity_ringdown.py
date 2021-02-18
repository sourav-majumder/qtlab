# To be run in qtlab
import qt
import numpy as np
import sys
import progressbar


from ZurichInstruments_UHFLI import ZurichInstruments_UHFLI
from constants import *

# def generate_meta_file(freq_points):
#     metafile = open('%s.meta.txt' % data.get_filepath()[:-4], 'w')
#     metafile.write('#inner loop\n%s\n%s\n%s\n%s\n'%
#             (record_length,  start_time, stop_time, 'Time(s)'))
#     metafile.write('#outer loop\n%s\n%s\n%s\n%s\n'%
#             (freq_points, start_frequency, stop_frequency, 'Frequency(Hz)'))
#     metafile.write('#outermost loop (unused)\n1\n0\n1\nNothing\n')

#     metafile.write('#for each of the values\n')
#     values = data.get_values()
#     i=0
#     while i<len(values):
#         metafile.write('%d\n%s\n'% (i+3, values[i]['name']))
#         i+=1
#     metafile.close()

# connection_check = True
# if (len(sys.argv) > 1 and sys.argv[1] == 'nocheck') or (len(sys.argv) > 2 and sys.argv[2] == 'nocheck'):
# 	connection_check = False
#############################
# Ringdown Parameters
#############################
center_frequency = 7.97906*GHz
span = 10*MHz
start_frequency = center_frequency-span/2  # RF Generator frequencies
stop_frequency = center_frequency+span/2 
numpoints = 1001
mix_freq = 100*MHz

signal_generator_source_power = -20 # dBm

# Oscilloscope parameters
setup_scope = True

channels = [1,2]
volt_per_div = [0.002,0.002]
ch_position = [-3.18,-4]#[-4,-3]
trig_source = 5
trig_level = 0.7
time_per_div = 0.5*us
resolution = 5*ns

average_count = 1e3
#############################
# Initialize Instruments
#############################
uhf = ZurichInstruments_UHFLI('dev2232', reset=True) # Initializing UHFLI
# znb = qt.instruments.create('ZNB20', 'RhodeSchwartz_ZNB20', address='TCPIP0::192.168.1.3::INSTR', reset=True)
# smf = qt.instruments.create('SMF100', 'RhodeSchwartz_SMF100', address = 'TCPIP0::192.168.1.4::INSTR', reset=True)
# rte = qt.instruments.create('RTE1104', 'RhodeSchwartz_RTE1104', address = 'TCPIP0::192.168.1.6::INSTR', reset=True)

# freq_array = np.linspace(start_frequency, stop_frequency, numpoints)

# # Setup VNA as source
# znb.set_external_reference(True)
# znb.set_external_reference_frequency(10)
# znb.set_sweep_type('cw')
# znb.set_center_frequency(center_frequency + mix_freq)
# znb.set_source_power(14) # dBm

# # Setup Signal Generator as source
# smf.set_frequency(center_frequency)
# smf.set_source_power(signal_generator_source_power) # dBm
# smf.pulse_mod_on()

# Setup Lock-in for Ringdown
uhf.extclk(True)
uhf.setup_for_cavity_ringdown(freq = mix_freq, pulse_length = 2*us, timeconstant = 30*ns)

# Connections
# if connection_check:
# 	print 'HAVE ALL THE CONNECTIONS BEEN MADE?'
# 	raw_input('1. Trig/Ref 1 of Lock-in to External Trigger of Oscilloscope')
# 	raw_input('2. Trig/Ref 2 of Lock-in to Pulse-in of Signal Generator')
# 	print '3. RF out of Signal Generator to Circulator Port 1 (or Directional Coupler Port -20dB)'
# 	raw_input('If no cavity then connect RF out of Signal Generator to Mixer Port R\n and skip to step 6')
# 	raw_input('4. Cavity to Circulator Port 2 (or Directional Coupler Port IN)')
# 	raw_input('5. Mixer Port R to Circulator Port 2 (or Directional Coupler Port OUT)')
# 	raw_input('6. Mixer Port I to Lock-in Signal Input 1')
# 	raw_input('7. Mixer Port Q to Lock-in Signal Input 2')
# 	raw_input('8. Mixer Port L to VNA Port 1')
# 	raw_input('9. Lock-in Aux 1 to Oscilloscope Channel 1')
# 	raw_input('10. Lock-in Aux 2 to Oscilloscope Channel 2')

# Turn on sources to setup oscilloscope
# znb.rf_on()
# smf.rf_on()
# uhf.cavity_ringdown()

# rte.set_ext_ref(True)
# rte.set_trig_source('EXT')
# rte.set_trig_level5(0.7)
# rte.set_reference_pos(0)

# for ch in channels:
# 	rte.ch_on(ch)
# 	rte.coupling_50(ch)

# # Setup Oscilloscope for Measurement
# if len(sys.argv) > 1 and sys.argv[1] == 'ask':
# 	volt_per_div = input('Enter a list of volt/divs in volts (Eg. [0.4, 0.8]) : ')
# 	ch_position = input('Enter a list of channel positions in divisions (Eg. [2, -3]) : ')
# 	time_per_div = input('Enter a time/division in seconds : ')
# 	resolution = input('Enter a resolution : ')
# 	signal_generator_source_power = input('Enter the Signal Generator source power : ')


# if setup_scope:
# 	rte.setup_scope(channels, volt_per_div, ch_position, time_per_div, resolution)
# rte.average_mode(True)
# rte.set_count(average_count)
# smf.set_source_power(signal_generator_source_power) # dBm
# data_file_name = raw_input('Enter name of data file : ')

# start_time, stop_time, record_length = rte.get_header()
# znb.set_center_frequency(start_frequency + mix_freq)
# smf.set_frequency(start_frequency)

# ### SETTING UP DATA FILE
# data=qt.Data(name=data_file_name)
# data.add_coordinate('Frequency', units='Hz')
# data.add_coordinate('Time', units='s')

# data.add_value('X-Quadrature')
# data.add_value('Y-Quadrature')

# bar = progressbar.ProgressBar(maxval=numpoints, \
#     widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage(), ' (', progressbar.ETA(), ') '])
# bar.start()

# for i in range(len(freq_array)):
# 	freq = freq_array[i]
# 	znb.set_center_frequency(freq + mix_freq)
# 	znb.send_trigger()
# 	smf.set_frequency(freq)
# 	rte.reset_averages()
# 	bar.update(i)
# 	# print 'Progress: %d/%d \r' % (i,numpoints)
# 	rte.run_nx_single(wait=True)
# 	farray = np.linspace(freq, freq, record_length)
# 	time_array, voltages = rte.get_data(channels)
# 	data.add_data_point(farray, time_array, *voltages)
# 	generate_meta_file(i+1)

# bar.finish()
# data.close_file()
# reset_all_instruments()