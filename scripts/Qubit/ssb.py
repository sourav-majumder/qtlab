from constants import *
import awg_on_first as opt

qubit_freq = 5.733*GHz
mix_freq = 1.8e9*6/128.

opt.center_freq = qubit_freq+mix_freq
opt.mix_freq = mix_freq
opt.sideband = 'left'
i_dc, q_dc, phase, i_amp, q_amp = opt.optimize_all()
# i_dc, q_dc, phase, i_amp, q_amp = 1,2,3,4,5
# with open('Qubit/optimize_data.txt', 'a') as file:
# 	file.write('\n%f %f %f %f %f %f'%(qubit_freq, i_dc, q_dc, phase, i_amp, q_amp))