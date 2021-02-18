import qt
import numpy as np
import shutil
import sys
import os
import time

KHz=1e3;
MHz=1e6;
GHz=1e9;

freq=8.007632*GHz
span=1.0*MHz
power=0
numpoints=1001

def generate_meta_file(i,starttime=0,endtime=0):
    metafile = open('%s.meta.txt' % data.get_filepath()[:-4], 'w')
    metafile.write('#inner loop\n%s\n%s\n%s\n%s\n'%
            (numpoints, freq-span/2, freq+span/2, 'Frequency(Hz)'))
    metafile.write('#outer loop\n%s\n%s\n%s\n%s\n'%
            (i, endtime, starttime, 'Time(s)'))
    metafile.write('#outermost loop (unused)\n1\n0\n1\nNothing\n')

    metafile.write('#for each of the values\n')
    values = data.get_values()
    i=0
    while i<len(values):
        metafile.write('%d\n%s\n'% (i+3, values[i]['name']))
        i+=1
    metafile.close()

znb = qt.instruments.create('ZNB20', 'RhodeSchwartz_ZNB20', address='TCPIP0::10.1.1.20::INSTR')
znb.reset()
znb.set_center_frequency(freq)
znb.set_span(span)
znb.set_source_power(power)
znb.set_numpoints(numpoints)
znb.set_sweep_mode('single')

dataname='Warming up the frigde'
data=qt.Data(name=dataname)
data.add_comment('sweeptime= '+str(znb.get_sweeptime))
data.add_coordinate('frequency', units='Hz')
data.add_value('S21 real')
data.add_value('S21 imag')
data.add_value('S21 abs')
data.add_value('S21 phase')

if_bw=300*KHz
znb.set_if_bandwidth(if_bw)



try:
    starttime=time.time()
    i=1
    while True:
        znb.send_trigger(wait=True)
        dd=znb.get_data('S21')
        data.add_data_point(np.linspace(freq-span/2,freq+span/2,numpoints),np.real(dd),np.imag(dd),np.abs(dd),np.angle(dd))
        generate_meta_file(i)
        qt.msleep(10)
        i+=1
except :
    print '\nInterrupted'
    endtime=time.time()
    generate_meta_file(i,endtime-starttime,0)
    print 'starttime = '+str(starttime)
    print 'endtime = '+str(endtime)

data.close_file()
