import qt
import time

from constants import *
from ZurichInstruments_UHFLI import ZurichInstruments_UHFLI
import timeout_decorator
from scipy.optimize import minimize
from noisyopt import minimizeCompass

def lo_power(dc):
	uhf.set('sigouts/0/offset', float(dc[0]))
	uhf.set('sigouts/1/offset', float(dc[1]))
	# qt.msleep(0.1)
	_ , power = fsv.get_max_freqs(1)
	return power[0]

def get_power():
	qt.msleep(0.1)
	_ , power = fsv.get_max_freqs(1)
	return power[0]

# @timeout_decorator.timeout(10)
def optimize_i_dc(prev_pow = 0):
	i_dc = uhf.get('sigouts/0/offset')
	power = get_power()
	diff = power - prev_pow
	inc = 1.
	while (abs(diff) > 0.01 and abs(inc) > 0.005):
		uhf.set('sigouts/0/offset', float(i_dc+inc*1e-3))
		prev_pow = power
		power = get_power()
		diff = power - prev_pow
		if (diff > 0):
			inc = -0.5*inc
		i_dc = uhf.get('sigouts/0/offset')
	return prev_pow

# @timeout_decorator.timeout(10)
def optimize_q_dc(prev_pow = 0):
	q_dc = uhf.get('sigouts/1/offset')
	power = get_power()
	diff = power - prev_pow
	inc = 1.
	while (abs(diff) > 0.01 and abs(inc) > 0.005):
		uhf.set('sigouts/1/offset', float(q_dc+inc*1e-3))
		prev_pow = power
		power = get_power()
		diff = power - prev_pow
		if (diff > 0):
			inc = -0.5*inc
		q_dc = uhf.get('sigouts/1/offset')
	return prev_pow

#################################
# PARAMETERS
#################################
center_freq = 6*GHz

#################################
#################################
#################################
fsv = qt.instruments.create('FSV', 'RhodeSchwartz_FSV', address = FSV_ADDRESS, reset=True)
# aps = qt.instruments.create('APSYN420',	'AnaPico_APSYN420',			address = APSYN420_ADDRESS,	reset=True)
uhf = ZurichInstruments_UHFLI('dev2232', reset=True) # Initializing UHFLI
fsv.set_centerfrequency(center_freq)
fsv.set_span(2*MHz)
fsv.set_bandwidth(10*kHz)
fsv.marker_to_max()
freq, power = fsv.get_max_freqs(1)
# uhf.set('sigouts/0/offset', -10.28e-3)
# uhf.set('sigouts/1/offset', -12.89e-3)

start = time.time()
power = optimize_i_dc()
power = optimize_q_dc(power)
# res = minimizeCompass(lo_power, x0=[0,0], bounds=((-0.75,0.75),(-0.75,0.75)), paired=False, deltatol=0.01)
# res = minimize(lo_power, x0=[-0.5,0.5], bounds=((-0.75,0.75),(-0.75,0.75)))
print time.time()-start