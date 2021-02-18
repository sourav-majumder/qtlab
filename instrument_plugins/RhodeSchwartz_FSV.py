from instrument import Instrument
from visa import VisaIOError
import visa
import types
import logging
import numpy as np

import qt

class FSV_Exception(Exception):
	pass

class RhodeSchwartz_FSV(Instrument):
	'''
	This is the driver for the Rohde & Schwarz FSV Signal Analyzer.

	Usage:
	Initialize with
	<name> = qt.instruments.create('<name>', 'RhodeSchwartz_FSV',
		address='TCPIP::<IP-address>::INSTR',
		reset=<bool>,)

	For GPIB the address is: 'GPIB<interface_nunmber>::<gpib-address>'
	'''
	def __init__(self, name, address, reset=False):
		
		# Initialize wrapper functions
		logging.info('Initializing instrument Rhode & Schwarz FSV Signal Generator')
		Instrument.__init__(self, name, tags=['physical'])

		# Add some global constants
		self._address = address
		self._default_timeout = 2000 # ms
		self._visainstrument = visa.ResourceManager().open_resource(self._address,
																	timeout=self._default_timeout)
		self._freq_unit = 1
		self._freq_unit_symbol = 'Hz'

		# Add parameters
		self.add_parameter('centerfrequency', type=types.FloatType,
			flags=Instrument.FLAG_GETSET | Instrument.FLAG_GET_AFTER_SET,
			minval=10, maxval=13.6e9,
			units='Hz')
		self.add_parameter('span', type=types.FloatType,
			flags=Instrument.FLAG_GETSET | Instrument.FLAG_GET_AFTER_SET,
			minval=0, maxval=13.6e9, 
			units='Hz')
		self.add_parameter('referencelevel', type=types.FloatType,
			flags=Instrument.FLAG_GETSET | Instrument.FLAG_GET_AFTER_SET,
			minval=-130, maxval=0,
			units='dBm', format='%.04e')
		self.add_parameter('mode', type=types.StringType,
			flags=Instrument.FLAG_GETSET | Instrument.FLAG_GET_AFTER_SET,
			format_map = {
							"SAN" : "Spectrum",
							"IQ" : "IQ Analyzer",
							"PNO" : "Phase Noise"
						  })
		self.add_parameter('continuous_sweep', type=types.BooleanType,
						  flags=Instrument.FLAG_GETSET|Instrument.FLAG_GET_AFTER_SET)
		self.add_parameter('sweep_points', type=types.IntType,
						   flags=Instrument.FLAG_GETSET|Instrument.FLAG_GET_AFTER_SET,
						   minval=101, maxval=32001)
		self.add_parameter('bandwidth', type=types.FloatType,
							flags=Instrument.FLAG_GETSET | Instrument.FLAG_GET_AFTER_SET,
							minval=1, maxval=10e6,
							units='Hz', format='%d')

	def get_instrument(self):
		return self._visainstrument

	def reset(self):
		self._visainstrument.write('*RST')

	def markers_to_peaks(self, no_of_peaks=3):
		for i in range(8):
			self._visainstrument.write('CALC:MARK%d OFF' % (i+1))
		for i in range(no_of_peaks):
			self._visainstrument.write('CALC:MARK%d ON' % (i+1))

	def marker_to_max(self):
		self.markers_to_peaks(1)

	def set_marker_frequency(self, freq):
		self._visainstrument.write('CALC:MARK1:X %dHz' % freq+';*WAI')

	def set_markerN_frequency(self,n, freq):
		self._visainstrument.write('CALC:MARK%d:X %dHz' %(n, freq))

	def marker_next(self, marker=1):
		if not int(self._visainstrument.query('CALC:MARK%d?' % (marker)).strip()):
				raise FSV_Exception('Marker %d is not on' % (marker))
		self._visainstrument.write('CALC:MARK%d:MAX:NEXT' % marker)

	def get_max_freqs(self, no_of_peaks=3):
		xvals = []
		yvals = []
		for i in range(no_of_peaks):
			if not int(self._visainstrument.query('CALC:MARK%d?' % (i+1)).strip()):
				raise FSV_Exception('Marker %d is not on' % (i+1))
			xvals.append(float(self._visainstrument.query('CALC:MARK%d:X?' % (i+1)).strip()))
			yvals.append(float(self._visainstrument.query('CALC:MARK%d:Y?' % (i+1)).strip()))
		return xvals, yvals

	# communication with machine
	def do_get_centerfrequency(self):
		'''
		Get center frequency from device

		Input:
			None

		Output:
			centerfrequency (float) : center frequency in Hz
		'''
		logging.debug(__name__ + ' : reading center frequency from instrument')
		return float(self._visainstrument.ask('FREQ:CENT?'))

	def do_set_centerfrequency(self, centerfrequency):
		'''
		Set center frequency of device

		Input:
			centerfrequency (float) : center frequency in Hz

		Output:
			None
		'''
		logging.debug(__name__ + ' : setting center frequency to %s Hz' % centerfrequency)
		self._visainstrument.write('FREQ:CENT %f' % centerfrequency+';*WAI')

	def do_get_span(self):
		'''
		Get span from device

		Input:
			None

		Output:
			span (float) : span in Hz
		'''
		logging.debug(__name__ + ' : reading span from instrument')
		return float(self._visainstrument.ask('FREQ:SPAN?'))

	def do_set_span(self,span):
		'''
		Set span of device

		Input:
			span (float) : span in Hz

		Output:
			None
		'''
		logging.debug(__name__ + ' : setting span to %s Hz' % span)
		self._visainstrument.write('FREQ:SPAN %e' % span)

	def do_get_referencelevel(self):
		'''
		Get reference level from device

		Input:
			None

		Output:
			referencelevel (float) : reference level in dBm
		'''
		logging.debug(__name__ + ' : reading referencelevel from instrument')
		return float(self._visainstrument.ask('DISP:TRAC:Y:RLEV?'))

	def do_set_referencelevel(self,referencelevel):
		'''
		Set referencelevel of device

		Input:
			referencelevel (float) : reference level in dBm(??)

		Output:
			None
		'''
		logging.debug(__name__ + ' : setting referencelevel to %s dBm' % referencelevel)
		self._visainstrument.write('DISP:TRAC:Y:RLEV %e' % referencelevel)

	def do_get_mode(self):
		'''
		Get mode from device

		Input:
			None

		Output:
			mode (float) : reference level in dBm
		'''
		logging.debug(__name__ + ' : reading mode from instrument')
		return self._visainstrument.ask('INST?').strip()

	def do_set_mode(self,mode):
		'''
		Set mode of device

		Input:
			mode (float) : mode

		Output:
			None
		'''
		logging.debug(__name__ + ' : setting sweep_mode to %s' % mode)
		self._visainstrument.write('INST %s' % mode)

	def do_get_continuous_sweep(self):
		'''
		Get continuous_sweep from device

		Input:
			None

		Output:
			continuous_sweep (float) : reference level in dBm
		'''
		logging.debug(__name__ + ' : reading continuous_sweep from instrument')
		return int(self._visainstrument.ask('INIT:CONT?').strip())

	def do_set_continuous_sweep(self, continuous_sweep):
		'''
		Set continuous_sweep of device

		Input:
			continuous_sweep (float) : continuous_sweep

		Output:
			None
		'''
		logging.debug(__name__ + ' : setting continuous_sweep to %r' % continuous_sweep)
		if continuous_sweep:
			string = 'ON'
		else:
			string = 'OFF'
		self._visainstrument.write('INIT:CONT %s' % string)

	def do_get_sweep_points(self):
		'''
		Get sweep_points from device

		Input:
			None

		Output:
			sweep_points (float) : reference level in dBm
		'''
		logging.debug(__name__ + ' : reading sweep_points from instrument')
		return int(self._visainstrument.ask('SWE:POIN?').strip())

	def get_sweep_time(self):
		'''
		 Get the sweep time in Seconds

		'''
		logging.debug(__name__ + ' : reading sweep_time from instrument')
		return float(self._visainstrument.ask('SWE:TIME?').strip())


	def do_set_sweep_points(self, sweep_points):
		'''
		Set sweep_points of device

		Input:
			sweep_points (float) : sweep_points

		Output:
			None
		'''
		logging.debug(__name__ + ' : setting sweep_points to %d' % sweep_points)
		self._visainstrument.write('SWE:POIN %d' % sweep_points)

	def do_get_bandwidth(self):
		'''
		Get bandwidth from device

		Input:
			None

		Output:
			bandwidth (float) : reference level in dBm
		'''
		logging.debug(__name__ + ' : reading bandwidth from instrument')
		return int(self._visainstrument.ask('BAND?').strip())

	def do_set_bandwidth(self, bandwidth):
		'''
		Set bandwidth of device

		Input:
			bandwidth (float) : bandwidth

		Output:
			None
		'''
		logging.debug(__name__ + ' : setting bandwidth to %d' % bandwidth)
		self._visainstrument.write('BAND %d' % bandwidth)

	def wait_till_complete(self):
		try:
			self._visainstrument.query('*ESR?')
			self._visainstrument.write('*OPC')

			sweeptime=self.get_sweep_time()*self.get_sweep_count()
			qt.msleep(sweeptime-2.)
			while int(self._visainstrument.query('*ESR?').strip())%2==0:
					qt.msleep(0.1)
		except VisaIOError:
			print ('FSV timed out. It may be preparing the sweep.\nPress enter to start the sweep.')
			raw_input()
			self.run_single(wait=True)
		except KeyboardInterrupt:
			raise Exception('Interrupted in middle of sweep')

	def get_data(self):
		logging.debug(__name__ + ' : fetching data')
		center = self.get_centerfrequency()
		span = self.get_span()
		npoints = self.get_sweep_points()
		#self.run_single(wait=True)
		xvals = np.linspace(center-span/2.0, center+span/2.0, npoints)
		yvals = self._visainstrument.query('TRAC? TRACE1').split(',')
		yvals = map(float,yvals)
		return xvals, yvals

	def run_single(self, wait=False):
		'''
		Trigger a single Sweep
		'''
		self._visainstrument.write('INIT:CONT OFF')
		self._visainstrument.write('INIT;*WAI')
		if wait:
			self.wait_till_complete()

	def set_sweep_mode_avg(self, mode = 'LIN'):
		logging.debug(__name__ + ' : setting mode to AVG')
		self._visainstrument.write('DISP:TRAC:MODE AVER')
		self._visainstrument.write('SENS:AVER:TYPE %s'%mode)

	def set_sweep_count(self, counts):
		logging.debug(__name__ + ' : setting sweep count to %d'%counts)
		self._visainstrument.write('SWE:COUN %s'%counts)

	def get_sweep_count(self):
		# logging.debug(__name__ + ' : setting sweep count to %d'%counts)
		return int(self._visainstrument.ask('SWE:COUN?'))

	def w(self, string):
		return self._visainstrument.write(string)

