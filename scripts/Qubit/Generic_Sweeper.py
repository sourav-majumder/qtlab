from constants import *
from ZurichInstruments_UHFLI import ZurichInstruments_UHFLI
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

# uhf = ZurichInstruments_UHFLI('dev2232')
rte = qt.instruments.create('RTE1104', 'RhodeSchwartz_RTE1104', address = 'TCPIP0::192.168.1.6::INSTR')
# aps = qt.instruments.create('APSYN420',   'AnaPico_APSYN420',         address = APSYN420_ADDRESS)
# fsv = qt.instruments.create('FSV', 'RhodeSchwartz_FSV', address = FSV_ADDRESS)
smf = qt.instruments.create('SMF100', 'RhodeSchwartz_SMF100', address = SMF100_ADDRESS)
# aps = qt.instruments.create('APSYN420',   'AnaPico_APSYN420',         address = APSYN420_ADDRESS)
znb = qt.instruments.create('ZNB20', 'RhodeSchwartz_ZNB20', address=ZNB20_ADDRESS)

##############################################

def metagen(var_outer,var_outermost): 
    # Meta file creator 
    metafile=open('%s.meta.txt' % data.get_filepath()[:-4], 'w+')
    metafile.write("#Inner"+"\n"+str(len_innerloop)+"\n"+str(inner_start)+"\n"+str(record_length)+"\n"+inner_meta_info) 
    metafile.write("#Outer"+"\n"+str(len_outerloop)+"\n"+str(outer_start)+"\n"+str(var_outer)+"\n"+outer_meta_info) 
    metafile.write("#OuterMost"+"\n"+str(len_outermostloop)+"\n"+str(outermost_start)+"\n"+str(var_outermost)+"\n"+outermost_meta_info)

    metafile.write('#for each of the values\n')
    values = data.get_values()
    i=0
    while i<len(values):
        metafile.write('%d\n%s\n'% (i+3, values[i]['name']))
        i+=1
    metafile.close()

def generate_meta_file(outer_index,outer_value, outermost_index,outermost_value):
    metafile = open('%s.meta.txt' % data.get_filepath()[:-4], 'w')
    metafile.write('#inner loop\n%s\n%s\n%s\n%s\n'%
            (record_length,  start_time/us, stop_time/us, 'Time(us)'))
    metafile.write('#outer loop\n%s\n%s\n%s\n%s\n'%
            (outer_index, outer_value, outerloop[0], 'Power (mV)'))
    metafile.write('#outermost loop\n%s\n%s\n%s\n%s\n'%
            (outermost_index, outermostloop[0], outermost_value, 'Frequency'))

    metafile.write('#for each of the values\n')
    values = data.get_values()
    i=0
    while i<len(values):
        metafile.write('%d\n%s\n'% (i+4, values[i]['name']))
        i+=1
    metafile.close()
##################################################
def copy_script(once):
    if once == 1:
        shutil.copy2('%s'%sys.argv[0],'%s/%s'%(data.get_filepath()[:-(len(data_file_name)+11)],os.path.basename(sys.argv[0])))

##################################################
def awg_program(delay, pulse_length, power_points, sigma):
    awg_program_string = """
    const cycle = 4.4e-9;
    const us = 1e-6;
    const delay = %f;
    const pulse_length = %f;
    const measure_pulse_length = 15 ; // us
    const power = %f;
    const sigma = %f;
    wave w_gauss= gauss(4*sigma, power/750, 2*sigma, sigma);
    wave w_rise = cut(w_gauss, 0, 2*sigma-1);
    wave w_fall = cut(w_gauss, 2*sigma, 4*sigma-1);
    wave w_flat = rect(pulse_length, power/750);
    wave w_pulse = join(zeros(1), w_rise, w_flat, w_fall);
    while (true) {
      playWave(1,w_pulse);
      waitWave();
      wait(6); // Unit CLK CYCLES; Added to have gap between control and measure pulses
      wait(delay);
      setTrigger(0b0010);
      wait(measure_pulse_length*us/cycle);
      setTrigger(0b0000);
      wait(200*us/cycle);
    }
    """ % (delay, pulse_length,power_points,sigma)
    return awg_program_string

###################################################################


data_file_name = raw_input('Enter name of data file: ')

data=qt.Data(name=data_file_name)
data.add_coordinate('Frequency', units = 'Hz')
# data.add_coordinate('Power', units = 'mV')
data.add_coordinate('Time', units = 's')

data.add_value('X-Quadrature')
data.add_value('Y-Quadrature')
data.add_value('R-Quadrature')

####################################################################
# mix_freq = 88*MHz

# OuterMost loop is Pulse Power
outermost_start = 5.733*GHz 
outermost_stop  = 5.733*GHz  # One more than the end point you 
outermost_len  =  1
outermost_meta_info = "PulsePower" 

#Outerloop is delay between measure and control (cycles) 
outer_start = 7.2535*GHz
outer_stop  = 7.2545*GHz  # 4.4*3 us 
outer_len = 21
outer_meta_info = "Measurement Frequency" 

#####################
outermostloop = np.linspace(outermost_start,outermost_stop,outermost_len) 
outerloop = np.linspace(outer_start,outer_stop,outer_len) 
len_outermostloop=len(outermostloop) 
len_outerloop=len(outerloop) 
data_info=["X","Y","R"] 

##### Initialization of Instruments
# uhf.setup_awg(awg_program(delay=0, pulse_length=0, power_points=outerloop[0], sigma=16))
# uhf.awg_on(single=False) 
channels = [1,2]
# aps.set_frequency(control_array[0])

#############  RUN once to setup the innermost loop

start = time.time()
rte.wait_till_complete()
start_time, stop_time, record_length = rte.get_header()
assert raw_input('continue? [y/n]').upper() != 'N'

inner_start = start_time 
inner_stop = stop_time+1
inner_meta_info = "Inner" 
innerloop = np.linspace(inner_start,inner_stop,record_length)
len_innerloop = len(innerloop) 

###########################################

delay_progress_bar = progressbar.ProgressBar(maxval=len_outerloop, \
    widgets=['Total: ', progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage(), ' (', progressbar.ETA(), ') '])
delay_progress_bar.start()

once=1   # THIS variable is to copy the script at the bigining of the code 
generate_meta_file(outer_len,outer_stop, outer_len,outermost_stop)

for outermost_index, outermost_value in enumerate(outermostloop):
    #Stuff can be added here to execute a 3D loop
    outermost_value_array = np.linspace(outermost_value, outermost_value, record_length)
    for outer_index, outer_value in enumerate(outerloop):
        smf.set_frequency(outer_value)
        znb.set_center_frequency(outer_value + 133*MHz)
        znb.send_trigger()
        # uhf.setup_awg(awg_program(delay=0, pulse_length=0, power_points=outer_value, sigma=32))
        # uhf.awg_on(single=False)
        # aps.set_frequency(control)
        rte.reset_averages()
        rte.run_nx_single(wait=True)
        outer_value_array = np.linspace(outer_value, outer_value, record_length)
        time_array, voltages = rte.get_data(channels)
        voltages.append((voltages[0]**2+voltages[1]**2)**0.5)
        data.add_data_point(outer_value_array, time_array, *voltages)
        # generate_meta_file(outer_index+1,outer_value, outermost_index+1,outermost_value)
        # copy_script(once)
        once=once+1
        delay_progress_bar.update(outer_index+1)


data.close_file()
print(time.time()-start)

 