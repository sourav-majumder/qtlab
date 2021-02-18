from instrument import Instrument
import visa
import types
import logging

import qt

class SMF100Exception(Exception):
        pass

class RhodeSchwartz_SMF100(Instrument):
	'''
	This is the driver for the Rohde & Schwarz SMF100 Signal Generator.

	Usage:
	Initialize with
	<name> = qt.instruments.create('<name>', 'RhodeSchwartz_SMF100',
		address='TCPIP::<IP-address>::INSTR',
		reset=<bool>,)

	For GPIB the address is: 'GPIB<interface_nunmber>::<gpib-address>'
	'''
	def __init__(self, name, address, reset=False):
		
		# Initialize wrapper functions
		logging.info('Initializing instrument Rhode & Schwarz SMF100 Signal Generator')
		Instrument.__init__(self, name, tags=['physical'])

		# Add some global constants
		self._address = address
		self._default_timeout = 12000 # ms
		self._visainstrument = visa.ResourceManager().open_resource(self._address,
																	timeout=self._default_timeout)
		self._freq_unit = 1
		self._freq_unit_symbol = 'Hz'

		self.add_parameter('frequency', type=types.FloatType, format='%.6e',
						   flags=Instrument.FLAG_GETSET|Instrument.FLAG_GET_AFTER_SET,
						   units=self._freq_unit_symbol, minval=1e9/self._freq_unit, maxval=22e9/self._freq_unit)
		self.add_parameter('source_power', type=types.FloatType,
						   flags=Instrument.FLAG_GETSET|Instrument.FLAG_GET_AFTER_SET,
						   units='dBm',minval=-20., maxval=30.)
		self.add_parameter('rf_status', type=types.BooleanType,
                          flags=Instrument.FLAG_GETSET|Instrument.FLAG_GET_AFTER_SET)
		self.add_parameter('mod_status', type=types.BooleanType,
                          flags=Instrument.FLAG_GETSET|Instrument.FLAG_GET_AFTER_SET)
		self.add_parameter('pulm_polarity', type=types.StringType,
                          flags=Instrument.FLAG_GETSET|Instrument.FLAG_GET_AFTER_SET,
                          format_map = {
                            "NORM" : "Normal",
                            "INV" : "Inverted"
                          })
		self.add_parameter('pulm_video_polarity', type=types.StringType,
                          flags=Instrument.FLAG_GETSET|Instrument.FLAG_GET_AFTER_SET,
                          format_map = {
                            "NORM" : "Normal",
                            "INV" : "Inverted"
                          })
		self.add_parameter('pulm_sync', type=types.BooleanType,
                          flags=Instrument.FLAG_GETSET|Instrument.FLAG_GET_AFTER_SET)
		self.add_parameter('trigger_level', type=types.StringType,
                          flags=Instrument.FLAG_GETSET|Instrument.FLAG_GET_AFTER_SET,
                          format_map = {
                            "TTL" : "Transistor-Transistor Logic",
                            "M2V5" : "-2.5V",
                            "P0V5" : "0.5V"
                          })
		self.add_parameter('external_impedance', type=types.FloatType,
                          flags=Instrument.FLAG_GETSET|Instrument.FLAG_GET_AFTER_SET,
                          minval=50, maxval=10e3)
		if reset:
			self.reset()

# --------------------------------------
#           functions
# --------------------------------------
	def reset(self):
		'''
		Resets the SMF100 to default settings.
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

	def do_get_frequency(self):
		'''
		Returns the Frequency (Hz)
		'''
		logging.debug('Reading frequency')
		return float(self._visainstrument.query('SOUR:FREQ?'))/self._freq_unit

	def do_set_frequency(self, freq):
		'''
		Sets the frequency to the desired one.
		'''
		logging.debug('Setting freq to %d' % freq)
		self._visainstrument.write('SOUR:FREQ %.3f' % freq*self._freq_unit)

	def do_get_source_power(self):
		'''
		Returns the power (in dBm)
		'''
		logging.debug('Reading Source power')
		return float(self._visainstrument.query('SOUR:POW?'))

	def do_set_source_power(self, source_power):
		'''
		Set output power in dBm.
		'''
		logging.debug('Setting generator power to %.2f' % source_power)
		self._visainstrument.write('SOUR:POW %.2f dBm' % source_power)

	def do_get_rf_status(self):
		'''
		Returns True if RF signal is set to ON.
		'''
		logging.debug('Reading RF status')
		return int(self._visainstrument.query('OUTP?').strip()) == 1

	def do_set_rf_status(self, status):
		'''
		Sets RF status to on or off if status is True or False.
		'''
		logging.debug('Setting RF to %r' % status)
		if status:
			status_str = 'ON'
		elif not status:
			status_str = 'OFF'
		else:
			raise SMF100Exception('Value must be boolean')
		self._visainstrument.write('OUTP %s' % status_str)

	def rf_on(self):
		'''
		Turns RF output on.
		'''
		self.set_rf_status(True)

	def rf_off(self):
		'''
		Turns RF output off.
		'''
		self.set_rf_status(False)

	def do_get_mod_status(self):
		'''
		Returns True if MOD signal is set to ON.
		'''
		logging.debug('Reading MOD status')
		return int(self._visainstrument.query('MOD?').strip()) == 1

	def do_set_mod_status(self, status):
		'''
		Sets MOD status to on or off if status is True or False.
		'''
		logging.debug('Setting MOD to %r' % status)
		if status:
			status_str = 'ON'
		elif not status:
			status_str = 'OFF'
		else:
			raise SMF100Exception('Value must be boolean')
		self._visainstrument.write('PULM:STAT %s' % status_str)

	def mod_on(self):
		'''
		Turns MOD output on.
		'''
		self.set_mod_status(True)

	def mod_off(self):
		'''
		Turns MOD output off.
		'''
		self.set_mod_status(False)

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
		self._visainstrument.write('PULM:POL %s', polarity)

	def toggle_pulm_polarity(self):
		'''
		Toggles the PUlse Modulation Polarity.
		'''
		if self.get_pulm_polarity() == 'NORM':
			self.set_pulm_polarity('INV')
		else:
			self.set_pulm_polarity('NORM')

	def do_get_pulm_sync(self):
		'''
		Returns if pulse modulation is synched to internal clock.
		'''
		logging.debug('Reading Pulse Modulation Sync to Internal Clock Status')
		return int(self._visainstrument.query('PULM:SYNC?').strip()) == 1

	def do_set_pulm_sync(self, sync):
		'''
		Sets the pulse modulation sync with internal clock on or off.
		'''
		logging.debug('Setting the Pulse Modulation Sync to Internal Clock to %r' % sync)
		if sync:
			sync_str = 'ON'
		elif not sync:
			sync_str = 'OFF'
		else:
			raise SMF100Exception('Value must be boolean')
		self._visainstrument.write('PULM:SYNC %s' % sync_str)

	def do_get_pulm_video_polarity(self):
		'''
		Returns pulse modulation polarity.
		'''
		logging.debug('Reading Pulse Modulation Video Polaity Status')
		return self._visainstrument.query('PULM:OUTP:VID:POL?')

	def do_set_pulm_video_polarity(self, polarity):
		'''
		Sets the desired polarity for pulse modulation.
		'''
		polarity = polarity.strip().upper()
		logging.debug('Setting the Pulse Modulation Video Polarity to %s' % polarity)
		self._visainstrument.write('PULM:OUTP:VID:POL %s', polarity)

	def do_get_trigger_level(self):
		'''
		Returns the trigger level.
		'''
		logging.debug('Reading the trigger level')
		return self._visainstrument.query('PULM:TRIG:EXT:LEV?')

	def do_set_trigger_level(self, level):
		'''
		Sets the trigger level.
		'''
		if level == -2.5 or level == '-2.5V':
			level = 'M2V5'
		elif level == 0.5 or level == '0.5V':
			level = 'P0V5'
		elif level == 'TTL':
			level = 'TTL'
		else:
			raise SMF100Exception('Trigger level can be \'-2.5V\', \'0.5V\', or \'TTL\'')
		level = level.strip().upper()
		logging.debug('Setting the trigger level to %s' % level)
		self._visainstrument.write('PULM:TRIG:EXT:LEV %s' % level)

	def do_get_external_impedance(self):
		'''
		Returns the external impedence.
		'''
		logging.debug('Reading the external impedance')
		if self._visainstrument.query('PULM:TRIG:EXT:IMP?') == 'G10K':
			return 10e3
		else:
			return 50

	def do_set_external_impedance(self, impedance):
		'''
		Sets the external impedance.
		'''
		if impedance == 50:
			logging.debug('Setting the external impedence to %e' % impedance)
			impedance_str = 'G50'
		elif impedance == 10e3:
			logging.debug('Setting the external impedence to %e' % impedance)
			impedance_str = 'G10K'
		else:
			raise SMF100Exception('External ipedance can be set to \'50\' or \'10e3\'')
		self._visainstrument.write('PULM:TRIG:EXT:IMP %s' % impedance_str)

	def pulse_mod_on(self, polarity = 'NORM', sync = False, video_polarity = 'NORM', trigger_level = 'TTL', external_impedance = 10e3):
		'''
		Sets pulse modulation on with given settings.
		'''
		self.set_pulm_polarity(polarity)
		self.set_pulm_sync(sync)
		self.set_pulm_video_polarity(video_polarity)
		self.set_trigger_level(trigger_level)
		self.set_external_impedance(external_impedance)
		self.mod_on()