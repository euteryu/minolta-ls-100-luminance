import keithley2400
import minolta


def initialise_keithley2400(voltage_input):
	keithley2400 = keithley.Keithley2400()

	keithley2400.source_type("voltage")
	keithley2400.source_mode("fixed")
	keithley2400.source_level(voltage_input)
	keithley2400.measure_type("current")
	keithley2400.voltage_compliance(5)
	keithley2400.nplc_cache(0.1)
	keithley2400.output("ON")
	keithley2400.read("voltage", "current")
	keithley2400.output("OFF")

def initialise_minolta():
	pass


if __name__=="__main__":

	voltage_input = 3

	# Instrument initialisation
	initialise_keithley2400(voltage_input)
	initialise_minolta()


	# Sweep across set voltage range.
	# NOTE: Don't use mode "sweep", as can't draw graph in real-time until finish!
	for i in range(-12,13):
	    voltage = i/10
	    print(keithley(voltage))