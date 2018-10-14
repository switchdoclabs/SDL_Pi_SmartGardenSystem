#
# extended plants and sensors
# August 2018
#

# Check for user imports
try:
                import conflocal as config
except ImportError:
                import config
import RPi.GPIO as GPIO


import state
import time

def turnOnExtendedPump(plantNumber,GDE1, GDE2):

    # check for valid plantNumber
    if (plantNumber > config.plant_number):
        print "Plant Number {:d} not present".format(plantNumber)
        return 0
    if (plantNumber < 6):
        GDE1.writeGPIO((plantNumber+2), 1) # Control
        GDE1.writeGPIO((plantNumber+2)+1, 0) # Enable Not
    else:
        GDE2.writeGPIO((plantNumber-2), 1) # Control
        GDE2.writeGPIO((plantNumber-2)+1, 0) # Enable Not
    print "Pump #{:d} turned ON".format(plantNumber)
    return 1


def turnOffExtendedPump(plantNumber,GDE1, GDE2):
    
    # check for valid plantNumber
    if (plantNumber > config.plant_number):
        print "Plant Number {:d} not present".format(plantNumber)
        return 0
    if (plantNumber < 6):
        GDE1.writeGPIO((plantNumber+2), 0) # Control
        GDE1.writeGPIO((plantNumber+2)+1, 0) # Enable Not
    else:
        GDE2.writeGPIO((plantNumber-2), 0) # Control
        GDE2.writeGPIO((plantNumber-2)+1, 0) # Enable Not
    print "Pump #{:d} turned OFF".format(plantNumber)


    return 1

def readExtendedMoisture(plantNumber,GDE1, ads1115_1, GDE2, ads1115_2):

   
    if (config.DEBUG):
        print "Reading Moisture Plant Number #", plantNumber
    # check for valid plantNumber
    if (plantNumber > config.plant_number):
        print "Plant Number {:d} not present".format(plantNumber)
    value = 0.0
    if (plantNumber < 6):
        value = readExtendedMoistureExt(plantNumber,GDE1, ads1115_1)
    else:
        value = readExtendedMoistureExt(plantNumber,GDE2, ads1115_2)
        
    return value 


# scale for capacitance sensor 1
def scaleMoistureCapacitance1(Moisture_Raw, PlantNumber):
    # do the varying scale of the moisture for Capacitance readers 
    # do the varying scale of the moisture
    # based on 10 bit values
    # > #0 100%
    #  = #1 0%
    # scale to 0% from there
    #
    if (Moisture_Raw < config.Capacitor1SensorCalibration[PlantNumber][1]):
          Moisture_Humidity = 100
    else:
          Moisture_Humidity = ((config.Capacitor1SensorCalibration[PlantNumber][0] - Moisture_Raw)*100.0)/(config.Capacitor1SensorCalibration[PlantNumber][0] - config.Capacitor1SensorCalibration[PlantNumber][1])
                            

    if (Moisture_Humidity < 0):
        Moisture_Humidity = 0.0

    return Moisture_Humidity

# Grove Resistive Moisture Sensor 1
def scaleMoistureResistance1(Moisture_Raw):
    # do the varying scale of the moisture
    # based on 10 bit values
    # > #1 100%
    #  = #2 65%
    # scale to 0% from there
    #
    if (Moisture_Raw < config.Resistor1SensorCalibration[1]):
          Moisture_Humidity = Moisture_Raw*(65.0/config.Resistor1SensorCalibration[1]) # low use linear to 0%
    else:
          Moisture_Humidity = Moisture_Raw*(100.0/config.Resistor1SensorCalibration[0]) # 65-100% use linear

    return Moisture_Humidity

# Grove / Gravity Resistance Moisture Sensor 2
def scaleMoistureResistance2(Moisture_Raw):
    # do the varying scale of the moisture
    # based on 10 bit values
    # > #0 100%
    #  = #1 0%
    # scale to 0% from there
    #
    if (Moisture_Raw < config.Resistor2SensorCalibration[1]):
          Moisture_Humidity = 100
    else:
          Moisture_Humidity = ((config.Resistor2SensorCalibration[0] - Moisture_Raw)*100.0)/(config.Resistor2SensorCalibration[0] - config.Resistor2SensorCalibration[1])
                            

    if (Moisture_Humidity < 0):
        Moisture_Humidity = 0.0

    return Moisture_Humidity


def readExtendedMoistureExt(plantNumber,GDE, ads1115):

    # Select the gain
    #gain = 6144  # +/- 6.144V
    gain = 4096  # +/- 4.096V

    # Select the sample rate
    sps = 250  # 250 samples per second
    if (config.DEBUG):
        print "readExtendedMoistureExt - Plant #", plantNumber

    if (plantNumber  == 1):
	    if (config.ADS1115_Present):
                #time.sleep(1.00)
       		#Moisture_Raw   = ads1115.readADCSingleEnded(0, gain, sps)/7 # AIN0 wired to AirQuality Sensor
       		#Moisture_Raw   = ads1115.readADCSingleEnded(plantNumber-2, gain, sps)

                GPIO.output(config.moisturePower, GPIO.HIGH)

       		Moisture_Raw   = ads1115.readRaw(config.moistureADPin, gain, sps) # Scale to 10 bits
                if (Moisture_Raw > 0x7FFF):
                    Moisture_Raw = 0 # Zero out negative Values
                Moisture_Raw = Moisture_Raw / 64 # scale to 10 bits

                state.Raw_Moisture_Humidity_Array[0] = Moisture_Raw 
       		Moisture_RawV   = ads1115.readADCSingleEnded(config.moistureADPin, gain, sps)
                print "Plant #%d Moisture_RawV=%0.2f"% (1,Moisture_RawV)
                if ((config.SensorType[plantNumber-1] == "R1") or (config.SensorType[plantNumber-1] == "R2")):
                    GPIO.output(config.moisturePower, GPIO.LOW)
                if (config.SensorType[plantNumber-1] == "C1"):
                    GPIO.output(config.moisturePower, GPIO.LOW)
                    time.sleep(0.25)
                    GPIO.output(config.moisturePower, GPIO.HIGH)

                 		

                state.Raw_Moisture_Humidity_Array[plantNumber -1] = Moisture_Raw  
              
                Moisture_Humidity = 0.0

                if (config.SensorType[plantNumber-1] == "C1"):
                    Moisture_Humidity = scaleMoistureCapacitance1(Moisture_Raw, plantNumber-1)

                if (config.SensorType[plantNumber-1] == "R1"):
                    Moisture_Humidity = scaleMoistureResistance1(Moisture_Raw)

                if (config.SensorType[plantNumber-1] == "R2"):
                    Moisture_Humidity = scaleMoistureResistance2(Moisture_Raw)

       		if (config.DEBUG):
                    print "Plant #%d -%s- Moisture_Raw =%0.2f, %0.2f" % (plantNumber, config.SensorType[plantNumber-1], Moisture_Raw, Moisture_Humidity )
       		

                 		
       	        if (config.DEBUG):
       		        print "Plant #%d Pre Limit Moisture_Humidity=%0.2f" % (plantNumber, Moisture_Humidity)
      	        if (Moisture_Humidity >100): 
       	 	        Moisture_Humidity = 100;
       	        if (Moisture_Humidity <0): 
               	        Moisture_Humidity = 0;
                    
       	        if (config.DEBUG):
        	        print "Plant #%d Moisture Humidity = %0.2f" % (plantNumber, Moisture_Humidity)
       	        if (config.DEBUG):
        	        print"------------------------------"
	        return Moisture_Humidity
	    else:
    	            Moisture_Humidity = 0.0
	            return Moisture_Humidity
    else:

        # do EXT1 
        if (plantNumber < 10):
             
	    
                GDE.writeGPIO((plantNumber-2 )%4, 1)
                #time.sleep(1.00)
       		#Moisture_Raw   = ads1115.readADCSingleEnded(0, gain, sps)/7 # AIN0 wired to AirQuality Sensor
       		#Moisture_Raw   = ads1115.readADCSingleEnded(plantNumber-2, gain, sps)
       		Moisture_Raw   = ads1115.readRaw((plantNumber-2)%4, gain, sps)
                if (Moisture_Raw > 0x7FFF):
                    Moisture_Raw = 0 # Zero out negative Values
                Moisture_Raw = Moisture_Raw / 64 # scale to 10 bits
                state.Raw_Moisture_Humidity_Array[plantNumber -1] = Moisture_Raw  
       		Moisture_RawV   = ads1115.readADCSingleEnded((plantNumber-2)%4, gain, sps) # Scale to 10 bits
                print "Plant #%d Moisture_RawV=%0.2f"% (plantNumber,Moisture_RawV)
                
              
                Moisture_Humidity = 0.0

                if (config.SensorType[plantNumber-1] == "C1"):
                    Moisture_Humidity = scaleMoistureCapacitance1(Moisture_Raw, plantNumber-1)

                if (config.SensorType[plantNumber-1] == "R1"):
                    Moisture_Humidity = scaleMoistureResistance1(Moisture_Raw)

                if (config.SensorType[plantNumber-1] == "R2"):
                    Moisture_Humidity = scaleMoistureResistance2(Moisture_Raw)

       		if (config.DEBUG):
                    print "Plant #%d -%s- Moisture_Raw =%0.2f, %0.2f" % (plantNumber, config.SensorType[plantNumber-1], Moisture_Raw, Moisture_Humidity )
       		

                if ((config.SensorType[plantNumber-1] == "R1") or (config.SensorType[plantNumber-1] == "R2")):
                    GDE.writeGPIO((plantNumber-2)%4, 0)
                if (config.SensorType[plantNumber-1] == "C1"):
                    GDE.writeGPIO((plantNumber-2)%4, 0)
                    time.sleep(0.25)
                    GDE.writeGPIO((plantNumber-2)%4, 1)

                 		
       	        if (config.DEBUG):
       		        print "Plant #%d Pre Limit Moisture_Humidity=%0.2f" % (plantNumber, Moisture_Humidity)
      	        if (Moisture_Humidity >100): 
       	 	        Moisture_Humidity = 100;
       	        if (Moisture_Humidity <0): 
               	        Moisture_Humidity = 0;
                    
       	        if (config.DEBUG):
        	        print "Plant #%d Moisture Humidity = %0.2f" % (plantNumber, Moisture_Humidity)
       	        if (config.DEBUG):
        	        print"------------------------------"
	        return Moisture_Humidity
                    
                
        return 0.0


