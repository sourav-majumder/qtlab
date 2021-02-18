from __future__ import print_function
import zhinst.utils as zutil
import numpy as np
import time

# Settings
apilevel_example = 5  # The API level supported by this example.
err_msg = "This example can only be ran on either a UHFAWG or a UHF with the AWG option enabled."
# Call a zhinst utility function that returns:
# - an API session `daq` in order to communicate with devices via the data server.
# - the device ID string that specifies the device branch in the server's node hierarchy.
# - the device's discovery properties.
(daq, device, props) = zutil.create_api_session('dev2232', apilevel_example, required_devtype='UHF',
                                                       required_options=['AWG'], required_err_msg=err_msg)

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

amplitude = 1

# Now configure the instrument for this experiment. The following channels
# and indices work on all device configurations. The values below may be
# changed if the instrument has multiple input/output channels and/or either
# the Multifrequency or Multidemodulator options installed.
out_channel = 0
out_mixer_channel = zutil.default_output_mixer_channel(props)#3
in_channel = 0
osc_index = 0
awg_channel = 0
frequency = 10e6
demod_index = 0
aux_index = 0
trig_index = 0

demod_order = 0
time_constant = 300e-9

exp_setting = [
    ['/%s/sigins/%d/imp50'             % (device, in_channel), 1],
    ['/%s/sigins/%d/ac'                % (device, in_channel), 0],
    ['/%s/sigins/%d/diff'              % (device, in_channel), 0],
    ['/%s/sigins/%d/range'             % (device, in_channel), 1],
    ['/%s/oscs/%d/freq'                % (device, osc_index), frequency],
    ['/%s/sigouts/%d/imp50'            % (device, out_channel), 1],
    ['/%s/sigouts/%d/on'               % (device, out_channel), 1],
    ['/%s/sigouts/%d/range'            % (device, out_channel), 1],
    ['/%s/sigouts/%d/enables/%d'       % (device, out_channel, out_mixer_channel), 1],
    ['/%s/sigouts/%d/amplitudes/*'     % (device, out_channel), 0.],
    ['/%s/awgs/0/outputs/%d/amplitude' % (device, awg_channel), amplitude],
    ['/%s/awgs/0/time'                 % device, 0],
    ['/%s/auxouts/%d/outputselect'     % (device, aux_index), 2], # 2 is Demod R
    ['/%s/triggers/out/%d/drive'       % (device, trig_index), 1],
    ['/%s/triggers/out/%d/source'      % (device, trig_index), 8], # 8 is AWG Marker 1
    ['/%s/demods/%d/enable'            % (device, demod_index), 1],
    ['/%s/demods/%d/order'             % (device, demod_index), demod_order],
    ['/%s/demods/%d/timeconstant'      % (device, demod_index), time_constant]
    ]
daq.set(exp_setting)

daq.sync()

## Set up AWG

# Number of points in AWG waveform
num_pulses = 10

awg_program = \
"""
const marker_pos = 6000;
wave w_gauss = sine(6000, 1, 0, 10);
wave w_left = marker(0, 0);
wave w_right = marker(marker_pos, 1);
wave w_marker = join(w_left, w_right);
wave w_gauss_marker = w_gauss + w_marker;
playWave(1, w_gauss_marker);
playWave(1, zeros(10000));

"""

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

## Run AWG

# Start the AWG in continuous mode
daq.set([['/' + device + '/awgs/0/single', 0],
         ['/' + device + '/awgs/0/enable', 1]])