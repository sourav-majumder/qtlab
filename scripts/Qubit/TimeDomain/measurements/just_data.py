from constants import *
from ZurichInstruments_UHFLI import ZurichInstruments_UHFLI
import sys
import os
import shutil
import qt


def generate_meta_file():
    metafile = open('%s.meta.txt' % data.get_filepath()[:-4], 'w')
    metafile.write('#inner loop\n%s\n%s\n%s\n%s\n'%
            (record_length,  start_time/us, stop_time/us, 'Time(us)'))
    metafile.write('#outer loop\n1\n0\n1\nNothing\n')
    metafile.write('#outermost loop (unused)\n1\n0\n1\nNothing\n')

    metafile.write('#for each of the values\n')
    values = data.get_values()
    i=0
    while i<len(values):
        metafile.write('%d\n%s\n'% (i+4, values[i]['name']))
        i+=1
    metafile.close()

def copy_script():
    shutil.copy2('%s'%sys.argv[0],'%s/%s'%(data.get_filepath()[:-(len(data_file_name)+11)],os.path.basename(sys.argv[0])))



rte = qt.instruments.create('RTE1104', 'RhodeSchwartz_RTE1104', address = 'TCPIP0::192.168.1.6::INSTR')
data_file_name = raw_input('Enter name of data file: ')

data=qt.Data(name=data_file_name)
# data.add_coordinate('Frequency', units = 'Hz')
data.add_coordinate('Time', units = 's')
data.add_value('X-Quadrature')
# data.add_value('Y-Quadrature')
# data.add_value('R-Quadrature')
channels = [1]
rte.wait_till_complete()
start_time, stop_time, record_length = rte.get_header()
assert raw_input('continue? [y/n]').upper() != 'N'
data_info=["X"] 
rte.reset_averages()
rte.run_nx_single(wait=True)
time_array, voltages = rte.get_data(channels)
# voltages.append((voltages[0]**2+voltages[1]**2)**0.5)
data.add_data_point(time_array, *voltages)
# try presetting scope if the below error occurs
# WARNING  add_data_point(): not all provided data arguments have same shape
generate_meta_file()
# copy_script()
data.close_file()
