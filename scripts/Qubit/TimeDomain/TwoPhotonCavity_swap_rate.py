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

##############################################

uhf = ZurichInstruments_UHFLI('dev2232')
rte = qt.instruments.create('RTE1104', 'RhodeSchwartz_RTE1104', address = 'TCPIP0::192.168.1.6::INSTR')
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
            (outer_index, outer_value, outerloop[0], 'Pulse lngth (sample)'))
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



def awg_program(length, flux):
    awg_program_string = """
    const control_power = 1;
    const length = %d;
    const flux = %f;
    const flux_power1 = (223.0-14.0)/750.0;
    const flux_power2 = (flux-14.0)/750.0;
    const cycle = 4.4e-9;
    const us = 1e-6;
    const ns = 1e-9;
    const len  = 100;

    wave w_rise = gauss(64,control_power, 64, 16);
    wave w_fall = gauss(64,control_power, 0, 16);
    wave w_flat = rect(len, control_power);
    wave w_join = join(w_rise ,w_flat, w_fall);

    wave w_rise1 = gauss(8, flux_power1, 8, 1);
    wave w_fall1 = gauss(8, flux_power1, 0, 1);
    wave w_flat1 = rect(5, flux_power1);
    wave w_pulse1 = join(w_rise1, w_flat1, w_fall1);

    wave w_rise2 = gauss(8, flux_power2, 8, 1);
    wave w_fall2 = gauss(8, flux_power2, 0, 1);
    wave w_flat2 = rect(length, flux_power2);
    wave w_pulse2 = join(w_rise2, w_flat2, w_fall2);

    const measure_pulse_length = 10 ; // us
    while (true) {
      playWave(1,w_join);
      waitWave();
      playWave(2,w_pulse1);
      waitWave();
      playWave(1,w_join);
      waitWave();
      playWave(2,w_pulse2);
      waitWave();
      wait(12);
      setTrigger(0b0010);
      wait(measure_pulse_length*us/cycle);
      setTrigger(0b0000);
      wait(200*us/cycle);
    }
    """%(length,flux)
    return awg_program_string





####################################################################
#mix_freq = 88*MHz
#power = 240

# OuterMost loop is Pulse Power
outermost_start = 219
outermost_stop  = 230 # One more than the end point you 
outermost_len  = 12
outermost_meta_info = "Frequency (Hz)" 

#Outerloop is delay between measure and control (cycles) 
outer_start = 0
outer_stop  = 60
outer_len = 61
outer_meta_info = "pulse_power" 

#####################
outermostloop = np.linspace(outermost_start,outermost_stop,outermost_len) 
outerloop = np.linspace(outer_start,outer_stop,outer_len) 
len_outermostloop=len(outermostloop) 
len_outerloop=len(outerloop) 
data_info=["X","Y","R"] 

##### Initialization of Instruments
uhf.setup_awg(awg_program(0,214))
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




for outermost_index, outermost_value in enumerate(outermostloop):
    #Stuff can be added here to execute a 3D loop
    data_file_name = 'Two_photon_swap_flux_%0.2f'%outermost_value
    data=qt.Data(name=data_file_name)
    # data.add_coordinate('Frequency', units = 'Hz')
    data.add_coordinate('Delay', units = 's')
    data.add_coordinate('Time', units = 's')
    data.add_value('X-Quadrature')
    data.add_value('Y-Quadrature')
    data.add_value('R-Quadrature')
    delay_progress_bar = progressbar.ProgressBar(maxval=len_outerloop, \
    widgets=['Total: ', progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage(), ' (', progressbar.ETA(), ') '])
    delay_progress_bar.start()
    first_time = True # to copy script and generate meta file once
    for outer_index, outer_value in enumerate(outerloop):
        uhf.setup_awg(awg_program(outer_value, outermost_value))
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
    data.close_file()
    print(time.time()-start)

 