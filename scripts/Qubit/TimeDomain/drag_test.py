from constants import *
from ZurichInstruments_UHFLI import ZurichInstruments_UHFLI
import sys
import os
import shutil
import qt
import progressbar
import numpy as np
import time

def awg_program(D):
    awg_program = '''
    const us = 1e-6;
    const cycle = 4.4e-9;
    const op = -1.710238;
    const pi = 3.141592653589793;

    const D = %f;
    const G = 1;

    wave g = gauss(64, G, 32, 16);
    wave d = drag(64, D, 32, 16);

    wave s1 = sine(64, 1, op, 3);
    wave s2 = sine(64, 1, 0, 3);
    wave c1 = cosine(64, 1, op, 3);
    wave c2 = cosine(64, 1, 0, 3);
    wave gs1 = multiply(g, s1);
    wave dc1 = multiply(d, c1);
    wave gs2 = multiply(g, s2);
    wave dc2 = multiply(d, c2);

    wave s_90_1 = sine(64, 1, op + pi/2, 3);
    wave s_90_2 = sine(64, 1, 0 + pi/2, 3);
    wave c_90_1 = cosine(64, 1, op + pi/2, 3);
    wave c_90_2 = cosine(64, 1, 0 + pi/2, 3);
    wave g_90_s1 = multiply(g, s_90_1);
    wave d_90_c1 = multiply(d, c_90_1);
    wave g_90_s2 = multiply(g, s_90_2);
    wave d_90_c2 = multiply(d, c_90_2);

    wave s_180_1 = sine(64, 1, op + pi, 3);
    wave s_180_2 = sine(64, 1, 0 + pi, 3);
    wave c_180_1 = cosine(64, 1, op + pi, 3);
    wave c_180_2 = cosine(64, 1, 0 + pi, 3);
    wave g_180_s1 = multiply(g, s_180_1);
    wave d_180_c1 = multiply(d, c_180_2);
    wave d_180_c2 = multiply(d, c_180_1);
    wave g_180_s2 = multiply(g, s_180_2);

    wave s_270_1 = sine(64, 1, op + 3*pi/2, 3);
    wave s_270_2 = sine(64, 1, 0 + 3*pi/2, 3);
    wave c_270_1 = cosine(64, 1, op + 3*pi/2, 3);
    wave c_270_2 = cosine(64, 1, 0 + 3*pi/2, 3);
    wave g_270_s1 = multiply(g, s_270_1);
    wave d_270_c1 = multiply(d, c_270_1);
    wave g_270_s2 = multiply(g, s_270_2);
    wave d_270_c2 = multiply(d, c_270_2);

    wave rxpi_out1 = 0.2*gs1+0.2*dc1;
    wave rxpi_out2 = 0.2*gs2+0.2*dc2;

    wave rxpiby2_out1 = 0.095*gs1+0.095*dc1;
    wave rxpiby2_out2 = 0.095*gs2+0.095*dc2;

    wave rxnpi_out1 = 0.2*g_180_s1+0.2*d_180_c1;
    wave rxnpi_out2 = 0.2*g_180_s2+0.2*d_180_c2;

    wave rxnpiby2_out1 = 0.095*g_180_s1+0.095*d_180_c1;
    wave rxnpiby2_out2 = 0.095*g_180_s2+0.095*d_180_c2;

    wave rypi_out1 = 0.2*g_90_s1+0.2*d_90_c1;
    wave rypi_out2 = 0.2*g_90_s2+0.2*d_90_c2;

    wave rypiby2_out1 = 0.095*g_90_s1+0.095*d_90_c1;
    wave rypiby2_out2 = 0.095*g_90_s2+0.095*d_90_c2;

    wave rynpi_out1 = 0.2*g_270_s1+0.2*d_270_c1;
    wave rynpi_out2 = 0.2*g_270_s2+0.2*d_270_c2;

    wave rynpiby2_out1 = 0.095*g_270_s1+0.095*d_270_c1;
    wave rynpiby2_out2 = 0.095*g_270_s2+0.095*d_270_c2;

    // IDENTITY (ground)
    while (getUserReg(0) == 1) {
        //playWave(zeros(1), zeros(1));
        waitWave();
        wait(6); // Unit CLK CYCLES; Added to have gap between control and measure pulses
        setTrigger(0b0010);
        wait(25*us/cycle);
        setTrigger(0b0000);
        wait(200*us/cycle);
    }

    // Rx(pi)
    while (getUserReg(0) == 2) {
        playWave(rxpi_out1, rxpi_out2);
        waitWave();
        wait(6); // Unit CLK CYCLES; Added to have gap between control and measure pulses
        setTrigger(0b0010);
        wait(25*us/cycle);
        setTrigger(0b0000);
        wait(200*us/cycle);
    }

    // Ry(pi)
    while (getUserReg(0) == 3) {
        playWave(rypi_out1, rypi_out2);
        waitWave();
        wait(6); // Unit CLK CYCLES; Added to have gap between control and measure pulses
        setTrigger(0b0010);
        wait(25*us/cycle);
        setTrigger(0b0000);
        wait(200*us/cycle);
    }

    // Rx(-pi)
    while (getUserReg(0) == 4) {
        playWave(rxnpi_out1, rxnpi_out2);
        waitWave();
        wait(6); // Unit CLK CYCLES; Added to have gap between control and measure pulses
        setTrigger(0b0010);
        wait(25*us/cycle);
        setTrigger(0b0000);
        wait(200*us/cycle);
    }

    // Ry(-pi)
    while (getUserReg(0) == 5) {
        playWave(rynpi_out1, rynpi_out2);
        waitWave();
        wait(6); // Unit CLK CYCLES; Added to have gap between control and measure pulses
        setTrigger(0b0010);
        wait(25*us/cycle);
        setTrigger(0b0000);
        wait(200*us/cycle);
    }

    // Rx(pi/2)
    while (getUserReg(0) == 6) {
        playWave(rxpiby2_out1, rxpiby2_out2);
        waitWave();
        wait(6); // Unit CLK CYCLES; Added to have gap between control and measure pulses
        setTrigger(0b0010);
        wait(25*us/cycle);
        setTrigger(0b0000);
        wait(200*us/cycle);
    }

    // Ry(pi/2)
    while (getUserReg(0) == 7) {
        playWave(rypiby2_out1, rypiby2_out2);
        waitWave();
        wait(6); // Unit CLK CYCLES; Added to have gap between control and measure pulses
        setTrigger(0b0010);
        wait(25*us/cycle);
        setTrigger(0b0000);
        wait(200*us/cycle);
    }

    // Rx(-pi/2)
    while (getUserReg(0) == 8) {
        playWave(rxnpiby2_out1, rxnpiby2_out2);
        waitWave();
        wait(6); // Unit CLK CYCLES; Added to have gap between control and measure pulses
        setTrigger(0b0010);
        wait(25*us/cycle);
        setTrigger(0b0000);
        wait(200*us/cycle);
    }

    // Ry(-pi/2)
    while (getUserReg(0) == 9) {
        playWave(rynpiby2_out1, rynpiby2_out2);
        waitWave();
        wait(6); // Unit CLK CYCLES; Added to have gap between control and measure pulses
        setTrigger(0b0010);
        wait(25*us/cycle);
        setTrigger(0b0000);
        wait(200*us/cycle);
    }

    // Rx(pi)Rx(pi)
    while (getUserReg(0) == 10) {
        playWave(join(rxpi_out1, rxpi_out1),
                 join(rxpi_out2, rxpi_out1));
        waitWave();
        wait(6); // Unit CLK CYCLES; Added to have gap between control and measure pulses
        setTrigger(0b0010);
        wait(25*us/cycle);
        setTrigger(0b0000);
        wait(200*us/cycle);
    }

    // Rx(-pi)Rx(-pi)
    while (getUserReg(0) == 11) {
        playWave(join(rxnpi_out1, rxnpi_out1),
                 join(rxnpi_out2, rxnpi_out1));
        waitWave();
        wait(6); // Unit CLK CYCLES; Added to have gap between control and measure pulses
        setTrigger(0b0010);
        wait(25*us/cycle);
        setTrigger(0b0000);
        wait(200*us/cycle);
    }

    // Rx(pi)Ry(pi)
    while (getUserReg(0) == 12) {
        playWave(join(rxpi_out1, rypi_out1),
                 join(rxpi_out2, rypi_out1));
        waitWave();
        wait(6); // Unit CLK CYCLES; Added to have gap between control and measure pulses
        setTrigger(0b0010);
        wait(25*us/cycle);
        setTrigger(0b0000);
        wait(200*us/cycle);
    }

    // Rx(pi)Ry(-pi)
    while (getUserReg(0) == 13) {
        playWave(join(rxpi_out1, rynpi_out1),
                 join(rxpi_out2, rynpi_out1));
        waitWave();
        wait(6); // Unit CLK CYCLES; Added to have gap between control and measure pulses
        setTrigger(0b0010);
        wait(25*us/cycle);
        setTrigger(0b0000);
        wait(200*us/cycle);
    }

    // Ry(pi)Rx(pi)
    while (getUserReg(0) == 14) {
        playWave(join(rypi_out1, rxpi_out1),
                 join(rypi_out2, rxpi_out1));
        waitWave();
        wait(6); // Unit CLK CYCLES; Added to have gap between control and measure pulses
        setTrigger(0b0010);
        wait(25*us/cycle);
        setTrigger(0b0000);
        wait(200*us/cycle);
    }

    // Ry(pi)Rx(-pi)
    while (getUserReg(0) == 15) {
        playWave(join(rypi_out1, rxnpi_out1),
                 join(rypi_out2, rxnpi_out1));
        waitWave();
        wait(6); // Unit CLK CYCLES; Added to have gap between control and measure pulses
        setTrigger(0b0010);
        wait(25*us/cycle);
        setTrigger(0b0000);
        wait(200*us/cycle);
    }

    // Ry(pi)Ry(pi)
    while (getUserReg(0) == 16) {
        playWave(join(rypi_out1, rypi_out1),
                 join(rypi_out2, rypi_out1));
        waitWave();
        wait(6); // Unit CLK CYCLES; Added to have gap between control and measure pulses
        setTrigger(0b0010);
        wait(25*us/cycle);
        setTrigger(0b0000);
        wait(200*us/cycle);
    }

    // Ry(pi)Ry(-pi)
    while (getUserReg(0) == 17) {
        playWave(join(rypi_out1, rynpi_out1),
                 join(rypi_out2, rynpi_out1));
        waitWave();
        wait(6); // Unit CLK CYCLES; Added to have gap between control and measure pulses
        setTrigger(0b0010);
        wait(25*us/cycle);
        setTrigger(0b0000);
        wait(200*us/cycle);
    }

    // Rx(pi)Rx(pi/2)
    while (getUserReg(0) == 18) {
        playWave(join(rxpi_out1, rxpiby2_out1),
                 join(rxpi_out2, rxpiby2_out1));
        waitWave();
        wait(6); // Unit CLK CYCLES; Added to have gap between control and measure pulses
        setTrigger(0b0010);
        wait(25*us/cycle);
        setTrigger(0b0000);
        wait(200*us/cycle);
    }

    // Rx(pi)Rx(-pi/2)
    while (getUserReg(0) == 19) {
        playWave(join(rxpi_out1, rxnpiby2_out1),
                 join(rxpi_out2, rxnpiby2_out1));
        waitWave();
        wait(6); // Unit CLK CYCLES; Added to have gap between control and measure pulses
        setTrigger(0b0010);
        wait(25*us/cycle);
        setTrigger(0b0000);
        wait(200*us/cycle);
    }

    // Rx(pi)Ry(pi/2)
    while (getUserReg(0) == 20) {
        playWave(join(rxpi_out1, rypiby2_out1),
                 join(rxpi_out2, rypiby2_out1));
        waitWave();
        wait(6); // Unit CLK CYCLES; Added to have gap between control and measure pulses
        setTrigger(0b0010);
        wait(25*us/cycle);
        setTrigger(0b0000);
        wait(200*us/cycle);
    }

    // Rx(pi)Ry(-pi/2)
    while (getUserReg(0) == 21) {
        playWave(join(rxpi_out1, rynpiby2_out1),
                 join(rxpi_out2, rynpiby2_out1));
        waitWave();
        wait(6); // Unit CLK CYCLES; Added to have gap between control and measure pulses
        setTrigger(0b0010);
        wait(25*us/cycle);
        setTrigger(0b0000);
        wait(200*us/cycle);
    }

    // Ry(pi)Rx(pi/2)
    while (getUserReg(0) == 22) {
        playWave(join(rypi_out1, rxpiby2_out1),
                 join(rypi_out2, rxpiby2_out1));
        waitWave();
        wait(6); // Unit CLK CYCLES; Added to have gap between control and measure pulses
        setTrigger(0b0010);
        wait(25*us/cycle);
        setTrigger(0b0000);
        wait(200*us/cycle);
    }

    // Ry(pi)Rx(-pi/2)
    while (getUserReg(0) == 23) {
        playWave(join(rypi_out1, rxnpiby2_out1),
                 join(rypi_out2, rxnpiby2_out1));
        waitWave();
        wait(6); // Unit CLK CYCLES; Added to have gap between control and measure pulses
        setTrigger(0b0010);
        wait(25*us/cycle);
        setTrigger(0b0000);
        wait(200*us/cycle);
    }

    // Ry(pi)Ry(pi/2)
    while (getUserReg(0) == 24) {
        playWave(join(rypi_out1, rypiby2_out1),
                 join(rypi_out2, rypiby2_out1));
        waitWave();
        wait(6); // Unit CLK CYCLES; Added to have gap between control and measure pulses
        setTrigger(0b0010);
        wait(25*us/cycle);
        setTrigger(0b0000);
        wait(200*us/cycle);
    }

    // Ry(pi)Ry(-pi/2)
    while (getUserReg(0) == 25) {
        playWave(join(rypi_out1, rynpiby2_out1),
                 join(rypi_out2, rynpiby2_out1));
        waitWave();
        wait(6); // Unit CLK CYCLES; Added to have gap between control and measure pulses
        setTrigger(0b0010);
        wait(25*us/cycle);
        setTrigger(0b0000);
        wait(200*us/cycle);
    }

    // Rx(pi/2)Rx(pi)
    while (getUserReg(0) == 26) {
        playWave(join(rxpiby2_out1, rxpi_out1),
                 join(rxpiby2_out2, rxpi_out1));
        waitWave();
        wait(6); // Unit CLK CYCLES; Added to have gap between control and measure pulses
        setTrigger(0b0010);
        wait(25*us/cycle);
        setTrigger(0b0000);
        wait(200*us/cycle);
    }

    // Rx(pi/2)Ry(pi)
    while (getUserReg(0) == 27) {
        playWave(join(rxpiby2_out1, rypi_out1),
                 join(rxpiby2_out2, rypi_out1));
        waitWave();
        wait(6); // Unit CLK CYCLES; Added to have gap between control and measure pulses
        setTrigger(0b0010);
        wait(25*us/cycle);
        setTrigger(0b0000);
        wait(200*us/cycle);
    }

    // Ry(pi/2)Rx(pi)
    while (getUserReg(0) == 28) {
        playWave(join(rypiby2_out1, rxpi_out1),
                 join(rypiby2_out2, rxpi_out1));
        waitWave();
        wait(6); // Unit CLK CYCLES; Added to have gap between control and measure pulses
        setTrigger(0b0010);
        wait(25*us/cycle);
        setTrigger(0b0000);
        wait(200*us/cycle);
    }

    // Ry(pi/2)Ry(pi)
    while (getUserReg(0) == 29) {
        playWave(join(rypiby2_out1, rypi_out1),
                 join(rypiby2_out2, rypi_out1));
        waitWave();
        wait(6); // Unit CLK CYCLES; Added to have gap between control and measure pulses
        setTrigger(0b0010);
        wait(25*us/cycle);
        setTrigger(0b0000);
        wait(200*us/cycle);
    }

    // Rx(pi/2)Rx(pi/2)
    while (getUserReg(0) == 30) {
        playWave(join(rxpiby2_out1, rxpiby2_out1),
                 join(rxpiby2_out2, rxpiby2_out1));
        waitWave();
        wait(6); // Unit CLK CYCLES; Added to have gap between control and measure pulses
        setTrigger(0b0010);
        wait(25*us/cycle);
        setTrigger(0b0000);
        wait(200*us/cycle);
    }

    // Rx(pi/2)Rx(-pi/2)
    while (getUserReg(0) == 31) {
        playWave(join(rxpiby2_out1, rxnpiby2_out1),
                 join(rxpiby2_out2, rxnpiby2_out1));
        waitWave();
        wait(6); // Unit CLK CYCLES; Added to have gap between control and measure pulses
        setTrigger(0b0010);
        wait(25*us/cycle);
        setTrigger(0b0000);
        wait(200*us/cycle);
    }

    // Rx(pi/2)Ry(pi/2)
    while (getUserReg(0) == 32) {
        playWave(join(rxpiby2_out1, rypiby2_out1),
                 join(rxpiby2_out2, rypiby2_out1));
        waitWave();
        wait(6); // Unit CLK CYCLES; Added to have gap between control and measure pulses
        setTrigger(0b0010);
        wait(25*us/cycle);
        setTrigger(0b0000);
        wait(200*us/cycle);
    }

    // Rx(pi/2)Ry(-pi/2)
    while (getUserReg(0) == 33) {
        playWave(join(rxpiby2_out1, rynpiby2_out1),
                 join(rxpiby2_out2, rynpiby2_out1));
        waitWave();
        wait(6); // Unit CLK CYCLES; Added to have gap between control and measure pulses
        setTrigger(0b0010);
        wait(25*us/cycle);
        setTrigger(0b0000);
        wait(200*us/cycle);
    }

    // Ry(pi/2)Rx(pi/2)
    while (getUserReg(0) == 34) {
        playWave(join(rypiby2_out1, rxpiby2_out1),
                 join(rypiby2_out2, rxpiby2_out1));
        waitWave();
        wait(6); // Unit CLK CYCLES; Added to have gap between control and measure pulses
        setTrigger(0b0010);
        wait(25*us/cycle);
        setTrigger(0b0000);
        wait(200*us/cycle);
    }

    // Ry(pi/2)Rx(-pi/2)
    while (getUserReg(0) == 35) {
        playWave(join(rypiby2_out1, rxnpiby2_out1),
                 join(rypiby2_out2, rxnpiby2_out1));
        waitWave();
        wait(6); // Unit CLK CYCLES; Added to have gap between control and measure pulses
        setTrigger(0b0010);
        wait(25*us/cycle);
        setTrigger(0b0000);
        wait(200*us/cycle);
    }

    // Ry(pi/2)Ry(pi/2)
    while (getUserReg(0) == 36) {
        playWave(join(rypiby2_out1, rypiby2_out1),
                 join(rypiby2_out2, rypiby2_out1));
        waitWave();
        wait(6); // Unit CLK CYCLES; Added to have gap between control and measure pulses
        setTrigger(0b0010);
        wait(25*us/cycle);
        setTrigger(0b0000);
        wait(200*us/cycle);
    }

    // Ry(pi/2)Ry(-pi/2)
    while (getUserReg(0) == 37) {
        playWave(join(rypiby2_out1, rynpiby2_out1),
                 join(rypiby2_out2, rynpiby2_out1));
        waitWave();
        wait(6); // Unit CLK CYCLES; Added to have gap between control and measure pulses
        setTrigger(0b0010);
        wait(25*us/cycle);
        setTrigger(0b0000);
        wait(200*us/cycle);
    }

    '''%D
    return awg_program

##############################################

uhf = ZurichInstruments_UHFLI('dev2232')
rte = qt.instruments.create('RTE1104', 'RhodeSchwartz_RTE1104', address = 'TCPIP0::192.168.1.6::INSTR')
# aps = qt.instruments.create('APSYN420',   'AnaPico_APSYN420',         address = APSYN420_ADDRESS)
# fsv = qt.instruments.create('FSV', 'RhodeSchwartz_FSV', address = FSV_ADDRESS)
# smf = qt.instruments.create('SMF100', 'RhodeSchwartz_SMF100', address = SMF100_ADDRESS)
# aps = qt.instruments.create('APSYN420',   'AnaPico_APSYN420',         address = APSYN420_ADDRESS)
# znb = qt.instruments.create('ZNB20', 'RhodeSchwartz_ZNB20', address=ZNB20_ADDRESS)

##############################################

def generate_meta_file():
    metafile = open('%s.meta.txt' % data.get_filepath()[:-4], 'w')
    metafile.write('#inner loop\n%s\n%s\n%s\n%s\n'%
            (record_length,  start_time/us, stop_time/us, 'Time(us)'))
    metafile.write('#outer loop\n%s\n%s\n%s\n%s\n'%
            (50, 50, 1, 'Tomography Step'))
    metafile.write('#outermost loop\n1\n0\n1\nNothing\n')

    metafile.write('#for each of the values\n')
    values = data.get_values()
    i=0
    while i<len(values):
        metafile.write('%d\n%s\n'% (i+4, values[i]['name']))
        i+=1
    metafile.close()
##################################################
def copy_script():
    shutil.copy2('%s'%sys.argv[0],'%s/%s'%(data.get_filepath()[:-(len(data_file_name)+11)],os.path.basename(sys.argv[0])))

###################################################################
#############  RUN once to setup the innermost loop

channels = [1,2]
start = time.time()
# rte.wait_till_complete()
start_time, stop_time, record_length = rte.get_header()
assert raw_input('continue? [y/n]').upper() != 'N'

####################################################################

data_file_name = raw_input('Enter name of data file: ')

data=qt.Data(name=data_file_name)
data.add_comment('Number of points in one step is %d' % record_length)

# data.add_comment('Step 1: IDENTITY')
# data.add_comment('Step 2: Rx(pi)')
# data.add_comment('Step 3: Rx(pi/2)')
# data.add_comment('Step 4: Rx(pi)Ry(pi/2)')
# data.add_comment('Step 5: Rx(pi)Ry(-pi/2)')

data.add_comment('Step 1: IDENTITY')
data.add_comment('Step 2: Rx(pi)')
data.add_comment('Step 3: Ry(pi)')
data.add_comment('Step 4: Rx(-pi)')
data.add_comment('Step 5: Ry(-pi)')

data.add_comment('Step 6: Rx(pi/2)')
data.add_comment('Step 7: Ry(pi/2)')
data.add_comment('Step 8: Rx(-pi/2)')
data.add_comment('Step 9: Ry(-pi/2)')

data.add_comment('Step 10: Rx(pi)Rx(pi)')
data.add_comment('Step 11: Rx(-pi)Rx(-pi)')
data.add_comment('Step 12: Rx(pi)Ry(pi)')
data.add_comment('Step 13: Rx(pi)Ry(-pi)')
data.add_comment('Step 14: Ry(pi)Rx(pi)')
data.add_comment('Step 15: Ry(pi)Rx(-pi)')
data.add_comment('Step 16: Ry(pi)Ry(pi)')
data.add_comment('Step 17: Ry(pi)Ry(-pi)')

data.add_comment('Step 18: Rx(pi)Rx(pi/2)')
data.add_comment('Step 19: Rx(pi)Rx(-pi/2)')
data.add_comment('Step 20: Rx(pi)Ry(pi/2)')
data.add_comment('Step 21: Rx(pi)Ry(-pi/2)')
data.add_comment('Step 22: Ry(pi)Rx(pi/2)')
data.add_comment('Step 23: Ry(pi)Rx(-pi/2)')
data.add_comment('Step 24: Ry(pi)Ry(pi/2)')
data.add_comment('Step 25: Ry(pi)Rx(-pi/2)')
data.add_comment('Step 26: Rx(pi/2)Rx(pi)')
data.add_comment('Step 27: Rx(pi/2)Ry(pi)')
data.add_comment('Step 28: Ry(pi/2)Rx(pi)')
data.add_comment('Step 29: Ry(pi/2)Ry(pi)')

data.add_comment('Step 30: Rx(pi/2)Rx(pi/2)')
data.add_comment('Step 31: Rx(pi/2)Rx(-pi/2)')
data.add_comment('Step 32: Rx(pi/2)Ry(pi/2)')
data.add_comment('Step 33: Rx(pi/2)Ry(-pi/2)')

data.add_comment('Step 34: Ry(pi/2)Rx(pi/2)')
data.add_comment('Step 35: Ry(pi/2)Rx(-pi/2)')
data.add_comment('Step 36: Ry(pi/2)Ry(pi/2)')
data.add_comment('Step 37: Ry(pi/2)Ry(-pi/2)')

# data.add_coordinate('Frequency', units = 'Hz')
data.add_coordinate('Time', units = 's')

data.add_value('X-Quadrature')
data.add_value('Y-Quadrature')
data.add_value('R-Quadrature')

#######################################################################
once = True

# Without and with DRAG
for D in [0.0, 0.5]:
    uhf.setup_awg(awg_program(D))
    uhf.awg_on(single=False)

    uhf.set('awgs/0/userregs/0', 1.0)
    rte.reset_averages()
    rte.run_nx_single(wait=True)
    time_array, voltages = rte.get_data(channels)
    voltages.append((voltages[0]**2+voltages[1]**2)**0.5)
    data.add_data_point(time_array, *voltages)

    if once:
        copy_script()
        generate_meta_file()
    once = False

    for reg_val in range(2, 38):
        uhf.set('awgs/0/userregs/0', float(reg_val))
        rte.reset_averages()
        rte.run_nx_single(wait=True)
        time_array, voltages = rte.get_data(channels)
        voltages.append((voltages[0]**2+voltages[1]**2)**0.5)
        data.add_data_point(time_array, *voltages)