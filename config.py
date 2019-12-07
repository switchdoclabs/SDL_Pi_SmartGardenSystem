
#
#
# configuration file - contains customization for exact system
# 
#

mailUser = "yourusename"
mailPassword = "yourmailpassword"

notifyAddress ="you@example.com"

fromAddress = "yourfromaddress@example.com"

#############
# Debug True or False
############

DEBUG = False

############
# Blynk configuration
############

USEBLYNK = False 
BLYNK_AUTH = 'xxxxx'
BLYNK_URL = 'http://blynk-cloud.com/'

############
# PubNub configuration
############

USEPUBNUB = False 
Pubnub_Publish_Key = "pub-c-xxxxxx"
Pubnub_Subscribe_Key = "sub-c-xxxxxx"


############
#MySQL Logging and Password Information
############

enable_MySQL_Logging = False
MySQL_Password = "password"


############
# Feature Enable/Disable
############
manual_water = True


############
# Moisture Sensor and Pump Count 
############

plant_number = 1
moisture_sensor_count = plant_number
USB_pump_count = plant_number

# R1 - Grove Reliable Resistive Moisture Sensor - SwitchDoc Labs
# R2 - HONG111 TE215 Dual Mode Resistive Moisture Sensor - Amazon.com 
# C1 - Grove Capacitive Moisture Sensor - SwitchDoc Labs

SensorType = ["C1","C1","C1","C1","C1","C1","C1","C1","C1"]
# for resistor1: first number is for 100%, second number is 65%
Resistor1SensorCalibration = [480,380]
# for resistor2: first number is for 0%, second number is 100%
Resistor2SensorCalibration = [460,131]
# for capacitance1: first number is for 0%, second number is 100%
Capacitor1SensorCalibration = [ [363,150], [363,150], [363,150], [363,150], [363,150], [363,150],[363,150], [363,150], [363,150]]

# if your pumps stick up too high, adjust this value so tank will still ready empty
Tank_Pump_Level = 15.0

############
# device present global variables
############


Lightning_Mode = False
SolarPower_Mode = False


SunAirPlus_Present = False
ADS1115_Present = False
ADS1115_Ext1_Present = False
ADS1115_Ext2_Present = False
GroveDigital_Ext1_Present = False
GroveDigital_Ext2_Present = False
ADS1115_Ext2_Present = False
OLED_Present = False
Sunlight_Present = False
hdc1000_Present = False

UltrasonicLevel_Present = True
############
#pin defines
############

UltrasonicLevel = 4
USBControl = 16
USBEnable = 19

AirQualityADPin = 0

moistureADPin = 1
moisturePower = 6
pixelPin = 21



