from constants import *
from ZurichInstruments_UHFLI import ZurichInstruments_UHFLI
import sys
import os
import shutil
import qt
import progressbar
import numpy as np
import time
import awg_on_first as opt
import ssb

##############################################

us = 1e-6
ns = 1e-9
##############################################

uhf = ZurichInstruments_UHFLI('dev2232')
rte = qt.instruments.create('RTE1104', 'RhodeSchwartz_RTE1104', address = 'TCPIP0::192.168.1.6::INSTR')
# aps = qt.instruments.create('APSYN420',   'AnaPico_APSYN420',         address = APSYN420_ADDRESS)
# fsv = qt.instruments.create('FSV', 'RhodeSchwartz_FSV', address = FSV_ADDRESS)
# smf = qt.instruments.create('SMF100', 'RhodeSchwartz_SMF100', address = SMF100_ADDRESS)
aps = qt.instruments.create('APSYN420',   'AnaPico_APSYN420',         address = APSYN420_ADDRESS)

##############################################



def generate_meta_file(outermost_index,outermost_value):
    metafile = open('%s.meta.txt' % data.get_filepath()[:-4], 'w')
    metafile.write('#inner loop\n%s\n%s\n%s\n%s\n'%
            (record_length,  start_time/us, stop_time/us, 'Time(us)'))
    metafile.write('#outermost loop\n%s\n%s\n%s\n%s\n'%
            (outermost_index, outermost_value, outermostloop[0], 'Frequency'))
    metafile.write('#outermost loop (unused)\n1\n0\n1\nNothing\n')

    metafile.write('#for each of the values\n')
    values = data.get_values()
    i=0
    while i<len(values):
        metafile.write('%d\n%s\n'% (i+4, values[i]['name']))
        i+=1
    metafile.close()
##################################################
def copy_script():
    shutil.copy2('%s'%sys.argv[0],'%s/%s'%(data.get_filepath()[:-(len(data_file_name)+11)],os.path.basename(sys.argv[0])))

##################################################
#
#   NOTE on the units used in AWG code
#
# delay         = CLC CYCLE     = Define the time between control and measure. Each cycle is 4.4ns
# pulse_length  = SAMPLE POINTS = Define the length of flat top of Gaussian control pulse.
# power_points  = mV            = Lock-in output is mV. Assume 750mV Full scaling
# sigma         = SAMPLE POINTS = Width of Gaussian rise+fall
#
######################


def awg_program():
    awg_program_string = """
    const cycle = 4.4e-9;
    const us = 1e-6;
    const measure_pulse_length = 10; // us
    const sigma = 44;
    //gauss(samples, amplitude, position, width)
    wave w1 = gauss(4*sigma, (17.14/750), 2*sigma, sigma);
    while (true) {
      playWave(2, w1);
      waitWave();
      wait(12); // Unit CLK CYCLES; Added to have gap between control and measure pulses
      setTrigger(0b0001);
      wait(measure_pulse_length*us/cycle);
      setTrigger(0b0000);
      wait(50*us/cycle);
    }
    """
    return awg_program_string


###################################################################

data_file_name = raw_input('Enter name of data file: ')

data=qt.Data(name=data_file_name)
# data.add_coordinate('Frequency', units = 'Hz')
data.add_coordinate('Drive Frequency', units = 'Hz')
data.add_coordinate('Time', units = 's')

data.add_value('X-Quadrature')
data.add_value('Y-Quadrature')
data.add_value('R-Quadrature')

####################################################################

# OuterMost loop is Pulse Power
outermost_start = 7.02327*GHz - 30*MHz
outermost_stop  = 7.02327*GHz + 30*MHz # One more than the end point you 
outermost_len  =  3
outermost_meta_info = "Frequency (Hz)" 

#####################
outermostloop = np.linspace(outermost_start,outermost_stop,outermost_len) 
len_outermostloop=len(outermostloop) 
data_info=["X","Y","R"] 

##### Initialization of Instruments
# uhf.setup_awg(awg_program())
# uhf.awg_on(single=False)
uhf.set('awgs/0/enable', 0)
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

delay_progress_bar = progressbar.ProgressBar(maxval=len_outermostloop, \
    widgets=['Total: ', progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage(), ' (', progressbar.ETA(), ') '])
delay_progress_bar.start()

first_time = True # to copy script and generate meta file once


for outermost_index, outermost_value in enumerate(outermostloop):
    aps.set_frequency(outermost_value)
    ssb.center_freq = outermost_value
    ssb.optimize_dc()
    qt.msleep(10)
    uhf.setup_awg(awg_program())
    uhf.awg_on(single=False)
    # aps.set_frequency(control)
    rte.reset_averages()
    rte.run_nx_single(wait=True)
    freq_array = np.linspace(outermost_value, outermost_value, record_length)
    time_array, voltages = rte.get_data(channels)
    voltages.append((voltages[0]**2+voltages[1]**2)**0.5)
    data.add_data_point(freq_array, time_array, *voltages)
    if first_time:
        generate_meta_file(outermost_len,outermost_stop)
        copy_script()
    first_time = False
    delay_progress_bar.update(outermost_index+1)
    uhf.set('awgs/0/enable', 0)

data.close_file()
print(time.time()-start)

 