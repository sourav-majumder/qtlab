import qt
import numpy as np
import shutil
import sys
import os
import time

kHz=KHz=1e3;
MHz=1e6;
GHz=1e9;

#center =7.46*GHz
#span= 8*GHz
num_points = 5001
start_power = -20 #dBm
end_power = -20 #dBm
power_points = 1
if_bw= 1000
average_count = 1

#start_freq=center-span/2
#stop_freq=center+span/2

start_freq = 4*GHz
stop_freq = 8*GHz
# power = -30
#numpoints=3
# if_bw=300

def generate_meta_file(i,starttime=0,endtime=0):
    metafile = open('%s.meta.txt' % data.get_filepath()[:-4], 'w')
    metafile.write('#inner loop\n%s\n%s\n%s\n%s\n'%
            (num_points, start_freq, stop_freq, 'Frequency(Hz)'))
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

znb = qt.instruments.create('ZNB20', 'RhodeSchwartz_ZNB20', address='TCPIP0::192.168.1.3::INSTR')
znb.reset()
znb.set_start_frequency(start_freq)
znb.set_stop_frequency(stop_freq)
# znb.set_center_frequency(center)
# znb.set_span(span)
znb.set_source_power(start_power)
znb.set_sweep_mode('single')
znb.set_if_bandwidth(if_bw)
znb.add_trace('S21')
# znb.set_average_mode('FLAT')
# znb.set_averages(average_count)
# znb.sweep_number(average_count)
znb.set_numpoints(num_points)
znb.rf_on()
#qt.msleep(60)


dataname='While_cooling_down2'
data=qt.Data(name=dataname)
data.add_comment('sweeptime= '+str(znb.get_sweeptime()) + 'no of points : ' + str(num_points))
data.add_coordinate('Time', units='s')
data.add_coordinate('frequency', units='Hz')
data.add_value('S21 real')
data.add_value('S21 imag')
data.add_value('S21 abs')
data.add_value('S21 phase')





try:
    starttime=time.time()
    i=1
    while True:
        znb.send_trigger(wait=True)
        znb.autoscale()
        print 'trigger count  '+str(i)
        dd=znb.get_data('S21')
        data.add_data_point(np.repeat(time.time(),num_points), np.linspace(start_freq,stop_freq,num_points),np.real(dd),np.imag(dd),np.abs(dd),np.angle(dd))
        generate_meta_file(i,starttime=0,endtime=time.time()-starttime)
        qt.msleep(60)
        if i==201: break
        i+=1
except KeyboardInterrupt:
    print '\nInterrupted'
    endtime=time.time()
    generate_meta_file(i,endtime-starttime,0)
    print 'starttime = '+str(starttime)
    print 'endtime = '+str(endtime)

shutil.copy2('%s'%sys.argv[0],'%s/%s'%(data.get_filepath()[:-(len(dataname)+11)],os.path.basename(sys.argv[0])))
data.close_file()
