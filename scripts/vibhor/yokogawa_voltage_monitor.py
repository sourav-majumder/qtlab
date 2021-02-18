import qt
import numpy as np
import matplotlib.pyplot as plt

qs2 = qt.instruments.create('GS820', 'Yokogawa_GS820', address ='USB0::0x0B21::0x002C::91W700679::INSTR')

f = open(r'D:\data\20210108\tracking.txt', 'w+')

for i in np.arange(1000):
	val = qs2.measure()
	print(val)
	f.write(str(val)+'\n')
	qt.msleep(2)

f.close()