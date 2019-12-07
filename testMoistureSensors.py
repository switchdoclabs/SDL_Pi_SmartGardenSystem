# reads all extended moisture sensors

import RPi as GPIO
# Check for user imports
try:
                import conflocal as config
except ImportError:
                import config
import sys
import time

sys.path.append('./SDL_Pi_Grove4Ch16BitADC/SDL_Adafruit_ADS1x15')

sys.path.append('./SDL_Pi_GroveDigitalExtender')

from SDL_Adafruit_ADS1x15 import ADS1x15

import extendedPlants

import RPi.GPIO as GPIO


################
#4 Channel ADC ADS1115 setup Plant #1
################
# Set this to ADS1015 or ADS1115 depending on the ADC you are using!
ADS1115 = 0x01  # 16-bit ADC

ads1115 = ADS1x15(ic=ADS1115, address=0x48)

# Select the gain
gain = 6144  # +/- 6.144V
#gain = 4096  # +/- 4.096V

# Select the sample rate
sps = 250  # 250 samples per second
# determine if device present
try:
       value = ads1115.readRaw(0, gain, sps) # AIN0 wired to AirQuality Sensor
       time.sleep(1.0)
       value = ads1115.readRaw(0, gain, sps) # AIN0 wired to AirQuality Sensor

       config.ADS1115_Present = True

except TypeError as e:
       config.ADS1115_Present = False


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

############
# Setup Moisture Pin for GrovePowerSave
############
GPIO.setup(config.moisturePower,GPIO.OUT)
GPIO.output(config.moisturePower, GPIO.LOW)


import SDL_Pi_GroveDigitalExtender
###############
#Grove Digital Extender Ext1 setup
###############
GDE_Ext1 = None
try:
   GDE_Ext1 = SDL_Pi_GroveDigitalExtender.SDL_Pi_GroveDigitalExtender(addr=0x20)
   # all outputs
   """
   GDE_Ext1.setPullupGPIOChannel(0, GDE_Ext1.SDL_Pi_GroveDigitalExtender_ON)
   GDE_Ext1.setPullupGPIOChannel(1, GDE_Ext1.SDL_Pi_GroveDigitalExtender_ON)
   GDE_Ext1.setPullupGPIOChannel(2, GDE_Ext1.SDL_Pi_GroveDigitalExtender_ON)
   GDE_Ext1.setPullupGPIOChannel(3, GDE_Ext1.SDL_Pi_GroveDigitalExtender_ON)
   GDE_Ext1.setPullupGPIOChannel(4, GDE_Ext1.SDL_Pi_GroveDigitalExtender_ON)
   GDE_Ext1.setPullupGPIOChannel(5, GDE_Ext1.SDL_Pi_GroveDigitalExtender_ON)
   GDE_Ext1.setPullupGPIOChannel(6, GDE_Ext1.SDL_Pi_GroveDigitalExtender_ON)
   GDE_Ext1.setPullupGPIOChannel(7, GDE_Ext1.SDL_Pi_GroveDigitalExtender_ON)
   """

   GDE_Ext1.setDirectionGPIOChannel(0, GDE_Ext1.OUTPUT)  
   GDE_Ext1.setDirectionGPIOChannel(1, GDE_Ext1.OUTPUT)  
   GDE_Ext1.setDirectionGPIOChannel(2, GDE_Ext1.OUTPUT)  
   GDE_Ext1.setDirectionGPIOChannel(3, GDE_Ext1.OUTPUT)  
   GDE_Ext1.setDirectionGPIOChannel(4, GDE_Ext1.OUTPUT)  
   GDE_Ext1.setDirectionGPIOChannel(5, GDE_Ext1.OUTPUT)  
   GDE_Ext1.setDirectionGPIOChannel(6, GDE_Ext1.OUTPUT)  
   GDE_Ext1.setDirectionGPIOChannel(7, GDE_Ext1.OUTPUT) 

   for i in range (0, 8):
       GDE_Ext1.writeGPIO(i, 0)

   #value = GDE_Ext1.readGPIO(1)
   config.GroveDigital_Ext1_Present = True
except Exception as e: 
   print(e)
   config.GroveDigital_Ext1_Present = False


###############
#Grove Digital Extender Ext2 setup
###############
GDE_Ext2 = None
try:
   GDE_Ext2 = SDL_Pi_GroveDigitalExtender.SDL_Pi_GroveDigitalExtender(addr=0x21)
   # all outputs
   """
   GDE_Ext2.setPullupGPIOChannel(0, GDE_Ext2.SDL_Pi_GroveDigitalExtender_ON)
   GDE_Ext2.setPullupGPIOChannel(1, GDE_Ext2.SDL_Pi_GroveDigitalExtender_ON)
   GDE_Ext2.setPullupGPIOChannel(2, GDE_Ext2.SDL_Pi_GroveDigitalExtender_ON)
   GDE_Ext2.setPullupGPIOChannel(3, GDE_Ext2.SDL_Pi_GroveDigitalExtender_ON)
   GDE_Ext2.setPullupGPIOChannel(4, GDE_Ext2.SDL_Pi_GroveDigitalExtender_ON)
   GDE_Ext2.setPullupGPIOChannel(5, GDE_Ext2.SDL_Pi_GroveDigitalExtender_ON)
   GDE_Ext2.setPullupGPIOChannel(6, GDE_Ext2.SDL_Pi_GroveDigitalExtender_ON)
   GDE_Ext2.setPullupGPIOChannel(7, GDE_Ext2.SDL_Pi_GroveDigitalExtender_ON)
   """
   GDE_Ext2.setDirectionGPIOChannel(0, GDE_Ext2.OUTPUT)  
   GDE_Ext2.setDirectionGPIOChannel(1, GDE_Ext2.OUTPUT)  
   GDE_Ext2.setDirectionGPIOChannel(2, GDE_Ext2.OUTPUT)  
   GDE_Ext2.setDirectionGPIOChannel(3, GDE_Ext2.OUTPUT)  
   GDE_Ext2.setDirectionGPIOChannel(4, GDE_Ext2.OUTPUT)  
   GDE_Ext2.setDirectionGPIOChannel(5, GDE_Ext2.OUTPUT)  
   GDE_Ext2.setDirectionGPIOChannel(6, GDE_Ext2.OUTPUT)  
   GDE_Ext2.setDirectionGPIOChannel(7, GDE_Ext2.OUTPUT) 
   
   for i in range (0, 8):
       GDE_Ext2.writeGPIO(i, 0)

   #value = GDE_Ext2.readGPIO(1)
   config.GroveDigital_Ext2_Present = True
except Exception as e: 
   print(e)
   config.GroveDigital_Ext2_Present = False





################
#4 Channel ADC ADS1115 Ext1 setup
################
# Set this to ADS1015 or ADS1115 depending on the ADC you are using!
ADS1115 = 0x01  # 16-bit ADC

ads1115_ext1 = ADS1x15(ic=ADS1115, address=0x49)

# Select the gain
gain = 6144  # +/- 6.144V
#gain = 4096  # +/- 4.096V

# Select the sample rate
sps = 250  # 250 samples per second
# determine if device present
try:
       value = ads1115_ext1.readRaw(0, gain, sps) # AIN0 wired to AirQuality Sensor
       time.sleep(1.0)
       value = ads1115_ext1.readRaw(0, gain, sps) # AIN0 wired to AirQuality Sensor

       config.ADS1115_Ext1_Present = True

except TypeError as e:
       config.ADS1115_Ext1_Present = False


################
#4 Channel ADC ADS1115 Ext2 setup
################

ads1115_ext2 = None

# Set this to ADS1015 or ADS1115 depending on the ADC you are using!
ADS1115 = 0x01  # 16-bit ADC

ads1115_ext2 = ADS1x15(ic=ADS1115, address=0x4A)

# Select the gain
gain = 6144  # +/- 6.144V
#gain = 4096  # +/- 4.096V

# Select the sample rate
sps = 250  # 250 samples per second
# determine if device present
try:
       value = ads1115_ext2.readRaw(0, gain, sps) # AIN0 wired to AirQuality Sensor
       time.sleep(1.0)
       value = ads1115_ext2.readRaw(0, gain, sps) # AIN0 wired to AirQuality Sensor

       config.ADS1115_Ext2_Present = True

except TypeError as e:
       config.ADS1115_Ext2_Present = False






config.DEBUG = False
while (1):

    print "Plant #%i: %0.2f/%s" % (1, extendedPlants.readExtendedMoistureExt(1,None,ads1115), config.SensorType[1-1])

    # do 2-9 plants
    if (config.ADS1115_Ext1_Present):
        for i in range(2, 6): 
                print "Plant #%i: %0.2f/%s" %(i,extendedPlants.readExtendedMoistureExt(i, GDE_Ext1, ads1115_ext1),config.SensorType[i-1] )
            
    else:
        print "ADS1115_Ext1 Not Present"
    
    # do the rest of the plants
    if (config.ADS1115_Ext2_Present):
        for i in range(6, 10): 
                print "Plant #%i: %0.2f/%s" %(i,extendedPlants.readExtendedMoistureExt(i, GDE_Ext2, ads1115_ext2),config.SensorType[i-1] )
    else:
        print "ADS1115_Ext2 Not Present"

    print"--------------------------"
    print"--------------------------"
    time.sleep(2.0)
    # do #1 plant
