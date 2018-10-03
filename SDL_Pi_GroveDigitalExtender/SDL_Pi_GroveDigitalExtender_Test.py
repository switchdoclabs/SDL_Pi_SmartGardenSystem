#!/usr/bin/env python
#
#
# Test case for SDL_Pi_GroveDigitalExtender
# SDL_Pi_GroveDigitalExtender Library for Rasbperry PI
#
# SwitchDoc Labs, August 2015
#

# imports

import sys
import time
import datetime
import random 
import SDL_Pi_GroveDigitalExtender

# Main Program

print ""
print "Test SDL_Pi_GroveDigitalExtender Version 1.0 - SwitchDoc Labs"
print ""
print "Sample uses 0x21 I2C Address"
print "Program Started at:"+ time.strftime("%Y-%m-%d %H:%M:%S")
print ""


filename = time.strftime("%Y-%m-%d%H:%M:%SRTCTest") + ".txt"
starttime = datetime.datetime.utcnow()

GDE = SDL_Pi_GroveDigitalExtender.SDL_Pi_GroveDigitalExtender(addr=0x21)
print "-----------------"
# blink IO 0 to see LED
# blink IO 2 to see LED
  
GDE.setDirectionGPIOChannel(0, GDE.OUTPUT)  
#GDE.setDirectionGPIOChannel(1, GDE.INPUT)  
GDE.setDirectionGPIOChannel(2, GDE.OUTPUT)  
#GDE.setDirectionGPIOChannel(3, GDE.OUTPUT)  
#GDE.setDirectionGPIOChannel(4, GDE.OUTPUT)  
#GDE.setDirectionGPIOChannel(5, GDE.OUTPUT)  
#GDE.setDirectionGPIOChannel(6, GDE.OUTPUT)  
#GDE.setDirectionGPIOChannel(7, GDE.OUTPUT)  
#GDE.setPullupGPIOChannel(0, GDE.SDL_Pi_GroveDigitalExtender_ON)
#GDE.setPulldownGPIOChannel(0, GDE.SDL_Pi_GroveDigitalExtender_ON)

#GDE.setInterruptMaskGPIOChannel(1, GDE.SDL_Pi_GroverDigitalExtender_ON)


while True:
    # read switch at GPIO1
    value = GDE.readGPIO(1)
    print("GPIO Value =",value)

    if (value == 1):

    
    	# loop about on IO 0 to see the LED blink
    
    	print("----------------")
    	GDE.writeGPIO(0,random.randint(0,1));
    	#GDE.writeGPIO(1,random.randint(0,1));
    	GDE.writeGPIO(2,random.randint(0,1));
    	#GDE.writeGPIO(3,random.randint(0,1));
    	#GDE.writeGPIO(4,random.randint(0,1));
    	#GDE.writeGPIO(5,random.randint(0,1));
    	#GDE.writeGPIO(6,random.randint(0,1));
    	#GDE.writeGPIO(7,random.randint(0,1));
	
    	time.sleep(0.02)
    	print("++++++++++++++")
   	 
    	GDE.writeGPIO(0,random.randint(0,1))
    	#GDE.writeGPIO(1,random.randint(0,1));
    	GDE.writeGPIO(2,random.randint(0,1));
    	#GDE.writeGPIO(3,random.randint(0,1));
    	#GDE.writeGPIO(4,random.randint(0,1));
    	#GDE.writeGPIO(5,random.randint(0,1));
    	#GDE.writeGPIO(6,random.randint(0,1));
    	#GDE.writeGPIO(7,random.randint(0,1));
    	value = GDE.readGPIO(1)
    	print("GPIO Value =",value)
    	time.sleep(0.02)
    	print("----------------")
    	print("----------------")
   
    else:

    	# loop about on IO 0 to see the LED blink
    
    	print("----------------")
    	GDE.writeGPIO(0,1);
    	#GDE.writeGPIO(1,1);
    	GDE.writeGPIO(2,1);
    	#GDE.writeGPIO(3,1);
    	#GDE.writeGPIO(4,1);
    	#GDE.writeGPIO(5,1);
    	#GDE.writeGPIO(6,1);
    	#GDE.writeGPIO(7,1);
	
    	time.sleep(0.02)
    	print("++++++++++++++")
   	 
    	GDE.writeGPIO(0,0)
    	#GDE.writeGPIO(1,0);
    	GDE.writeGPIO(2,0);
    	#GDE.writeGPIO(3,0);
    	#GDE.writeGPIO(4,0);
    	#GDE.writeGPIO(5,0);
    	#GDE.writeGPIO(6,0);
    	#GDE.writeGPIO(7,0);
    	value = GDE.readGPIO(1)
    	print("GPIO Value =",value)
    	time.sleep(0.02)
    	print("----------------")
    	print("----------------")
 
  
