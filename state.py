# 
# contains all the state variables for SmartPlantPi
#

# Check for user imports
try:
            import conflocal as config
except ImportError:
            import config

##################
#  English or Metric
##################
# if False, then English
# if True, then Metric
EnglishMetric = False 

##################
# blynk State Variable 
##################

blynkPlantNumberDisplay = 1

##################
# Sunlight sensor variable
##################

Sunlight_Vis = 0
Sunlight_IR = 0
Sunlight_UV = 0.0
Sunlight_UVIndex = 0.0


##################
# Moisture Sensors
##################
Moisture_Humidity = 100.0

Raw_Moisture_Humidity_Array = []
for i in range(1, config.moisture_sensor_count+1):
    Raw_Moisture_Humidity_Array.append(3400.0)
Moisture_Humidity_Array = []
for i in range(1, config.moisture_sensor_count+1):
    Moisture_Humidity_Array.append(100.0)

#water below this limit

Moisture_Threshold = 60.0   
##################
# Pump State
##################

Pump_Running = False
Pump_Water_Full = False

##################
# Tank State
##################

Tank_Level = 5.0
Tank_Empty_Level = 10.0
Tank_Full_Level = 2.0
Tank_Percentage_Full = 30.0

##################
# Temp/Humid sensor
##################

Temperature = 0.0
Humidity = 0.0

##################
# Air Quality Sensor
##################

AirQuality_Sensor_Value = 0
AirQuality_Sensor_Number = 4
AirQuality_Sensor_Text = ""


##################
# Alarm States
##################
Alarm_Temperature = 5.0  
Alarm_Moisture = 60.0
Alarm_Water = False
Alarm_Air_Quality = 10000 
Alarm_Moisture_Sensor_Fault = 15.0

Alarm_Active = True
Alarm_Cancel = False

Alarm_Last_State = False
Is_Alarm_Temperature = False
Is_Alarm_Moisture = False
Is_Alarm_MoistureFault = False
Is_Alarm_AirQuality = False
Is_Alarm_WaterEmpty = False

##################
# Internal States
##################


# run rainbow simulation on LEDs

runRainbow = False

# turn LED display on/off

runLEDs = True
# plant water requests

#-1 means no plant request
Plant_Number_Water_Request = -1   

Plant_Water_Request_Previous = False
Plant_Water_Request = False




# State Enum
class SGS_States():
    Idle = 0
    Monitor = 1
    Watering = 2
    RotarySelect = 3
    Rotary = 4
    Alarm = 5
    Sampling = 6
    Button = 7

SGS_Values = ["Idle", "Monitor", "Watering", "Rotary Select", "Rotary", "Alarm", "Sampling", "Button"]

SGS_State = SGS_States.Monitor

Last_Event = ""




