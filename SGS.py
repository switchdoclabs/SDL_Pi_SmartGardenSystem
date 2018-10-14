#!/usr/bin/env python

#
# Smart Garden System 
#
# SwitchDoc Labs
#

SGSVERSION = "007"
#imports 

import sys, traceback
import os
import RPi.GPIO as GPIO
import time
import threading
import json
import pickle

import logging; 
logging.basicConfig(level=logging.ERROR) 

import updateBlynk

from pubnub.pubnub import PubNub
from pubnub.pubnub import PNConfiguration


#appends
sys.path.append('./SDL_Pi_HDC1000')
sys.path.append('./SDL_Pi_SSD1306')
sys.path.append('./Adafruit_Python_SSD1306')
sys.path.append('./SDL_Pi_SI1145')
sys.path.append('./SDL_Pi_Grove4Ch16BitADC/SDL_Adafruit_ADS1x15')
sys.path.append('./SDL_Pi_GroveDigitalExtender')

from neopixel import *

import pixelDriver

import SDL_Pi_HDC1000

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import Adafruit_SSD1306

import Scroll_SSD1306


import SDL_Pi_SI1145
import SI1145Lux

import extendedPlants

import ultrasonicRanger

from SDL_Adafruit_ADS1x15 import ADS1x15

import AirQualitySensorLibrary 

from datetime import datetime
from datetime import timedelta

from apscheduler.schedulers.background import BackgroundScheduler

import apscheduler.events


# Check for user imports
try:
            import conflocal as config
except ImportError:
            import config

if (config.enable_MySQL_Logging == True):
            import MySQLdb as mdb

import state

import extendedPlants

#############
# Debug True or False
############

DEBUG = True

#initialization

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

################
# Update State Lock - keeps smapling from being interrupted (like by checkAndWater)
################
UpdateStateLock = threading.Lock()

###############
# Pixel Strip  LED
###############

# Create NeoPixel object with appropriate configuration.
strip = Adafruit_NeoPixel(pixelDriver.LED_COUNT, pixelDriver.LED_PIN, pixelDriver.LED_FREQ_HZ, pixelDriver.LED_DMA, pixelDriver.LED_INVERT, pixelDriver.LED_BRIGHTNESS, pixelDriver.LED_CHANNEL, pixelDriver.LED_STRIP)
# Intialize the library (must be called once before other functions).
strip.begin()
PixelLock = threading.Lock()


###############
# Flash LED
###############

def blinkLED(pixel, color, times, length):

    if (state.runLEDs == True):
        PixelLock.acquire()

        print "N--->Blink LED:%i/%i/%i/%6.2f" % (pixel, color, times, length)

        for x in range(0, times):
            strip.setPixelColor(0, color)
            strip.show()
            time.sleep(length)
	
        strip.setPixelColor(0, Color(0,0,0))
        strip.show()

        PixelLock.release()


    
###############
# pump setup
###############
GPIO.setup(config.USBEnable, GPIO.OUT)
GPIO.setup(config.USBControl, GPIO.OUT)
GPIO.output(config.USBEnable, GPIO.LOW)

def startPump():
        if (config.DEBUG):
            print("Pump #1 turned On")
        blinkLED(0,Color(0,255,0),1,0.5)
        GPIO.output(config.USBEnable, GPIO.LOW)
        GPIO.output(config.USBControl, GPIO.HIGH)

def stopPump():
        if (config.DEBUG):
            print("Pump #1 turned Off")

        blinkLED(0,Color(255,0,0),1,0.5)
        GPIO.output(config.USBEnable, GPIO.HIGH)
        GPIO.output(config.USBControl, GPIO.LOW)

def pumpWater(timeInSeconds, plantNumber):
    if (timeInSeconds <= 0.0):
        return 0.0
    if (plantNumber == 1):
        startPump()
    else:
        extendedPlants.turnOnExtendedPump(plantNumber, GDE_Ext1, GDE_Ext2)

    i = timeInSeconds 
    while (i > 0.0):
  	    time.sleep(1);   #Wait 1 second
            i = i -1.0    
    if (plantNumber == 1):
        stopPump()
    else:
        extendedPlants.turnOffExtendedPump(plantNumber, GDE_Ext1, GDE_Ext2)


    return 1

def forceWaterPlant(plantNumber):

            previousState = state.SGS_State;
	    #if(state.SGS_State == state.SGS_States.Monitor):
            state.SGS_State =state.SGS_States.Watering
            if (config.USEPUBNUB):
                publishStatusToPubNub()
            if (config.USEBLYNK):
                updateBlynk.blynkStatusUpdate()
            
            pumpWater(2.0, plantNumber)
            state.Last_Event = "Plant #{:d} Force Watered at: ".format(plantNumber)+time.strftime("%Y-%m-%d %H:%M:%S")
            if (config.USEBLYNK):
                updateBlynk.blynkTerminalUpdate(time.strftime("%Y-%m-%d %H:%M:%S")+": Plant #{:d} Force Watered".format(plantNumber)+"\n")
           
                updateBlynk.blynkEventUpdate()
            state.SGS_State = previousState
            if (config.USEPUBNUB):
                publishStatusToPubNub()
            if (config.USEBLYNK):
                updateBlynk.blynkStatusUpdate()


def waterPlant(plantNumber):
            # We want to put off this state if Update State is .is locked.   That will prevent Update State from being hosed by this state machine
            if (config.DEBUG):
                  print "WP-Attempt Aquire"
	    UpdateStateLock.acquire()
            if (config.DEBUG):
                  print "WP-UpdateStateLock acquired"



            previousState = state.SGS_State;
	    #if(state.SGS_State == state.SGS_States.Monitor):
            state.SGS_State =state.SGS_States.Watering
            if (config.USEPUBNUB):
                publishStatusToPubNub()
            if (config.USEBLYNK):
                updateBlynk.blynkStatusUpdate()
            
            if ((state.Tank_Percentage_Full > config.Tank_Pump_Level) or (state.Plant_Water_Request == True)) :
                pumpWater(2.0, plantNumber)
                state.Last_Event = "Plant #{:d} Watered at: ".format(plantNumber)+time.strftime("%Y-%m-%d %H:%M:%S")
                if (config.USEBLYNK):
                    updateBlynk.blynkTerminalUpdate(time.strftime("%Y-%m-%d %H:%M:%S")+": Plant #{:d} Watered".format(plantNumber)+"\n")
            else:
                if (config.DEBUG):
                    print "Plant #{:d} pumpWater overruled - Tank Empty".format(plantNumber)
                if (config.USEBLYNK):
                    updateBlynk.blynkTerminalUpdate(time.strftime("%Y-%m-%d %H:%M:%S")+": Plant #{:d} pumpWater overruled - Tank Empty".format(plantNumber)+"\n")
                state.Last_Event = "NW-Tank Empty at: " + time.strftime("%Y-%m-%d %H:%M:%S")
           
            if (config.USEBLYNK):
                updateBlynk.blynkEventUpdate()
            state.SGS_State = previousState
            if (config.USEPUBNUB):
                publishStatusToPubNub()
            if (config.USEBLYNK):
                updateBlynk.blynkStatusUpdate()
            if (config.DEBUG):
                  print "WP-Attempt released"
            UpdateStateLock.release()
            if (config.DEBUG):
                  print "WP-UpdateStateLock released"

###############
# Sunlight SI1145 Sensor Setup
################



try:
        Sunlight_Sensor = SDL_Pi_SI1145.SDL_Pi_SI1145()
        time.sleep(1)
        state.Sunlight_Visible = SI1145Lux.SI1145_VIS_to_Lux(Sunlight_Sensor.readVisible())

        config.Sunlight_Present = True
except:
        config.Sunlight_Present = False

################
#SSD 1306 setup
################

# OLED SSD_1306 Detection

try:
        RST =27
        display = Adafruit_SSD1306.SSD1306_128_64(rst=RST, i2c_address=0x3C)
        # Initialize library.
        display.begin()
        display.clear()
        display.display()
        config.OLED_Present = True
	OLEDLock = threading.Lock()
except:
        config.OLED_Present = False
        print "Smart Garden System must have OLED Present"
        raise SystemExit



################
#4 Channel ADC ADS1115 setup
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

###############
#Ultrasonic Level Teset
###############

percentFull = ultrasonicRanger.returnPercentFull()
# check for abort
if (percentFull < 0.0):
    if (config.DEBUG):
        print "---->Bad Measurement from Ultrasonic Sensor for Tank Level"
    config.UltrasonicLevel_Present = False
else:
    config.UltrasonicLevel_Present = True


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

   value = GDE_Ext1.readGPIO(1)
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

   value = GDE_Ext2.readGPIO(1)
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
# 
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




################
# HDC1000 Setup
################
config.HDC1000_Present = False
try:

    hdc1000 = SDL_Pi_HDC1000.SDL_Pi_HDC1000()
    config.hdc1000_Present = True

except:
    config.hdc1000_Present = False


import util

################
#Pubnub configuration 
################
# 

if (config.USEPUBNUB):
    pnconf = PNConfiguration()
 
    pnconf.subscribe_key = config.Pubnub_Subscribe_Key
    pnconf.publish_key = config.Pubnub_Publish_Key
  

    pubnub = PubNub(pnconf)

def publish_callback(result, status):
        if (config.DEBUG):
		print "status.is_error", status.is_error()
		print "status.original_response", status.original_response
		pass
        # handle publish result, status always present, result if successful
        # status.isError to see if error happened

def publishStatusToPubNub():

        myMessage = {}
        myMessage["SmartPlantPi_CurrentStatus"] = state.SGS_Values[state.SGS_State]
        
        if (config.DEBUG):
        	print myMessage

        pubnub.publish().channel('SmartPlantPi_Data').message(myMessage).async(publish_callback)

def publishEventToPubNub():

        myMessage = {}
        myMessage["SmartPlantPi_Last_Event"] = state.Last_Event
        
        if (config.DEBUG):
        	print myMessage

        pubnub.publish().channel('SmartPlantPi_Data').message(myMessage).async(publish_callback)

def publishAlarmToPubNub(alarmText):

        myMessage = {}
        myMessage["SmartPlantPi_Alarm"] = alarmText 
        
        if (config.DEBUG):
        	print myMessage

        pubnub.publish().channel('SmartPlantPi_Data').message(myMessage).async(publish_callback)

def publishStateToPubNub():
	
        if (config.DEBUG):
        	print('Publishing Data to PubNub time: %s' % datetime.now())


        myMessage = {}
        myMessage["SmartPlantPi_Visible"] = "{:4.2f}".format(state.Sunlight_Vis) 
        myMessage["SmartPlantPi_IR"] = "{:4.2f}".format(state.Sunlight_IR) 
        myMessage["SmartPlantPi_UVIndex"] = "{:4.2f}".format(state.Sunlight_UVIndex) 
        myMessage["SmartPlantPi_MoistureHumidity"] = "{:4.1f}".format(state.Moisture_Humidity) 
        myMessage["SmartPlantPi_AirQuality_Sensor_Value"] = "{}".format(state.AirQuality_Sensor_Value) 
        myMessage["SmartPlantPi_AirQuality_Sensor_Number"] = "{}".format(state.AirQuality_Sensor_Number) 
        myMessage["SmartPlantPi_AirQuality_Sensor_Text"] = "{}".format(state.AirQuality_Sensor_Text) 
        myMessage["SmartPlantPi_Temperature"] = "{:4.1f} {}".format(util.returnTemperatureCF(state.Temperature), util.returnTemperatureCFUnit() )
        myMessage["SmartPlantPi_Humidity"] = "{:4.1f}".format(state.Humidity) 
        myMessage["SmartPlantPi_CurrentStatus"] = "{}".format(state.SGS_Values[state.SGS_State])
        myMessage["SmartPlantPi_Moisture_Threshold"] = '{:4.1f}'.format(state.Moisture_Threshold)
        myMessage["SmartPlantPi_Version"] = '{}'.format(SGSVERSION) 
        myMessage["TimeStamp"] = '{}'.format( datetime.now().strftime( "%m/%d/%Y %H:%M:%S"))
        myMessage["SmartPlantPi_Last_Event"] = "{}".format(state.Last_Event)
        if (state.Pump_Water_Full == 0): 
            myMessage["SmartPlantPi_Water_Full_Text"] = "{}".format("Empty" )
            myMessage["SmartPlantPi_Water_Full_Direction"] = "{}".format("180" )
        else:
            myMessage["SmartPlantPi_Water_Full_Text"] = "{}".format("Full" )
            myMessage["SmartPlantPi_Water_Full_Direction"] = "{}".format("0" )

        if (config.DEBUG):
        	print myMessage

        pubnub.publish().channel('SmartPlantPi_Data').message(myMessage).async(publish_callback)
        pubnub.publish().channel('SmartPlantPi_Alexa').message(myMessage).async(publish_callback)

        blinkLED(0,Color(0,255,255),3,0.200)


#############################
# apscheduler setup
#############################
# setup tasks
#############################

def tick():
    print('Tick! The time is: %s' % datetime.now())


def killLogger():
    scheduler.shutdown()
    print "Scheduler Shutdown...."
    exit()


def checkAndWater():


    for i in range(1, config.plant_number+1):
        if (config.DEBUG):
            print "checkandWater: Plant#%i %0.2f Threshold / %0.2f Current" % (i,state.Moisture_Threshold, state.Moisture_Humidity_Array[i-1])
        if (state.Moisture_Humidity_Array[i-1] <= state.Alarm_Moisture_Sensor_Fault):
	      print "No Watering Plant #%i - Moisture Sensor Fault Detected!"	% (i)	
        else:
    	    if (state.Moisture_Threshold > state.Moisture_Humidity_Array[i-1]):
                if (config.DEBUG):
	    	    print "Attempting to Watering Plant"
            	waterPlant(i);
    
def forceWaterPlantCheck():
    if ((state.Plant_Water_Request == True) and (state.Plant_Number_Water_Request > 0)):
        # now check for forced watering
        if (config.DEBUG):
            print ">>>>>>>>>>>>>>"
            print "Entering Force Water"
            print ">>>>>>>>>>>>>>"
            print "FW-Attempt UpdateStateLock acquired"
        UpdateStateLock.acquire()
        if (config.DEBUG):
            print "FW-UpdateStateLock acquired"

        PlantNumber = state.Plant_Number_Water_Request
        if (config.DEBUG):
                print "<<<<<<<<>>>>>>>"
                print "Force Plant {:d} Water from Button ".format(PlantNumber)
                print "<<<<<<<<>>>>>>>"
        forceWaterPlant(PlantNumber)
        state.Plant_Number_Water_Request = -1
        updateBlynk.blynkResetButton("V41")
        state.Plant_Water_Request = False
        # now reset water information
         
        if (config.DEBUG):
            print "FW-Attempt UpdateStateLock released"
        UpdateStateLock.release()
        if (config.DEBUG):
                print "FW-UpdateStateLock released"
                print ">>>>>>>>>>>>>>"
                print "Exiting Force Water"
                print ">>>>>>>>>>>>>>"




def ap_my_listener(event):
        if event.exception:
              print event.exception
              print event.traceback


def returnStatusLine(device, state):

        returnString = device
        if (state == True):
                returnString = returnString + ":   \t\tPresent"
        else:
                returnString = returnString + ":   \t\tNot Present"
        return returnString


#############################
# get and store sensor state
#############################




def saveState():
	    output = open('SGSState.pkl', 'wb')

	    # Pickle dictionary using protocol 0.
	    pickle.dump(state.Moisture_Threshold, output)
	    pickle.dump(state.EnglishMetric, output)
	    pickle.dump(state.Alarm_Temperature, output)
	    pickle.dump(state.Alarm_Moisture, output)
	    pickle.dump(state.Alarm_Water, output)
	    pickle.dump(state.Alarm_Air_Quality, output)
	    pickle.dump(state.Alarm_Active, output)

	    output.close()

############
# Setup Moisture Pin for GrovePowerSave
############
GPIO.setup(config.moisturePower,GPIO.OUT)
GPIO.output(config.moisturePower, GPIO.LOW)


def updateState():

  if (config.DEBUG):
      print "Attempt UpdateStateLock acquired"
  UpdateStateLock.acquire()
  if (config.DEBUG):
      print "UpdateStateLock acquired"


  # catch Exceptions and MAKE SURE THE LOCK is released!
  try:
    if (state.SGS_State == state.SGS_States.Monitor):  
            state.SGS_State =state.SGS_States.Sampling
            if (config.USEBLYNK):
                updateBlynk.blynkStatusUpdate()
	    if (config.DEBUG):
            	print "----------------- "
            	print "Update State"
            	print "----------------- "
            if (config.Sunlight_Present == True):
        			if (config.DEBUG):
                                	print " Sunlight Vi/state.Sunlight_IR/UV Sensor"
            else:
        			if (config.DEBUG):
                                	print " Sunlight Vi/state.Sunlight_IR/UV Sensor Not Present"
            if (config.DEBUG):
            	print "----------------- "
    
            if (config.Sunlight_Present == True):
                    ################
                    state.Sunlight_Vis = SI1145Lux.SI1145_VIS_to_Lux(Sunlight_Sensor.readVisible())
                    state.Sunlight_IR = SI1145Lux.SI1145_IR_to_Lux(Sunlight_Sensor.readIR())
                    state.Sunlight_UV = Sunlight_Sensor.readUV()
                    state.Sunlight_UVIndex = state.Sunlight_UV / 100.0

            	    if (config.DEBUG):
                    	print 'Sunlight Visible:  ' + str(state.Sunlight_Vis)
                    	print 'Sunlight state.Sunlight_IR:       ' + str(state.Sunlight_IR)
                    	print 'Sunlight UV Index (RAW): ' + str(state.Sunlight_UV)
                    	print 'Sunlight UV Index: ' + str(state.Sunlight_UVIndex)
                    ################
    
    
            if (config.ADS1115_Present):
                state.Moisture_Humidity  = extendedPlants.readExtendedMoisture(1, None, ads1115, None, None) 
                state.Moisture_Humidity_Array[0] =  state.Moisture_Humidity 

                for i in range(2,config.plant_number+1):     
                    state.Moisture_Humidity_Array[i-1] = extendedPlants.readExtendedMoisture(i,GDE_Ext1, ads1115_ext1, GDE_Ext2, ads1115_ext2)

                if (config.DEBUG):
                    print ("From Moisture Array")
                    for i in range(0,config.plant_number):     
                        print "plant #%i: Moisture: %0.2f" % (i+1, state.Moisture_Humidity_Array[i])
                    print ("From RAW Moisture Array")
                    for i in range(0,config.plant_number):     
                        print "plant #%i: Moisture: %0.2f" % (i+1, state.Raw_Moisture_Humidity_Array[i])

                state.AirQuality_Sensor_Value =  AirQualitySensorLibrary.readAirQualitySensor(ads1115)
    
                sensorList = AirQualitySensorLibrary.interpretAirQualitySensor(state.AirQuality_Sensor_Value)
            	if (config.DEBUG):
                	print "Sensor Value=%i --> %s  | %i"% (state.AirQuality_Sensor_Value, sensorList[0], sensorList[1])

                state.AirQuality_Sensor_Number = sensorList[1] 
                state.AirQuality_Sensor_Text = sensorList[0] 

            # update water Level
            percentFull = ultrasonicRanger.returnPercentFull()
            # check for abort
            if (percentFull < 0.0):
                if (config.DEBUG):
                    print "---->Bad Measurement from Ultrasonic Sensor for Tank Level"
                # leave the previous value
            else:
                state.Tank_Percentage_Full = percentFull
        
            if (state.Tank_Percentage_Full > config.Tank_Pump_Level):
                state.Pump_Water_Full = True
            else:
                state.Pump_Water_Full = False

            # read temp humidity
   
            if (config.hdc1000_Present):
                state.Temperature= hdc1000.readTemperature()
                state.Humidity = hdc1000.readHumidity()
    
           	if (config.DEBUG):
            		print 'Temp             = {0:0.3f} deg C'.format(state.Temperature)
            		print 'Humidity         = {0:0.2f} %'.format(state.Humidity)
    
            state.SGS_State =state.SGS_States.Monitor
            if (config.USEBLYNK):
                updateBlynk.blynkStatusUpdate()
          

            if (config.OLED_Present) and (state.SGS_State == state.SGS_States.Monitor) :


                    if (config.DEBUG):
                          print "Attempt OLEDLock acquired"
		    OLEDLock.acquire()
                    if (config.DEBUG):
                          print "OLEDLock acquired"
                    Scroll_SSD1306.addLineOLED(display,  ("----------"))
                    Scroll_SSD1306.addLineOLED(display,  ("Plant Moisture = \t%0.2f %%")%(state.Moisture_Humidity))
                    Scroll_SSD1306.addLineOLED(display,  ("Temperature = \t%0.2f %s")%(util.returnTemperatureCF(state.Temperature), util.returnTemperatureCFUnit()))
                    Scroll_SSD1306.addLineOLED(display,  ("Humidity =\t%0.2f %%")%(state.Humidity))
                    Scroll_SSD1306.addLineOLED(display,  ("Air Qual = %d/%s")%(state.AirQuality_Sensor_Value, state.AirQuality_Sensor_Text))
                    Scroll_SSD1306.addLineOLED(display,  ("Sunlight = \t%0.2f Lux")%(state.Sunlight_Vis))
                    if (config.DEBUG):
                        print "Attempt OLEDLock released"
		    OLEDLock.release()
                    if (config.DEBUG):
 
                        print "OLEDLock released"

  except Exception as e:
    if (config.DEBUG):
        print "Exception Raised in Update State"
    print e 
    traceback.print_exc(file=sys.stdout)
  finally:
    pass 
  if (config.DEBUG):
    print "Attempt UpdateStateLock released"
  UpdateStateLock.release()
  if (config.DEBUG):
          print "UpdateStateLock released"
          print ">>>>>>>>>>>>>>"
          print "Exiting Update State"
          print ">>>>>>>>>>>>>>"

  if (config.USEBLYNK):
     updateBlynk.blynkStateUpdate()



    

#############################
# Alarm Displays 
#############################
def checkForAlarms():

	# check to see alarm
        if (config.DEBUG):
		print "checking for alarm"
                if (state.Alarm_Active == True):
                    print "Alarm_Active = True"
                else:
                    print "Alarm_Active = False"
        # initialize 
        list = startAlarmStatementDisplay(display)

        lastAlarm = state.Alarm_Active
	if (state.Alarm_Active == True):
		activeAlarm = False
                state.Is_Alarm_MoistureFault = False
    		
                for i in range(0,config.plant_number):
                    if (state.Moisture_Humidity_Array[i] <= state.Alarm_Moisture_Sensor_Fault):
        		if (config.DEBUG):
                            print "Plant #{:d}---->Moisture Sensor Fault".format(i+1)
                        displayAlarmOLEDDisplay(list, "#{:d}MS FLT!".format(i), 10)
                        state.Is_Alarm_MoistureFault = True
        	
                
                if (state.Alarm_Air_Quality < state.AirQuality_Sensor_Value):
                    if (config.DEBUG):
			print "state.Alarm_Air_Quality=", state.Alarm_Air_Quality
			print "state.AirQuality_Sensor_Value", state.AirQuality_Sensor_Value
                    state.Is_Alarm_AirQuality = True
	            activeAlarm = True
                else:
                    state.Is_Alarm_AirQuality = False

		if (state.Alarm_Temperature >= state.Temperature):
        	    if (config.DEBUG):
			print "---->Low Temperature Alarm!"
	            activeAlarm = True
                    state.Is_Alarm_Temperature = True
                else:
                    state.Is_Alarm_Temperature = False

                state.Is_Alarm_Moisture = False
                for i in range(0,config.plant_number):
                    if (state.Moisture_Humidity_Array[i] <= state.Alarm_Moisture):
        		if (config.DEBUG):
                            print "Plant #{:d}---->Moisture Low Alarm".format(i+1)
                        state.Is_Alarm_Moisture = True
		        activeAlarm = True

		if (state.Alarm_Water  == True ):
		    if (state.Pump_Water_Full == False):
        		if (config.DEBUG):
		        	print "---->Water Empty Alarm!"
			activeAlarm = True
                        state.Is_Alarm_Water = True
                else:
                    state.Is_Alarm_Water = False
		

        	if (config.DEBUG):
			print "activeAlarm = ", activeAlarm		
		if (activeAlarm == True):
                    # hold for display
                    displayActiveAlarms()
                    state.Last_Event = "Alarm Active: "+time.strftime("%Y-%m-%d %H:%M:%S")
                    # release display
                else:
                    print "lastAlarm=", lastAlarm
                    print "activeAlarm=", activeAlarm
                    if (state.Alarm_Last_State != activeAlarm):
                        state.Last_Event = "Alarm Ended: "+time.strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        state.Last_Event = "SGS Running: "+time.strftime("%Y-%m-%d %H:%M:%S")
               
                if (config.USEPUBNUB):
                    publishEventToPubNub()
                if (config.USEBLYNK):
                    updateBlynk.blynkEventUpdate()
		
                if (config.USEPUBNUB): 
	            publishAlarmToPubNub("")
                if (config.USEBLYNK):
                    updateBlynk.blynkAlarmUpdate()    


def centerText(text,sizeofline):
        textlength = len(text)
        spacesCount = (sizeofline - textlength)/2
        mytext = ""
        if (spacesCount > 0):
                for x in range (0, spacesCount):
                        mytext = mytext + " "
        return mytext+text
	
def startAlarmStatementDisplay(display):

        width = 128
        height = 64
        top = 0
        lineheight = 10
        currentLine = 0
        offset = 0

        image = Image.new('1', (width, height))
        draw = ImageDraw.Draw(image)
        # Load font.
        font = ImageFont.truetype('roboto/Roboto-Regular.ttf', 12)
        display.clear()
        display.display()
        return [image, draw, font, display]

def displayAlarmStatementOLEDDisplay(list, text,lengthofline=18):

        image = list[0]
        draw = list[1]
        font = list[2]
        display = list[3]

        font = ImageFont.truetype('roboto/Roboto-BoldItalic.ttf', 25)
        draw.rectangle((0,0,127,5*12+2), outline=0, fill=255)
        draw.text((0, 1*12),    centerText(text, lengthofline),  font=font, fill=0)


        display.image(image)
        display.display()

        return [image, draw, font, display]

def displayAlarmOLEDDisplay(list, text, lengthofline=18):

        image = list[0]
        draw = list[1]
        font = list[2]
        display = list[3]

        font = ImageFont.truetype('roboto/Roboto-Bold.ttf', 25)
        draw.rectangle((0,0,127,5*12+2), outline=0, fill=0)
        draw.text((0, 2*12-4),    centerText(text, lengthofline),  font=font, fill=255)


        display.image(image)
        display.display()

        return [image, draw, font, display]


def finishAlarmStatementDisplay(list):
        image = list[0]
        display = list[3]
        display.clear()
        display.display()


def displayActiveAlarms():

        # do not do this during update state

        if (config.DEBUG):
            print "DA-Attempt UpdateStateLock acquired"
        UpdateStateLock.acquire()
        if (config.DEBUG):
            print "DA-UpdateStateLock acquired"

	# display Alarm
        if (config.DEBUG):
		print "Display Alarms"
    	if ((config.OLED_Present == True) and (state.SGS_State == state.SGS_States.Monitor)):

                if (config.DEBUG):
                      print "Attempt OLEDLock acquired"
        	OLEDLock.acquire()
                if (config.DEBUG):
                      print "OLEDLock acquired"
		
        	state.SGS_State =state.SGS_States.Alarm
                if (config.USEPUBNUB):
                    publishStatusToPubNub()
                if (config.USEBLYNK):
                    updateBlynk.blynkStatusUpdate()
		# initialize 
		list = startAlarmStatementDisplay(display)
		# Flash white screen w/Alarm in middle
		displayAlarmStatementOLEDDisplay(list, "ALARM!",lengthofline=13)
                time.sleep(0.25)
		# wait 2 seconds
		finishAlarmStatementDisplay(list)

		# display alarms, one per screen on black screen
		list = startAlarmStatementDisplay(display)


                state.Is_Alarm_MoistureFault = False
    		
                for i in range(0,config.plant_number):
                    if (state.Moisture_Humidity_Array[i] <= state.Alarm_Moisture_Sensor_Fault):
        		if (config.DEBUG):
                            print "Plant #{:d}---->Moisture Sensor Fault".format(i+1)
                        displayAlarmOLEDDisplay(list, "#{:d}MS FLT!".format(i), 10)
                        state.Is_Alarm_MoistureFault = True
                        time.sleep(0.25)

		if (state.Alarm_Temperature >= state.Temperature):
        		if (config.DEBUG):
				print "---->Temperature Alarm!"
			displayAlarmOLEDDisplay(list, "Low Temp", 10)
		  	time.sleep(0.25)

		if (state.Alarm_Moisture >= state.Moisture_Humidity):
			displayAlarmOLEDDisplay(list, "Plant Dry", 14)
		  	time.sleep(0.25)

		if (state.Alarm_Water  == True ):
			if (state.Pump_Water_Full == False):
				displayAlarmOLEDDisplay(list, "No Water", 12)
			        time.sleep(0.25)

		if (state.Alarm_Air_Quality <  state.AirQuality_Sensor_Value):
			displayAlarmOLEDDisplay(list, "Air Quality", 14)
			time.sleep(0.25)


		finishAlarmStatementDisplay(list)


		# Flash white to end
		list = startAlarmStatementDisplay(display)
		# Flash white screen w/Alarm in middle
		displayAlarmStatementOLEDDisplay(list, "ALARM!",lengthofline=15)
		time.sleep(1.0)
		# wait 1 seconds
		finishAlarmStatementDisplay(list)

        	state.SGS_State = state.SGS_States.Monitor
                if (config.USEBLYNK):
                    updateBlynk.blynkStatusUpdate()

                if (config.USEPUBNUB):
                    publishStatusToPubNub()

                if (config.DEBUG):
                    print "Attempt OLEDLock released"
        	OLEDLock.release()
                if (config.DEBUG):
                    print "OLEDLock released"

		if (state.Alarm_Active == False):   # it has been disabled
                        if (config.USEPUBNUB):
			    publishAlarmToPubNub("deactivated")
                        if (config.USEBLYNK):
                            updateBlynk.blynkAlarmUpdate()    
        if (config.DEBUG):
          print "DA-Attempt UpdateStateLock released"
        UpdateStateLock.release()
        if (config.DEBUG):
          print "DA-UpdateStateLock released"
#############################
# main program
#############################


# Main Program
if __name__ == '__main__':

    print ""
    print "SGS Version "+SGSVERSION+"  - SwitchDoc Labs"
    print ""
    print "Program Started at:"+ time.strftime("%Y-%m-%d %H:%M:%S")
    print ""

    if (config.USEBLYNK):
        updateBlynk.blynkTerminalUpdate(time.strftime("%Y-%m-%d %H:%M:%S")+": SGS Program Started"+ "\n")
        updateBlynk.blynkTerminalUpdate( "SGS Version "+SGSVERSION+"  - SwitchDoc Labs"+"\n")
    
    print returnStatusLine("ADS1115",config.ADS1115_Present)
    print returnStatusLine("OLED",config.OLED_Present)
    print returnStatusLine("Sunlight Sensor",config.Sunlight_Present)
    print returnStatusLine("hdc1000 Sensor",config.hdc1000_Present)
    print returnStatusLine("Ultrasonic Level Sensor",config.UltrasonicLevel_Present)
    print
    print "----------------------"
    print "Plant / Sensor Counts"
    print "----------------------"
    print "Sensor Count: ",config.moisture_sensor_count
    print "Pump Count: ",config.USB_pump_count
    print
    if (config.USEBLYNK):
        updateBlynk.blynkTerminalUpdate( "Sensor Count: %d\n"%config.moisture_sensor_count)
        updateBlynk.blynkTerminalUpdate("Pump Count: %d\n"%config.USB_pump_count)

    print "----------------------"
    print "Extender Devices"
    print "----------------------"
    print returnStatusLine("ADS1115_Ext1",config.ADS1115_Ext1_Present)
    print returnStatusLine("ADS1115_Ext2",config.ADS1115_Ext2_Present)
    print returnStatusLine("GPIO Extender 1",config.GroveDigital_Ext1_Present)
    print returnStatusLine("GPIO Extender 2",config.GroveDigital_Ext2_Present)
    print


    print "----------------------"
    print "Future Smart Garden System Expansions"
    print "----------------------"
    print returnStatusLine("SunAirPlus",config.SunAirPlus_Present)
    print returnStatusLine("Lightning Mode",config.Lightning_Mode)
    print returnStatusLine("Solar Power Mode",config.SolarPower_Mode)

    print returnStatusLine("MySQL Logging Mode",config.enable_MySQL_Logging)
    print
    print "----------------------"
    value = extendedPlants.readExtendedMoisture(1, None, ads1115, None, None)
    if (value <= state.Alarm_Moisture_Sensor_Fault):
    	 print "Moisture Sensor Fault:   Not In Plant or not Present. Value %0.2f%%" % value 
    else:
    	print returnStatusLine("Moisture Sensor",True)
    print "----------------------"



    scheduler = BackgroundScheduler()

    '''
    ##############
    # state persistance
    # if pickle file present, read it in
    ##############
    if (os.path.exists('SGSState.pkl')):

    	input = open('SGSState.pkl', 'rb')

    	# Pickle dictionary using protocol 0.
    	state.Moisture_Threshold = pickle.load(input)
    	state.EnglishMetric = pickle.load(input)
    	state.Alarm_Temperature = pickle.load(input)
    	state.Alarm_Moisture = pickle.load(input)
    	state.Alarm_Water = pickle.load(input)
    	state.Alarm_Air_Quality = pickle.load(input)
    	state.Alarm_Active = pickle.load(input)

    	input.close()
	
      '''


    scheduler.add_listener(ap_my_listener, apscheduler.events.EVENT_JOB_ERROR)	


    # prints out the date and time to console
    scheduler.add_job(tick, 'interval', seconds=60)

    # blink optional life light
    scheduler.add_job(blinkLED, 'interval', seconds=5, args=[0,Color(0,0,255),1,0.250])
    
    # blink life light
    scheduler.add_job(pixelDriver.statusLEDs, 'interval', seconds=15, args=[strip, PixelLock])


    # update device state
    scheduler.add_job(updateState, 'interval', seconds=10)

    # check for force water - note the interval difference with updateState
    scheduler.add_job(forceWaterPlantCheck, 'interval', seconds=8)
    

    # check for alarms
    scheduler.add_job(checkForAlarms, 'interval', seconds=15)
    #scheduler.add_job(checkForAlarms, 'interval', seconds=300)


    # send State to PubNub 
    if (config.USEPUBNUB):
        scheduler.add_job(publishStateToPubNub, 'interval', seconds=60)
    #if (config.USEBLYNK):
    #scheduler.add_job(updateBlynk.blynkStateUpdate, 'interval', seconds=60)

    # check and water  
    scheduler.add_job(checkAndWater, 'interval', minutes=15)

	
    # save state to pickle file 
    #scheduler.add_job(saveState, 'interval', minutes=30)

    #init blynk app state
    if (config.USEBLYNK):
        updateBlynk.blynkInit()
	
	
    # start scheduler
    scheduler.start()
    print "-----------------"
    print "Scheduled Jobs" 
    print "-----------------"
    scheduler.print_jobs()
    print "-----------------"
  
    if (config.USEBLYNK):
        print "Blynk Status=", updateBlynk.blynkSGSAppOnline()
        updateBlynk.blynkAlarmUpdate();

    state.Last_Event = "SGS Started:"+time.strftime("%Y-%m-%d %H:%M:%S")

    if (config.USEPUBNUB):
        publishEventToPubNub()
    if (config.USEBLYNK):
        updateBlynk.blynkEventUpdate()

    if (config.OLED_Present):
        if (config.DEBUG):
             print "Attempt OLEDLock acquired"
        OLEDLock.acquire()
        if (config.DEBUG):
             print "OLEDLock acquired"
	# display logo
    	image = Image.open('SmartPlantPiSquare128x64.ppm').convert('1')

	display.image(image)
	display.display()
	time.sleep(3.0)
	display.clear()

	Scroll_SSD1306.addLineOLED(display,  ("    Welcome to "))
        Scroll_SSD1306.addLineOLED(display,  ("   Smart Garden "))
        if (config.DEBUG):
             print "Attempt OLEDLock released"
        OLEDLock.release()
        if (config.DEBUG):
             print "OLEDLock released"

    
     
    
    # initialize variables
    #
    state.Pump_Water_Full = False
    
    try: 
            
            updateState()

            checkAndWater()
            checkForAlarms()
	    #############
	    #  Main Loop
    	    #############
            


            while True:
		time.sleep(10.0)
		


    except KeyboardInterrupt:  
    	    # here you put any code you want to run before the program   
    	    # exits when you press CTRL+C  
            print "exiting program" 
    #except:  
    	    # this catches ALL other exceptions including errors.  
    	    # You won't get any error messages for debugging  
    	    # so only use it once your code is working  
            #    	print "Other error or exception occurred!"  
  
    finally:  
	    #time.sleep(5)
    	    #GPIO.cleanup() # this ensures a clean exit 
	    stopPump()
            for i in range(2,config.plant_number+1):
                extendedPlants.turnOffExtendedPump(i, GDE_Ext1, GDE_Ext2)
	    saveState()

	    print "done"
