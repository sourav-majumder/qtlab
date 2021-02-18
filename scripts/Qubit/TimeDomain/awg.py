class AwgProgram(object):

  sigma = 16
  periods = 3

  def __init__(self):
    self.final_string = '''
      while (true) {
      playWave(p1, p2);
      waitWave();
      wait(12); // Unit CLK CYCLES; Added to have gap between control and measure pulses
      setTrigger(0b0010);
      wait(measure_pulse_length*us/cycle);
      setTrigger(0b0000);
      wait(200*us/cycle);
    }
    '''
  def pi(self, phase_offset=0, coherent=False):
    return '''
    // Pi Pulse
    wave w1 = gauss(64, 1, 32, 16);
    sine(64, 1, %f, 64*3/64);
    '''%(2*pi*self.control_points*AwgProgram.periods/(4*AwgProgram.sigma) + phase_offset)

  def pi(self, phase_offset=0, coherent=False):
    return '''
    // Pi Pulse
    wave w1 = gauss(64, 1, 32, 16);
    sine(64, 1, %f, 64*3/64);
    '''%(2*pi*self.control_points*AwgProgram.periods/(4*AwgProgram.sigma) + phase_offset)


def two_photon_swap(length, flux):
    awg_program_string = """
    const control_power = 1;
    const length = %d;
    const flux = %f;
    const flux_power1 = (223.0-14.0)/750.0;
    const flux_power2 = (flux-14.0)/750.0;
    const cycle = 4.4e-9;
    const us = 1e-6;
    const ns = 1e-9;
    const len  = 100;

    wave w_rise = gauss(64,control_power, 64, 16);
    wave w_fall = gauss(64,control_power, 0, 16);
    wave w_flat = rect(len, control_power);
    wave w_join = join(w_rise ,w_flat, w_fall);

    wave w_rise1 = gauss(8, flux_power1, 8, 1);
    wave w_fall1 = gauss(8, flux_power1, 0, 1);
    wave w_flat1 = rect(5, flux_power1);
    wave w_pulse1 = join(w_rise1, w_flat1, w_fall1);

    wave w_rise2 = gauss(8, flux_power2, 8, 1);
    wave w_fall2 = gauss(8, flux_power2, 0, 1);
    wave w_flat2 = rect(length, flux_power2);
    wave w_pulse2 = join(w_rise2, w_flat2, w_fall2);

    const measure_pulse_length = 10 ; // us
    while (true) {
      playWave(1,w_join);
      waitWave();
      playWave(2,w_pulse1);
      waitWave();
      playWave(1,w_join);
      waitWave();
      playWave(2,w_pulse2);
      waitWave();
      wait(12);
      setTrigger(0b0010);
      wait(measure_pulse_length*us/cycle);
      setTrigger(0b0000);
      wait(200*us/cycle);
    }
    """%(length,flux)
    return awg_program_string


def ramsey(phase, gap):
    awg_program_string = """
    const phase = %f;
    //const pulse_length = 0;
    const gap = %f;
    const pi = 3.141592653589793;
    const cycle = 4.4e-9;
    const us = 1e-6;
    const measure_pulse_length = 15 ; // us
    //gauss(samples, amplitude, position, width)
    wave w1 = gauss(64, 1, 32, 16);
    wave w_pulse = join(w1, zeros(gap), w1);
    //wave w_rise = cut(w1, 0, 31);
    //wave w_fall = cut(w1, 32, 63);
    //wave w_flat = rect(pulse_length, 1);
    //sine(samples, amplitude, phaseOffset, nrOfPeriods)
    wave w2 = join(sine(64, 1, phase, 64*3/64), zeros(gap), sine(64, 1, (2*pi*gap*3/64 + 2*pi*gap/200 + phase), 64*3/64));
    wave w3 = join(sine(64, 1, 0, 64*3/64), zeros(gap), sine(64, 1, (2*pi*gap*3/64 + 2*pi*gap/200 + 0), 64*3/64));
    //wave w_pulse = join(w_rise, w_flat, w_fall);
    wave p1 = multiply(w_pulse, w2);
    wave p2 = multiply(w_pulse, w3);
    while (true) {
      playWave(p1, p2);
      waitWave();
      wait(12); // Unit CLK CYCLES; Added to have gap between control and measure pulses
      setTrigger(0b0010);
      wait(measure_pulse_length*us/cycle);
      setTrigger(0b0000);
      wait(200*us/cycle);
    }
    """%(phase, gap)
    return awg_program_string


def t2_echo(phase, gap):
    awg_program_string = """
    const phase = %f;
    //const pulse_length = 0;
    const gap = %f;
    const pi = 3.141592653589793;
    const cycle = 4.4e-9;
    const us = 1e-6;
    const measure_pulse_length = 15 ; // us
    //gauss(samples, amplitude, position, width)
    wave wpiby2 = gauss(64, 28/58, 32, 16);
    wave wpi = gauss(64, 1, 32, 16);
    wave w_pulse = join(wpiby2, zeros(gap), wpi, zeros(gap), wpiby2);
    //sine(samples, amplitude, phaseOffset, nrOfPeriods)
    //wave w2 = sine(64, 1, phase, 3);
    //wave w3 = sine(64, 1, 0, 3);
    wave w2 = join(sine(64, 1, phase, 64*3/64),
                    zeros(gap), 
                    sine(64, 1, (2*pi*gap*3/64 + phase), 64*3/64),
                    zeros(gap),
                    sine(64, 1, (2*pi*(2*gap+64)*3/64 + 2*pi*(2*gap+64)/200 + phase), 64*3/64));
    wave w3 = join(sine(64, 1, 0, 64*3/64),
                    zeros(gap), 
                    sine(64, 1, (2*pi*gap*3/64 + 0), 64*3/64),
                    zeros(gap),
                    sine(64, 1, (2*pi*(2*gap+64)*3/64 + 2*pi*(2*gap+64)/200 + 0), 64*3/64));
    //wave w_pulse = join(w_rise, w_flat, w_fall);
    wave p1 = multiply(w_pulse, w2);
    wave p2 = multiply(w_pulse, w3);
    while (true) {
      playWave(p1, p2);
      waitWave();
      wait(12); // Unit CLK CYCLES; Added to have gap between control and measure pulses
      setTrigger(0b0010);
      wait(measure_pulse_length*us/cycle);
      setTrigger(0b0000);
      wait(200*us/cycle);
    }
    """%(phase, gap)
    return awg_program_string

def rabi(phase, pulse_length):
    awg_program_string = """
    const phase = %f;
    const pulse_length = %f;
    const delay = 0;
    const cycle = 4.4e-9;
    const us = 1e-6;
    const measure_pulse_length = 15 ; // us
    //gauss(samples, amplitude, position, width)
    wave w1 = gauss(128, 1, 64, 32);
    wave w_rise = cut(w1, 0, 63);
    wave w_fall = cut(w1, 64, 127);
    wave w_flat = rect(pulse_length, 1);
    //sine(samples, amplitude, phaseOffset, nrOfPeriods)
    wave w2 = sine(pulse_length+128, 1, phase, (pulse_length+128)/128*6);
    wave w3 = sine(pulse_length+128, 1, 0, (pulse_length+128)/128*6);
    wave w_pulse = join(w_rise, w_flat, w_fall);
    wave p1 = multiply(w_pulse, w2);
    wave p2 = multiply(w_pulse, w3);
    while (true) {
      playWave(p1, p2);
      waitWave();
      wait(12); // Unit CLK CYCLES; Added to have gap between control and measure pulses
      wait(delay);
      setTrigger(0b0010);
      wait(measure_pulse_length*us/cycle);
      setTrigger(0b0000);
      wait(200*us/cycle);
    }
    """%(phase,pulse_length)
    return awg_program_string

