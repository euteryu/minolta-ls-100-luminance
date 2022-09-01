# -*- coding: utf-8 -*-
"""
Created on Wed Aug 31 15:59:30 2022
@author: gryu
"""

import time
import serial


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
