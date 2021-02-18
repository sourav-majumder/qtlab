from instrument import Instrument
import visa
import types
import logging
import numpy as np

import qt

class GS200Exception(Exception):
	pass

class Yokogawa_GS200(Instrument):
	'''
	This is the driver for the Yokogawa GS200 DC Voltage/Current Source

	Usage:
	Initialize with
	<name> = qt.instruments.create('<name>', 'Yokogawa_GS200',
		address='USB[board]::manufacturer ID::model code::serial number[::USB interface number][::INSTR]',
		reset=<bool>,)

	For TCP/IP (Ethernet), the address is: 'TCPIP::<IP-address>::INSTR'
	'''

	def __init__(self, name, address, reset = False):
		'''
		Initializes the Yokogawa GS200 DC Voltage/Current Source

		Input:
			name (string)           : name of the instrument
			address (string)        : GPIB, USB, TCP/IP address
			reset (bool)            : resets to default values
		'''
		# Initialize wrapper functions
		logging.info('Initializing instrument Yokogawa GS200 DC Voltage/Current Source')
		Instrument.__init__(self, name, tags=['physical'])

		# Add some global constants
		self._address = address
		self._default_timeout = 12000. # ms
		self._visainstrument = visa.ResourceManager().open_resource(self._address,
																	timeout=self._default_timeout)
		# Add parameters to wrapper

		self.add_parameter('function', type=types.StringType,
							flags=Instrument.FLAG_GETSET|Instrument.FLAG_GET_AFTER_SET)
							# format_map = {
							#     'VOLT' : 'voltage'
							#     'CURR' : 'current'
							#     })
		self.add_parameter('range', type=types.FloatType,
							flags=Instrument.FLAG_GETSET|Instrument.FLAG_GET_AFTER_SET)
						   
		self.add_parameter('level', type=types.FloatType,
							flags=Instrument.FLAG_GETSET|Instrument.FLAG_GET_AFTER_SET)

		self.add_parameter('current_limit', type=types.FloatType,
							flags=Instrument.FLAG_GETSET|Instrument.FLAG_GET_AFTER_SET)

		self.add_parameter('voltage_limit', type=types.FloatType,
							flags=Instrument.FLAG_GETSET|Instrument.FLAG_GET_AFTER_SET)

		self.add_parameter('output', type=types.BooleanType,
							flags=Instrument.FLAG_GETSET|Instrument.FLAG_GET_AFTER_SET)

		if reset:
			self.reset()

# --------------------------------------
#           functions
# --------------------------------------

	def get_instrument(self):
		return self._visainstrument

	def units(self):
		s = self.get_function()
		if s == 'VOLT':
			return 'V'
		else: return 'A'

	def reset(self):
		self._visainstrument.write('*RST')
		
	def do_get_function(self):
		logging.debug('Reading the function')
		return self._visainstrument.query(':SOURce:FUNCtion?').strip()

	def do_set_function(self, function = 'VOLT'):
		logging.debug('Setting the function to %s' % (function.strip().upper()))
		self._visainstrument.write(':SOURce:FUNCtion %s' % (function.strip().upper()))

	def do_get_range(self):
		logging.debug('Reading the range')
		return float(self._visainstrument.query(':SOURce:RANGe?').strip())

	def do_set_range(self, newrange = None, extra = None):
		if type(newrange) is types.IntType or type(newrange) is types.FloatType:
			logging.debug('Setting the range to %f' % (newrange))
			minrange = float(self._visainstrument.query(':SOURce:RANGe? MIN').strip())
			maxrange = float(self._visainstrument.query(':SOURce:RANGe? MAX').strip())
			if newrange >= minrange and newrange <= maxrange:
				self._visainstrument.write(':SOURce:RANGe %f' % (newrange))
				setrange = self._visainstrument.query(':SOURce:RANGe?')
				print 'Range set to %f %s' % (setrange, self.units())
			else:
				raise GS200Exception('Incorrect Value for Range. Value must be between %.2f and %.2f' % (minrange,maxrange))
		elif type(newrange) is types.StringType:
			logging.debug('Trying to set the range to %s' % (newrange))
			newrange = newrange.upper()
			if newrange == ['MAX', 'MIN', 'UP', 'DOWN']:
				logging.debug('Setting the range to %s' % (newrange))
				self._visainstrument.write(':SOURce:RANGe %s' % (newrange))
				setrange = self._visainstrument.query(':SOURce:RANGe?')
				print 'Range set to %f %s' % (setrange, self.units())
			else:
				raise GS200Exception('The Range must be <Voltage> or <Current> in int or float form,\n Or a string \'MAX\', \'MIN\', \'UP\', \'DOWN\'')
	
	def do_get_level(self):
		logging.debug('Reading the Level')
		return float(self._visainstrument.query(':SOURce:LEVel?').strip())

	def do_set_level(self, level, force = False):
		logging.debug('Trying to set the Level to %f' % (level))
		ran = self.get_range()
		levelran = self.range_for_level(level)
		if levelran < 0:
			raise GS200Exception('Cannot set level that high')
		if force:
			self.set_range(levelran)
			logging.debug('Setting the level to %f' % (level))
			self._visainstrument.write(':SOURce:LEVel %f' % (level))
		elif levelran <= ran:
			logging.debug('Setting the level to %f' % (level))
			self._visainstrument.write(':SOURce:LEVel %f' % (level))
		else:
			raise GS200Exception('Value must be in range +/- %f' % (ran))

	def do_get_voltage_limit(self):
		return self._visainstrument.query(':SOURce:PROTection:VOLTage?')

	def do_set_voltage_limit(self, curr_limit):
		if curr_limit > 30:
			raise GS200Exception('Maximum voltage limit is 30 V')
		elif curr_limit < 1:
			raise GS200Exception('Minimum voltage limit is 1 V')
		else:
			self._visainstrument.write(':SOURce:PROTection:VOLTage %f' % (curr_limit))

	def do_get_current_limit(self):
		return self._visainstrument.query(':SOURce:PROTection:CURRent?')

	def do_set_current_limit(self, curr_limit):
		if curr_limit > 200.e-3:
			raise GS200Exception('Maximum current limit is 200 mA')
		elif curr_limit < 1e-3:
			raise GS200Exception('Minimum current limit is 1 mA')
		else:
			self._visainstrument.write(':SOURce:PROTection:CURRent %f' % (curr_limit))
	
	def do_get_output(self):
		return (int(self._visainstrument.query(':OUTPut?').strip())>0)

	def do_set_output(self, output):
		if output:
			self._visainstrument.write(':OUTPut 1')
		else:
			self._visainstrument.write(':OUTPut 0')

	def output_on(self):
		self.set_output(True)

	def output_off(self):
		self.set_output(False)

	def set_current(self, current, force = False):
		if force:
			self.set_function('CURR')
			self.set_range(self.range_for_current(current))
			self.set_level(current, force=True)
		elif self.get_function() == 'CURR':
			self.set_level(current)
		else:
			raise GS200Exception('Cannot set current in voltage mode.\nYou may use set_current(<current>, force = True)\nto change to current mode and set the desired current.')

	def set_voltage(self, voltage, force = False):
		if force:
			self.set_function('VOLT')
			self.set_range(self.range_for_voltage(voltage))
			self.set_level(voltage, force = True)
		elif self.get_function() == 'VOLT':
			self.set_level(voltage)
		else:
			raise GS200Exception('Cannot set voltage in current mode.\nYou may use set_voltage(<voltage>, force = True)\nto change to voltage mode and set the desired current.')

	def range_for_current(self, current):
		if abs(current) <= 1e-3:
			return 1e-3
		elif abs(current) <= 10e-3:
			return 10e-3
		elif abs(current) <= 100e-3:
			return 100e-3
		elif abs(current) <= 200e-3:
			return 200e-3
		else:
			return -1

	def range_for_voltage(self, voltage):
		if abs(voltage) <= 10e-3:
			return 10e-3
		elif abs(voltage) <= 100e-3:
			return 100e-3
		elif abs(voltage) <= 1:
			return 1
		elif abs(voltage) <= 10:
			return 10
		elif abs(voltage) <= 30:
			return 30
		else:
			return -1

	def range_for_level(self, level):
		if self.get_function() == 'CURR':
			return self.range_for_current(level)
		else:
			return self.range_for_voltage(level)

	def sweep_gate(self, value, step=0.001, delay=0.01):
		flag1 = True
		# step = 0.01
		while flag1 == True:
			ins = np.round(self.get_level()*1000)/1000
			if np.abs(ins-value) <= 1.1*step:
				self.set_voltage(value)
				flag1 = False
			elif ins > value:
				self.set_voltage(ins - step)
				qt.msleep(delay)
			elif ins < value:
				self.set_voltage(ins + step)
				qt.msleep(delay)

	def sweep_current(self, value, delay=0.1):
		flag1 = True
		step = self.get_range()/2000
		while flag1 == True:
			ins = self.get_level()
			if np.abs(ins-value) <= 2.1*step:
				self.set_current(value)
				flag1 = False
			elif ins > value:
				self.set_current(ins - step)
				qt.msleep(delay)
			elif ins < value:
				self.set_current(ins + step)
				qt.msleep(delay)

	def sweep_current_high_resolution(self, value, delay=0.1):
		flag1 = True
		step = self.get_range()/100000
		while flag1 == True:
			ins = self.get_level()
			if np.abs(ins-value) <= 2*step:
				self.set_current(value)
				flag1 = False
			elif ins > value:
				self.set_current(ins - step)
				qt.msleep(delay)
			elif ins < value:
				self.set_current(ins + step)
				qt.msleep(delay)