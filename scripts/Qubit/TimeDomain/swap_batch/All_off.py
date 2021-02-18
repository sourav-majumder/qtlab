from constants import *
from ZurichInstruments_UHFLI import ZurichInstruments_UHFLI
import qt



uhf = ZurichInstruments_UHFLI('dev2232')
znb = qt.instruments.create('ZNB20', 'RhodeSchwartz_ZNB20', address=ZNB20_ADDRESS, reset=True)
# rte = qt.instruments.create('RTE1104', 'RhodeSchwartz_RTE1104', address = 'TCPIP0::192.168.1.6::INSTR')
aps = qt.instruments.create('APSYN420',   'AnaPico_APSYN420',         address = APSYN420_ADDRESS)
# fsv = qt.instruments.create('FSV', 'RhodeSchwartz_FSV', address = FSV_ADDRESS)
smf = qt.instruments.create('SMF100', 'RhodeSchwartz_SMF100', address = SMF100_ADDRESS)
sgs = qt.instruments.create('sgs', 'RS_SGS100A', address = SGS100A_ADDRESS)
##############################################

