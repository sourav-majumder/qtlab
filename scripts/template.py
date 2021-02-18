# This is a template for new scripts
from constants import *

instruments = [
	#UHFLI_ADDRESS = 'TCPIP0::192.168.1.2::INSTR'
	#'RhodeSchwartz_ZNB20',	#znb		# Rhode & Schwarz ZNB20 VNA					ADDRESS = 192.168.1.3
	'RhodeSchwartz_SMF100',	#smf		# Rhode & Schwarz SMF100 Signal Generator	ADDRESS = 192.168.1.4
	#'Rigol_DP832A',			#rig		# Rigol DP832A Volage/Current Source		ADDRESS = 192.168.1.5
	#'RhodeSchwartz_RTE1104',#rte		# Rhode & Schwarz RTE1104 Oscilloscope		ADDRESS = 192.168.1.6
	#'AnaPico_APSYN420',		#aps		# AnaPico APSYN420 Signal Generator			ADDRESS = 192.168.1.7
	'RhodeSchwartz_FSV',	#fsv		# Rhode & Schwarz Spectrum Analyzer			ADDRESS = 192.168.1.8
	#'Yokogawa_GS200'		#yok		# Yokogawa GS200 DC Voltage/Current Source	ADDRESS = 'USB0::0x0B21::0x0039::91T416206::INSTR'
]

setup_instruments(instruments)

# Setup parameter sweep
# Innermost to outermost
params = [
	#inst : ['parameter',	start,	stop,	resolution,		numpoints]
	smf : ['frequency',		3*GHz,	4*GHz,	1*MHz,			None],
	smf : ['power',			-10,	0,		None,			21]
]

measure = [
	fsv : ['']
]