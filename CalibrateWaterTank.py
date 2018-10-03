#
# This is used to calibrate your Water Tank and Ultrasonic Sensor for SPP2
#
# SwitchDoc Labs 2018

VERSION = "001"

try:
    import conflocal as config
except ImportError:
    import config

import ultrasonicRanger

print "############################"
print "Ultrasonic Tank Calibration"
print "SwitchDoc Labs"
print "Software Version:", VERSION
print "############################"
print ""
print "Step 1) Empty Water Tank"
print "Step 2) Put Ultrasonic Sensor in place on top of tank"
print ""
raw_input('hit return to continue:')




print "Measuring Empty Level"

total = 0.0
# test 10 times
for i in range(10):
    measurement = ultrasonicRanger.measurementInCM()
    print "{:5.3f}{}".format(measurement,"cm")
    total = total + measurement 

emptyaverage = total/10.0

print "{} {:6.1f} ".format( "calibrated EMPTY Level=", emptyaverage)
print ""
print "Step 3) Fill Water Tank"
print "Step 4) Put Ultrasonic Sensor in place on top of tank"
print ""

raw_input('hit return to continue:')




print "Measuring Full Level"

total = 0.0
# test 10 times
for i in range(10):
    measurement = ultrasonicRanger.measurementInCM()
    print "{:5.3f}{}".format(measurement,"cm")
    total = total + measurement 

fullaverage = total/10.0

print "{} {:6.1f} ".format( "calibrated EMPTY Level=", fullaverage)
print ""

f = open("TankCalibration","w+")

f.write("{:6.1f}".format(emptyaverage))
f.write(",")
f.write("{:6.1f}".format(fullaverage))
f.close()

print "############################"
print "Values written to TankCalibration File"
print "############################"
print "Calibration Complete"
print "############################"
