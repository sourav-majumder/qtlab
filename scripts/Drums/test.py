import numpy as np
from lmfit import Model
import matplotlib.pyplot as plt
from fitter import *

path = r'D:\data\20191206\141911_power_sweep_evaporated_drum_device\141911_power_sweep_evaporated_drum_device.dat'
power, fr, _, _, a ,_ = np.loadtxt(path, unpack=True)
pw = np.linspace(power[0],power[-1],71)
freq = np.split(fr, 71)[0]

data = np.split(a,71)
print(freq)