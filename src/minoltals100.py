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


class Minolta():
    def __init__(self, port, baudrate, parity, bytesize, stopbits, timeout=1e-1, command_list=[]):
        self.port = port
        self.baudrate = baudrate
        self.parity = parity
        self.bytesize = bytesize
        self.stopbits = stopbits
        self.timeout = timeout
        self.command_list = command_list

    #     if not self._is_on():
    #         raise Exception('No response from LS-100... '\
    #                         'Check if it is ON '\
    #                         'or RESTART equipment!!!')          

    # # =============================================================================
    # # TODO:
    # #        Below ON check is for Keithley2400;  see Minolta manual
    # # =============================================================================    
    # def _is_on(self):
    #     with serial.Serial(self.port, self.baudrate, self.timeout) as ser_minolta:
    #         ser_minolta.write(b'*RST\r')
    #         ser_minolta.write(b':STAT:MEAS?\r')
    #         response_state = ser_minolta.readline()
    #         ser_minolta.close()
    #         return response_state

    def measure():

    def measure(self):
        raw_data = ""

        with serial.Serial(self.port, self.baudrate, self.parity, self.bytesize, self.stopbits) as ser_minolta:
            for command in self.command_list:
                command = command.encode('utf-8')
                ser_minolta.write(command)
                if command == "\MES\r\n":
                    raw_data = ser_minolta.read(11)  ## byte string output len is 28
                
            ser_minolta.close()

        # Luminance read output format: " ... ... "
        luminance = raw_data.decode('ascii')

        return luminance[4:-2]
