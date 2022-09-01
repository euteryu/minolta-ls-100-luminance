# -*- coding: utf-8 -*-
"""
@author: gryu
"""

import serial
import numpy as np


class Keithley_2400():
    def __init__(self, port, baudrate, parity=serial.PARITY_NONE, bytesize=8, stopbits=1, timeout=1e-1, command_list=[]):
        self.port = port
        self.baudrate = baudrate
        self.parity = parity
        self.bytesize = bytesize
        self.stopbits = stopbits
        self.timeout = timeout
        self.command_list = command_list

        if not self._is_on():
            raise Exception('No response from Keithley... '\
                            'Check if it is ON '\
                            'or RESTART !!!')          
    
    def _is_on(self):
        with serial.Serial(self.port, self.baudrate, self.timeout) as ser_keithley:
            ser_keithley.write(b'*RST\r')
            ser_keithley.write(b':STAT:MEAS?\r')
            response_state = ser_keithley.readline()
            ser_keithley.close()
            return response_state
                 
    # =============================================================================
    # Scan given single fixed voltage.
    # 
    # TODO: RAISE EXCEPTION AND CLOSE SERIAL PORT IF ANY WRITE FAILURE OCCUR,
    #       TO PREVENT `SerialException`  ERROR.
    #
    # See:
    #     https://github.com/charkster/keithley_2308
    #     https://stackoverflow.com/questions/53882152/how-to-merge-f-string-with-b-string-in-one-line-usage-in-python
    # =============================================================================
    def single_scan(self, voltage):
        fixed_voltage = str(voltage)
        raw_data = ""

        with serial.Serial(self.port, self.baudrate, self.parity, self.bytesize, self.stopbits, self.fixed_voltage) as ser_keithley:
            for command in self.command_list:
                command = command.encode('utf-8')
                if command == ":SOUR:VOLT:LEV {0}\r":
                    command.format(fixed_voltage)
                if command == ":OUTP OFF\r":
                    raw_data = ser_keithley.read(28)  ## byte string output len is 28
                    # sleep(10)
                ser_keithley.write(command)
                
            values = [float(i) for i in raw_data.decode('utf-8').strip().split(',')]
            voltage = values[0]
            current = values[1]
            ser_keithley.close()
            return voltage, current


    # =============================================================================
    # Incremental scan from start to stop voltage every fixed step.
    # =============================================================================
    def incr_scan(self, start_v, stop_v, v_step, nplc, hys=False):
        raw_data = ""
        num_of_read = 0
        value_lists = []
        v_list, c_list = [], []

        if (stop_v - start_v) * v_step < 0:
            v_step = -v_step
            print("Swapping v_step polarity  +  <-->  -")
            trigger_count = int(1 + (stop_v - start_v) / v_step)
            num_of_read = 28 * trigger_count

        with serial.Serial(self._keith_com,self._baudrate) as ser_keithley:
            for command in self.command_list:
                command = command.encode('utf-8')

                if command == ":READ?\r":
                    raw_data = ser_keithley.read(num_of_read)
                    #Convert read values to float number and separate to voltage and current
                    value_lists = [[float(i) for i in 
                                    raw_data.decode('ascii').strip().split(',')]]
     
                    if hys:
                        ser_keithley.write(b':SOUR:SWE:DIR DOWN\r')
                        ser_keithley.write(b':READ?\r')
                        raw_data = ser_keithley.read(num_of_read)
                        value_lists += [[float(i) for i in 
                                       raw_data.decode('ascii').strip().split(',')]]

                ser_keithley.write(command)

        for value in value_lists:
            v_list.append(np.array(value[::2]))
            c_list.append(np.array(value[1::2]) * 1e3)
        return v_list, c_list




##  TODO: RAISE EXCEPTION AND CLOSE SERIAL PORT IF ANY WRITE FAILURE OCCUR,
##        TO PREVENT `SerialException`  ERROR.
def keithley(voltage):
    voltf = float(voltage)
    #voltfe = str(voltf).encode('utf-8')
    ser_keithley = serial.Serial(port="COM7", baudrate=38400, parity=serial.PARITY_NONE, bytesize=8, stopbits=1)
    
    ser_keithley.write(b"*RST\r")                           #Reset Keithley
    ser_keithley.write(b":SOUR:FUNC VOLT\r")                #Set Voltage as SOURCE
    ser_keithley.write(b":SOUR:VOLT:MODE FIXED\r")          #Fixed Voltage
    #ser_keithley.write(b":SOUR:VOLT:LEV %f\r" % voltf)    #Set Voltage from request
    #ser_keithley.write(b":SOUR:VOLT:LEV " + voltfe + "\r")
    #voltf_fixed = bytes(":SOUR:VOLT:LEV {0}\r".format(voltf))
    ser_keithley.write(bytes(":SOUR:VOLT:LEV {0}\r".format(voltf), encoding='utf8'))

    ser_keithley.write(b':SENS:FUNC "CURRENT"\r')           #Set Current as SENSOR
    ser_keithley.write(b':FORM:ELEM VOLT, CURR\r')          #Retrieve Voltage and Current only 
    ser_keithley.write(b':SENS:VOLT:PROT 5\r')              #Cmpl voltage in Volt
    ser_keithley.write(b':SENS:CURR:PROT 0.5\r')            #Cmpl current in Ampere
    ser_keithley.write(b':SENS:CURR:NPLC 0.1\r')            #AC noise integrating time
    ser_keithley.write(b':OUTP ON\r')
    ser_keithley.write(b':READ?\r')
        
    raw_data = ser_keithley.read(28)

    ser_keithley.write(b':OUTP OFF\r')
        
    values = [float(i) for i in raw_data.decode('utf-8').strip().split(',')]
    voltage = values[0]
    current = values[1]
    ser_keithley.close()
    return voltage, current

def Minolta():
    import serial

    ser_minolta = serial.Serial(port="COM5", baudrate=4800, parity=serial.PARITY_EVEN, bytesize=7, stopbits=2)

    # setting_var = b'\MDS02\r\n'
    message = b'\MES\r\n'
    # ser_minolta.write(setting_var)
    ser_minolta.write(b'\CLE\r\n')
    ser_minolta.write(message)
    raw_data = ser_minolta.read(11)  #11 bits received

    # print(luminance)
    luminance = raw_data.decode('ascii')
    print('Luminance = ', luminance[4:-1], 'cd/m2')
    ser_minolta.close()
    
    return luminance[4:-2]


# baudrate:
# 38400  --  ph-splsim lab
# 19200  --  ls-100 lab
for i in range(-12,13):
    voltage = i/10
    print(keithley(voltage))
    #print("voltf {0}".format(voltage))
    #Minolta()
    #time.sleep(0.1)
