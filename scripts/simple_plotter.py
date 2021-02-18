import numpy as np
import matplotlib.pyplot as plt

x, y1, y2, y3  = np.loadtxt('SSBwith_mixer2_v1.txt', unpack = True)

plt.figure(figsize = (6,4))
plt.plot(x,y1, '-ro')
plt.plot(x,y2, '-bo')
plt.plot(x,y3, '-co')
plt.xlabel('Time (min)')
plt.ylabel('Power (dBm)')

plt.tight_layout()
plt.show()
