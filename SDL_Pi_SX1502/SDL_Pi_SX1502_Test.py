#!/usr/bin/env python
#
#
# Test case for SX1502
# SDL_Pi_SX1502 Library for Rasbperry PI
#
# SwitchDoc Labs, August 2015
#

# imports

import sys
import time
import datetime
import random 
import SDL_Pi_SX1502


# Main Program

print ""
print "Test SDL_Pi_SX1502 Version 1.0 - SwitchDoc Labs"
print ""
print "Sample uses 0x21 I2C Address"
print "Blinks IO0 once every second"
print "Program Started at:"+ time.strftime("%Y-%m-%d %H:%M:%S")
print ""


filename = time.strftime("%Y-%m-%d%H:%M:%SRTCTest") + ".txt"
starttime = datetime.datetime.utcnow()

sx1502 = SDL_Pi_SX1502.SDL_Pi_SX1502()
print "-----------------"
# blink IO 0 to see LED
  
sx1502.setDirectionGPIOChannel(sx1502.SX1502_REG_IO0, sx1502.SX1502_OUTPUT)  
sx1502.setDirectionGPIOChannel(sx1502.SX1502_REG_IO1, sx1502.SX1502_OUTPUT)
sx1502.setDirectionGPIOChannel(sx1502.SX1502_REG_IO2, sx1502.SX1502_OUTPUT)
sx1502.setDirectionGPIOChannel(sx1502.SX1502_REG_IO3, sx1502.SX1502_OUTPUT)
#sx1502.setPullupGPIOChannel(sx1502.SX1502_REG_IO0, sx1502.SX1502_ON)
#sx1502.setPulldownGPIOChannel(sx1502.SX1502_REG_IO0, sx1502.SX1502_ON)

#sx1502.setInterruptMaskGPIOChannel(sx1502.SX1502_REG_IO0, sx1502.SX1502_ON)
while True:


    
    # loop about on IO 0 to see the LED blink
    
    print("----------------")
    sx1502.writeGPIO(0x01);
    time.sleep(1)
    print("++++++++++++++")
    value = sx1502.readGPIO()
    print("GPIO Value =",value)
    
    sx1502.writeGPIO(0x00)
    time.sleep(1)
    print("----------------")
    print("----------------")
   
    
  
