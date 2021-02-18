import numpy as np
from lmfit import Model
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button

path = r'D:\data\20191016\182437_power_sweep_dressed_cavity_6.025GHZ'
data_name = path+path[16:]+r'.dat'
power, fr, _, _, a ,ph = np.loadtxt(data_name, unpack=True)

n=151

pw = np.linspace(power[0],power[-1],n)
freq = np.split(fr, n)[0]

def derv(x):
    dx=[]
    for i in np.arange(len(x)-1):
        dx=np.append(dx,(x[i+1]-x[i]))
    return dx

#file=open('D:\data\20191016\182437_power_sweep_dressed_cavity_6.025GHZ\\unwrap.dat', 'w+')

dummy = 0;
dnw=[]
data = np.split(ph,n)
for i in np.arange(n):
    nw = np.unwrap(data[i])
    dnw=np.append(dnw, derv(nw))
#	for value in nw:
#		file.write(str(power[dummy])+'\t'+str(fr[dummy])+'\t'+str(value)+'\n')
#		dummy = dummy + 1
#	plt.plot(freq, np.unwrap(data[i]), label = str(i))

ax1 = freq[:-1]
ax2=pw

f = plt.figure(figsize = (10,5))
f1 = f.add_subplot(1,2,1)
plt.imshow(dnw2d, cmap = 'flag', extent = [ax1[0], ax1[-1], ax2[-1], ax2[0]], aspect =3e6)

f2 = f.add_subplot(1,2,2)
l, = plt.plot(ax1, dnw2d[0])

axamp = plt.axes([0.15, 0.01, 0.65, 0.03], facecolor='lightgoldenrodyellow')
idxS = Slider(axamp, 'index', 0, len(ax2), valinit = 0, valfmt = '%i')




def update(val):
    idx = idxS.val 
    l.set_ydata(dnw2d[int(idx)])
    f2.canvas.draw_idle()

idxS.on_changed(update)
plt.tight_layout()

plt.show()