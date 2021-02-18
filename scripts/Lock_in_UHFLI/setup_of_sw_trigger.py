## Set up SW Trigger

# Create an instance of the Software Trigger Module (ziDAQRecorder class).
trigger = daq.record()

trigger_path = '/%s/demods/%d/sample' % (device, demod_index)
triggernode = trigger_path + '.TrigAWGTrig1'#'.r'
trigger.set('trigger/0/triggernode', triggernode)
# Use an edge trigger.
trigger.set('trigger/0/type', 1)  # 1 = edge
# Trigger on the negative edge.
trigger.set('trigger/0/edge', 1)  # 0 = negative

# The set the trigger level.
trigger_level = 0.5*amplitude
print("Setting trigger/0/level to {:.3f}.".format(trigger_level))
trigger.set('trigger/0/level', trigger_level)

trigger_hysteresis = 0.05*trigger_level
print("Setting trigger/0/hysteresis {:.3f}.".format(trigger_hysteresis))
trigger.set('trigger/0/hysteresis', trigger_hysteresis)
# The number of times to trigger.
trigger_count = int(num_pulses)
trigger.set('trigger/0/count', trigger_count)
trigger.set('trigger/0/holdoff/count', 0)
trigger.set('trigger/0/holdoff/time', 0.100)
trigger_delay = -0.020
trigger.set('trigger/0/delay', trigger_delay)
# The length of time to record each time we trigger
trigger_duration = 0.180
trigger.set('trigger/0/duration', trigger_duration)
# Do not extend the recording of the trigger frame if another
# trigger arrives within trigger_duration.
trigger.set('trigger/0/retrigger', 0)
# The size of the internal buffer used to record triggers (in seconds), this
# should be larger than trigger_duration.
buffer_size = 2*trigger_duration
trigger.set('trigger/buffersize', buffer_size)
trigger.set('trigger/historylength', 100)

# We subscribe to the same demodulator sample we're triggering on, but we
# could additionally subscribe to other node paths.
trigger.subscribe('/%s/demods/%d/sample' % (device, demod_index))

# Start the Software Trigger's thread.
trigger.execute()
time.sleep(2*buffer_size)