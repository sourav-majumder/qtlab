import os
import sys
import lib

def insert_in_file_list(entries, entry, ignore_list):
    adddir, addname = entry
    if os.path.splitext(addname)[1] != ".py":
        return

    for start in ignore_list:
        if addname.startswith(start):
            return

    index = 0
    for (dir, name) in entries:
        if name[0] > addname[0] or (name[0] == addname[0] and name[1] > addname[1]):
            entries.insert(index, entry)
            break
        index += 1

    if index == len(entries):
        entries.append(entry)

def get_shell_files(path, ignore_list):
    ret = []

    entries = os.listdir(path)
    for i in entries:
        if len(i) > 0 and i[0] == '.':
            continue

        if os.path.isdir(i):
            subret = get_shell_files(os.path.join(path, i))
            for j in subret:
                insert_in_file_list(ret, j, ignore_list)
        else:
            insert_in_file_list(ret, (path, i), ignore_list)

    return ret

def show_start_help():
    print 'Usage: qtlab <options> <directory> <files>'
    print '\t<directory> is an optional directory to start in'
    print '\t<files> is an optional list of scripts to execute'
    print '\tOptions:'
    print '\t--help\t\tShow this help'
    print '\t-i <pattern>\tIgnore shell scripts starting with <pattern>'
    print '\t\t\t(can be used multiple times'

    import IPython
    ip = lib.misc.get_ipython_backward_compatible()
    ip_version = IPython.__version__.split('.')
    if int(ip_version[0]) > 0 or int(ip_version[1]) > 10:
        ip.exit()
    else:
        ip.magic('Exit')

def do_start():
    basedir = os.path.split(os.path.dirname(sys.argv[0]))[0]
    sys.path.append(os.path.abspath(os.path.join(basedir, 'source')))

    ignorelist = []
    i = 1

    global __startdir__
    __startdir__ = None
    # FIXME: use of __startdir__ is spread over multiple scripts:
    # 1) source/qtlab_client_shell.py
    # 2) init/02_qtlab_start.py
    # This should be solved differently
    while i < len(sys.argv):
        if os.path.isdir(sys.argv[i]):
            __startdir__ = sys.argv[i]
        elif sys.argv[i] == '-i':
            i += 1
            ignorelist.append(sys.argv[i])
        elif sys.argv[i] == '--help':
            show_start_help()
            return []
        i += 1

    filelist = get_shell_files(os.path.join(basedir, 'init'), ignorelist)
    return filelist

if __name__ == '__main__':
    print 'Starting QT Lab environment...'
    filelist = do_start()
    for (dir, name) in filelist:
        filename = '%s/%s' % (dir, name)
        print 'Executing %s...' % (filename)
        try:
            execfile(filename)
        except SystemExit:
            break

    try:
        del filelist, dir, name, filename
    except:
        pass

import qt
import easygui
import numpy as np

from constants import *

meas = []
tr_chan_numbers = []
trace_numbers = []
trace_names = []

def generate_meta_file():
    metafile = open('%s.meta.txt' % data.get_filepath()[:-4], 'w')
    metafile.write('#inner loop\n%s\n%s\n%s\n%s\n'%
            (numpoints, start_frequency, stop_frequency, 'Frequency(Hz)'))
    metafile.write('#outer loop\n1\n0\n1\nNothing\n')
    metafile.write('#outermost loop (unused)\n1\n0\n1\nNothing\n')

    metafile.write('#for each of the values\n')
    values = data.get_values()
    i=0
    while i<len(values):
        metafile.write('%d\n%s\n'% (i+3, values[i]['name']))
        i+=1
    metafile.close()

def s_to_ch_tr(znb):
	channel_numbers, channel_names = znb.ch_catalog()
	inst = znb.get_instrument()
	
	for chan in channel_numbers:
		  tr_numbers, tr_names = znb.trace_catalog(chan)
		  for tr_n, tr in zip(tr_numbers,tr_names):
			inst.write('CALC%d:PAR:SEL "%s"' % (chan,tr))
			sparam = inst.ask('SENSE%u:FUNCTION?' % chan).strip().strip("'").upper().split(":")[2]
			meas.append(sparam)
			tr_chan_numbers.append(chan)
			trace_numbers.append(tr_n)
			trace_names.append(tr)

znb = qt.instruments.create('ZNB20', 'RhodeSchwartz_ZNB20', address=ZNB20_ADDRESS)
s_to_ch_tr(znb)

msg = "Enter details of trace"
title = "VNA get data"
fieldNames = ["Datafile Name", "Parameter","Channel"]
fieldValues = ['Just 1 Trace', meas[0], tr_chan_numbers[0]]  # we start with blanks for the values
fieldValues = easygui.multenterbox(msg,title, fieldNames)

if fieldValues is not None:
	try:
		filename = str(fieldValues[0])
		### SETTING UP DATA FILE
		data=qt.Data(name=filename)
		s_param = str(fieldValues[1]).upper()
		channel_to_get_from = znb.s_to_ch_tr_dict(int(fieldValues[2]))[s_param][0]
		# data.add_comment('No. of repeated measurements for average is 60')
		data.add_coordinate('Frequency', units='Hz')
		data.add_comment('Power: %.12f dBm' % znb.get_source_power())
		start_frequency = znb.get_start_frequency()
		stop_frequency = znb.get_stop_frequency()
		numpoints = znb.get_numpoints()
		data.add_comment('Start Frequency: %.12f Hz' % start_frequency)
		data.add_comment('Stop Frequency: %.12f Hz' % stop_frequency)
		data.add_comment('IF Bandwidth: %.12f Hz' % znb.get_if_bandwidth())
		data.add_comment('Points: %d' % numpoints)
		data.add_value('%s real' % s_param)
		data.add_value('%s imag' % s_param)
		data.add_value('%s abs' % s_param)
		data.add_value('%s phase' % s_param)

		freq_array = np.linspace(start_frequency, stop_frequency, numpoints)
		traces = []
		trace = znb.get_data(s_param, channel_to_get_from)
		traces.append(np.real(trace))
		traces.append(np.imag(trace))
		traces.append(np.absolute(trace))
		traces.append(np.angle(trace))
		data.add_data_point(freq_array, *traces)
		generate_meta_file()

	except KeyError:
		print "%s is not being measured in channel %d" % (str(fieldValues[0]).upper(), int(fieldValues[1]))
	except ValueError:
		print "Please enter an integer for channel and a valid s-parameter"
	finally:
		data.close_file()