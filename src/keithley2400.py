# import instrument_instruction    ## for JSON repr of manual
import serial


class Keithley2400:
    def __init__(self, port, baudrate, bytesize=EIGHTBITS, parity=serial.PARITY_NONE, stopbits=STOPBITS_ONE, timeout=0):
        """
        Constructor for Keithley 2400 Sourcemeter
        
        ::param  port      Device name or None
        ::param  baudrate  Baud rate (configured on Keithley 2400)
        ::param  parity    Enable parity checking. Possible values: PARITY_NONE, PARITY_EVEN, PARITY_ODD PARITY_MARK, PARITY_SPACE
        ::param  bytesize  Number of data bits. Possible values: FIVEBITS, SIXBITS, SEVENBITS, EIGHTBITS
        ::param  stopbits  Number of stop bits. Possible values: STOPBITS_ONE, STOPBITS_ONE_POINT_FIVE, STOPBITS_TWO
        ::param  timeout   Set a read timeout value in seconds
        """
        self._port = port
        self._baudrate = baudrate
        self._bytesize = bytesize
        self._parity = parity
        self._stopbits = stopbits
        self._timeout = timeout
        
        self._ke2400 = serial.Serial(self.port, self.baudrate, self.bytesize, self.parity, self.stopbits, self.timeout)
        
        if not self.is_on():
            raise Exception("No response from Keithley... "\
                            "Check if it is ON "\
                            "or RESTART !!!")          
        
        @property
        def is_on(self):
            self._ke2400.write(b"*RST\r")
            self._ke2400.write(b":STAT:MEAS?\r")        ##CHANGE TO QUERY WHEN IMPLEMENTING VISA
            response_state = self._ke2400.readline()
            self._ke2400.close()
            return response_state

        @property
        def port(self):
            """
            Returns the com port of the Keithley 2400 Sourcemeter.
            """
            return self._port

        @property
        def baudrate(self):
            """
            Returns the baudrate used to communicate with the Keithley 2400 Sourcemeter.
            """
            return self._baudrate


        #Source functions

        @property
        def source_type(self):
            """
            ::action  Select source function.

            Gets or sets the source type of the Keithley 2400 SourceMeter.
            Expected strings for setting: 'voltage', 'current'
            """
            # response = self._ke2400.query("source:function:mode?").strip()
            response = self._ke2400.write(b":SOUR:FUNC:MODE?\r")
            return response

        @source_type.setter
        def source_type(self, value):
            value = value.lower()
            source_type = {"voltage": "VOLT", "current": "CURR"}
            if value in source_type:
                self._ke2400.write(b":SOUR:FUNC %s\r" % source_type[value])
            else:
                raise RuntimeError("Not a valid source type.")


        @property
        def source_mode(self):
            """
            ::action  Select source mode.

            Gets or sets the mode of the source.
            Expected strings for setting: 'fixed', 'sweep', 'list'
            """
            # TODO: test
            response = self._ke2400.write(b":SOUR:%s:MODE?\r" % (self.source_type))
            return response

        @source_mode.setter
        def source_mode(self, mode):
            mode = mode.upper()
            if mode in ("FIXED", "SWEEP" "LIST"):
                self._ke2400.write(b":SOUR:%s:MODE %s\r" % (self.source_type, mode))
            else:
                raise RuntimeError("Mode is not one of [fixed | sweep | list]")


        @property
        def source_range(self):
            """
            ::action  Select source range.

            Get or set the numeric value of the source chosen from Keithley2400.source_type.
            """
            # TODO: test
            return self._ke2400.write(b":SOUR:%s:RANG?\r" % (self.source_type))

        @source_value.setter
        def source_range(self, value):
            if isinstance(value, float) or isinstance(value, int):
                self._ke2400.write(b":SOUR:%s:RANG %s\r" % (self.source_type, value))
            else:
                raise RuntimeError("Source range must be of type float or int.")


        @property
        def source_level(self):
            """
            ::action  Select source level.

            Get or set the numeric value of the source chosen from Keithley2400.source_type.
            """
            # TODO: test
            return self._ke2400.write(b":SOUR:%s:LEV?\r" % (self.source_type))

        @source_range.setter
        def source_level(self, value):
            if isinstance(value, float) or isinstance(value, int):
                self._ke2400.write(b":SOUR:%s:LEV %f\r" % (self.source_type, value))
            else:
                raise RuntimeError("Source level must be of type float or int.")


###############
#PICK OFF FROM HERE ONWARDS
###############
        @property
        def measure_type(self):
            """
            The type of measurement the Keithley 2400 SourceMeter will make.
            Expected strings for setting: 'voltage', 'current', 'resistance'
            """
            measure_type = {"VOLT": "voltage", "CURR": "current", "RES": "resistance"}

            # measure_type_response = self._instrument.query("sense:function?").strip().replace('\"', '').split(',')[-1]
            measure_type = self._ke2400.write(b":SENS:FUNC?")
            return measure_type[measure_type_response]

        @measure_type.setter
        def measure_type(self, value):
            measure_type = {"voltage": "\'VOLT\'", "current": "\'CURR\'", "resistance": 'RES'}
            if value.lower() in measure_type:
                # self._instrument.write("sense:function:ON {}".format(measure_type[value.lower()]))
                self._ke2400.write(b":SENS:FUNC %s\r" % measure_type[value])
            else:
                raise RuntimeError('Expected a value from [\'voltage\'|\'current\'|\'resistance\'')



        # Resistance sensing

        @property
        def resistance_ohms_mode(self):
            """
            Gets or sets the resistance mode.
            Expected strings for setting: 'manual', 'auto'
            """
            modes = {"MAN": "manual", "AUTO": "auto"}
            # response = self._instrument.query('sense:resistance:mode?').strip()
            response = self._ke2400.write(b":SENS:FUNC:MODE?")
            return modes[response]

        @resistance_ohms_mode.setter
        def resistance_ohms_mode(self, value):
            modes = {"manual": "MAN", "auto": "AUTO"}
            if value.lower() in modes:
                # self._instrument.write("sense:resistance:mode {}".format(modes[value.lower()]))
                self._ke2400.write(b":SENS:RES:MODE %s" % modes[value.lower()])
            else:
                raise RuntimeError('Expected a value from [\'manual\'|\'auto\']')