import sys
import qt
from constants import *

center = 5*GHz
span = 8*GHz
num_points = 2001

znb = qt.instruments.create('ZNB20', 'RhodeSchwartz_ZNB20', address='TCPIP0::192.168.1.3::INSTR')
znb.reset()
znb.set_center_frequency(center)
znb.set_span(span)
znb.set_numpoints(num_points)
filename='Soumya'
data=qt.Data(name=filename)
data.add_coordinate('Index')
data.add_coordinate('Frequency', units='Hz')
data.add_value('S21 real')
data.add_value('S21 imag')
data.add_value('S21 abs')
data.add_value('S21 phase')
bla= np.linspace(0,2000,num_points)
freq_array= np.linspace(center-span/2,center+span/2,num_points)
znb.rf_on()

i=0
while i<10:
	znb.send_trigger(wait=True)
	database=znb.get_data("S21")
	data.add_data_point(bla, freq_array, np.real(database), np.imag(database),np.absolute(database), np.angle(database))
	i+=1

def generate_meta_file():
    metafile = open('%s.meta.txt' % data.get_filepath()[:-4], 'w')
    metafile.write('#inner loop\n%s\n%s\n%s\n%s\n'%
            (num_points,center-span/2,center+span/2, 'Frequency(Hz)'))
    metafile.write('#outer loop\n%s\n%s\n%s\n%s\n'%
            (10, 1, 10, 'Power(dBm)'))
    metafile.write('#outermost loop (unused)\n1\n0\n1\nNothing\n')

    metafile.write('#for each of the values\n')
    values = data.get_values()
    i=0
    while i<len(values):
        metafile.write('%d\n%s\n'% (i+3, values[i]['name']))
        i+=1
    metafile.close()
generate_meta_file()
data.close_file()