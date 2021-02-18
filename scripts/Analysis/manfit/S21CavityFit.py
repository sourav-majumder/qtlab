import numpy as np
import matplotlib.pyplot as plt
from fitter import *
d = Data(r'D:\data\20180908\105731_S21_large_span\105731_S21_large_span.dat')
freq = d.x
s21 = d.data
plt.plot(freq,s21)
plt.show()
# model = Fitter(rootLorentzianWithOffset)
# myfit = model.fit(freq,amp,print_report=True)
# model.plot()