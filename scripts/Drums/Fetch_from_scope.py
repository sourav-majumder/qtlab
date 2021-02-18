from constants import *
import sys
import os
import shutil
import qt
import progressbar
import numpy as np
import time

data_file_name = raw_input('Enter name of data file: ')

rte = qt.instruments.create('RTE1104', 'RhodeSchwartz_RTE1104', address = 'TCPIP0::192.168.1.6::INSTR')

channels = [1,2]


start = time.time()
rte.wait_till_complete()
start_time, stop_time, record_length = rte.get_header()
assert raw_input('continue? [y/n]').upper() != 'N'


rte.reset_averages()
rte.run_nx_single(wait=True)
time_array, voltages = rte.get_data(channels)
x = voltages[0][::2]
y = voltages[1][1::2]
r = (x**2+y**2)**0.5

f = open('D:\\data\\20201213\\injection data\\'+ data_file_name +'.dat', 'w')

for i in np.arange(record_length):
	f.write(str(time_array[i])+'\t'+str(x[i])+'\t'+str(y[i])+'\t'+str(r[i])+'\n')
f.close()