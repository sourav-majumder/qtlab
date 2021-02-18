# Driver for Rhode & Schwartz VNA ZNB40
# Russell Lake <russell.lake@aalto.fi>, 2014
# Joonas Govenius <joonas.govenius@aalto.fi>, 2015
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

from instrument import Instrument
import visa
from visa import VisaIOError
import types
import logging
import numpy as np
import struct


import qt

class ZNB20Exception(Exception):
        pass
    
class RhodeSchwartz_ZNB20(Instrument):
    '''
    This is the driver for the Rohde & Schwarz ZNB20 VNA.

    Note that, for simplicity, the set functions set the specified
    parameter for all channels.
    The get functions return the value for the currently active channel.

    Usage:
    Initialize with
    <name> = qt.instruments.create('<name>', 'RhodeSchwartz_ZNB20',
        address='TCPIP::<IP-address>::INSTR',
        reset=<bool>,)

    For GPIB the address is: 'GPIB<interface_nunmber>::<gpib-address>'
    '''
        
    
    def __init__(self, name, address, reset=False):
        '''
        Initializes a R&S ZNB20, and communicates with the wrapper.

        Input:
            name (string)           : name of the instrument
            address (string)        : GPIB address
            reset (bool)            : resets to default values
        '''
        # Initialize wrapper functions
        logging.info('Initializing instrument Rohde & Schwarz ZNB 2 Vector Network Analyser.')
        Instrument.__init__(self, name, tags=['physical'])

        # Add some global constants
        self._address = address
        self._default_timeout = 4000. # ms
        self._visainstrument = visa.ResourceManager().open_resource(self._address,
                                                                    timeout=self._default_timeout)
        self._freq_unit = 1
        self._freq_unit_symbol = 'Hz'
        

        # Add parameters to wrapper

        self.add_parameter('start_frequency', type=types.FloatType, format='%.6e',
                           flags=Instrument.FLAG_GETSET|Instrument.FLAG_GET_AFTER_SET,
                           units=self._freq_unit_symbol, minval=100e3/self._freq_unit, maxval=20e9/self._freq_unit)
        self.add_parameter('stop_frequency', type=types.FloatType, format='%.6e',
                           flags=Instrument.FLAG_GETSET|Instrument.FLAG_GET_AFTER_SET,
                           units=self._freq_unit_symbol, minval=100e3/self._freq_unit, maxval=20e9/self._freq_unit)
        self.add_parameter('start_power', type=types.FloatType, format='%.6e',
                           flags=Instrument.FLAG_GETSET|Instrument.FLAG_GET_AFTER_SET,
                           units=self._freq_unit_symbol, minval=-60, maxval=13)
        self.add_parameter('stop_power', type=types.FloatType, format='%.6e',
                           flags=Instrument.FLAG_GETSET|Instrument.FLAG_GET_AFTER_SET,
                           units=self._freq_unit_symbol, minval=-60, maxval=13)

        self.add_parameter('center_frequency', type=types.FloatType, format='%.06e',
                          flags=Instrument.FLAG_GETSET|Instrument.FLAG_GET_AFTER_SET,
                           units=self._freq_unit_symbol, minval=110e3/self._freq_unit, maxval=20e9/self._freq_unit)

        self.add_parameter('span', type=types.FloatType, format='%.06e',
                          flags=Instrument.FLAG_GETSET|Instrument.FLAG_GET_AFTER_SET,
                          units=self._freq_unit_symbol, minval=1/self._freq_unit, maxval=19e9/self._freq_unit)

        self.add_parameter('numpoints', type=types.IntType, format='%g',
                           flags=Instrument.FLAG_GETSET|Instrument.FLAG_GET_AFTER_SET,
                           units='', minval=1, maxval=100001)
        self.add_parameter('average_mode', type=types.StringType,
                           flags=Instrument.FLAG_GETSET|Instrument.FLAG_GET_AFTER_SET,
                           format_map={'AUTO': 'automatic',
                                       'FLAT': 'cumulative average of magnitude and phase',
                                       'RED': 'cumulative average of quadratures',
                                       'MOV': 'simple average of quadratures'})
        self.add_parameter('averages', type=types.IntType,
                           flags=Instrument.FLAG_GETSET|Instrument.FLAG_GET_AFTER_SET,
                           minval=1, maxval=1000)
        self.add_parameter('if_bandwidth', type=types.FloatType, format='%.0e',
                           minval=1., maxval=1e6,
                           flags=Instrument.FLAG_GETSET|Instrument.FLAG_GET_AFTER_SET,
                           units=self._freq_unit_symbol)
        self.add_parameter('if_selectivity', type=types.StringType,
                           flags=Instrument.FLAG_GETSET|Instrument.FLAG_GET_AFTER_SET,
                           format_map={'NORM': 'normal',
                                       'MED': 'medium',
                                       'HIGH': 'high'})
        #changed sweeptime parameter to GETSET
        self.add_parameter('sweeptime', type=types.FloatType, format='%g',
                           flags=Instrument.FLAG_GETSET|Instrument.FLAG_GET_AFTER_SET,
                           units='s')
        self.add_parameter('sweeptime_auto', type=types.BooleanType,
                           flags=Instrument.FLAG_GETSET|Instrument.FLAG_GET_AFTER_SET)

        #min power is set to -60 dBm for the power extended option
        self.add_parameter('source_power', type=types.FloatType,
                           flags=Instrument.FLAG_GETSET|Instrument.FLAG_GET_AFTER_SET,
                           units='dBm',minval=-60., maxval=15.)

        self.add_parameter('trigger_source', type=types.StringType,
                          flags=Instrument.FLAG_GETSET|Instrument.FLAG_GET_AFTER_SET,
                          format_map = {
                            "imm" : "immediate (continuous)",
                            "ext" : "external",
                            "line" : "line",
                            "tim" : "periodic timer",                            "rtcl" : "real time clock",
                            "man" : "manual"
                          })

        self.add_parameter('sweep_mode', type=types.StringType,
                          flags=Instrument.FLAG_GETSET|Instrument.FLAG_GET_AFTER_SET,
                          format_map = {
                           "single" : "single",
                           "cont" : "continuous"
                          })

        self.add_parameter('external_reference', type=types.BooleanType,
                          flags=Instrument.FLAG_GETSET|Instrument.FLAG_GET_AFTER_SET)

        self.add_parameter('external_reference_frequency', type=types.IntType,
                          flags=Instrument.FLAG_GETSET|Instrument.FLAG_GET_AFTER_SET,
                          units='MHz')
        self.add_parameter('sweep_type', type=types.StringType,
                          flags=Instrument.FLAG_GETSET|Instrument.FLAG_GET_AFTER_SET,
                          format_map = {
                            "lin" : "linear",
                            "log" : "logarithmic",
                            "pow" : "power",
                            "cw" : "cw",
                            "point":"point",
                            "seg": "segment"
                          })

        self.add_function('reset')
        self.add_function('send_trigger')
        self.add_function('get_all')

        # for backwards compatibility with the old parameter name ("span_frequency")
        self.add_function('get_span_frequency')
        self.add_function('set_span_frequency')
        
        if reset:
            self.reset()
        else:
#            self.set_default_window_config()
#            self.set_default_channel_config()
            self.get_all()
        

# --------------------------------------
#           functions
# --------------------------------------

    # for backwards compatibility with the old parameter name "span_frequency"
    def get_span_frequency(self): return self.get_span()
    def set_span_frequency(self, s): self.set_span(s)

    #[US]for convenience
    def address(self):
        return self._address
    def get_instrument(self):
        return self._visainstrument
    def wait(self):
        self._visainstrument.write('*WAI')
    def wait_till_complete(self, channel_number):
        try:
                self._visainstrument.query('*ESR?')
                self._visainstrument.write('*OPC')
                sweeptime=self.get_sweeptime(channel_number = channel_number)
                # print (sweeptime)
                qt.msleep(sweeptime - 2.)
                while int(self.ask('*ESR?').strip())%2==0:
                        qt.msleep(0.1)
        except VisaIOError:
                print ('VNA timed out. It may be preparing the sweep.\nPress enter to start the sweep.')
                raw_input()
                self.send_trigger(channel_number = channel_number ,wait=True)
        except KeyboardInterrupt:
                raise ZNB20Exception('Interrupted in middle of sweep')
        
    def reset(self):
        self._visainstrument.write('*RST') #reset to default settings
#      self.set_default_channel_config()
#      self.set_default_window_config()
        self.set_sweep_mode('single')
        self._visainstrument.write('SOUR:POW1:STAT OFF')
        self._visainstrument.write('SOUR:POW2:STAT OFF')
        self.delete_all_traces()
        self.get_all()

    def autoscale(self):
        wnd_numbers, wnd_names = self.window_catalog()
        for wnd in wnd_numbers:
          self._visainstrument.write('DISP:WIND%d:TRAC%d:Y:AUTO ONCE' % (wnd,wnd))

    def rf_on(self):
        self._visainstrument.write('SOUR:POW:STAT ON')
    def rf_off(self):
        self._visainstrument.write('SOUR:POW:STAT OFF')
 

    def clear_status_reg(self):
      self._visainstrument.write('*CLS')

    def send_trigger(self,channel_number=1, wait=False):
      s = self.get_trigger_source(channel_number)
      if s == 'imm':
          self._visainstrument.write('INIT%s'%channel_number)
          # self._visainstrument.write('*WAI')
          if wait:
                self.wait_till_complete(channel_number)
      elif s == 'man':
          self._visainstrument.write('*TRG')
          if wait:
                self.wait_till_complete(channel_number)
      else:
          raise Exception('Not sure how to trigger manually when trigger source is set to "%s"' % s)

    def sweep_number(self, n):
        self._visainstrument.write('SENSE:SWEEP:COUNT:ALL %u' % n)
        
    def trigger_n_times(self, n, block_until_done=False):
        ''' Trigger exactly n sweeps. Waits until done before returning iff block_until_done==True. '''
        self._visainstrument.write('SENSE:SWEEP:COUNT:ALL %u' % n)
        cmd = 'INIT:IMM:ALL%s' % ('; *OPC?' if block_until_done else '')
        min_wait_time = n*self.get_sweeptime()
        if block_until_done and min_wait_time < 10.:
          r = self._visainstrument.ask(cmd)
          assert r.strip() == '1', r
        else:
          self._visainstrument.write(cmd)
          if block_until_done:
            qt.msleep(min_wait_time - 5.)
            r = self._visainstrument.read()
            assert r.strip() == '1', r

    def clear_averages(self):
        ''' Restart averaging (on all channels). '''
        ch_numbers, ch_names = self.ch_catalog()
        for chan in ch_numbers:
          self._visainstrument.write('SENSE%s:AVER:CLE' % (chan))

    def autoscale_diagram(self, window_number = 1):
        # ch_numbers, ch_names = self.ch_catalog()
        tr_num, _ =  self.list_traces_in_window(window_number)
        for i in tr_num:
          self._visainstrument.write('DISPlay:WINDow%s:TRAC%s:Y:SCALe:AUTO ONCE' % (window_number,i))
    
    def autoscale_once(self, channel_number = 1):
        # ch_numbers, ch_names = self.ch_catalog()
        self._visainstrument.write('DISPlay:WINDow%u:TRAC%u:Y:SCALe:AUTO ONCE' % (channel_number,channel_number))

    def set_S21_only_channel_config(self):
        self._visainstrument.write('*RST')
        self._visainstrument.write('SYSTEM:DISPLAY:UPDATE ON')
        self.set_sweep_mode('single')
        self.autoscale_once()
        self.get_all()

    def set_default_channel_config(self):
        default_channel_to_s = { 1: 'S11', 2: 'S21', 3: 'S12', 4: 'S22' }
        self._visainstrument.write('*RST')
        self.set_sweep_mode('single')
        for chan in range(1,5):
          self._visainstrument.write(':CALCULATE%d:PARAMETER:SDEFINE "Trc%u", "%s"' % (chan,chan, default_channel_to_s[chan]))
          self._visainstrument.write(':DISPLAY:WINDOW%u:STATE ON' % chan)
          self._visainstrument.write(':DISPLAY:WINDOW%u:TRACE%u:FEED "Trc%u"' % (chan, chan, chan))
        self._visainstrument.write('SYSTEM:DISPLAY:UPDATE ON')
        self.get_all()

    def delete_all_traces(self):
        self._visainstrument.write('CALC:PAR:DEL:ALL')
        
    #[US]funtion to add channel
    def add_channel(self, parameter):
        self.set_sweep_mode('cont')
        ch_numbers, ch_names = self.ch_catalog()
        i=1
        while i<=len(ch_numbers)+1:
            if i in ch_numbers:
                i+=1
            else:
                chan=i
                break
        print chan
        self._visainstrument.write(':CALCULATE%d:PARAMETER:SDEFINE "Trc%u", "%s"' % (chan, chan, parameter))
        self._visainstrument.write(':DISPLAY:WINDOW%u:STATE ON' % chan)
        self._visainstrument.write(':DISPLAY:WINDOW%u:TRACE%u:FEED "Trc%u"' % (chan, chan,chan))
        self._visainstrument.write('SYSTEM:DISPLAY:UPDATE ON')

     #[US]
    def add_trace(self,measurement,channel_number=1):
        tr_numbers, tr_names = self.trace_catalog()
        ch_numbers, ch_names = self.ch_catalog()
        i=1
        p=1
        while i<=len(tr_numbers)+1:
            if i in tr_numbers:
                i+=1
            else:
                trace_number=i
                break
        trace_name = 'Ch%dTr%d' % (channel_number, trace_number)
        if trace_name in tr_names:
          print 'trace name already exist'
        else:
          self._visainstrument.write(':CALCULATE%d:PARAMETER:SDEFINE "%s", "%s"' % (channel_number, trace_name,measurement ))
          self._visainstrument.write(':DISPLAY:WINDOW%u:STATE ON' % channel_number)
          self._visainstrument.write(':DISPLAY:WINDOW%u:TRACE%u:FEED "%s"' % (channel_number, trace_number,trace_name))
          self._visainstrument.write('SYSTEM:DISPLAY:UPDATE ON')
        

    def get_all(self):
        self.get_sweep_mode()
        self.get_trigger_source()
        self.get_start_frequency()
        self.get_stop_frequency()
        self.get_numpoints()
        self.get_average_mode()
        self.get_averages()
        self.get_if_bandwidth()
        self.get_if_selectivity()
        self.get_external_reference()
        self.get_external_reference_frequency()
        self.get_source_power()
        self.get_sweeptime()
        self.get_sweeptime_auto()
        self.get_center_frequency()
        self.get_span()
        
    def get_data(self, s_parameter, channel_number=1):
        '''
        Get the measured S parameter.
        s_parameter --- must be one of ['S11', 'S21', 'S12', 'S22']
        '''
        s = s_parameter.upper().strip()
        assert s in ['S11', 'S21', 'S12', 'S22'], 'Invalid S-parameter: %s' % s
        logging.debug(__name__ + ' : Get %s data.' % s)
        
        # check that the requested S parameter is being measured on some channel_number
        try:
            s2chan, s2tr, s2tr_name = self.s_to_ch_tr_dict(channel_number)[s]
        except KeyError:
            logging.warn('%s is not currently being measured.', s)
            raise

        # Verify the function (again <-- seems unnecessary but doesn't hurt either)
        self._visainstrument.write('CALC%d:PAR:SEL "%s"' % (s2chan, s2tr_name))
        r = self._visainstrument.ask('SENSe%u:FUNCtion?' % s2chan)
        assert r.strip().strip("'").upper().endswith(s), 'Channel_number configuration has been changed! (%s)' % r

        self._visainstrument.write('FORM REAL,32')
        raw = self._visainstrument.query_binary_values('TRAC? CH%uDATA' % s2chan,
                                                        datatype='f',
                                                        is_big_endian=False,
                                                        container=np.array,
                                                        header_fmt='ieee')

        return np.array([ r + 1j*i for r,i in raw.reshape((-1,2)) ])

    #[US]wa
    def q(self, string):
        return self._visainstrument.query(string)

    def ask(self, string):
        return self._visainstrument.ask(string)

    def w(self, string):
        return self._visainstrument.write(string)

    def channel_to_s_dict(self):
        channel_numbers, channel_names = self.ch_catalog()
        meas = []
        for chan in channel_numbers:
          sparam = self._visainstrument.ask('SENSE%u:FUNCTION?' % chan).strip().strip("'").upper().split(":")[2]
          meas.append(sparam)
        return dict(zip(channel_numbers, meas))

    def s_to_channel_dict(self):
        return dict([(v,k) for k,v in self.channel_to_s_dict().iteritems()])

    def s_to_ch_tr_dict(self, channel=None):
        channel_numbers, channel_names = self.ch_catalog()
        meas = []
        tr_chan_numbers = []
        trace_numbers = []
        trace_names = []
        if channel is not None:
        	assert channel in channel_numbers
        	channel_numbers = [channel]
        for chan in channel_numbers:
          tr_numbers, tr_names = self.trace_catalog(chan)
          for tr_n, tr in zip(tr_numbers,tr_names):
            self._visainstrument.write('CALC%d:PAR:SEL "%s"' % (chan,tr))
            sparam = self._visainstrument.ask('SENSE%u:FUNCTION?' % chan).strip().strip("'").upper().split(":")[2]
            meas.append(sparam)
            tr_chan_numbers.append(chan)
            trace_numbers.append(tr_n)
            trace_names.append(tr)
        # print zip(meas, zip(tr_chan_numbers, trace_numbers,trace_names))
        return dict(zip(meas, zip(tr_chan_numbers, trace_numbers,trace_names)))
        
    def start_single_sweep(self):
        '''
        Same as restart sweep in manual operation.
        '''
        logging.debug(__name__ + 'start a single sweep')

    def get_function(self,chan):
        r = self._visainstrument.ask('SENSe%u:FUNCtion?' % chan)        
        return r

    def get_frequency_data(self, channel_number=None):
        '''
        Get the current x-axis frequency values.

        If channel_number == None, use the first channel in the channel catalog.
        '''
        logging.debug(__name__ + 'Get the current x-axis values.')

        ch = self.ch_catalog()[0][0] if channel_number == None else channel_number
        assert int(ch) == ch, 'channel_number must be an integer'

        self._visainstrument.write('FORM REAL,32')
        return self._visainstrument.query_binary_values('TRAC:STIM? CH%dDATA' % ch,
                                                        datatype='f',
                                                        is_big_endian=False,
                                                        container=np.array,
                                                        header_fmt='ieee')

#       return eval('[' + self._visainstrument.ask('TRAC:STIM? CH1DATA') + ']')    

    def do_get_start_frequency(self,channel_number = 1):
        '''
        Start of sweep (Hz)
        '''
        logging.debug('Reading start frequency')
        return float(self._visainstrument.ask('SENS%s:FREQ:STAR?'%channel_number))/self._freq_unit

    def do_get_start_power(self):
        return float(self._visainstrument.ask('SOURce:POWer:STARt?'))

    def do_set_start_frequency(self, start, channel_number = 1): #in Hz
        logging.debug('Setting start freq to %s' % start)
        # ch_numbers, ch_names = self.ch_catalog()
        self._visainstrument.write('SENSE%s:FREQ:STAR %E' % (channel_number, start*self._freq_unit))
        self.get_center_frequency()
        self.get_span()

    def do_set_start_power(self, start):
        ch_numbers, ch_names = self.ch_catalog()
        for chan in ch_numbers:
          self._visainstrument.write('SOURce%d:POWer:STARt %E' % (chan, start))

    def do_get_stop_frequency(self, channel_number = 1):
        '''
        End of sweep (Hz)
        '''
        logging.debug('Reading stop frequency')
        return float(self._visainstrument.ask('SENS%s:FREQ:STOP?'%channel_number))/self._freq_unit

    def do_get_stop_power(self):
        return float(self._visainstrument.ask('SOURce:POWer:STOP?'))

    def do_set_stop_frequency(self, stop, channel_number = 1): #in Hz
        logging.debug('Setting stop freq to %s' % stop)
        # ch_numbers, ch_names = self.ch_catalog()
        self._visainstrument.write('SENSE%s:FREQ:STOP %E' % (channel_number, stop*self._freq_unit))
        self.get_center_frequency()
        self.get_span()

    def do_set_stop_power(self, stop):
        ch_numbers, ch_names = self.ch_catalog()
        for chan in ch_numbers:
          self._visainstrument.write('SOURce%d:POWer:STOP %E' % (chan, stop))

    def do_get_center_frequency(self,channel_number = 1):
        '''
        End of sweep (Hz)
        '''
        logging.debug('Reading the center frequency')
        return float(self._visainstrument.ask('SENS%s:FREQ:CENT?'%channel_number))/self._freq_unit

    def do_set_center_frequency(self, s, channel_number = 1): #in Hz
        logging.debug('Setting center freq to %s' % s)
        sweep_type = self.do_get_sweep_type()
        # ch_numbers, ch_names = self.ch_catalog()
        if sweep_type == 'CW' or sweep_type == 'POIN':
            self._visainstrument.write('SOUR%d:FREQ:FIX %s Hz' % (channel_number,s))
        else:
            self._visainstrument.write('SENSE%s:FREQ:CENT %s Hz' % (channel_number,s))
        self.get_start_frequency()
        self.get_stop_frequency()

    def do_get_span(self,channel_number = 1):
        '''
        End of sweep (Hz)
        '''
        logging.debug('Reading the span')
        return float(self._visainstrument.ask('SENS%s:FREQ:SPAN?'%channel_number))/self._freq_unit

    def do_set_span(self, s, channel_number = 1):
        logging.debug('Setting span to %s' % s)
        # ch_numbers, ch_names = self.ch_catalog()
        self._visainstrument.write('SENSE%s:FREQ:SPAN %s Hz' % (channel_number,s))
        self.get_start_frequency()
        self.get_stop_frequency()


    def do_get_numpoints(self, channel_number=1):
        '''
        Number of points in frequency
        '''
        logging.debug('Reading sweep points')
        return int(self._visainstrument.ask('SENS%s:SWE:POIN?'%channel_number))

    def do_set_numpoints(self,numpoints,channel_number = 1):
        logging.debug('Setting sweep points to %f' % numpoints)
        # ch_numbers, ch_names = self.ch_catalog()
        self._visainstrument.write('SENSE%s:SWE:POIN %f' % (channel_number, numpoints))
        return self._visainstrument.ask('SWE:POIN?')

    def do_get_if_bandwidth(self,channel_number = 1):
        logging.debug('Reading resolution bandwidth')
        r = self._visainstrument.ask('SENSE%s:BAND?'%channel_number)
        if r.strip().lower().startswith('max'): r = 1e6
        return float(r)/self._freq_unit

    def do_get_if_selectivity(self):
        logging.debug('Reading IF filter selectivity')
        r = self._visainstrument.ask('BAND:SEL?')
        return r.strip().upper()
    
    def ch_catalog(self):
        logging.debug('return numbers and names of all channels')
        catalog = self._visainstrument.ask('CONFIGURE:CHANNEL:CATALOG?').strip().strip("'").upper().split(",")
        ch_names = catalog[1::2]
        ch_numbers = map(int, catalog[0::2])
        return ch_numbers, ch_names

    def trace_catalog(self, channel = None):
        logging.debug('return numbers and names of all channels')
        if channel is None:
          tr_catalog = self._visainstrument.ask('CONFIGURE:TRACE:CATALOG?').strip().strip("'").upper().split(",")
        else:
          tr_catalog = self._visainstrument.ask('CONFIGURE:CHANNEL%d:TRACE:CATALOG?' % channel).strip().strip("'").upper().split(",")
        if len(tr_catalog) > 1:
          tr_names = tr_catalog[1::2]
          tr_numbers = map(int, tr_catalog[0::2])
          return tr_numbers, tr_names
        else:
          return [],[]
#map(funtion, sequence) calls funtion(item) for each of the sequence's items and returns a list of the return values.

    def window_catalog(self):
        logging.debug('return numbers and names of all channels')
        # return self._visainstrument.ask('DISPLAY:WINDOW%u:TRACE%u:CATALOG?' % (wnd,wndtr))
        wnd_catalog = self._visainstrument.ask('DISPLAY:CATALOG?').strip().strip("'").upper().split(",")
        if len(wnd_catalog) > 1:
          wnd_names = wnd_catalog[1::2]
          wnd_numbers = map(int, wnd_catalog[0::2])
          return wnd_numbers, wnd_names
        else:
          return [],[]

    def list_traces_in_chan(self,chan):
        logging.debug('return numbers and names of all channels')
        return self._visainstrument.ask('CONFIGURE%u:TRACE:CATALOG?' % chan)

    def list_traces_in_window(self,window_number = 1):
        logging.debug('return numbers and names of all traces in window')
        catalog = self._visainstrument.ask('DISP:WIND%s:TRAC:CAT?'%window_number).strip().strip("'").upper().split(",")
        if len(catalog) > 1:
          tr_names = catalog[1::2]
          tr_numbers = map(int, catalog[0::2])
          return tr_numbers, tr_names
        else:
          return [],[]


    def paramter_select_query(self,chan):
        logging.debug('return numbers and names of all channels')
        return self._visainstrument.ask(':CALCULATE%u:PARAMETER:SELECT?' % chan)


    def do_set_if_bandwidth(self,if_bandwidth, channel_number = 1):
        logging.debug('Setting Resolution BW to %s' % if_bandwidth)
        # ch_numbers, ch_names = self.ch_catalog()
        self._visainstrument.write('SENSE%s:BWIDTH:RESOLUTION %s' % (channel_number,if_bandwidth))
        self.get_sweeptime(channel_number = channel_number)

    def do_set_if_selectivity(self, if_sel):
        logging.debug('Setting IF filter selectivity to %s' % if_sel)
        ch_numbers, ch_names = self.ch_catalog()
        for chan in ch_numbers:
            self._visainstrument.write('SENSE%s:BWIDTH:SEL %s' % (chan, if_sel))
        self.get_sweeptime()

    def do_get_sweeptime(self, channel_number = 1):
        logging.debug('reading sweeptime')
        return float(self._visainstrument.ask('SENS%s:SWE:TIME?'%channel_number))

    #[US]
    def do_set_sweeptime(self, stime, channel_number =1):
        logging.debug('setting sweeptime to %s' % stime)
        self._visainstrument.write('SENS%s:SWE:TIME %.12f' %(channel_number,stime))

    def do_get_sweeptime_auto(self):
        logging.debug('reading sweeptime')
        r = self._visainstrument.ask('SWE:TIME:AUTO?').lower().strip()
        return r.startswith('1') or r.startswith('on')

    def do_set_sweeptime_auto(self, val): #in seconds
        logging.debug('Setting sweeptime auto to %s' % val)
        self._visainstrument.write('SWE:TIME:AUTO %s' % ('ON' if val else 'OFF'))

    def do_get_source_power(self, channel_number = 1):
        logging.debug('Reading Source power')
        return float(self._visainstrument.ask('SOUR%s:POW?'%channel_number))

    def do_get_average_mode(self):
        logging.debug(__name__ + ' : get averaging mode')
        m = self._visainstrument.ask('AVER:MODE?').strip().upper()
        if m.startswith('AUTO'): m = 'AUTO'
        elif m.startswith('FLAT'): m = 'FLAT'
        elif m.startswith('RED'): m = 'RED'
        elif m.startswith('MOV'): m = 'MOV'
        else: raise Exception('unknown averaging mode: %s' % m)
        return m

    def do_set_average_mode(self, m):
        logging.debug(__name__ + ' : set averaging mode to %s' % m)
        if m.startswith('AUTO'): m = 'AUTO'
        elif m.startswith('FLAT'): m = 'FLAT'
        elif m.startswith('RED'): m = 'RED'
        elif m.startswith('MOV'): m = 'MOV'
        ch_numbers, ch_names = self.ch_catalog()
        for chan in ch_numbers:
          self._visainstrument.write('SENSE%s:AVER:MODE %s' % (chan, m))

    def do_get_averages(self):
        '''
        Number of sweeps to average.
        '''
        logging.debug('Reading number of averages')
        return int(self._visainstrument.ask('AVER:COUN?'))

    def do_set_averages(self, averages):
        logging.debug('Setting number of averages to %s' % averages)
        ch_numbers, ch_names = self.ch_catalog()
        for chan in ch_numbers:
          self._visainstrument.write('SENSE%s:AVER:COUN %s' % (chan, averages))
          self._visainstrument.write('SENSE%s:AVER:STAT %s' % (chan, (1 if averages > 1 else 0)))

    def do_set_source_power(self, source_power, channel_number = 1):
        '''
        Set output power in dBm.
        '''
        logging.debug('Setting generator power to %s' % source_power)
        self._visainstrument.write('SOUR%s:POW %s dBm' % (channel_number, source_power))

    def set_sweeps(self, sweeps):
        logging.debug('Setting sweeps to %d' % sweeps)
        self._visainstrument.write('SWE:COUN %d' % sweeps)
    
    def reset_averages(self):
        logging.debug('clearing averages')
        self._visainstrument.write('AVER:CLE')
    
    def do_get_sweep_mode(self):
        logging.debug('Getting sweep mode.')
        return 'cont' if self._visainstrument.ask('INIT:CONT?').strip().lower() in ['1'] else 'single'

    def do_set_sweep_mode(self, val):
        logging.debug('Setting sweep mode: %s' % val)
        ch_numbers, ch_names = self.ch_catalog()
        for chan in ch_numbers:
          self._visainstrument.write('INIT%d:CONT %d' % (chan, int(val=='cont')))    

    def do_get_external_reference(self):
        logging.debug('Getting ext ref mode.')
        return self._visainstrument.ask('SENS:ROSC:SOUR?').lower().startswith('ext')

    def do_set_external_reference(self, val):
        logging.debug('Setting ext ref: %s' % val)
        if val:
          val_str = 'EXT'
        else:
          val_str = 'INT'
        self._visainstrument.write('ROSC %s' % (val_str))

    def do_get_external_reference_frequency(self):
        logging.debug('Getting ext ref freq.')
        if not self.get_external_reference(): return -1
        return self._visainstrument.ask('SENS:ROSC:EXT:FREQ?')

    def do_set_external_reference_frequency(self, val):
        logging.debug('Setting ext ref freq: %s' % val)
        self._visainstrument.write('ROSC:EXT:FREQ %d MHZ' % (val))

    def do_get_trigger_source(self, channel_number = 1):
        logging.debug('Getting trigger source.')
        r = self._visainstrument.ask('TRIGGER%s:SEQUENCE:SOURCE?'%channel_number).lower().strip()
        if r.startswith('lin') or r.startswith('rtc'):
          r = r[:4]
        else:
          r = r[:3]
        return r

    def do_set_trigger_source(self, val, channel_number = 1):
        logging.debug('Setting trigger source: %s' % val)
        self._visainstrument.write('TRIGGER%s:SEQUENCE:SOURCE %s' % (channel_number,val))

    def do_get_sweep_type(self):
        logging.debug('Getting sweep type')
        return self._visainstrument.ask('SWE:TYPE?').upper().strip()

    def do_set_sweep_type(self, sw_type):
        logging.debug('Setting sweep type: %s' % sw_type)
        sw_type_list=["lin","log","pow","cw","point","seg"]
        if sw_type in sw_type_list:
            self._visainstrument.write('SWE:TYPE %s' % sw_type)
            if sw_type is 'cw':
                freq=self.get_center_frequency()
                power=self.get_source_power()
                self._visainstrument.write('SOUR:POW %s' % power)
                self._visainstrument.write('SOUR:FREQ:CW %s' % freq)
        else:
            print 'Invalid Sweep Type\n'


    def LO_mode(self, frequency = 1e9):
        self.set_S21_only_channel_config()
        self._visainstrument.write('SENS1:SWE:TYPE CW')
        self._visainstrument.write('SENS1:SWE:TIME 10')
        self._visainstrument.write('SENS1:AVER:STAT OFF')
        self._visainstrument.write('FREQuency:FIXed {}'.format(frequency))
        self._visainstrument.write('SOUR1:POW 7')
        self._visainstrument.write('OUTP1 ON')
        self._visainstrument.write('TRIG1:SEQ:SOUR IMM')
        
      # The last command trigger the source set_S21_only_channel_config
        # To use sweep trigger, and znb.send_trigger()

    def LO_mode_frequency(self, frequency):
        self._visainstrument.write('FREQuency:FIXed {}'.format(frequency))
        self._visainstrument.write('TRIG1:SEQ:SOUR IMM')

    def LO_mode_power(self, power = 7):
        self._visainstrument.write('SOUR1:POW {}'.format(power))
        self._visainstrument.write('TRIG1:SEQ:SOUR IMM')

    # def find_peak_vibhor(self, center=6*1e9, span=5*1e6, numpoints = 201, IFBW = 1e3, power = -30, channel_number = 1):
    #     self.reset()
    #     self.set_external_reference(True)
    #     self.set_source_power(power, channel_number)
    #     self.set_center_frequency(center,channel_number)
    #     self.set_span(span, channel_number)
    #     self.set_numpoints(numpoints, channel_number)
    #     self.set_if_bandwidth(IFBW, channel_number)
    #     self.add_trace('S21', channel_number)
    #     # self.rf_on()
    #     self.send_trigger(channel_number=1, wait = True)
    #     self.autoscale_once()
    #     self.w('CALC:MARK ON')
    #     self.w('CALC:MARK:FUNC:EXEC MAX')
    #     _temp = self.ask('CALC:MARK:FUNC:RES?')
    #     _trace = self.get_data('S21')
    #     return {"trace": _trace, "freq": float(_temp.split(',')[0]), "value": float(_temp.split(',')[1])}

    def find_peak(self,channel_number):
        self.w('CALC%s:MARK ON'%channel_number)
        self.w('CALC%s:MARK:FUNC:EXEC MAX'%channel_number)
        _temp = self.ask('CALC%s:MARK:FUNC:RES?'%channel_number)
        return {"freq": float(_temp.split(',')[0]), "value": float(_temp.split(',')[1])}


    def set_frequency_fixed(self, frequency):
      self.w('FREQuency:FIXed {}'.format(frequency))