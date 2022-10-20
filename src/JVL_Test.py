#--------------------------------------------------------------------------------
# This code is for measuring current and luminance of light emitting device while
# changing supply voltage to the device.
# Voltage supply and current measurement will be controlled by Keithley 2400 and
# luminance measurement will be done by Minolta LS-100.
# 
# date: 20th October 2022
# version: v1.
#----------------------------------------------------------------------------------
__author__ = 'Gihan Ryu'


import wx
import matplotlib
matplotlib.use('Agg')             #Some computer use 'Agg' rather than 'WXAgg'
matplotlib.interactive(False)
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
from matplotlib.figure import Figure
import serial
import time
import matplotlib.pyplot as plt
import datetime
import tkinter as tk , tkinter.filedialog
import csv
import os, sys
from itertools import zip_longest
import numpy as np


#start_time = time.time()        #Reference time stamp

class MyFrame(wx.Frame):

    def __init__(self, *args, **kw):
        super(MyFrame, self).__init__(*args, **kw)

        self.SetTitle('JVL Measurement')
        self.InitUI()
        
    def InitUI(self):
        self.start_time = time.time()
        #Define the main panel as pnl
        pnl = wx.Panel(self)
        #Devide the main panel vertically to upperPanel and lowerPanel
        upperPanel = wx.Panel(pnl)
        lowerPanel = wx.Panel(pnl)
        
        font = wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT)
        # font = wx.Font(12, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
#        font.SetPointSize(12)
#        font.SetUnderlined(True)
        
#----------------------------------------------------------------------------------
        # parameter = wx.StaticText(lowerPanel, label='Parameters')
        # parameter.SetFont(font)
        # parameter.SetForegroundColour((255, 255, 0))
        # parameter.SetBackgroundColour((100, 100, 100))
        
        ParamBox = wx.GridBagSizer(3, 9)
        
#------------------------------------------------------------------------------------  
        #Define parameters
        textfont = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        
        st1 = wx.StaticText(lowerPanel, label='Start_Voltage')
        st1.SetFont(textfont)
        self.tc1 = wx.TextCtrl(lowerPanel, 1,value="0", size=(55,20))
        ParamBox.Add(st1, pos=(0,0), flag=wx.LEFT, border=20)
        ParamBox.Add(self.tc1, pos=(0,1), flag=wx.LEFT, border=2)
        ParamBox.Add(wx.StaticText(lowerPanel, label='V'), pos=(0,2), flag=wx.LEFT, border=1)
        
        st2 = wx.StaticText(lowerPanel, label='Stop_Voltage')
        st2.SetFont(textfont)
        self.tc2 = wx.TextCtrl(lowerPanel, -1, value='2', size=(55,20))
        ParamBox.Add(st2, pos=(1,0), flag=wx.LEFT, border=20)
        ParamBox.Add(self.tc2, pos=(1,1), flag=wx.LEFT, border=2)
        ParamBox.Add(wx.StaticText(lowerPanel, label='V'), pos=(1,2), flag=wx.LEFT, border=1)
        
        st3 = wx.StaticText(lowerPanel, label='Step')
        st3.SetFont(textfont)
        self.tc3 = wx.TextCtrl(lowerPanel, -1, value='0.01', size=(55,20))      
        ParamBox.Add(st3, pos=(2,0), flag=wx.LEFT, border=20)
        ParamBox.Add(self.tc3, pos=(2,1), flag=wx.LEFT, border=2)
        ParamBox.Add(wx.StaticText(lowerPanel, label='V'), pos=(2,2), flag=wx.LEFT, border=1)
        
        st4 = wx.StaticText(lowerPanel, label='Delay')
        st4.SetFont(textfont)
        self.tc4 = wx.TextCtrl(lowerPanel, -1, value='5', size=(55,20))      
        ParamBox.Add(st4, pos=(0,4), flag=wx.LEFT, border=20)
        ParamBox.Add(self.tc4, pos=(0,5), flag=wx.LEFT, border=2)
        ParamBox.Add(wx.StaticText(lowerPanel, label='ms'), pos=(0,6), flag=wx.LEFT, border=1)
        
        st5 = wx.StaticText(lowerPanel, label='Area')
        st5.SetFont(textfont)
        self.tc5 = wx.TextCtrl(lowerPanel, -1, value='0.045', size=(55,20))      
        ParamBox.Add(st5, pos=(1,4), flag=wx.LEFT, border=20)
        ParamBox.Add(self.tc5, pos=(1,5), flag=wx.LEFT, border=2)
        ParamBox.Add(wx.StaticText(lowerPanel, label='cm2'), pos=(1,6), flag=wx.LEFT, border=1)
        
        # st6 = wx.StaticText(lowerPanel, label='xxxx')
        # st6.SetFont(textfont)
        # self.tc6 = wx.TextCtrl(lowerPanel, -1, value='100', size=(55,20))
        # ParamBox.Add(st6, pos=(2,4), flag=wx.LEFT, border=15)
        # ParamBox.Add(self.tc6, pos=(2,5), flag=wx.LEFT, border=2)
        # ParamBox.Add(wx.StaticText(lowerPanel, label='yyyy'), pos=(2,6), flag=wx.LEFT, border=1)

#----------------------------------------------------------------------------------------------------
        #Define function binded Buttons 
        button_font = wx.Font(14, wx.ROMAN, wx.NORMAL, wx.BOLD)               
        # single_measure_Btn = wx.Button(lowerPanel, label='Jsc CHECK', size=(120, 70))
        # single_measure_Btn.SetFont(button_font)
        # single_measure_Btn.SetBackgroundColour(wx.YELLOW)  # set background color
        # # single_measure_Btn.SetForegroundColour((176, 0, 255)) # set text color
        # multi_measure_Btn = wx.Button(lowerPanel, label='J-V MEASURE', size=(120, 70))
        # multi_measure_Btn.SetFont(button_font)
        # multi_measure_Btn.SetBackgroundColour((0, 100, 200))  # set background color
        # stability_Btn = wx.Button(lowerPanel, label='STABILITY', size=(120, 70))
        # stability_Btn.SetFont(button_font)
        # stability_Btn.SetBackgroundColour((176, 0, 200))  # set background color
        finish_Btn = wx.Button(lowerPanel, label='FINISH', size=(80, 70))
        finish_Btn.SetFont(button_font)
        finish_Btn.SetBackgroundColour(wx.RED)  # set background color
        start_Btn = wx.Button(lowerPanel, label='START', size=(80, 70))
        start_Btn.SetFont(button_font)
        start_Btn.SetBackgroundColour(wx.GREEN)  # set background color
        reset_Btn = wx.Button(lowerPanel, label='STOP', size=(80, 70))
        reset_Btn.SetFont(button_font)
        reset_Btn.SetBackgroundColour(wx.YELLOW)  # set background color
        
        # self.Bind(wx.EVT_BUTTON, self.OnSingleMeasurement, single_measure_Btn)
        # self.Bind(wx.EVT_BUTTON, self.OnMultiMeasurement, multi_measure_Btn)
        self.Bind(wx.EVT_BUTTON, self.OnStart, start_Btn)
        self.Bind(wx.EVT_BUTTON, self.OnClose, finish_Btn)
        self.Bind(wx.EVT_BUTTON, self.OnReset, reset_Btn)

        # self.Bind(wx.EVT_BUTTON, self.OnStability, stability_Btn)          

#---------------------------------------------------------------------------------
        #Define graph region
        vbox2 = wx.BoxSizer(wx.VERTICAL)
        # graph = wx.StaticText(upperPanel, label='Graphs')
        # graph.SetFont(wx.Font(16, wx.ROMAN, wx.NORMAL, wx.BOLD))
        
        #Define Graph Plotting
        self.matplotlibhrapg = MatplotPanel(upperPanel)

        # vbox2.Add(graph, 0, wx.LEFT|wx.TOP, border=10)
        # vbox2.Add(hbox2)
        vbox2.Add(self.matplotlibhrapg, flag=wx.EXPAND, proportion=1)
        
        upperPanel.SetSizer(vbox2)
        
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(ParamBox, wx.LEFT, border=20)
        hbox.Add(finish_Btn, wx.LEFT,border=20)
        hbox.Add(start_Btn, wx.LEFT,border=20)
        hbox.Add(reset_Btn, wx.LEFT,border=20)
        
        lowerPanel.SetSizer(hbox)
        
#---------------------------------------------------------------------------------
        #Construct all components in the upperPanel screen        
        vBox = wx.BoxSizer(wx.VERTICAL)
        vBox.Add(upperPanel, 1, wx.ALL|wx.EXPAND)
        vBox.Add(lowerPanel, 0, wx.ALL|wx.EXPAND)
                
        pnl.SetSizer(vBox)

        self.Centre()
        self.Maximize()
        

#---------------------------------------------------------------------------------------        
    def OnReset(self, event):
        
        self.keithley_off()
        # self.timer.Stop()
        ex = MyFrame(None)
        ex.Show()
        self.Destroy()

#---------------------------------------------------------------------------------------
    def OnStart(self, event):
        
        self.saveData()
        self.keithley_setup()
        voltage_list = self.list_gen()
        print(voltage_list)
        area = float(self.tc5.GetValue())                    #dimension is cm2
        
        voltages = []
        currents = []
        luminances = []
        
        #Create a file for saving data
        filename = self.fname + ".csv"
        with open(filename, 'a', newline='') as ff:
            wr = csv.writer(ff)
            wr.writerow(["Voltage (V)", "Current (mA)", "Current Density (mA/cm2)", "Luminance (cd/m2)"])
            
        for voltage in voltage_list:
            voltage_current = self.keithley(voltage)
            voltage = voltage_current[0]
            current = voltage_current[1]
            time.sleep(0.1)
            luminance = self.Minolta()
            current_density = current / area
            # time.sleep(0.1)
            
            voltages.append(voltage)
            currents.append(current)
            luminances.append(luminance)
            
            #Drawing a graph in realtime
            self.matplotlibhrapg.drawGraph(voltage, current, luminance, area)
            # self.matplotlibhrapg.drawGraphs(voltages, currents, luminances, area)
            #Save data
            with open(filename, 'a', newline='') as ff:
                wr = csv.writer(ff)
                wr.writerow([voltage, current, current_density, luminance])
                
        self.keithley_off()
        #Draw all graphs together after finishing measurement
        self.matplotlibhrapg.cleargraph()
        self.matplotlibhrapg.drawGraphs(voltages, currents, luminances, area)
                
        
#--------------------------------------------------------------------------------------       
    def OnClose(self, event):

        self.Destroy()

#-------------------------------------------------------------------------------------
    def list_gen(self):
        self.voltage_list = []
        start_voltage = float(self.tc1.GetValue())
        stop_voltage = float(self.tc2.GetValue())
        voltage_step = float(self.tc3.GetValue())
        num_of_count = int(1 + (abs(stop_voltage - start_voltage) // voltage_step))
    
        for i in range(num_of_count + 1):
            voltage = round((start_voltage + i * voltage_step), 3)
            if voltage <= stop_voltage:
                self.voltage_list.append(voltage)
    
        return self.voltage_list

#-----------------------------------------------------------------------------------
    def keithley(self, voltage):
        volt = float(voltage)
        ser_keithley = serial.Serial(port="COM4", baudrate=19200, parity=serial.PARITY_NONE, bytesize=8, stopbits=1)
    
        # ser_keithley.write(b'*RST\r')                       #Reset Keithley
        # ser_keithley.write(b':SOUR:FUNC VOLT\r')            #Set Voltage as SOURCE
        # ser_keithley.write(b':SOUR:VOLT:MODE FIXED\r')      #Fixed Voltage
        ser_keithley.write(b':SOUR:VOLT:LEV %f\r' %volt)   #Set Voltage from request
        # ser_keithley.write(b':SENS:FUNC "CURRENT"\r')       #Set Current as SENSOR
        # ser_keithley.write(b':FORM:ELEM VOLT, CURR\r')      #Retrieve Voltage and Current only 
        # ser_keithley.write(b':SENS:VOLT:PROT 5\r')          #Cmpl voltage in Volt
        # ser_keithley.write(b':SENS:CURR:PROT 0.5\r')        #Cmpl current in Ampere
        # ser_keithley.write(b':SENS:CURR:NPLC 0.1\r')        #AC noise integrating time
        ser_keithley.write(b':OUTP ON\r')
        ser_keithley.write(b':READ?\r')
        
        raw_data = ser_keithley.read(28)

        # ser_keithley.write(b':OUTP OFF\r')
        
        values = [float(i) for i in raw_data.decode('ascii').strip().split(',')]
        voltage = values[0]
        current = values[1]
    
        return voltage, current

#----------------------------------------------------------------------------------
    def keithley_setup(self):
        ser_keithley = serial.Serial(port="COM4", baudrate=19200, parity=serial.PARITY_NONE, bytesize=8, stopbits=1)
    
        ser_keithley.write(b'*RST\r')                       #Reset Keithley
        ser_keithley.write(b':SOUR:FUNC VOLT\r')            #Set Voltage as SOURCE
        ser_keithley.write(b':SOUR:VOLT:MODE FIXED\r')      #Fixed Voltage
        # ser_keithley.write(b':SOUR:VOLT:LEV %f\r' %volt)   #Set Voltage from request
        ser_keithley.write(b':SENS:FUNC "CURRENT"\r')       #Set Current as SENSOR
        ser_keithley.write(b':FORM:ELEM VOLT, CURR\r')      #Retrieve Voltage and Current only 
        ser_keithley.write(b':SENS:VOLT:PROT 5\r')          #Cmpl voltage in Volt
        ser_keithley.write(b':SENS:CURR:PROT 0.5\r')        #Cmpl current in Ampere
        ser_keithley.write(b':SENS:CURR:NPLC 0.1\r')        #AC noise integrating time
        # ser_keithley.write(b':OUTP ON\r')

#----------------------------------------------------------------------------------
    def keithley_off(self):
        ser_keithley = serial.Serial(port="COM4", baudrate=19200, parity=serial.PARITY_NONE, bytesize=8, stopbits=1)
        ser_keithley.write(b':OUTP OFF\r')
        
#----------------------------------------------------------------------------------
    def Minolta(self):

        ser_minolta = serial.Serial(port="COM5", baudrate=4800, parity=serial.PARITY_EVEN, bytesize=7, stopbits=2)

        message = b'\MES\r\n'
        ser_minolta.write(b'\CLE\r\n')
        ser_minolta.write(message)
        raw_data = ser_minolta.read(11)  #11 bits received
           
        luminance = raw_data.decode('ascii')
        # print('Luminance = ', luminance[4:-1], 'cd/m2')
        # ser_minolta.close()
        if luminance[4:-1] == 'E0':
            return 0
        else:
            return luminance[4:-2]   
    
#---------------------------------------------------------------------------------------------
    def saveData(self):
        root = tk.Tk()	#get root location for the later GUI default start point
        # saveloc = tkinter.filedialog.askdirectory(parent=root, initialdir='C:/Users/test/Desktop/User folders', title='Please select a directory to save your data')
        # os.chdir(saveloc) 	#change to the location where works should be done
        dlg = tkinter.filedialog.asksaveasfilename(confirmoverwrite=False)
        # self.fname = dlg
        os.chdir(os.path.split(dlg)[0])
        self.fname = os.path.split(dlg)[1]
        root.withdraw()	#closing the UI interface remanent

                

#--------Graph Window-----------------------------------------------------------------------------
class MatplotPanel(wx.Window):
    
    def __init__(self, parent):
        wx.Window.__init__(self, parent)
        self.lines = []
        self.figure = Figure()
        self.canvas = FigureCanvasWxAgg(self, 1, self.figure)
#        self.drawData()
        self.Bind(wx.EVT_SIZE, self.sizeHandler)

    def sizeHandler(self, parent):
        self.canvas.SetSize(self.GetSize())
        
    def repaint(self):
        self.canvas.draw()

    def GetLineFormats(self):
        colors = ('r', 'g', 'b', 'c', 'm', 'y')
#        linestyles = ['-', '--', ':']
        lineFormats = []
        for col in colors:
            lineFormats.append(col)
        return lineFormats
    
    def drawGraph(self, voltage, current, luminance, area):
        area = float(area)
        current_density = float(current)*1000 / area   #current in mA
        efficiency = float(luminance) * 12.56  #it is not clear
        Yield = float(luminance) / (current_density / 1000)
        
        self.plot_VL = self.figure.add_subplot(1, 1, 1)
       
        # Voltage-Luminance Plot       
        self.plot_VL.plot(voltage, luminance, 'o', markersize=3)
        self.plot_VL.set_title('V-L', size=16, fontweight='bold')
        self.plot_VL.set_xlabel('Voltage(V)')
        self.plot_VL.set_ylabel('Luminance (cd/cm2)')
        
        # self.figure.tight_layout()
        self.repaint()
    
    def cleargraph(self):
        self.plot_VL.clear()
    
    def drawGraphs(self, voltage_list, current_list, luminance_list, area):
        area = float(area)
        voltage = [float(x) for x in np.asarray(voltage_list)]
        current = [float(x) for x in np.asarray(current_list)]
        luminance = [float(x) for x in np.asarray(luminance_list)]
        # print(current)
        current_density = np.asarray(current) * 1000 / area   #current in mA
        efficiency = np.asarray(luminance) * 12.56  #it is not clear
        Yield = np.asarray(luminance) / (current_density / 1000)
        
        # print(voltage, current, luminance)
        # self.plot_VL.clear()
        # self.plot_VL.set(xlabel=None, ylabel=None)
        # self.plot_VL.tick_params(bottom=False)
        # self.canvas.draw()
        
        self.plot_VJ = self.figure.add_subplot(2, 3, 1)
        self.plot_JL = self.figure.add_subplot(2, 3, 2)
        self.plot_VL = self.figure.add_subplot(2, 3, 3)
        self.plot_VE = self.figure.add_subplot(2, 3, 4)
        self.plot_VY = self.figure.add_subplot(2, 3, 5)
        self.plot_JE = self.figure.add_subplot(2, 3, 6)
       
        # Voltage-Current Density Plot
        self.plot_VJ.plot(voltage, current_density, 'o', markersize=3)
        self.plot_VJ.set_title('V-J', size=16, fontweight='bold')
        self.plot_VJ.set_xlabel('Voltage (V)')
        self.plot_VJ.set_ylabel('Current Density (mA/cm2)')
        # Current Density-Luminance Plot       
        self.plot_JL.plot(current_density, luminance, 'o', markersize=3)
        self.plot_JL.set_title('J-L', size=16, fontweight='bold')
        self.plot_JL.set_xlabel('Current Density (mA/cm2)')
        self.plot_JL.set_ylabel('Luminance (cd/m2)')
        # Voltage-Luminance Plot       
        self.plot_VL.plot(voltage, luminance, 'o', markersize=3)
        self.plot_VL.set_title('V-L', size=16, fontweight='bold')
        self.plot_VL.set_xlabel('Voltage(V)')
        self.plot_VL.set_ylabel('Luminance (cd/cm2)')
        # Voltage-Efficiency Plot       
        self.plot_VE.plot(voltage, efficiency, 'o', markersize=3)
        self.plot_VE.set_title('V-Eff', size=16, fontweight='bold')
        self.plot_VE.set_xlabel('Voltage(V)')
        self.plot_VE.set_ylabel('Efficiency (lm/W)')
        # Voltage-Yield Plot       
        self.plot_VY.plot(voltage, Yield, 'o', markersize=3)
        self.plot_VY.set_title('V-Yield', size=16, fontweight='bold')
        self.plot_VY.set_xlabel('Voltage(V)')
        self.plot_VY.set_ylabel('Yield (cd/A)')
        # Current Density-Efficiency Plot       
        self.plot_JE.plot(current_density, efficiency, 'o', markersize=3)
        self.plot_JE.set_title('J-Eff', size=16, fontweight='bold')
        self.plot_JE.set_xlabel('Current Density (mA/cm2)')
        self.plot_JE.set_ylabel('Efficiency (lm/W)')
        
        # self.figure.tight_layout()
        self.repaint()


def main():

    app = wx.App()
    ex = MyFrame(None)
    ex.Show()
    app.MainLoop()


if __name__ == '__main__':
    try:        
        main()
        
    except KeyboardInterrupt:
        MyFrame.Destroy()
