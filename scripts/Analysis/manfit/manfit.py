import Tkinter as Tk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import lmfit as lm

class Manipulator(Tk.Frame):

	def __init__(self, param, update_plots, length=600, master=None, fmt='%.3e'):
		Tk.Frame.__init__(self, master)               
		self.master = master
		self.param = param
		self.length = length
		self.update_plots = update_plots
		self.init_window(param.start, param.stop, self.length, fmt)

	def init_window(self, start, stop, length, fmt):
		self.slider = Tk.Scale(self, from_=start, to=stop, orient=Tk.HORIZONTAL, resolution=(float(stop)-float(start))/100., length=length, command=self.update_func)
		self.slider.pack(side=Tk.TOP)

		self.init_val = Tk.Entry(self,)
		self.init_val.insert(0, fmt%start)
		self.init_val.pack(side=Tk.LEFT, padx=10)

		self.end_val = Tk.Entry(self,)
		self.end_val.insert(0, fmt%stop)
		self.end_val.pack(side=Tk.RIGHT, padx=10)

		self.update_ends_button = Tk.Button(self, text='Update Ends', command=self.update_ends, bg='black', fg='white')
		self.update_ends_button.pack()

		self.pack(side=Tk.TOP)

	def update_ends(self):
		new_init = float(self.init_val.get())
		new_end = float(self.end_val.get())
		self.param.start = new_init
		self.param.stop = new_end
		self.slider.configure(from_=new_init, to=new_end, resolution = (float(new_end)-float(new_init))/100.)

	def update_func(self,e):
		self.param.val = (self.slider.get())
		self.update_plots()

	def set(self, val):
		if self.param.start<=val<=self.param.stop:
			self.slider.set(val)
		else:
			raise Exception('Value not in between start and stop')

	def new_parameter(self, param):
		self.param = param
		new_init = param.start
		new_end = param.stop
		self.init_val.delete(0,Tk.END)
		self.init_val.insert(0,new_init)
		self.end_val.delete(0,Tk.END)
		self.end_val.insert(0,new_end)
		self.slider.configure(from_=new_init, to=new_end, resolution = (float(new_end)-float(new_init))/100.)
		self.slider.set(param.val)

class Parameter(object):

	no_of_params = 0

	def __init__(self, start, stop, init=None, name=None):
		self.start = start
		self.stop = stop
		if init is None:
			init = start
		self.val = init
		if name is None:
			name = 'Parameter_%d' % (Parameter.no_of_params+1)
		self.name = name
		Parameter.no_of_params+=1

class ParameterWindow(Tk.Frame):

	def __init__(self, params, manipulator, master=None, columns=2):
		Tk.Frame.__init__(self, master)               
		self.master = master
		self.params = params
		self.columns = columns
		self.manipulator = manipulator
		self.variable = Tk.IntVar(master)
		self.variable.set(0)
		self.init_window()

	def init_window(self):
		for number, param in enumerate(self.params):
			self.single_param_frame(param,number)#.grid(row=number/self.columns)
		self.pack(side=Tk.TOP, fill=Tk.BOTH, padx=10, pady=10)

	def single_param_frame(self, param, number):
		radio_button = Tk.Radiobutton(self, text=param.name, variable=self.variable, value=number, command=self.radio_pressed, indicatoron=0, padx=10).pack(side=Tk.LEFT)
		
	def radio_pressed(self):
		print self.variable.get()
		self.manipulator.new_parameter(self.params[self.variable.get()])

def manfit(figure, params, lines_and_funcs, ydata, xdata, fit_func):
	root = Tk.Tk()

	# Put figure in Frame
	canvas = FigureCanvasTkAgg(figure, master=root)
	canvas.show()
	canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)
	canvas._tkcanvas.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

	# update function
	def update():
		param_values = []
		for param in params:
			param_values.append(param.val)

		for line, func in lines_and_funcs.iteritems():
			line.set_ydata(func(xdata, *param_values))

		figure.canvas.draw_idle()


	# Put Manipulator in Frame
	manipulator = Manipulator(params[0], master=root, update_plots=update)

	# Put Parameter list in Frame
	param_window = ParameterWindow(params, manipulator, master=root)

	def fit():
		def residual(params):
			p=[]
			for key,value in params.valuesdict().items():
				p.append(value)
			return fit_func(xdata, *p)-ydata

		lmfit_params = lm.Parameters()
		for param in params:
			# print param.val, param.start, param.stop
			lmfit_params.add(param.name, value=param.val)#, min=param.start, max=param.stop)
		# print lmfit_params
		mi = lm.minimize(residual,lmfit_params,method='leastsq')
		print lm.fit_report(mi)

		for param in params:
			param.val = mi.params[param.name].value

		# manipulator.set(manipulator.param.val)
		update()

	# Fit button
	fit_button = Tk.Button(master=root, text='Fit', activebackground='#442211', bg='#553322', fg="#FFFFFF", activeforeground='#FFFFFF', height=2, command=fit)
	fit_button.pack(side=Tk.BOTTOM, fill=Tk.X, expand=1)
	
	# show window
	root.mainloop()

