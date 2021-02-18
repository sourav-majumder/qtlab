from instrument import Instrument
import visa
import types
import logging
import numpy as np

import qt

class DP832AException(Exception):
	pass

class Rigol_DP832A(Instrument):
	'''
	This is the driver for the Rigol DP832A Programmable DC Power Supply.

	Usage:
	Initialize with
	<name> = qt.instruments.create('<name>', 'Rigol_DP832A',
		address='USB[board]::manufacturer ID::model code::serial number[::USB interface number][::INSTR]',
		reset=<bool>,)

	For TCP/IP (Ethernet), the address is: 'TCPIP::<IP-address>::INSTR'
	'''

	def __init__(self, name, address, reset = False):
		'''
		Initializes the Rigol DP832A Programmable DC Power Supply.

		Input:
			name (string)           : name of the instrument
			address (string)        : GPIB, USB, TCP/IP address
			reset (bool)            : resets to default values
		'''
		# Initialize wrapper functions
		logging.info('Initializing instrument Rigol DP832A Programmable DC Power Supply.')
		Instrument.__init__(self, name, tags=['physical'])

		# Add some global constants
		self._address = address
		self._default_timeout = 4000. # ms
		self._visainstrument = visa.ResourceManager().open_resource(self._address,
																	timeout=self._default_timeout)
		# Add parameters to wrapper

		self.add_parameter('voltage', type=types.FloatType, channels = (1,3),
							flags=Instrument.FLAG_GETSET|Instrument.FLAG_GET_AFTER_SET,
							minval=0., maxval=32.,
							units='V', format='%.3f',)
		self.set_channel_bounds('voltage', channel=3, minval=0., maxval=5.3)
		self.add_parameter('current', type=types.FloatType, channels = (1,3),
							flags=Instrument.FLAG_GETSET|Instrument.FLAG_GET_AFTER_SET,
							minval=0., maxval=3.2,
							units='A', format='%.3f',)
		self.add_parameter('ovp_voltage', type=types.FloatType, channels = (1,3),
							flags=Instrument.FLAG_GETSET|Instrument.FLAG_GET_AFTER_SET,
							minval=0., maxval=33.,
							units='V', format='%.3f',)
		self.set_channel_bounds('ovp_voltage', channel=3, minval=0., maxval=5.5)
		self.add_parameter('ocp_current', type=types.FloatType, channels = (1,3),
							flags=Instrument.FLAG_GETSET|Instrument.FLAG_GET_AFTER_SET,
							minval=0., maxval=3.3,
							units='A', format='%.3f',)
		self.add_parameter('output', type=types.BooleanType, channels = (1,3),
							flags=Instrument.FLAG_GETSET|Instrument.FLAG_GET_AFTER_SET)
		self.add_parameter('ovp_on', type=types.BooleanType, channels = (1,3),
							flags=Instrument.FLAG_GETSET|Instrument.FLAG_GET_AFTER_SET)
		self.add_parameter('ocp_on', type=types.BooleanType, channels = (1,3),
							flags=Instrument.FLAG_GETSET|Instrument.FLAG_GET_AFTER_SET)
		if reset:
			self.reset()

# --------------------------------------
#           functions
# --------------------------------------

	def get_instrument(self):
		'''
		Returns the instrument object directly to make queries.
		Note: This function should only be used for testing purposes
		since it does not go through qtlab.
		'''
		return self._visainstrument

	def reset(self):
		'''
		Resets the DP832A to default settings.
		'''
		logging.debug('Resetting ...')
		self._visainstrument.write('*RST')

	def do_get_voltage(self, channel):
		'''
		Returns the Voltage that is set on the desired channel.
		'''
		logging.debug('Reading the Voltage on channel %d' % channel)
		return self._visainstrument.query('SOUR%d:VOLT?' % channel)

	def do_set_voltage(self, voltage, channel, ramp=True):
		'''
		Sets the desired Voltage on the desired channel
		'''
		logging.debug('Setting the Voltage on channel %d to %.3f' % (channel, voltage))
		if ramp:
			get_volt = getattr(self, 'get_voltage%d' % channel)
			init_volt = get_volt()
			if voltage>=init_volt:
				volt_arr = np.arange(init_volt,voltage,0.001)
			else:
				volt_arr = np.flip(np.arange(voltage, init_volt,0.001),0)
			for volt in volt_arr:
				self._visainstrument.write('SOUR%d:VOLT %.3f' % (channel, volt))
				qt.msleep(0.3)
		self._visainstrument.write('SOUR%d:VOLT %.3f' % (channel, voltage))

	def do_get_current(self, channel):
		'''
		Returns the Current that is set on the desired channel.
		'''
		logging.debug('Reading the Current on channel %d' % channel)
		return self._visainstrument.query('SOUR%d:CURR?' % channel)

	def do_set_current(self, current, channel):
		'''
		Sets the desired Curent on the desired channel
		'''
		logging.debug('Setting the Current on channel %d to %.3f' % (channel, current))
		self._visainstrument.write('SOUR%d:CURR %.3f' % (channel, current))

	def do_get_ovp_voltage(self, channel):
		'''
		Returns the Over-Voltage Protection that is set on the desired channel.
		'''
		logging.debug('Reading the Over-Voltage Protection on channel %d' % channel)
		return self._visainstrument.query('OUTP:OVP:VAL? CH%d' % channel)

	def do_set_ovp_voltage(self, voltage, channel):
		'''
		Sets the desired Over-Voltage Protection on the desired channel
		'''
		logging.debug('Setting the Over-Voltage Protection on channel %d to %.3f' % (channel, voltage))
		self._visainstrument.write('OUTP:OVP:VAL CH%d,%.3f' % (channel, voltage))

	def do_get_ocp_current(self, channel):
		'''
		Returns the Over-Current Protection that is set on the desired channel.
		'''
		logging.debug('Reading the Over-Current Protection on channel %d' % channel)
		return self._visainstrument.query('OUTP:OCP:VAL? CH%d' % channel)

	def do_set_ocp_current(self, current, channel):
		'''
		Sets the Over-Current Protection on the desired channel
		'''
		logging.debug('Setting the Over-Current Protection on channel %d to %.3f' % (channel, current))
		self._visainstrument.write('OUTP:OCP:VAL CH%d,%.3f' % (channel, current))

	def do_get_output(self, channel):
		'''
		Returns True or False if output on the particular channel is on or off.
		'''
		logging.debug('Reading the output status of channel %d' % channel)
		self._visainstrument.query('OUTP? CH%d' % channel)

	def do_set_output(self, value, channel):
		'''
		Sets the Output of the desired channel to on or off.
		'''
		if value:
			value_str = 'ON'
		else:
			value_str = 'OFF'
		logging.debug('Turning %s the output of channel %d' % (value_str, channel))
		self._visainstrument.write('OUTP CH%d,%s' % (channel, value_str))

	def do_get_ovp_on(self, channel):
		'''
		Returns Over-Voltage Protection status of channel.
		'''
		logging.debug('Reading the Over-Voltage Protection status of channel %d' % channel)
		self._visainstrument.query('OUTP:OVP? CH%d' % channel)

	def do_set_ovp_on(self, value, channel):
		'''
		Sets the Over-Voltage Protection status of channel.
		'''
		if value:
			value_str = 'ON'
		else:
			value_str = 'OFF'
		logging.debug('Turning %s the Over-Voltage Protection of channel %d' % (value_str, channel))
		self._visainstrument.write('OUTP:OVP CH%d,%s' % (channel, value_str))

	def do_get_ocp_on(self, channel):
		'''
		Returns Over-Current Protection status of channel.
		'''
		logging.debug('Reading the Over-Current Protection status of channel %d' % channel)
		self._visainstrument.query('OUTP:OCP? CH%d' % channel)

	def do_set_ocp_on(self, value, channel):
		'''
		Sets the Over-Current Protection status of channel
		'''
		if value:
			value_str = 'ON'
		else:
			value_str = 'OFF'
		logging.debug('Turning %s the Over-Current Protection of channel %d' % (value_str, channel))
		self._visainstrument.write('OUTP:OCP CH%d,%s' % (channel, value_str))

	def ovp_on(self, channel):
		'''
		Turte.rns on Over-Voltage Protection on the desired channel.
		'''
		ovp = getattr(self, 'set_ovp_on%d' % channel)
		ovp(True)

	def ocp_on(self, channel):
		'''
		Turns on Over-Current Protection on the desired channel.
		'''
		ocp = getattr(self, 'set_ocp_on%d' % channel)
		ocp(True)

	def ovp_off(self, channel):
		'''
		Turns off Over-Voltage Protection on the desired channel.
		'''
		ovp = getattr(self, 'set_ovp_on%d' % channel)
		ovp(False)

	def ocp_off(self, channel):
		'''
		Turns off Over-Current Protection on the desired channel.
		'''
		ocp = getattr(self, 'set_ocp_on%d' % channel)
		ocp(False)

	def output_on(self, channel):
		'''
		Turns on the output of a particular channel
		'''
		out = getattr(self, 'set_output%d' % channel)
		out(True)

	def output_off(self, channel):
		'''
		Turns off the output of a particular channel
		'''
		out = getattr(self, 'set_output%d' % channel)
		out(False)

	def all_outputs_on(self):
		'''
		Turns on all outputs.
		'''
		self.output_on(1)
		self.output_on(2)
		self.output_on(3)

	def all_outputs_off(self):
		'''
		Turns off all outputs.
		'''
		self.output_off(1)
		self.output_off(2)
		self.output_off(3)

	def all_ocp_ovp_on(self):
		'''
		Turns on all protections
		'''
		self.ocp_on(1)
		self.ovp_on(1)
		self.ocp_on(2)
		self.ovp_on(2)
		self.ocp_on(3)
		self.ovp_on(3)

	def get_current(self, channel):
		'''
		Returns the Current that is set on the desired channel.
		'''
		logging.debug('Reading the Current on channel %d' % channel)
		return self._visainstrument.query('SOUR%d:CURR?' % channel)

	def do_set_current(self, current, channel):
		'''
		Sets the desired Curent on the desired channel
		'''
		logging.debug('Setting the Current on channel %d to %.3f' % (channel, current))
		self._visainstrument.write('SOUR%d:CURR %.3f' % (channel, current))

