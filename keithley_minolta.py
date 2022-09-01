# -*- coding: utf-8 -*-
"""
Created on Wed Aug 31 15:59:30 2022

@author: gryu
"""

import time
import serial

def keithley(voltage):
    volt = float(voltage)
    ser_keithley = serial.Serial(port="COM4", baudrate=19200, parity=serial.PARITY_NONE, bytesize=8, stopbits=1)
    
    ser_keithley.write(b'*RST\r')                       #Reset Keithley
    ser_keithley.write(b':SOUR:FUNC VOLT\r')            #Set Voltage as SOURCE
    ser_keithley.write(b':SOUR:VOLT:MODE FIXED\r')      #Fixed Voltage
    ser_keithley.write(b':SOUR:VOLT:LEV %f\r' %volt)   #Set Voltage from request
    ser_keithley.write(b':SENS:FUNC "CURRENT"\r')       #Set Current as SENSOR
    ser_keithley.write(b':FORM:ELEM VOLT, CURR\r')      #Retrieve Voltage and Current only 
    ser_keithley.write(b':SENS:VOLT:PROT 5\r')          #Cmpl voltage in Volt
    ser_keithley.write(b':SENS:CURR:PROT 0.5\r')        #Cmpl current in Ampere
    ser_keithley.write(b':SENS:CURR:NPLC 0.1\r')        #AC noise integrating time
    ser_keithley.write(b':OUTP ON\r')
    ser_keithley.write(b':READ?\r')
        
    raw_data = ser_keithley.read(28)

    ser_keithley.write(b':OUTP OFF\r')
        
    values = [float(i) for i in raw_data.decode('ascii').strip().split(',')]
    voltage = values[0]
    current = values[1]
    
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


for i in range(-12,13):
    voltage = i/10
    keithley(voltage)
    Minolta()
    # time.sleep(0.1)
    
    