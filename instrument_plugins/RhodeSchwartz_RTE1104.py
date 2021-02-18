from instrument import Instrument
import visa
import types
import logging
import numpy as np

import qt

class RTE1104Exception(Exception):
	pass
class RTE1104NotExactException(Exception):
	pass

class RhodeSchwartz_RTE1104(Instrument):
	'''
	This is the driver for the Rhode & Schwartz RTE 1104 Oscilloscope.

	Usage:
	Initialize with
	<name> = qt.instruments.create('<name>', 'RhodeSchwartz_RTE1104',
		address='TCPIP::<IP-address>::INSTR',
		reset=<bool>,)

	For GPIB the address is: 'GPIB<interface_nunmber>::<gpib-address>'
	'''
	def __init__(self, name, address, reset=False, interpolation=False):

		# Initialize wrapper functions
		logging.info('Initializing instrument Rohde & Schwarz FSL RTE 1104 Oscilloscope.')
		Instrument.__init__(self, name, tags=['physical'])

		# Add some global constants
		self._address = address
		self._default_timeout = 4000 # ms
		self._visainstrument = visa.ResourceManager().open_resource(self._address,
																	timeout=self._default_timeout)

		self._time_unit = 1
		self._time_unit_symbol = 's'
		self._volt_unit = 1
		self._volt_unit_symbol = 'V'

		self.add_parameter('time_per_div', type=types.FloatType, format='%.12f',
						   flags=Instrument.FLAG_GETSET|Instrument.FLAG_GET_AFTER_SET,
						   units=self._time_unit, minval=25e-12, maxval=5e3)
		self.add_parameter('acquisition_time', type=types.FloatType, format='%.12f',
						   flags=Instrument.FLAG_GETSET|Instrument.FLAG_GET_AFTER_SET,
						   units=self._time_unit, minval=250e-12, maxval=5e4)
		self.add_parameter('trigger_time_pos', type=types.FloatType, format='%.12f',
						   flags=Instrument.FLAG_GETSET|Instrument.FLAG_GET_AFTER_SET,
						   units=self._time_unit, minval=-100e24, maxval=100e24)
		self.add_parameter('reference_pos', type=types.IntType, format='%d',
						   flags=Instrument.FLAG_GETSET|Instrument.FLAG_GET_AFTER_SET,
						   minval=0, maxval=100)
		self.add_parameter('resolution', type=types.FloatType, format='%.11f',
						   flags=Instrument.FLAG_GETSET|Instrument.FLAG_GET_AFTER_SET,
						   units=self._time_unit, minval=1e-15, maxval=0.5)
		self.add_parameter('sample_rate', type=types.IntType, format='%d',
						   flags=Instrument.FLAG_GETSET|Instrument.FLAG_GET_AFTER_SET,
						   minval=2, maxval=2e12)
		self.add_parameter('record_length', type=types.IntType, format='%d',
						   flags=Instrument.FLAG_GETSET|Instrument.FLAG_GET_AFTER_SET,
						   minval=1e3, maxval=1e9)
		self.add_parameter('ch_state', type=types.BooleanType, channels=(1,4),
							flags=Instrument.FLAG_GETSET|Instrument.FLAG_GET_AFTER_SET)
		self.add_parameter('ch_coupling', type=types.StringType, channels=(1,4),
							flags=Instrument.FLAG_GETSET|Instrument.FLAG_GET_AFTER_SET,
							format_map = {
								"DC" : "Direct connection with 50 ohm termination.",
								"DCL" : "Direct connection with 1 Mega ohm termination.",
								"AC" : "Connection through DC capacitor."
							})
		self.add_parameter('volt_per_div', type=types.FloatType, format='%.3f', channels=(1,4),
						   flags=Instrument.FLAG_GETSET|Instrument.FLAG_GET_AFTER_SET,
						   units=self._volt_unit, minval=5e-4, maxval=1)
		self.add_parameter('ch_position', type=types.FloatType, format='%.2f', channels=(1,4),
						   flags=Instrument.FLAG_GETSET|Instrument.FLAG_GET_AFTER_SET,
						   minval=-5, maxval=5)
		self.add_parameter('ch_bandwidth', type=types.StringType, channels=(1,4),
						   flags=Instrument.FLAG_GETSET|Instrument.FLAG_GET_AFTER_SET,
						   format_map = {
								"FULL" : "Use full bandwidth.",
								"B200" : "Limit to 200 MHz.",
								"B20" : "Limit to 20 MHz."
						   })
		self.add_parameter('trig_mode', type=types.StringType,
						   flags=Instrument.FLAG_GETSET|Instrument.FLAG_GET_AFTER_SET,
						   format_map = {
								"AUTO" : "The instrument triggers repeatedly after a time interval if the trigger \
										  conditions are not fulfilled. If a real trigger occurs, it takes \
										  precedence. The time interval depends on the time base.",
								"NORM" : "The instrument acquires a waveform only if a trigger occurs.",
								"FRE" : "The instrument triggers after a very short time interval - faster \
										than in AUTO mode. Real triggers are ignored."
						   })
		self.add_parameter('trig_source', type=types.StringType,
						   flags=Instrument.FLAG_GETSET|Instrument.FLAG_GET_AFTER_SET,
						   format_map = {
								"CHAN1" : "Channel 1",
								"CHAN2" : "Channel 2",
								"CHAN3" : "Channel 3",
								"CHAN4" : "Channel 4",
								"EXT" : "External Analog Trigger"
						   })
		self.add_parameter('trig_level', type=types.FloatType, format='%.3f', channels=(1,5), # CHAN 1-4, 5:EXTernal
						   flags=Instrument.FLAG_GETSET|Instrument.FLAG_GET_AFTER_SET)
		self.add_parameter('trig_slope', type=types.StringType,
						   flags=Instrument.FLAG_GETSET|Instrument.FLAG_GET_AFTER_SET,
						   format_map = {
								"POS" : "Positive Edge",
								"NEG" : "Negative Edge",
								"EITH" : "Either"
						   })
		self.add_parameter('trig_holdoff_mode', type=types.StringType,
						   flags=Instrument.FLAG_GETSET|Instrument.FLAG_GET_AFTER_SET,
						   format_map = {
								"TIME" : "Holdoff for some time",
								"EVEN" : "Holfoff for a numer of events",
								"RAND" : "Holdoff for a random time",
								"AUTO" : "Holdoff time depending on time scale",
								"OFF" : "No Holdoff"
						   })
		self.add_parameter('trig_holdoff_time', type=types.FloatType, format='%.7f',
						   flags=Instrument.FLAG_GETSET|Instrument.FLAG_GET_AFTER_SET,
						   minval=100e-9, maxval=10)
		self.add_parameter('trig_holdoff_events', type=types.IntType,
						   flags=Instrument.FLAG_GETSET|Instrument.FLAG_GET_AFTER_SET,
						   minval=1, maxval=2147483647)
		self.add_parameter('trig_hysterisis', type=types.StringType,
						   flags=Instrument.FLAG_GETSET|Instrument.FLAG_GET_AFTER_SET,
						   format_map = {
								"AUTO" : "Automatic Hysterisis",
								"MAN" : "Manual Hysterisis"
						   })
		self.add_parameter('trig_hysterisis_mode', type=types.StringType,
						   flags=Instrument.FLAG_GETSET|Instrument.FLAG_GET_AFTER_SET,
						   format_map = {
								"ABS" : "Absolute Hysterisis in Volts",
								"REL" : "Relative Hysterisis in Divisions"
						   })
		self.add_parameter('trig_hysterisis_abs', type=types.FloatType, format='%.3f',
						   flags=Instrument.FLAG_GETSET|Instrument.FLAG_GET_AFTER_SET,
						   minval=0, maxval=1)
		self.add_parameter('trig_hysterisis_rel', type=types.IntType, format='%d',
						   flags=Instrument.FLAG_GETSET|Instrument.FLAG_GET_AFTER_SET,
						   minval=0, maxval=50)
		self.add_parameter('ext_ref', type=types.BooleanType,
							flags=Instrument.FLAG_GETSET|Instrument.FLAG_GET_AFTER_SET)
		self.add_parameter('ch_skew', type=types.FloatType, format='%.12f', channels=(1,4),
						   flags=Instrument.FLAG_GETSET|Instrument.FLAG_GET_AFTER_SET,
						   minval=-100e-9, maxval=100e9)
		self.add_parameter('arithmetic', type=types.StringType,
						   flags=Instrument.FLAG_GETSET|Instrument.FLAG_GET_AFTER_SET,
						   format_map = {
								"OFF" : "No Arithmetic",
								"ENV" : "Envelope",
								"AVER" : "Average Mode"
						   })
		self.add_parameter('count', type=types.IntType, format='%d',
						   flags=Instrument.FLAG_GETSET|Instrument.FLAG_GET_AFTER_SET,
						   minval=1, maxval=16777215)

		if reset:
			self.reset()
		if interpolation:
			self.interpolation(True)
		else:
			self.interpolation(False)

# --------------------------------------
#           functions
# --------------------------------------
	def reset(self):
		'''
		Resets the RTE1104 to default settings.
		'''
		logging.debug('Resetting ...')
		self._visainstrument.write('*RST')
		self.ch_off(1)
		self.interpolation(False)
		self.set_trig_mode('NORM')

	def get_instrument(self):
		'''
		Returns the instrument object directly to make queries.
		Note: This function should only be used for testing purposes
		since it does not go through qtlab.
		'''
		return self._visainstrument

	def interpolation(self, state):
		'''
		Sets the interpolation on of off.
		'''
		if state:
			int_str = 'ITIM'
		else:
			int_str = 'RTIM'
		self._visainstrument.write('ACQ:MODE %s' % int_str)

	def reset_averages(self):
		'''
		Forces the immediate restart of the envelope and average calculation for all waveforms.
		'''
		self._visainstrument.write('ACQ:ARE:IMM')

	def run_continuous(self):
		'''
		Starts acquiring waveforms continuosly
		'''
		self._visainstrument.write('RUN')

	def wait_till_complete(self):
		'''
		Waits till all operations are completed.
		'''
		# try:
		self._visainstrument.query('*ESR?')
		self._visainstrument.write('*OPC')
		count = self.get_count()
		acq_data = int(self._visainstrument.query('ACQ:CURR?').strip())
		qt.msleep((count-acq_data)/70000.)
		while int(self._visainstrument.query('*ESR?').strip())%2==0:
			qt.msleep(0.1)

	def run_nx_single(self, n=None, wait=False):
		'''
		Starts acquiring n waveforms.
		'''
		if n is not None:
			self.set_count(n)
		self._visainstrument.write('SING')
		if wait:
			self.wait_till_complete()

	def stop_acquisition(self):
		'''
		Stop acquisition.
		'''
		self._visainstrument.write('STOP')

	def do_get_time_per_div(self, **kwargs):
		'''
		Returns the Time Scale in <time_units>/division.
		'''
		logging.debug('Reading Time Scale')
		return float(self._visainstrument.query('TIM:SCAL?').strip())/self._time_unit

	def do_set_time_per_div(self, tpd, exact=False):
		'''
		Sets the Time Scale to the desired one.
		'''
		logging.debug('Setting Time Scale to %f %s/div' % (tpd/self._time_unit, self._time_unit_symbol))
		self._visainstrument.write('TIM:SCAL %.12f' % (tpd/self._time_unit))
		if exact and self.get_time_per_div() != tpd/self._time_unit:
			raise RTE1104NotExactException('The value has not been set exactly.')
		self.get_time_per_div()
		self.get_acquisition_time()

	def do_get_acquisition_time(self, **kwargs):
		'''
		Returns the Acquisition Time for each run.
		'''
		logging.debug('Reading Acquisition Time')
		return float(self._visainstrument.query('TIM:RANG?').strip())/self._time_unit

	def do_set_acquisition_time(self, acq_time, exact=False):
		'''
		Sets the Acquisition Time for each run.
		'''
		logging.debug('Setting Acquisition Time to %f %s' % (acq_time/self._time_unit, self._time_unit_symbol))
		self._visainstrument.write('TIM:RANG %.12f' % (acq_time/self._time_unit))
		if exact and self.get_acquisition_time() != acq_time/self._time_unit:
			raise RTE1104NotExactException('The value has not been set exactly.')
		self.get_time_per_div()
		self.get_acquisition_time()

	def do_get_trigger_time_pos(self):
		'''
		Returns the time distance between the reference point and the trigger point (the zero
		point of the diagram). The reference point marks the rescaling center of the time scale.
		'''
		logging.debug('Reading Reference Time Posision')
		return float(self._visainstrument.query('TIM:HOR:POS?').strip())/self._time_unit

	def do_set_trigger_time_pos(self, tpd):
		'''
		Sets the time distance between the reference point and the trigger point (the zero
		point of the diagram). The reference point marks the rescaling center of the time scale.
		'''
		logging.debug('Setting Reference Time Position to %f %s' % (tpd/self._time_unit, self._time_unit_symbol))
		self._visainstrument.write('TIM:HOR:POS %.12f' % (tpd/self._time_unit))
		self.get_trigger_time_pos()

	def do_get_resolution(self, **kwargs):
		'''
		Returns the time between two waveform points in the record.
		'''
		logging.debug('Reading the resolution.')
		return float(self._visainstrument.query('ACQ:RES?').strip())

	def do_set_resolution(self, res, exact=False):
		'''
		Sets the time between two waveform points in the record.
		'''
		logging.debug('Setting the resolution to %e' % res)
		self._visainstrument.write('ACQ:RES %e' % res)
		if exact and self.get_resolution() != res/self._time_unit:
			raise RTE1104NotExactException('The value has not been set exactly.')
		self.get_resolution()
		self.get_sample_rate()
		self.get_record_length()

	def do_get_reference_pos(self):
		'''
		Returns the position of the reference point in % of the screen. The reference point marks
		the rescaling center of the time scale. If you modify the time scale, the reference point
		remains fixed on the screen, and the scale is stretched or compresses to both sides of
		the reference point.
		'''
		logging.debug('Reading Reference position')
		return int(self._visainstrument.query('TIM:REF?').strip())

	def do_set_reference_pos(self, ref_pos):
		'''
		Sets the position of the reference point in % of the screen. The reference point marks
		the rescaling center of the time scale. If you modify the time scale, the reference point
		remains fixed on the screen, and the scale is stretched or compresses to both sides of
		the reference point.
		'''
		logging.debug('Setting the Reference Position to %d%%' % ref_pos)
		self._visainstrument.write('TIM:REF %d' % ref_pos)
		self.get_reference_pos()

	def do_get_sample_rate(self, **kwargs):
		'''
		Returns the sample rate, that is the number of recorded waveform samples per second.
		'''
		logging.debug('Reading the Sample Rate')
		return int(self._visainstrument.query('ACQ:SRAT?').strip())

	def do_set_sample_rate(self, srate, exact=False):
		'''
		Sets the sample rate, that is the number of recorded waveform samples per second.
		'''
		logging.debug('Setting the sample rate to %d Sa/s' % srate)
		self._visainstrument.write('ACQ:SRAT %d' % srate)
		if exact and self.get_sample_rate() != srate:
			raise RTE1104NotExactException('The value has not been set exactly.')
		self.get_sample_rate()
		self.get_resolution()
		self.get_record_length()

	def do_get_record_length(self, **kwargs):
		'''
		Returns the record length, the number of recorded waveform points that build the
		waveform across the acquisition time.
		'''
		logging.debug('Reading the record length')
		return int(self._visainstrument.query('ACQ:POIN?').strip())

	def do_set_record_length(self, length, exact=False):
		'''
		Sets the record length, the number of recorded waveform points that build the
		waveform across the acquisition time.
		'''
		logging.debug('Setting the record length to %e Sa' % length)
		self._visainstrument.write('ACQ:POIN %d' % length)
		if exact and self.get_record_length() != length:
			raise RTE1104NotExactException('The value has not been set exactly.')
		self.get_record_length()
		self.get_resolution()
		self.get_sample_rate()

	def do_get_ch_state(self, channel):
		'''
		Returns the Channel State (ON or OFF).
		'''
		logging.debug('Reading the Status of channel %d' % channel)
		return self._visainstrument.query('CHAN%d:STAT?' % channel).strip()=='ON'

	def do_set_ch_state(self, state, channel):
		'''
		Sets the Channel state (ON or OFF).
		'''
		logging.debug('Setting the Status of channel %d to %r' % (channel, state))
		if state:
			state_str = 'ON'
		elif not state:
			state_str = 'OFF'
		else:
			raise RTE1104Exception('Value must be boolean')
		self._visainstrument.write('CHAN%d:STAT %s' % (channel, state_str))

	def ch_on(self, channel):
		'''
		Turns on selected channel.
		'''
		on_func = getattr(self, 'set_ch_state%d' % channel)
		on_func(True)

	def ch_off(self, channel):
		'''
		Turns off selected channel.
		'''
		off_func = getattr(self, 'set_ch_state%d' % channel)
		off_func(False)

	def do_get_ch_coupling(self, channel):
		'''
		Returns the Channel Coupling.
		'''
		logging.debug('Reading the Coupling on channel %d' % channel)
		return self._visainstrument.query('CHAN%d:COUP?' % channel).strip()

	def do_set_ch_coupling(self, coupling, channel):
		'''
		Sets the Channel Coupling.
		'''
		logging.debug('Setting the Coupling of channel %d to %s' % (channel, coupling))
		self._visainstrument.write('CHAN%d:COUP %s' % (channel, coupling))

	def coupling_50(self, channel):
		'''
		Sets the Channel Coupling to 50 ohm.
		'''
		set_coupling = getattr(self, 'set_ch_coupling%d' % channel)
		set_coupling('DC')

	def do_get_volt_per_div(self, channel):
		'''
		Returns the Voltage Scale of the channel in <volt_units>/division.
		'''
		logging.debug('Reading the Voltage per divion on channel %d' % channel)
		return float(self._visainstrument.query('CHAN%d:SCAL?' % channel).strip())/self._volt_unit

	def do_set_volt_per_div(self, scale, channel):
		'''
		Sets the Voltage Scale of the channel in <volt_units>/division.
		'''
		logging.debug('Setting the Voltage Scale on Channel %d to %f %s/div' % (channel, scale, self._volt_unit_symbol))
		self._visainstrument.write('CHAN%d:SCAL %f' % (channel, scale))
		get_volt_div = getattr(self, 'get_volt_per_div%d' % channel)
		get_volt_div()

	def do_get_ch_position(self, channel):
		'''
		Returns the vertical position of the channel.
		'''
		logging.debug('Reading the vertical position of channel %d' % channel)
		return float(self._visainstrument.query('CHAN%d:POS?' % channel).strip())

	def do_set_ch_position(self, position, channel):
		'''
		Sets the vertical position of the channel.
		'''
		logging.debug('Setting the vertical position of channel %d to %f' % (channel, position))
		self._visainstrument.write('CHAN%d:POS %f' % (channel, position))

	def do_get_ch_bandwidth(self, channel):
		'''
		Returns the channel bandwidth (FULL|B200|B20).
		'''
		logging.debug('Reading the bandwidth of channel %d' % channel)
		return self._visainstrument.query('CHAN%d:BAND?' % channel).strip()
 
	def do_set_ch_bandwidth(self, bw, channel):
		'''
		Sets the channel bandwidth (FULL|B200|B20).
		'''
		logging.debug('Setting the bandwidth of channel %d to %s' % (channel, bw))
		self._visainstrument.write('CHAN%d:BAND %s' % (channel, bw))

	def do_get_trig_mode(self):
		'''
		Returns the trigger mode (AUTO|NORM|FRE).
		'''
		logging.debug('Reading the trigger mode')
		return self._visainstrument.query('TRIG:MODE?').strip()

	def do_set_trig_mode(self, mode):
		'''
		Sets the trigger mode (AUTO|NORM|FRE).
		'''
		logging.debug('Setting the trigger mode to %s' % mode)
		self._visainstrument.write('TRIG:MODE %s' % mode)

	def do_get_trig_source(self):
		'''
		Returns the trigger source.
		'''
		logging.debug('Reading the trigger source')
		return self._visainstrument.query('TRIG1:SOUR?').strip()
 
	def do_set_trig_source(self, source):
		'''
		Sets the trigger source.
		'''
		logging.debug('Setting the trigger source to %s' % source)
		self._visainstrument.write('TRIG1:SOUR %s' % source)

	def set_ext_trig(self):
		'''
		Sets the trigger source to external.
		'''
		self.set_trig_source('EXT')
		self._visainstrument.write('TRIG1:TYPE EDGE')

	def do_get_trig_level(self, channel):
		'''
		Returns the trigger level for the specified source 1-4 : Channel 1-4, 5: External Trigger.
		'''
		if channel == 5:
			source_str = 'External Trigger'
		else:
			source_str = 'Channel %d' % channel
		logging.debug('Reading the trig level for %s' % source_str)
		return float(self._visainstrument.query('TRIG1:LEVEL%d?' % channel).strip())

	def do_set_trig_level(self, level, channel):
		'''
		Sets the trigger level for the specified source 1-4 : Channel 1-4, 5: External Trigger.
		'''
		if channel == 5:
			source_str = 'External Trigger'
		else:
			source_str = 'Channel %d' % channel
		logging.debug('Setting the trig level for %s to %f' % (source_str, level))
		self._visainstrument.write('TRIG1:LEVEL%d %f' % (channel, level))

	def do_get_trig_slope(self):
		'''
		Returns the trigger slope.
		'''
		logging.debug('Reading the slope of the trigger')
		return self._visainstrument.query('TRIG1:EDGE:SLOP?')

	def do_set_trig_slope(self, slope):
		'''
		Sets the trigger slope.
		'''
		logging.debug('Setting the trigger slope to %s' % slope)
		self._visainstrument.write('TRIG1:EDGE:SLOP %s' % slope)

	def do_get_trig_holdoff_mode(self):
		'''
		Returns the Trigger holdoff mode (TIME|EVEN|RAND|AUTO|OFF).
		'''
		logging.debug('Reading the trigger holdoff mode')
		return self._visainstrument.query('TRIG:HOLD:MODE?').strip()

	def do_set_trig_holdoff_mode(self, mode):
		'''
		Sets the Trigger holdoff mode (TIME|EVEN|RAND|AUTO|OFF).
		'''
		logging.debug('Setting the trigger holdoff mode to %s' % mode)
		self._visainstrument.write('TRIG:HOLD:MODE %s' % mode)

	def do_get_trig_holdoff_time(self):
		'''
		Returns the trigger holdoff time.
		'''
		logging.debug('Reading the trigger holdoff time')
		return self._visainstrument.query('TRIG:HOLD:TIME?')

	def do_set_trig_holdoff_time(self, time):
		'''
		Sets the trigger holdoff time.
		'''
		logging.debug('Setting the trigger holdoff time to %e' % time)
		self._visainstrument.write('TRIG:HOLD:TIME %e' % time)

	def do_get_trig_holdoff_events(self):
		'''
		Returns the trigger holdoff events.
		'''
		logging.debug('Reading the trigger holdoff events')
		return self._visainstrument.query('TRIG:HOLD:EVEN?')

	def do_set_trig_holdoff_events(self, events):
		'''
		Sets the trigger holdoff events.
		'''
		logging.debug('Setting the trigger holdoff events to %d' % events)
		self._visainstrument.write('TRIG:HOLD:EVEN %d' % events)

	def do_get_trig_hysterisis(self):
		'''
		Returns the trigger hysterisis type
		'''
		logging.debug('Reading the trigger hysterisis type')
		trig_source_str = self.get_trig_source()
		if 'CHAN' in trig_source_str:
			trig_source = int(trig_source_str[-1])
		elif trig_source_str == 'EXT':
			trig_source = 5
		else:
			raise RTE1104Exception('Do not know how to get hysterisis type for trigger source : %s' % trig_source_str)
		return self._visainstrument.query('TRIG:LEV%d:NOIS?' % trig_source).strip()

	def do_set_trig_hysterisis(self, typ):
		'''
		Sets the trigger hysterisis type
		'''
		logging.debug('Setting the trigger hysterisis type to %s' % typ)
		trig_source_str = self.get_trig_source()
		if 'CHAN' in trig_source_str:
			trig_source = int(trig_source_str[-1])
		elif trig_source_str == 'EXT':
			trig_source = 5
		else:
			raise RTE1104Exception('Do not know how to set hysterisis type for trigger source : %s' % trig_source_str)
		self._visainstrument.write('TRIG:LEV%d:NOIS %s' % (trig_source, typ))

	def do_get_trig_hysterisis_mode(self):
		'''
		Returns the trigger hysterisis mode (ABS|REL).
		'''
		logging.debug('Reading the trigger hysterisis mode.')
		trig_source_str = self.get_trig_source()
		if 'CHAN' in trig_source_str:
			trig_source = int(trig_source_str[-1])
		elif trig_source_str == 'EXT':
			trig_source = 5
		else:
			raise RTE1104Exception('Do not know how to get hysterisis mode for trigger source : %s' % trig_source_str)
		return self._visainstrument.query('TRIG:LEV%d:NOIS:MODE?' % trig_source).strip()

	def do_set_trig_hysterisis_mode(self, mode):
		'''
		Sets the trigger hysterisis mode (ABS|REL).
		'''
		logging.debug('Setting the trigger hysterisis mode to %s' % mode)
		trig_source_str = self.get_trig_source()
		if 'CHAN' in trig_source_str:
			trig_source = int(trig_source_str[-1])
		elif trig_source_str == 'EXT':
			trig_source = 5
		else:
			raise RTE1104Exception('Do not know how to set hysterisis mode for trigger source : %s' % trig_source_str)
		self._visainstrument.write('TRIG:LEV%d:NOIS:MODE %s' % (trig_source, mode))

	def do_get_trig_hysterisis_abs(self):
		'''
		Returns the absolute trigger hysterisis.
		'''
		logging.debug('Reading the absolute trigger hysterisis.')
		trig_source_str = self.get_trig_source()
		if 'CHAN' in trig_source_str:
			trig_source = int(trig_source_str[-1])
		elif trig_source_str == 'EXT':
			trig_source = 5
		else:
			raise RTE1104Exception('Do not know how to get hysterisis for trigger source : %s' % trig_source_str)
		return float(self._visainstrument.query('TRIG:LEV%d:NOIS:ABS?' % trig_source).strip())

	def do_set_trig_hysterisis_abs(self, hysterisis):
		'''
		Sets the absolute trigger hysterisis.
		'''
		logging.debug('Setting the absolute trigger hysterisis to %e' % hysterisis)
		trig_source_str = self.get_trig_source()
		if 'CHAN' in trig_source_str:
			trig_source = int(trig_source_str[-1])
		elif trig_source_str == 'EXT':
			trig_source = 5
		else:
			raise RTE1104Exception('Do not know how to set hysterisis for trigger source : %s' % trig_source_str)
		self._visainstrument.write('TRIG:LEV%d:NOIS:ABS %e' % (trig_source, hysterisis))

	def do_get_trig_hysterisis_rel(self):
		'''
		Returns the relative trigger hysterisis.
		'''
		logging.debug('Reading the relative trigger hysterisis.')
		trig_source_str = self.get_trig_source()
		if 'CHAN' in trig_source_str:
			trig_source = int(trig_source_str[-1])
		elif trig_source_str == 'EXT':
			trig_source = 5
		else:
			raise RTE1104Exception('Do not know how to get hysterisis for trigger source : %s' % trig_source_str)
		return int(self._visainstrument.query('TRIG:LEV%d:NOIS:REL?' % trig_source).strip())

	def do_set_trig_hysterisis_rel(self, hysterisis):
		'''
		Sets the relative trigger hysterisis.
		'''
		logging.debug('Setting the relative trigger hysterisis to %e' % hysterisis)
		trig_source_str = self.get_trig_source()
		if 'CHAN' in trig_source_str:
			trig_source = int(trig_source_str[-1])
		elif trig_source_str == 'EXT':
			trig_source = 5
		else:
			raise RTE1104Exception('Do not know how to set hysterisis for trigger source : %s' % trig_source_str)
		self._visainstrument.write('TRIG:LEV%d:NOIS:REL %d' % (trig_source, hysterisis))
	
	def do_get_ext_ref(self):
		'''
		Returns the state of the reference clock.
		'''
		logging.debug('Reading the state of the reference clock.')
		return self._visainstrument.query('SENS:SOUR?').strip() == 'ON'

	def do_set_ext_ref(self, state):
		'''
		Sets the state of the reference clock.
		'''
		logging.debug('Setting the state of the reference clock to %r' % state)
		if state:
			state_str = 'ON'
		else:
			state_str = 'OFF'
		self._visainstrument.write('SENS:SOUR %s' % state_str)

	def do_get_ch_skew(self, channel):
		'''
		Returns the skew for the channel.
		'''
		logging.debug('Reading the skew for the channel %d' % channel)
		return float(self._visainstrument.query('CHAN%d:SKEW:TIME?' % channel).strip())

	def do_set_ch_skew(self, skew, channel):
		'''
		Sets the skew for the channel.
		'''
		logging.debug('Setting the skew for the channel %d to %e' % (channel, skew))
		if skew == 0.:
			self._visainstrument.write('CHAN%d:SKEW:MAN OFF' % channel)
		else:
			self._visainstrument.write('CHAN%d:SKEW:MAN ON' % channel)
		self._visainstrument.write('CHAN%d:SKEW:TIME %e' % (channel, skew))

	def do_get_arithmetic(self):
		'''
		Returns the arithmetic setting on the waveforms.
		'''
		logging.debug('Reading the arithmetic setting on the waveforms.')
		return self._visainstrument.query('CHAN:ARIT?').strip()

	def do_set_arithmetic(self, setting):
		'''
		Sets the arithmetic setting on the waveforms.
		'''
		logging.debug('Setting the arithmetic setting on the waveforms to %s' % setting)
		self._visainstrument.write('CHAN:ARIT %s' % setting)

	def average_mode(self, state):
		'''
		Sets arithmetic to average or off.
		'''
		if state:
			self.set_arithmetic('AVER')
		else:
			self.set_arithmetic('OFF')

	def do_get_count(self):
		'''
		Returns the number of waveforms to be collected/averaged.
		'''
		logging.debug('Reading the acquisition count.')
		return int(self._visainstrument.query('ACQ:COUN?').strip())

	def do_set_count(self, count):
		'''
		Sets the number of waveforms to be collected/averaged.
		'''
		logging.debug('Setting the acquisition count to %d' % count)
		self._visainstrument.write('ACQ:COUN %d' % count)

	def get_data(self, channels):
		'''
		Returns:

		xvals : array of time values
		yvals : array of y-values
		'''
		logging.debug('Getting data')
		
		xstart, xstop, xnum = self.get_header()

		xvals = np.linspace(xstart, xstop, xnum)

		yvals = []
		for channel in channels:
			values = self._visainstrument.query('CHAN%d:DATA?' % channel).strip()
			yvals.append(np.fromstring(values, dtype=float, sep=','))

		return xvals, yvals

	def get_header(self, channel = 1):
		'''
		Returns xstart, xstop, numpoints.
		'''
		header = self._visainstrument.query('CHAN:DATA:HEAD?').strip().split(',')
		xstart = float(header[0])
		xstop = float(header[1])
		xnum = int(header[2])

		return xstart, xstop, xnum

	def setup_scope(self, channels,
					volt_per_div,
					ch_position,
					time_per_div,
					resolution):
		'''
		Sets up the View and the trigger.
		'''
		for ch in channels:
			self.coupling_50(ch)
			getattr(self, 'set_volt_per_div%d' % ch)(volt_per_div[ch-1])
			getattr(self, 'set_ch_position%d' % ch)(ch_position[ch-1])
		self.set_time_per_div(time_per_div)
		self.set_resolution(resolution)
		for ch in channels:
			self.ch_on(ch)

	def w(self, arg):
		'''
		Forces the immediate restart of the envelope and average calculation for all waveforms.
		'''
		self._visainstrument.write(arg)


	def q(self, arg ):
		'''
		Forces the immediate restart of the envelope and average calculation for all waveforms.
		'''
		return self._visainstrument.query(arg)

	def save_shots_local(self, shots = 10):
		'''
		It saves all acquisition to a local folder on the disk.

		'''
		self.w('STOP;*OPC?')
		self.w('EXPort:WAVeform:FASTexport ON')
		self.w('CHAN:WAV:STATe 1')
		self.w('EXP:WAV:MULT ON')
		self.w('EXPort:WAVeform:SCOPe WFM')
		self.w("EXPort:WAVeform:NAME 'C:\\Users\\Instrument.RTE-XXXXXX.000\\Desktop\\transfer\\test.csv'")
		self.w('EXPort:WAVeform:RAW OFF')
		self.w('EXPort:WAVeform:DLOGging OFF')
		self.w('ACQuire:COUNt %d' % shots)
		self.w('RUNSingle;*OPC?')
		self.w('CHAN:HISTory:STATe ON')
		first =-1*shots+1
		self.w('CHAN:HISTory:CURRent %d;*OPC?'% first)
		self.w('CHAN:HISTory:STOP 0')
		self.w('CHAN:HISTory:REPLay OFF')
		self.w('EXPort:WAVeform:SAVE')
