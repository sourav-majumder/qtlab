import qt

from constants import *

rte = qt.instruments.create('RTE1104', 'RhodeSchwartz_RTE1104', address='TCPIP0::192.168.1.6::INSTR')

rte.reset()
rte.ch_off(1)


# Add Time per Division
# Example : time_per_div = 10*ns
# Add list of channels to turn on
# Example : channels = [1,2]
channels = [1,2]

# Add gain and position information per channel if known
# Example : volt_per_div = [0.4, 0.8]
# Example : ch_position = [2, -3]
volt_per_div = [0.4, 0.8]
ch_position = [2, -3]

# Add Trigger source and level. Options are 1-5. 1-4 : Channel 1-4, 5:External
# Example : trig_source = 5
# Example : trig_level = 0.7
trig_source = 2
trig_level = 0.7

for ch in channels:
	rte.coupling_50(ch)
	getattr(rte, 'set_volt_per_div%d' % ch)(volt_per_div[ch-1])
	getattr(rte, 'set_ch_position%d' % ch)(ch_position[ch-1])

if trig_source < 5:
	rte.set_trig_source('CHAN%d' % trig_source)
elif trig_source == 5:
	rte.set_trig_source('EXT')
getattr(rte, 'set_trig_level%d' % trig_source)(trig_level)

# Turn on channels
for ch in channels:
	rte.ch_on(ch)

# Setup Averaging

rte.average_mode(True)
rte.set_count(1e3)

yarr = []
rte.reset_averages()
for i in range(100):
	rte.run_nx_single(wait=True)
	x, y1 = rte.get_data(1)
	yarr.append(y1)

import matplotlib.pyplot as plt

plt.imshow(yarr, aspect='auto')
plt.show()
