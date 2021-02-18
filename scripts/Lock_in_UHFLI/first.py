from __future__ import print_function
import zhinst.utils as zutil
import numpy as np
import time


apilevel_example = 5  # The API level supported by this example.
# Call a zhinst utility function that returns:
# - an API session `daq` in order to communicate with devices via the data server.
# - the device ID string that specifies the device branch in the server's node hierarchy.
# - the device's discovery properties.
# This example runs on any device type but requires either the Multifrequency
# or Multidemodulator option.
required_devtype = '.*LI|.*IA|.*IS'
required_options = [r"AWG"]
err_msg = 	"This example requires either an HF2/UHF Instrument with the Multifrequency (MF)" + \
			"Option installed or an MF Instrument with Multidemodulator (MD)" + \
			"Option installed. Note: The MF/MD Option is not a requirement to" + \
			"use the SW Trigger module itself, just to run this example."
# Create an API session; connect to the correct Data Server for the device.
err_msg = "This example only supports instruments with demodulators."
(daq, device, props) = zutil.create_api_session('dev2232', apilevel_example,
												required_devtype=required_devtype,
												required_options=required_options,
												required_err_msg=err_msg)

# Enable ziPython's log, the lower the level the more verbose.
daq.setDebugLevel(3)

# Create a base instrument configuration: disable all outputs, demods and scopes.
general_setting = [['/%s/demods/*/enable' % device, 0],
					 ['/%s/demods/*/trigger' % device, 0],
					 ['/%s/sigouts/*/enables/*' % device, 0],
					 ['/%s/scopes/*/enable' % device, 0]]
if 'IA' in props['options']:
		general_setting.append(['/%s/imps/*/enable' % device, 0])
daq.set(general_setting)
# Perform a global synchronisation between the device and the data server:
# Ensure that the settings have taken effect on the device before setting
# the next configuration.
daq.sync()

# Now configure the instrument for this experiment. The following channels
# and indices work on all device configurations. The values below may be
# changed if the instrument has multiple input/output channels and/or either
# the Multifrequency or Multidemodulator options installed.
out_channel = 0
out_mixer_channel = 3
in_channel = 0
osc_index = 0
awg_channel = 0
frequency = 1e6
amplitude = 1.0

exp_setting = [
	['/%s/sigins/%d/imp50'             % (device, in_channel), 1],
	['/%s/sigins/%d/ac'                % (device, in_channel), 0],
	['/%s/sigins/%d/diff'              % (device, in_channel), 0],
	['/%s/sigins/%d/range'             % (device, in_channel), 1],
	['/%s/oscs/%d/freq'                % (device, osc_index), frequency],
	['/%s/sigouts/%d/on'               % (device, out_channel), 1],
	['/%s/sigouts/%d/range'            % (device, out_channel), 1],
	['/%s/sigouts/%d/enables/%d'       % (device, out_channel, out_mixer_channel), 1],
	['/%s/sigouts/%d/amplitudes/*'     % (device, out_channel), 0.],
	['/%s/awgs/0/outputs/%d/amplitude' % (device, awg_channel), amplitude],
	['/%s/awgs/0/time'                 % device, 0]
	]
daq.set(exp_setting)

daq.sync()

# Number of points in AWG waveform
AWG_N = 2000

awg_program = \
"""
const AWG_N = _c1_;
wave w = rect(AWG_N, 1);
wave w1 = zeros(AWG_N/20);
repeat(5) {
playWave(w1);
playWave(w);
}
"""

awg_program = awg_program.replace('_c1_', str(AWG_N))

# Create an instance of the AWG Module
awgModule = daq.awgModule()
awgModule.set('awgModule/device', device)
awgModule.execute()

# Transfer the AWG sequence program. Compilation starts automatically.
awgModule.set('awgModule/compiler/sourcestring', awg_program)
# Note: when using an AWG program from a source file (and only then), the compiler needs to
# be started explicitly with awgModule.set('awgModule/compiler/start', 1)
while awgModule.get('awgModule/compiler/status')['compiler']['status'][0] == -1:
	time.sleep(0.1)

if awgModule.get('awgModule/compiler/status')['compiler']['status'][0] == 1:
	# compilation failed, raise an exception
	raise Exception(awgModule.get('awgModule/compiler/statusstring')['compiler']['statusstring'][0])
else:
	if awgModule.get('awgModule/compiler/status')['compiler']['status'][0] == 0:
		print("Compilation successful with no warnings, will upload the program to the instrument.")
	if awgModule.get('awgModule/compiler/status')['compiler']['status'][0] == 2:
		print("Compilation successful with warnings, will upload the program to the instrument.")
		print("Compiler warning: " + awgModule.get('awgModule/compiler/statusstring')['compiler']['statusstring'][0])
	# wait for waveform upload to finish
	i = 0
	while awgModule.get('awgModule/progress')['progress'][0] < 1.0:
		print("{} progress: {}".format(i, awgModule.get('awgModule/progress')['progress'][0]))
		time.sleep(0.5)
		i += 1

time.sleep(1)

# Disable the scope.
daq.setInt('/%s/scopes/0/enable' % device, 0)
# Configure the length of the scope shot.
daq.setInt('/%s/scopes/0/length' % device, 16836)
# Now configure the scope's trigger to get aligned data
# 'trigenable' : enable the scope's trigger (boolean).
daq.setInt('/%s/scopes/0/trigenable' % device, 1)
# Specify the trigger channel, chose same as input
daq.setInt('/%s/scopes/0/trigchannel' % device, in_channel)
# Trigger on rising edge
daq.setInt('/%s/scopes/0/trigslope' % device, 1)
# Set the hold off time in-between triggers.
daq.setDouble('/%s/scopes/0/trigholdoff' % device, 0.025)
# Set the level to trigger at
daq.setDouble('/%s/scopes/0/triglevel' % device, 0.5)
# Set hysteresis triggering threshold to avoid triggering on noise
# 'trighysteresis/mode' :
#  0 - absolute, use an absolute value ('trighysteresis/absolute')
#  1 - relative, use a relative value (trighysteresis/relative') of the trigchannel's input range
daq.setDouble('/%s/scopes/0/trighysteresis/mode' % device, 0)
daq.setDouble('/%s/scopes/0/trighysteresis/absolute' % device, 0.1)  # 0.1=10%

# Set up the Scope Module.
scopeModule = daq.scopeModule()
scopeModule.set('scopeModule/mode', 0)
scopeModule.subscribe('/' + device + '/scopes/0/wave')
daq.setInt('/%s/scopes/0/single' % device, 1)

scopeModule.execute()

# Start the scope...
daq.setInt('/%s/scopes/0/enable' % device, 1)
daq.sync()
time.sleep(1)

# Start the AWG in single-shot mode
daq.set([['/' + device + '/awgs/0/single', 1],
         ['/' + device + '/awgs/0/enable', 1]])

# Read the scope data (manual timeout of 1 second)
local_timeout = 1.0
while scopeModule.progress()[0] < 1.0 and local_timeout > 0:
    time.sleep(0.1)
    local_timeout -= 0.1

data_read = scopeModule.read(True)
print(data_read)
wave_nodepath = '/{}/scopes/0/wave'.format(device)
assert wave_nodepath in data_read, "Error: The subscribed data `{}` was returned.".format(wave_nodepath)
data = data_read[wave_nodepath][0][0]

f_s = 1.8e9 # sampling rate of scope and AWG
for n in range(0, len(data['channelenable'])):
    p = data['channelenable'][n]
    if p:
        y_measured = np.double(data['wave'][n])*data['channelscaling'][n] + data['channeloffset'][n]
        x_measured = np.arange(0, len(y_measured))*data['dt'] - (data['timestamp'] - data['triggertimestamp'])/f_s

import matplotlib.pyplot as plt
plt.plot(x_measured, y_measured)
plt.show()

