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
            response = self._ke2400.write(b":SOUR:FUNC:MODE?\r")
            return response

        @source_type.setter
        def source_type(self, source_type):
            source_type = source_type.lower()
            source_types = {"voltage": "VOLT", "current": "CURR"}
            if source_type in source_types:
                self._ke2400.write(b":SOUR:FUNC %s\r" % source_types[source_type])
            else:
                raise RuntimeError("Not a valid source type.")


        @property
        def source_mode(self):
            """
            ::action  Select source mode.
            Gets or sets the mode of the source.
            Expected strings for setting:  'fixed', 'sweep', 'list'
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



        # Sensor functions

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



        # # Resistance sensing

        # @property
        # def resistance_ohms_mode(self):
        #     """
        #     Gets or sets the resistance mode.
        #     Expected strings for setting: 'manual', 'auto'
        #     """
        #     modes = {"MAN": "manual", "AUTO": "auto"}
        #     # response = self._instrument.query('sense:resistance:mode?').strip()
        #     response = self._ke2400.write(b":SENS:FUNC:MODE?")
        #     return modes[response]

        # @resistance_ohms_mode.setter
        # def resistance_ohms_mode(self, value):
        #     modes = {"manual": "MAN", "auto": "AUTO"}
        #     if value.lower() in modes:
        #         # self._instrument.write("sense:resistance:mode {}".format(modes[value.lower()]))
        #         self._ke2400.write(b":SENS:RES:MODE %s" % modes[value.lower()])
        #     else:
        #         raise RuntimeError('Expected a value from [\'manual\'|\'auto\']')


    # Voltage sensing and compliance

        # @property
        # def expected_voltage_reading(self):
        #     """
        #     Gets or sets the expected voltage reading from the device under test.
        #     """
        #     response = self._instrument.query('sense:voltage:RANGE?').strip()
        #     return float(response)

        # @expected_voltage_reading.setter
        # def expected_voltage_reading(self, value):
        #     if isinstance(value, int) or isinstance(value, float):
        #         self._instrument.write('sense:voltage:range {}'.format(value))
        #     else:
        #         raise RuntimeError('Expected an int or float.')


        @property
        def voltage_compliance(self):
            """
            Gets or sets the voltage compliance.
            Expected range of floats: 200e-6 <= x <= 210
            """
            response = self._ke2400.write(b"SENS:VOLT:PROT:LEV?\r")
            return float(response)

        @voltage_compliance.setter
        def voltage_compliance(self, value):
            if 200e-6 <= value <= 210:
                self._ke2400.write(b"SENS:VOLT:PROT %f\r" % float(value))
            else:
                raise RuntimeError("Voltage compliance cannot be set. Value must be between 200 \u03BC' + 'V and 210 V.")


        def within_voltage_compliance(self):
            """
            Queries if the measured voltage is within the set compliance.
            :returns:  boolean
            """
            response = self._ke2400.write(b"SENS:VOLT:PROT:TRIP?")
            return not bool(int(response))


    # Current sensing and compilance

    # @property
    # def expected_current_reading(self):
    #     """Gets or sets the expected current reading from the device under test."""
    #     response = self._instrument.query('sense:current:range?').strip()
    #     return float(response)

    # @expected_current_reading.setter
    # def expected_current_reading(self, value):
    #     if isinstance(value, int) or isinstance(value, float):
    #         self._instrument.write('sense:current:range {}'.format(value))
    #     else:
    #         RuntimeError('Expected an int or float.')


    @property
    def current_compliance(self):
        """Sets or gets the current compliance level in Amperes."""
        response = self._ke2400.query(b"SENS:CURR:PROT:LEV?\r")
        return float(response)

    @current_compliance.setter
    def current_compliance(self, value):
        if 1e-9 <= value <= 1.05:
            self._ke2400.write(b"SENS:CURR:PROT %f\r" % float(value))
        else:
            raise RuntimeError("Current compliance cannot be set. Value must be between 1 nA and 1.05 A.")


    def within_current_compliance(self):
        """
        Queries if the measured current is within the set compliance.
        :returns:  boolean
        """
        response = self._ke2400.write(b"SENS:CURR:PROT:TRIP?")
        return not bool(int(response))


    def nplc_cache(self, value):
        """
        NPLC caching speeds up source memory sweeps by caching A/D reference and zero values.

        AC noise integrating time, in second(s).
        """
        if value > 0:
            self._ke2400.write(b"SENS:CURR:NPLC %f\r" % float(value))
        else:
            raise RuntimeError("NPLC cache time (in sec.) must be positive.")



        # Output configuration

        @property
        def output(self):
            """
            Gets or sets the source output of the Keithley 2400.
            Expected input: boolean
            :returns:  boolean
            """
            output = {"0": False, "1": True}
            response = self._ke2400.write(b"OUTP?\r")
            return output[response]

        @output.setter
        def output(self, mode):
            if mode == "ON" or mode == "on":
                self._ke2400.write(b"OUTP ON\r")
            elif mode == "OFF" or mode == "off":
                self._ke2400.write(b"OUTP OFF\r")
            else:
                RuntimeError("Output mode must either be ON or OFF.")


        @property
        def output_off_mode(self):
            """
            Gets or sets the output mode when the output is off.
            Expected input strings: 'himp', 'normal', 'zero', 'guard'
            :returns:  description of the output's off mode
            """
            modes = {"HIMP": "high impedance", "NORM": "normal", "ZERO": "zero", "GUAR": "guard"}
            response = self._ke2400.write(b"OUTP:SMOD?\r")
            return modes[response]

        @output_off_mode.setter
        def output_off_mode(self, value):
            value = value.lower()
            modes = {"high impedance": "HIMP", "himp": "HIMP", "normal": "NORM", "norm": "NORM", "zero": "ZERO", "guard": "GUARD"}
            if value in modes:
                self._ke2400.write(b"OUTP:SMOD %s\r" % modes[value])



        # Data acquisition

        def read(self, *measurements):
            """
            Reads data from the Keithley 2400. Equivalent to the command :INIT; :FETCH?
            Multiple string arguments may be used. For example::
                
                keithley.read('voltage', 'current')
                keithley.read('time')

            The first line returns a list in the form [voltage, current] and the second line
            returns a list in the form [time].

            NOTE: The returned lists contains the values in the order that you requested.
            :param   str *measurements:        Any number of arguments that are from: 'voltage', 'current', 'resistance', 'time'
            :return  list measure_list:        A list of the arithmetic means in the order of the given arguments
            :return  list measure_stdev_list:  A list of the standard deviations (if more than 1 measurement) in the order
                of the given arguments
            """
            self._ke2400.write(b":READ?\r")
            response = self._ke2400.read(56)  #Each response len is 14

            # TEST::
            # response = b"+0.00E+00,-5.66E-08,+9.22,+1.22"
            # test_response = [float(r) for r in response.decode('utf-8').strip().split(',')]
            # :return  [0.0, -5.66e-08, 9.22, 1.22]

            response = [float(r) for r in response.decode('utf-8').strip().split(',')]
            read_types = {'voltage': 0, 'current': 1, 'resistance': 2, 'time': 3}

            measure_list = []
            measure_stdev_list = []

            for measurement in measurements:
                samples = response[read_types[measurement]::5]
                measure_list.append(mean(samples))
                if len(samples) > 1:
                    measure_stdev_list.append(stdev(samples))

            return measure_list, measure_stdev_list
