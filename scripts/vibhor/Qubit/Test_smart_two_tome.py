from __future__ import print_function

import qt
import shutil
import sys
import os
import time
import progressbar
from constants import *
import numpy as np

znb = qt.instruments.create('ZNB20', 'RhodeSchwartz_ZNB20', address=ZNB20_ADDRESS, reset=True)

znb.set_external_reference(True)
znb.set_source_power(-30)
znb.set_start_frequency(12.17*GHz - 40*MHz + 25*MHz)
znb.set_stop_frequency(12.17*GHz + 40*MHz)
znb.set_numpoints(201)
znb.set_if_bandwidth(50)
znb.add_trace('S21')

znb.rf_on()
znb.send_trigger(wait=True)
znb.autoscale_once()

znb.w('CALC:MARK ON') 
znb.w('CALC:MARK:FUNC:EXEC MAX')

_res = znb.ask('CALC:MARK:FUNC:RES?')
peak_freq = float(_res.split(',')[0])
peak_value = float(_res.split(',')[1])

print(peak_freq, peak_value)