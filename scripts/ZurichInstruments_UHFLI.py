import logging
import types
import numpy as np
import time

import qt

import zhinst.utils

from constants import *

class UHFLIException(Exception):
	pass

class UHFLINotExactException(Exception):
	pass

class ZurichInstruments_UHFLI(object):
	'''
	This is a driver with subroutines for Zurich Instruments UHFLI Lock in Amplifier.
	'''
	def __init__(self, device_id, reset=False):
		apilevel = 5
		err_msg = "This example can only be ran on either a UHFAWG or a UHF with the AWG option enabled."
		(daq, device, props) = zhinst.utils.create_api_session(device_id, apilevel, required_devtype='UHF',required_options=['AWG'], required_err_msg=err_msg)

		self.daq = daq
		self.props = props
		self.device_id = '/'+device_id+'/'
		self.awgModule = None

		self.param_string = ''
		self.param_value = None
		try:
			self.awg_sample_rate = 1.8e9/2**(self.get('awgs/0/time'))
			self.scope_sample_rate = 1.8e9/2**(self.get('scopes/0/time'))
		except:
			self.awg_sample_rate = DEFAULT_SAMPLE_RATE_AWG_UHFLI
			self.scope_sample_rate = DEFAULT_SAMPLE_RATE_SCOPE_UHFLI
		
		if reset:
			self.disable_all()

	def get(self, param_string = None):
		'''
		Gets a parameter.
		'''
		if param_string is None and self.param_string != '':
			param_string = self.param_string
		elif param_string is not None:
			self.param_string = param_string
		else:
			raise UHFLIException('param_string not passed or set.')
		logging.debug('Reading the value of \'%s\'' % param_string)
		param_str = self.device_id + param_string
		val = self.daq.get(param_str, True)[param_str]['value'][0]
		if type(val) == np.int64:
			val = int(val)
		elif type(val) == np.float64:
			val = float(val)
		else:
			raise UHFLIException('I do not know how to deal with %r type of value yet' % type(val))
		return val

	def set(self, param_string, value, exact=False):
		'''
		Sets a parameter.
		'''
		if param_string is None and self.param_string != '':
			param_string = self.param_string
		elif param_string is not None:
			self.param_string = param_string
		else:
			raise UHFLIException('param_string not passed or set.')
		logging.debug('Setting the value of \'%s\' to %r' % (param_string, value))
		param_str = self.device_id + param_string
		if type(value) == int:
			value = int(value)
			self.daq.setInt(param_str, value)
		elif type(value) == float or type(value) == np.float64:
			value = float(value)
			self.daq.setDouble(param_str, value)
		else:
			raise UHFLIException('I do not know how to deal with %r type of value yet' % type(value))
		if exact:
			set_val = '%r' % self.get(param_string)
			if set_val != ('%r' % value):
				raise UHFLINotExactException('The value of \'%s\' is : %r\nThe desired value was : %r' % (param_string, set_val, value))

	def sync(self):
		'''
		Perform a global synchronisation between the device and the data server:
		Ensure that the settings have taken effect on the device before setting
		the next configuration.
		'''
		self.daq.sync()

	def disable_all(self):
		'''
		Disables all outputs, demods and scopes.
		'''
		general_setting = [['/%s/demods/*/enable' % self.device_id, 0],
						   ['/%s/demods/*/trigger' % self.device_id, 0],
						   ['/%s/sigouts/*/enables/*' % self.device_id, 0],
						   ['/%s/scopes/*/enable' % self.device_id, 0]]
		if 'IA' in self.props['options']:
			general_setting.append(['/%s/imps/*/enable' % self.device_id, 0])
		self.daq.set(general_setting)
		self.sync()

	def imp_50(self):
		'''
		Sets all impedences to 50 ohm.
		'''
		self.set('sigouts/*/imp50', 1)
		self.set('sigins/*/imp50', 1)
		self.sync()

	def setup_demod(self, demod_index=1,
					harm=1,
					phase=0.,
					input_signal=0,
					order=3,
					timeconstant=0,
					sinc=False,
					data_transfer=False,
					rate=1717.):
		'''
		Sets all parameters for a demodulator.
		'''
		demod_index -= 1
		self.set('demods/%d/harmonic' % demod_index, harm)
		self.set('demods/%d/phaseshift' % demod_index, phase)
		self.set('demods/%d/adcselect' % demod_index, input_signal)
		self.set('demods/%d/order' % demod_index, order)
		self.set('demods/%d/timeconstant' % demod_index, timeconstant)
		self.set('demods/%d/sinc' % demod_index, int(sinc))
		self.set('demods/%d/enable' % demod_index, int(data_transfer))
		self.set('demods/%d/rate' % demod_index, rate)
		self.sync()

	def setup_auxout(self, aux_index=1,
					output=2,
					demod=0,
					preoffset=0,
					scale=10,
					offset=0,
					limitlower=-10,
					limitupper=10):
		'''
		Sets all parameters for aux out.
		'''
		aux_index -= 1
		self.set('auxouts/%d/outputselect' % aux_index, output)
		self.set('auxouts/%d/demodselect' % aux_index, demod-1)
		self.set('auxouts/%d/preoffset' % aux_index, preoffset)
		self.set('auxouts/%d/scale' % aux_index, scale)
		self.set('auxouts/%d/offset' % aux_index, offset)
		self.set('auxouts/%d/limitlower' % aux_index, limitlower)
		self.set('auxouts/%d/limitupper' % aux_index, limitupper)
		self.sync()

	def extclk(self, set=True):
		'''
		Sets the clock to external or not.
		'''
		self.set('system/extclk', int(set))

	def start_awg(self):

		# Create an instance of the AWG Module
		self.awgModule = self.daq.awgModule()
		self.awgModule.set('awgModule/device', self.device_id[1:-1])
		self.awgModule.execute()

	def setup_awg(self, awg_program, prin=False):
		'''
		Sets up the awg module.
		'''
		if self.awgModule is None:
			self.start_awg()

		# Transfer the AWG sequence program. Compilation starts automatically.
		self.awgModule.set('awgModule/compiler/sourcestring', awg_program)
		# Note: when using an AWG program from a source file (and only then), the compiler needs to
		# be started explicitly with self.awgModule.set('awgModule/compiler/start', 1)
		while self.awgModule.get('awgModule/compiler/status')['compiler']['status'][0] == -1:
		    time.sleep(0.1)

		if self.awgModule.get('awgModule/compiler/status')['compiler']['status'][0] == 1:
		    # compilation failed, raise an exception
		    raise UHFLIException(self.awgModule.get('awgModule/compiler/statusstring')['compiler']['statusstring'][0])
		else:
		    if self.awgModule.get('awgModule/compiler/status')['compiler']['status'][0] == 0:
		    	if prin:
		        	print("Compilation successful with no warnings, will upload the program to the instrument.")
		    if self.awgModule.get('awgModule/compiler/status')['compiler']['status'][0] == 2:
		        print("Compilation successful with warnings, will upload the program to the instrument.")
		        print("Compiler warning: " + self.awgModule.get('awgModule/compiler/statusstring')['compiler']['statusstring'][0])
		    # wait for waveform upload to finish
		    i = 0
		    while self.awgModule.get('awgModule/progress')['progress'][0] < 1.0:
		        # print("{} progress: {}".format(i, self.awgModule.get('awgModule/progress')['progress'][0]))
		        time.sleep(0.5)
		        i += 1

		time.sleep(1)
		self.sync()

	def trig_out_on(self, trig_index=1, drive=True, source=8):
		'''
		Sets trigger out state.
		'''
		trig_index -=1
		self.set('triggers/out/%d/source' % trig_index, source)
		self.set('triggers/out/%d/drive' % trig_index, int(drive))
		self.sync()

	def awg_on(self, single=True):
		'''
		Sets the AWG on.
		'''
		self.set('awgs/0/single', int(single))
		self.set('awgs/0/enable', 1)
		self.sync()

	def time_to_samples(self, time, scope = False):
		'''
		Converts time to samples using the sampling rate.
		'''
		if scope:
			sample_rate = self.scope_sample_rate
		else:
			sample_rate = self.awg_sample_rate
		return int(self.awg_sample_rate*time)

	def samples_to_time(self, samples, scope = False):
		'''
		Converts samples to time using the sampling rate.
		'''
		if scope:
			sample_rate = self.scope_sample_rate
		else:
			sample_rate = self.awg_sample_rate
		return samples/self.awg_sample_rate

	def awg_sine(self, frequency, cycles=None, samples=None, phase=0, amplitude=1., sample_rate=1.8e9):
		'''
		Returns a string 'sine(<samples>, <amplitude>, <phaseOffset>, <noOfcycles>')
		'''
		if cycles is not None:
			try:
				cycles = float(cycles)
				samples = int(cycles/(float(frequency)*sample_rate))
			except ValueError:
				raise UHFLIException('Must set a float or int value for cycles and frequency.')
		elif samples is not None:
			try:
				samples = int(samples)
				cycles = samples*frequency/sample_rate
			except ValueError:
				raise UHFLIException('Must set an integer number of samples.')
		else:
			raise UHFLIException('Must provide samples or cycles.')

		return 'sine(%d, %f, %f, %f);' % (samples, amplitude, phase, cycles)

	def awg_marker_rect(self, samples_on, samples_off = 0, triggers=[1,2], marker_id_start=1, invert_polarity=False):
		'''
		Returns a string that makes a rectangle trigger, turning it on for a certain period of time and then off.
		Also Returns the marker id
		'''
		marker_id = marker_id_start
		marker_str = 'wave m%d = marker(0, 0);\n' % marker_id # make the marker 0
		marker_id+=1
		trig_no = 0
		for t in triggers:
			trig_no += t
		marker_str += 'wave m%d = marker(%d, %d);\n' % (marker_id, samples_on, trig_no)
		marker_id +=1
		marker_str += 'wave m%d = marker(%d, 0);\n' % (marker_id, samples_off)
		marker_str += 'wave m = join(m%d, m%d, m%d);\n' % (marker_id_start, marker_id_start+1, marker_id_start+2)
		return marker_str, marker_id

	def setup_for_cavity_ringdown(self, freq = 100*MHz, pulse_length = 1*us, off_length = 4*us, timeconstant = 100*ns):
		'''
		Setup Lockin for cavity ringdown.
		'''
		self.set('oscs/0/freq', freq)
		self.setup_demod(demod_index = 1, order = 1, timeconstant = timeconstant)
		# self.setup_demod(demod_index = 2, input_signal = 1, order = 1, timeconstant = timeconstant)
		self.setup_auxout(aux_index = 1, output=0, demod = 1)
		self.setup_auxout(aux_index = 2, output=1, demod = 1)
		self.setup_auxout(aux_index = 3, output=2, demod = 1)
		self.setup_auxout(aux_index = 4, output=3, demod = 1)
		self.trig_out_on(1)
		self.trig_out_on(2)

		marker_prog, marker_id = self.awg_marker_rect(self.time_to_samples(pulse_length), self.time_to_samples(off_length))
		print marker_prog
		awg_program = marker_prog + \
		r"""
		while(true) {
			playWave(1, m);
		}
		"""
		self.setup_awg(awg_program)

	def cavity_ringdown(self):
		'''
		Starts the cavity ringdown.
		'''
		self.awg_on(single=False)

	def save_settings(self, filename):
		zhinst.utils.save_settings(self.daq, self.device_id[1:-1],filename)