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
ns = 1e-9

##############################################

uhf = ZurichInstruments_UHFLI('dev2232')
rte = qt.instruments.create('RTE1104', 'RhodeSchwartz_RTE1104', address = 'TCPIP0::192.168.1.6::INSTR')
# aps = qt.instruments.create('APSYN420',   'AnaPico_APSYN420',         address = APSYN420_ADDRESS)
# fsv = qt.instruments.create('FSV', 'RhodeSchwartz_FSV', address = FSV_ADDRESS)
# smf = qt.instruments.create('SMF100', 'RhodeSchwartz_SMF100', address = SMF100_ADDRESS)
# aps = qt.instruments.create('APSYN420',   'AnaPico_APSYN420',         address = APSYN420_ADDRESS)
# znb = qt.instruments.create('ZNB20', 'RhodeSchwartz_ZNB20', address=ZNB20_ADDRESS)

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
            (outer_index, outer_value, outerloop[0], outer_meta_info))
    metafile.write('#outermost loop\n%s\n%s\n%s\n%s\n'%
            (outermost_index, outermostloop[0], outermost_value, outermost_meta_info))

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

def get_IQ():
    with open('Qubit/optimize_data_update.txt', 'r') as f:
        lines = f.read().splitlines()
        print('**** Reading the last calibration ****')
        last_line = lines[-1].split(' ')
        ph = float(last_line[4])
    return ph


ph = get_IQ()

def awg_program(gap, ph = ph):
    awg_program_string = """
    const gap = %d;
    const phase = %f;
    const cycle = 4.4e-9;
    const us = 1e-6;
    const ns = 1e-9;
    const measure_pulse_length = 10 ; // us
    //Define the frequency.
    wave w1 = sine(64*1000, 1.0, phase, 6*1000);
    wave w2 = sine(64*1000, 1.0, 0    , 6*1000);
    //Gaussian pulse.
    wave w_gauss_piby2 = gauss(128, 0.5 , 64, 16);
    wave w_gauss_pi = gauss(128, 1.0 , 64, 16);
    wave w_zeros = zeros(gap);
    wave w_join = join(w_gauss_piby2 , w_gauss_pi, w_gauss_piby2);
    //Cut the sin wave as the envelope length.
    wave w_cut1 = cut(w1, 0, 383);
    wave w_cut2 = cut(w2, 0, 383);
    //Multiply both sin and envelope.
    wave w_play1 = multiply(w_cut1, w_join);
    wave w_play2 = multiply(w_cut2, w_join);
    //Final
    wave w_use1 = join(cut(w_play1, 0, 127), w_zeros, cut(w_play1, 128, 255), w_zeros, cut(w_play1, 256, 383));
    wave w_use2 = join(cut(w_play2, 0, 127), w_zeros, cut(w_play2, 128, 255), w_zeros, cut(w_play2, 256, 383));
    while (true) {
      playWave(w_use1, w_use2);
      waitWave();
      wait(14);
      setTrigger(0b0001);
      wait(measure_pulse_length*us/cycle);
      setTrigger(0b0000);
      wait(150*us/cycle);
    }
    """%(gap//2,ph)
    return awg_program_string



data_file_name = raw_input('Enter name of data file: ')

data=qt.Data(name=data_file_name)
# data.add_coordinate('Frequency', units = 'Hz')
data.add_coordinate('Power', units = '%')
data.add_coordinate('Time', units = 's')

data.add_value('X-Quadrature')
data.add_value('Y-Quadrature')
data.add_value('R-Quadrature')

####################################################################


# OuterMost loop is Pulse Power
outermost_start = 4.721*GHz
outermost_stop  = 4.721*GHz  # One more than the end point you 
outermost_len  =  1
outermost_meta_info = "Frequency (Hz)" 

#Outerloop is delay between measure and control (cycles) 
outer_start = 0
outer_stop  = 500
outer_len = 26
outer_meta_info = "Control Power"

#####################
outermostloop = np.linspace(outermost_start,outermost_stop,outermost_len) 
outerloop = np.linspace(outer_start,outer_stop,outer_len) 
len_outermostloop=len(outermostloop) 
len_outerloop=len(outerloop) 
data_info=["X","Y","R"] 

##### Initialization of Instruments
uhf.setup_awg(awg_program(1))
uhf.awg_on(single=False) 
channels = [1,2]
# aps.set_frequency(control_array[0])

#############  RUN once to setup the innermost loop

start = time.time()
# rte.wait_till_complete()
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


first_time = True # to copy script and generate meta file once

for outermost_index, outermost_value in enumerate(outermostloop):
    #Stuff can be added here to execute a 3D loop
    outermost_value_array = np.linspace(outermost_value, outermost_value, record_length)
    for outer_index, outer_value in enumerate(outerloop):
        uhf.setup_awg(awg_program(outer_value))
        uhf.awg_on(single=False)
        rte.reset_averages()
        rte.run_nx_single(wait=True)
        outer_value_array = np.linspace(outer_value, outer_value, record_length)
        time_array, voltages = rte.get_data(channels)
        voltages.append((voltages[0]**2+voltages[1]**2)**0.5)
        data.add_data_point(outer_value_array, time_array, *voltages)
        if first_time:
            generate_meta_file(outer_len, outer_stop, outermost_len,outermost_stop)
            copy_script()
        first_time = False
        delay_progress_bar.update(outer_index+1)

delay_progress_bar.finish()
data.close_file()
print(time.time()-start)

 