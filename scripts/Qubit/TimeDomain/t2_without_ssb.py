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
sgs = qt.instruments.create('sgs', 'RS_SGS100A', address = SGS100A_ADDRESS)
# aps = qt.instruments.create('APSYN420',   'AnaPico_APSYN420',         address = APSYN420_ADDRESS)
# fsv = qt.instruments.create('FSV', 'RhodeSchwartz_FSV', address = FSV_ADDRESS)
# smf = qt.instruments.create('SMF100', 'RhodeSchwartz_SMF100', address = SMF100_ADDRESS)
# aps = qt.instruments.create('APSYN420',   'AnaPico_APSYN420',         address = APSYN420_ADDRESS)

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
            (outer_index, outer_value, outerloop[0], 'Delay (us)'))
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


def awg_program(delay):
    awg_program_string = """
    const control_power = 1;
    const cycle = 4.4e-9;
    const us = 1e-6;
    const ns = 1e-9;
    const len  = 55;
    const maadi = %d;
    const measure_pulse_length = 10 ; // us
    wave w_rise = gauss(32,control_power, 32, 8);
    wave w_fall = gauss(32,control_power, 0, 8);
    wave w_flat = rect(len, control_power);
    wave w_join = join(w_rise ,w_flat, w_fall);
    while (true) {
      playWave(w_join);
      waitWave();
      wait(maadi);
      playWave(w_join);
      waitWave();
      wait(14);
      setTrigger(0b0010);
      wait(measure_pulse_length*us/cycle);
      setTrigger(0b0000);
      wait(200*us/cycle);
    }
    """%(delay)
    return awg_program_string

###################################################################

# def optimize(qubit_freq):
#     # mix_freq = (sampling rate) x (number of oscillations) / (sample points)
#     mix_freq = 1.8e9*6/128.
#     opt.center_freq = qubit_freq+mix_freq
#     opt.mix_freq = mix_freq
#     opt.sideband = 'left'
#     aps.set_frequency(opt.center_freq)
#     # i_dc, q_dc, phase, i_amp, q_amp = opt.optimize_all()
#     return opt.optimize_all()

###################################################################

data_file_name = raw_input('Enter name of data file: ')

data=qt.Data(name=data_file_name)
# data.add_coordinate('Frequency', units = 'Hz')
data.add_coordinate('Delay', units = 's')
data.add_coordinate('Time', units = 's')

data.add_value('X-Quadrature')
data.add_value('Y-Quadrature')
data.add_value('R-Quadrature')

####################################################################
# mix_freq = 88*MHz
power = 240

# OuterMost loop is Qubit frequency
outermost_start = 7.595510*GHz
outermost_stop  = 7.595510*GHz  # One more than the end point you 
outermost_len  =  1
outermost_meta_info = "Frequency (Hz)" 

#Outerloop is delay between measure and control (cycles) 
outer_start = 0
outer_stop  = 5*us/(4.4*ns)  # 4.4*3 us 
outer_len = 51
outer_meta_info = "Delay (us)" 

#####################
outermostloop = np.linspace(outermost_start,outermost_stop,outermost_len) # qubit frequency loop
outerloop = np.linspace(outer_start,outer_stop,outer_len)  # delay loop
len_outermostloop=len(outermostloop) 
len_outerloop=len(outerloop) 
data_info=["X","Y","R"] 

##### Initialization of Instruments
uhf.setup_awg(awg_program(0))
uhf.awg_on(single=False)
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

first_time = True # to copy script and generate meta file once




# control_length = float(raw_input('Please enter last used phase : '))
# max_i_amp = uhf.get('awgs/0/outputs/0/amplitude')
# max_q_amp = uhf.get('awgs/0/outputs/1/amplitude')
# uhf.set('awgs/0/outputs/0/amplitude', 40/100.*max_i_amp)
# uhf.set('awgs/0/outputs/1/amplitude', 40/100.*max_q_amp)
# # phase = -1.710238;

for outermost_index, outermost_value in enumerate(outermostloop):
    #Stuff can be added here to execute a 3D loop
    # sgs.set_frequency(outermost_value)
    outermost_value_array = np.linspace(outermost_value, outermost_value, record_length)
    for outer_index, outer_value in enumerate(outerloop):
        # i_amp = outer_value/100*max_i_amp
        # q_amp = outer_value/100*max_q_amp
        
        uhf.setup_awg(awg_program(delay=outer_value))
        uhf.awg_on(single=False)
        # aps.set_frequency(control)
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

# uhf.set('awgs/0/outputs/0/amplitude', max_i_amp)
# uhf.set('awgs/0/outputs/1/amplitude', max_q_amp)
data.close_file()
print(time.time()-start)

 