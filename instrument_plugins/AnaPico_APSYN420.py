from instrument import Instrument
import visa
import types
import logging

import qt

class AnaPico_APSYN420(Instrument):
	'''
	This is the driver for the AnaPico APSYN 420 Signal Generator.

	Usage:
	Initialize with
	<name> = qt.instruments.create('<name>', 'AnaPico_ASPYN420',
		address='TCPIP::<IP-address>::INSTR',
		reset=<bool>,)

	For GPIB the address is: 'GPIB<interface_nunmber>::<gpib-address>'
	'''
	def __init__(self, name, address, reset=False):
		
		# Initialize wrapper functions
		logging.info('Initializing instrument AnaPico APSYN 420 Signal Generator')
		Instrument.__init__(self, name, tags=['physical'])

		# Add some global constants
		self._address = address
		self._default_timeout = 12000 # ms
		self._visainstrument = visa.ResourceManager().get_instrument(self._address)#,
																	#timeout=self._default_timeout)
		self._freq_unit = 1
		self._freq_unit_symbol = 'Hz'
		self.source_power = 20 # dBm

		self.add_parameter('blanking', type=types.BooleanType,
                          flags=Instrument.FLAG_GETSET|Instrument.FLAG_GET_AFTER_SET)
		self.add_parameter('output', type=types.BooleanType,
                          flags=Instrument.FLAG_GETSET|Instrument.FLAG_GET_AFTER_SET)
		self.add_parameter('frequency', type=types.FloatType, format='%.6e',
						   flags=Instrument.FLAG_GETSET|Instrument.FLAG_GET_AFTER_SET,
						   units=self._freq_unit_symbol, minval=0.65e9/self._freq_unit, maxval=20.4e9/self._freq_unit)
		self.add_parameter('pulm_state', type=types.BooleanType,
                          flags=Instrument.FLAG_GETSET|Instrument.FLAG_GET_AFTER_SET)
		self.add_parameter('pulm_polarity', type=types.StringType,
                          flags=Instrument.FLAG_GETSET|Instrument.FLAG_GET_AFTER_SET,
                          format_map = {
                            "NORM" : "Normal",
                            "INV" : "Inverted"
                          })
		self.add_parameter('pulm_source', type=types.StringType,
                          flags=Instrument.FLAG_GETSET|Instrument.FLAG_GET_AFTER_SET,
                          format_map = {
                            "INT" : "Internal",
                            "EXT" : "External"
                          })

		if reset:
			self.reset()

	# def __del__(self):
	# 	self._visainstrument.close()

# --------------------------------------
#           functions
# --------------------------------------
	def remove(self):
		self._visainstrument.close()
		super(AnaPico_APSYN420, self).remove()
		
	def reset(self):
		'''
		Resets the APSYN420 to default settings.
		'''
		logging.debug('Resetting ...')
		self._visainstrument.write('*RST')

	def get_instrument(self):
		'''
		Returns the instrument object directly to make queries.
		Note: This function should only be used for testing purposes
		since it does not go through qtlab.
		'''
		return self._visainstrument

	def do_get_blanking(self):
		'''
		Returns the blanking state.
		'''
		return int(self._visainstrument.query('OUTP:BLAN?').strip) == 1

	def do_set_blanking(self, state):
		'''
		Sets the blanking state.
		'''
		logging.debug('Setting blanking %r' % state)
		self._visainstrument.write('OUTP:BLAN %d' % state)

	def do_get_output(self):
		'''
		Returns the output state.
		'''
		logging.debug('Reading the output state.')
		return int(self._visainstrument.query('OUTP?').strip()) == 1
	
	def do_set_output(self, state):
		'''
		Sets the output state.
		'''
		logging.debug('Setting the output state to %r' % state)
		self._visainstrument.write('OUTP %d' % state)

	def rf_on(self):
		'''
		Turns on RF output.
		'''
		self.set_output(True)

	def rf_off(self):
		'''
		Turns off RF output.
		'''
		self.set_output(False)

	def do_get_frequency(self):
		'''
		Returns the frequency.
		'''
		logging.debug('Reading the frequency.')
		return float(self._visainstrument.query('FREQ?').strip())

	def do_set_frequency(self, freq):
		'''
		Sets the frequency.
		'''
		logging.debug('Setting the frequency to %e.' % freq)
		self._visainstrument.write('FREQ %e' % freq)

	def do_get_pulm_state(self):
		'''
		Returns the Pulse Modulation State.
		'''
		logging.debug('Reading the pulse modulation state.')
		return int(self._visainstrument.query('PULM:STAT?').strip()) == 1

	def do_set_pulm_state(self, state):
		'''
		Sets the Pulse Modulation State.
		'''
		logging.debug('Setting the pulse modulation state to %r.' % state)
		self._visainstrument.write('PULM:STAT %d' % state)

	def do_get_pulm_polarity(self):
		'''
		Returns pulse modulation polarity.
		'''
		logging.debug('Reading Pulse Modulation Polaity Status')
		return self._visainstrument.query('PULM:POL?')

	def do_set_pulm_polarity(self, polarity):
		'''
		Sets the desired polarity for pulse modulation.
		'''
		polarity = polarity.strip().upper()
		logging.debug('Setting the Pulse Modulation Polarity to %s' % polarity)
		self._visainstrument.write('PULM:POL %s' % polarity)

	def do_get_pulm_source(self):
		'''
		Returns pulse modulation source.
		'''
		logging.debug('Reading Pulse Modulation Source Status')
		return self._visainstrument.query('PULM:SOUR?')

	def do_set_pulm_source(self, source):
		'''
		Sets the desired source for pulse modulation.
		'''
		source = source.strip().upper()
		logging.debug('Setting the Pulse Modulation Source to %s' % source)
		self._visainstrument.write('PULM:SOUR %s' % source)

	def do_get_pulm_int_period(self):
		'''
		Returns internal pulse modulation period.
		'''
		logging.debug('Reading the Internal Pulse Modulation Period.')
		return float(self._visainstrument.query('PULM:INT:PER').strip())

	def do_set_pulm_int_period(self, period):
		'''
		Sets internal pulse modulation period.
		'''
		logging.debug('Setting the Internal Pulse Modulation Period to %e' % period)
		self._visainstrument.write('PULM:INT:PER %e' % period)

	def do_get_pulm_int_pulse_width(self):
		'''
		Returns internal pulse modulation pulse width.
		'''
		logging.debug('Reading the Internal Pulse Modulation Pulse Width.')
		return float(self._visainstrument.query('PULM:INT:PWID').strip())

	def do_set_pulm_int_pulse_width(self, width):
		'''
		Sets internal pulse modulation pulse width.
		'''
		logging.debug('Setting the Internal Pulse Modulation Pulse Width to %e' % width)
		self._visainstrument.write('PULM:INT:PWID %e' % width)

	def set_external_reference(self, frequency = 10e6):
		'''
		Sets external reference and outputs the 10 MHz.
		'''
		logging.debug('Setting the Oscillator source to external')
		self._visainstrument.write('ROSC:SOUR EXT')
		self._visainstrument.write('ROSC:EXT:FREQ %d' % frequency)
		self._visainstrument.write('ROSC:OUTP:STATE 1')
		self._visainstrument.write('ROSC:OUTP:FREQ %d' % frequency)

		try:
			while int(self._visainstrument.query('ROSC:LOCK?').strip()) != 1:
				print 'Waiting for lock on APSYN'
				qt.msleep(0.1)
		except KeyboardInterrupt:
			print 'Interrupted before lock was achieved on APSYN 420'