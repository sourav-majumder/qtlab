import qt
import visa
import datetime

x = datetime.datetime.now()
print(x)

address = 'USB0::6833::2500::DM3R180400083::0::INSTR'
inst = visa.ResourceManager().open_resource(address, 5)

datafile = open("resistance_vs_time_MoRe.dat", "w")
datafile.write("#RESISTANCE vs TIME")

inst.write("TRIG:SING:TRIG")
print inst.query("MEAS:RES?")

try:
	while True:
		inst.write("TRIG:SING:TRIG")
		qt.msleep(60)
		res = float(inst.query("MEAS:RES?").strip())
		string = "%f %s\n" % (res,datetime.datetime.now())
		print string
		datafile.write(string)

finally:
	datafile.close()
	inst.close()