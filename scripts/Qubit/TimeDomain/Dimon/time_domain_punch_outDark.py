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

##############################################

us = 1e-6

def dBm_to_mVolt(dbm):
    return 1000*np.sqrt(10**(dbm/10.0)*0.05)

##############################################

uhf = ZurichInstruments_UHFLI('dev2232')
# znb = qt.instruments.create('ZNB20', 'RhodeSchwartz_ZNB20', address='TCPIP0::192.168.1.3::INSTR')
rte = qt.instruments.create('RTE1104', 'RhodeSchwartz_RTE1104', address = 'TCPIP0::192.168.1.6::INSTR')
# sgs = qt.instruments.create('sgs', 'RS_SGS100A', address = SGS100A_ADDRESS)
# aps = qt.instruments.create('APSYN420',   'AnaPico_APSYN420',         address = APSYN420_ADDRESS)
# fsv = qt.instruments.create('FSV', 'RhodeSchwartz_FSV', address = FSV_ADDRESS)
smf = qt.instruments.create('SMF100', 'RhodeSchwartz_SMF100', address = SMF100_ADDRESS)
aps = qt.instruments.create('APSYN420',   'AnaPico_APSYN420',         address = APSYN420_ADDRESS)

##############################################


def generate_meta_file():
    metafile = open('%s.meta.txt' % data.get_filepath()[:-4], 'w')
    metafile.write('#inner loop\n%s\n%s\n%s\n%s\n'%
            (inner_len,  inner_start, inner_stop, 'Frequency'))
    metafile.write('#outer loop\n%s\n%s\n%s\n%s\n'%
            (outer_len, outer_stop, outer_start, 'Pulse len (samples)'))
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
    const control_power = 1;
    const cycle = 4.4e-9;
    const us = 1e-6;
    const ns = 1e-9;
    const len = 133; //120
    const phase = 1.482180;
    const measure_pulse_length = 10 ; // us
    //Define the frequency.
    wave w1 = sine(1800, 0.95*0.983, phase, 377);
    wave w2 = sine(1800, 0.95*1.0, 0    , 377);
    //Define the envelope.
    wave w_rise = gauss(64,control_power, 64, 16);
    wave w_fall = gauss(64,control_power, 0, 16);
    wave w_rect = rect(len, control_power);
    wave w_join = join(w_rise, w_rect, w_fall);
    //Cut the sine wave.
    wave w_cut1 = cut(w1, 0,127+len);
    wave w_cut2 = cut(w2, 0,127+len);
    //Multiply both sin and envelope.
    wave w_play1 = multiply(w_cut1, w_join);
    wave w_play2 = multiply(w_cut2, w_join);
    while (true) {
      playWave(w_play1, w_play2);
      waitWave();
      wait(14);
      setTrigger(0b0001);
      wait(measure_pulse_length*us/cycle);
      setTrigger(0b0000);
      wait(150*us/cycle);
    }
    """
    return awg_program_string



data_file_name = raw_input('Enter name of data file: ')

data=qt.Data(name=data_file_name)
# data.add_coordinate('Frequency', units = 'Hz')
data.add_coordinate('power', units = 'dBm')
data.add_coordinate('Freq', units = 'Hz')

data.add_value('Integrated power')




#Outerloop  
outer_start = -20
outer_stop  = 23
outer_len = 44
outer_meta_info = "Power" 


#Outerloop  
inner_start = 7.390*GHz
inner_stop  = 7.470*GHz
inner_len = 401
inner_meta_info = "Inner" 
Mix_freq = 133*MHz

#####################
outerloop = np.linspace(outer_start,outer_stop,outer_len) 
innerloop = np.linspace(inner_start,inner_stop,inner_len) 
data_info=["X","Y","R"] 

##### Initialization of Instruments
uhf.setup_awg(awg_program())
uhf.awg_on(single=False)
aps.set_frequency(inner_start - Mix_freq)
smf.rf_on()
aps.rf_on()
channels = [1,2]
# aps.set_frequency(control_array[0])

##Initioalization of sgs
# sgs.set_power(-20)

#############  RUN once to setup the innermost loop

start = time.time()
rte.wait_till_complete()
assert raw_input('continue? [y/n]').upper() != 'N'


###########################################

delay_progress_bar = progressbar.ProgressBar(maxval=outer_len, \
    widgets=['Total: ', progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage(), ' (', progressbar.ETA(), ') '])
delay_progress_bar.start()

first_time = True # to copy script and generate meta file once


for outer_index, outer_value in enumerate(outerloop):
    smf.set_source_power(outer_value)
    outer_value_array = np.linspace(outer_value, outer_value, inner_len)
    trace = []
    for inner_index, inner_value in enumerate(innerloop):
        smf.set_frequency(inner_value)
        aps.set_frequency(inner_value - Mix_freq)
        rte.reset_averages()
        rte.run_nx_single(wait=True)
        time_array, voltages = rte.get_data(channels)
        temp = (voltages[0]**2+voltages[1]**2)**0.5
        trace.append(sum(temp[240:340])/dBm_to_mVolt(outer_value))
    data.add_data_point(outer_value_array, innerloop, trace)
    if first_time:
        generate_meta_file()
        copy_script()
    first_time = False
    delay_progress_bar.update(outer_index+1)

data.close_file()
print(time.time()-start)

 