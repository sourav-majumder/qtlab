'''
attenuation after VNA is  30dBm
one amplifier in use 30dBm gain

'''
from __future__ import print_function

import qt
import shutil
import sys
import os
import time
import visa
# from future import print_function
################################
rm = visa.ResourceManager()
################################


from constants import *

def generate_meta_file():
	metafile = open('%s.meta.txt' % data.get_filepath()[:-4], 'w')
	metafile.write('#inner loop\n%s\n%s\n%s\n%s\n'%
			(probe_numpoints, drive_start_freq, drive_stop_freq, 'Frequency(Hz)'))
	metafile.write('#outer loop\n%s\n%s\n%s\n%s\n'%
			(drive_power_numpoint, drive_stop_amplitude, drive_start_amplitude, 'dBm'))
	metafile.write('#outermost loop (unused)\n1\n0\n1\nNothing\n')

	metafile.write('#for each of the values\n')
	values = data.get_values()
	i=0
	while i<len(values):
		metafile.write('%d\n%s\n'% (i+3, values[i]['name']))
		i+=1
	metafile.close()

def copy_script(once):
  if once:
	shutil.copy2('%s'%sys.argv[0],'%s/%s'%(data.get_filepath()[:-(len(data.get_filename())+1)],os.path.basename(sys.argv[0])))


def r(list1, list2):
	return [ np.sqrt(x**2+y**2) for x, y in zip(list1, list2) ]



#############################
# Measurement Parameters
#############################
# VNA sweep parameters
probe_center = 6.198598*GHz
probe_span = 1*Hz
probe_start_freq = probe_center - probe_span/2
probe_stop_freq = probe_center + probe_span/2

if_bw = 10*Hz
probe_power = -30 # 30 dB att + 1 dB cab;e + 6 dir coupler
s_params = ['S21']
avg_point = 1

# SRS sweep parameters
drive_center_freq = 15.5*MHz
drive_span = 0.5*MHz
drive_start_freq = drive_center_freq - drive_span/2
drive_stop_freq = drive_center_freq + drive_span/2
drive_start_amplitude = 1 #Volt peak to peak
drive_stop_amplitude = 1
drive_power_numpoint = 1

probe_numpoints = int(drive_span / 10) + 20


filename = 'center_%0.02f_M'%(drive_center_freq/1e6)



#############################
# Initialize Instruments
#############################
znb = qt.instruments.create('ZNB20', 'RhodeSchwartz_ZNB20', address=ZNB20_ADDRESS, reset=True)
#smf = qt.instruments.create('SMF100', 'RhodeSchwartz_SMF100', address = SMF100_ADDRESS, reset=True)
#dg = rm.open_resource('USB0::0x1AB1::0x0642::DG1ZA194405642::INSTR')
ins= rm.open_resource('TCPIP0::192.168.1.9::inst0::INSTR')

# Setup VNA as source
znb.set_external_reference(True)
znb.set_external_reference_frequency(10)
znb.set_sweep_type('point') # cw mode
znb.w('SOUR:FREQ:CW %s'%probe_center)
znb.set_numpoints(probe_numpoints)
znb.set_if_bandwidth(if_bw)
znb.set_source_power(probe_power)
znb.set_sweep_mode('single')
znb.add_trace('S21')
znb.w('DISPlay:WINDow1:TRAC1:Y:SCALe:RLEVel -45')
znb.w('DISPlay:WINDow1:TRAC1:Y:SCALe:RPOS 60')
znb.w('DISPlay:WINDow1:TRAC1:Y:SCALe:PDIV 1')

swap_rate = 1/(znb.get_sweeptime() - 1)
## SRS Ready
ins.write('*RST;*WAI')
ins.write('ENBR 0;ENBL 0;*WAI')             ## Swich off RF output for both LF and RF

ins.write('FREQ %f;*WAI'%drive_center_freq)
ins.write('AMPL %f;*WAI'% drive_start_amplitude)
ins.write('TYPE 3;*WAI')                   ## selects frequency sweep as moduolation type
ins.write('SFNC 1;*WAI')                   ## select ramp as Modulation sweep function 
ins.write('SRAT %f;*WAI'%swap_rate)		   ## Sweep rate 
ins.write('SDEV %f;*WAI'%drive_span)	   ## frequency span

ins.write('MODL 1;*WAI')				   ## Turn on modulation



# Turn on sources
znb.rf_on()


# Test trigger
# znb.send_trigger(wait=True)
# znb.autoscale()
# go_on = raw_input('Continue? [y/n] ')

# assert go_on.strip().upper() != 'N'

### SETTING UP DATA FILE
data=qt.Data(name=filename)
# data.add_comment('No. of repeated measurements for average is 60')
data.add_coordinate('Probe Power', units='dBm')
data.add_coordinate('Drive Frequency', units='Hz')
data.add_value('S21 real')
data.add_value('S21 imag')
data.add_value('S21 abs')
data.add_value('S21 phase')


drive_freq_array = np.linspace(drive_start_freq, drive_start_freq, probe_numpoints)
drive_power_array = np.linspace(drive_start_amplitude, drive_stop_amplitude, drive_power_numpoint)

qt.mstart()

#num_avs = 0
once = True


for SRS_div_power in drive_power_array:
	start_time = time.time()
	ins.write('AMPL %f;*WAI'% SRS_div_power)
	power_list = np.linspace(SRS_div_power, SRS_div_power, num=probe_numpoints)
	traces=[[],[],[],[]]
	ins.write('ENBL 1;*WAI')
	znb.send_trigger(wait=True)
	trace = znb.get_data('S21')
	traces[0].append(np.real(trace))
	traces[1].append(np.imag(trace))
	traces[2].append(np.absolute(trace))
	traces[3].append(np.angle(trace)  )
	end_time = time.time()
	data.add_data_point(power_list, drive_freq_array, traces[0][0], traces[1][0], traces[2][0], traces[3][0])
	generate_meta_file()
	copy_script(once);once = False
	print(end_time - start_time)



ins.write('ENBL 0;*WAI')

#create script in data directory
# shutil.copy2('%s'%sys.argv[0],'%s/%s'%(data.get_filepath()[:-(len(filename)+11)],os.path.basename(sys.argv[0])))
# copy_script(sys.argv[0], filename)
data.close_file(sys.argv[0])