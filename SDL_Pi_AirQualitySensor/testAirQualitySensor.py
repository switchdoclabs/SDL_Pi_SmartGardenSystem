# SwitchDoc Labs
# AirQualitySensor Extender Pack for OurWeather/Raspberry Pi/Arudino/ESP8266
# Raspberry Pi Python Drivers
#
# Test Program
#
# April 2016
#

import AirQualitySensorLibrary
import time

# Import the ADS1x15 module.

from MADS1x15 import ADS1x15




# Initialise the ADC using the default mode (use default I2C address)
ADS1115 = 0x01	# 16-bit ADC
ads1115 = ADS1x15(ic=ADS1115)

while (1):


	print"------------------------------"
	sensor_value =  AirQualitySensorLibrary.readAirQualitySensor(ads1115)

        sensorList = AirQualitySensorLibrary.interpretAirQualitySensor(sensor_value)
	print "Sensor Value=%i --> %s  | %i"% (sensor_value, sensorList[0], sensorList[1])


	time.sleep(1.0) 


