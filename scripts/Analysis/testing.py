import matplotlib
matplotlib.use('TkAgg')

from numpy import arange, sin, pi
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

import sys
if sys.version_info[0] < 3:
    import Tkinter as Tk
else:
    import tkinter as Tk


def destroy(e):
    sys.exit()

root = Tk.Tk()
root.wm_title("Embedding in TK")

figsize = (6,4)
dpi = 96
f = Figure(figsize=figsize, dpi=dpi)
a = f.add_subplot(111)
t = arange(0.0, 3.0, 0.01)
s = sin(2*pi*t)

plotline, =a.plot(t, s)
a.set_title('Tk embedding')
a.set_xlabel('X axis label')
a.set_ylabel('Y label')

def print_stuff(e):
	print 'stuff'

def update(e):
	plotline.set_ydata(sin(2*pi*slider.get()*t))
	f.canvas.draw()

def update_ends():
	new_init = init_val.get()
	new_end = end_val.get()
	slider.configure(from_=new_init, to=new_end)


# a tk.DrawingArea
canvas = FigureCanvasTkAgg(f, master=root)
canvas.show()
canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

canvas._tkcanvas.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

slider_frame = Tk.Frame(root)

slider = Tk.Scale(slider_frame, from_=-0.5, to=0.5, orient=Tk.HORIZONTAL, resolution=0.01, length=figsize[0]*dpi, command=update)
slider.pack(side=Tk.TOP)

init_val = Tk.Entry(slider_frame)
init_val.pack(side=Tk.LEFT)

end_val = Tk.Entry(slider_frame)
end_val.pack(side=Tk.RIGHT)

update_ends_button = Tk.Button(slider_frame, text='Update Ends', command=update_ends)
update_ends_button.pack()

slider_frame.pack()

Tk.mainloop()