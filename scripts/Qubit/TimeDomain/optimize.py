from constants import *
from ZurichInstruments_UHFLI import ZurichInstruments_UHFLI
import sys
import os
import shutil
import qt
import progressbar
import numpy as np
import time
import awg_on_first as opt

##############################################

us = 1e-6

##############################################

uhf = ZurichInstruments_UHFLI('dev2232')
# rte = qt.instruments.create('RTE1104', 'RhodeSchwartz_RTE1104', address = 'TCPIP0::192.168.1.6::INSTR')
# aps = qt.instruments.create('APSYN420',   'AnaPico_APSYN420',         address = APSYN420_ADDRESS)
# fsv = qt.instruments.create('FSV', 'RhodeSchwartz_FSV', address = FSV_ADDRESS)
# smf = qt.instruments.create('SMF100', 'RhodeSchwartz_SMF100', address = SMF100_ADDRESS)
# aps = qt.instruments.create('APSYN420',   'AnaPico_APSYN420',         address = APSYN420_ADDRESS)

##############################################



###################################################################

def optimize(qubit_freq):
    mix_freq = 1.8e9*6/64.
    opt.center_freq = qubit_freq + mix_freq
    opt.mix_freq = mix_freq
    opt.sideband = 'left'
    # aps.set_frequency(opt.center_freq)
    # i_dc, q_dc, phase, i_amp, q_amp = opt.optimize_all()
    return opt.optimize_all()

###################################################################
qubit_freq = 9.786*GHz

i_dc, q_dc, phase, max_i_amp, max_q_amp = optimize(qubit_freq)



 