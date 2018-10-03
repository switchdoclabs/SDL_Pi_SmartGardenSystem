#!/usr/bin/env python
#   SDL_Arduino_SX1502 Library
#   SDL_Arduino_SX1502.py Raspberry Pi Drivers
#   Version 1.1
#   SwitchDoc Labs   August 3, 2015


import smbus
from datetime import datetime

class SDL_Pi_SX1502():

	################
	# SX1502 Code
	################
	#I2C ADDRESS/BITS
	#   -----------------------------------------------------------------------
	SX1502_ADDRESS                         =    (0x21)    # 0x21 (Addr=VDD)
	
	#=========================================================================
	
	#=========================================================================
	#    REGISTERS (R/W)
	#    -----------------------------------------------------------------------
	
	SX1502_REGDATA_ADDR                   =    (0x00) # RegData
	SX1502_REGDIR_ADDR                    =    (0x01) # Direction
	SX1502_REGPULLUP_ADDR                 =    (0x02) # Pullups
	SX1502_REGPULLDOWN_ADDR               =    (0x03) # Pulldowns
  	 
	SX1502_INTERRUPTMASK_ADDR             =    (0x05) # Interrupt Mask
	SX1502_SENSEHIGH_ADDR                 =    (0x06) # Interrupt direction 7-4
	SX1502_SENSELOW_ADDR                  =    (0x07) # Interrupt direction 3-0
  	 
	SX1502_INTERRUPTSOURCE_ADDR           =    (0x08) # Interrupt Source 
	SX1502_EVENTSTATUS_ADDR               =    (0x09) # Event Status of I/Os
  	 
	SX1502_REGPLDMODE_ADDR                =    (0x10) # PLD Mode  
	SX1502_REGPLDPLDTABLE0_ADDR           =    (0x11) # PLD Truth Table 
	SX1502_REGPLDPLDTABLE1_ADDR           =    (0x12) # PLD Truth Table  
	SX1502_REGPLDPLDTABLE2_ADDR           =    (0x13) # PLD Truth Table  
	SX1502_REGPLDPLDTABLE3_ADDR           =    (0x14) # PLD Truth Table  
	SX1502_REGPLDPLDTABLE4_ADDR           =    (0x15) # PLD Truth Table  
	 
	SX1502_REGADVANCED_ADDR               =    (0xAB) # Advanced Settings
  	 
	
  	 
	#---------------------------------------------------------------------
	SX1502_CONFIG_RESET                    =    (0x8000)  # Reset Bit
		
	SX1502_REG_IO7                     =    (0x80)  # Channel IO7 
	SX1502_REG_IO6                     =    (0x40)  # Channel IO6 
	SX1502_REG_IO5                     =    (0x20)  # Channel IO5 
	SX1502_REG_IO4                     =    (0x10)  # Channel IO4 
	SX1502_REG_IO3                     =    (0x08)  # Channel IO3 
	SX1502_REG_IO2                     =    (0x04)  # Channel IO2 
	SX1502_REG_IO1                     =    (0x02)  # Channel IO1 
	SX1502_REG_IO0                     =    (0x01)  # Channel IO0 
  	 
	SX1502_INPUT                       =    (0x01)  # 0 means input
	SX1502_OUTPUT                      =    (0x00)  # 1 means output
  	 
	SX1502_OFF                         =    (0x00)  # 0 means off
	SX1502_ON                          =    (0x01)  # 1 means on
  	 
   	
	SX1502_REG_SENS_NONE              =    (0x0)  # None - Interrupt Edge Sensitivity
	SX1502_REG_SENS_RISING            =    (0x1)  # Rising - Interrupt Edge Sensitivity
	SX1502_REG_SENS_FALLING           =    (0x2)  # Falling - Interrupt Edge Sensitivity
	SX1502_REG_SENS_BOTH              =    (0x3)  # None - Interrupt Edge Sensitivity
	
    


	def __init__(self, twi=1, addr=SX1502_ADDRESS):
		self._bus = smbus.SMBus(twi)
		self._SX1502_i2caddr = addr
		
		# variables
    		self._SX1502_direction = 0xFF
        	self._SX1502_pullup = 0
        	self._SX1502_pulldown = 0
		self._SX1502_interruptmask = 0
    


			

	def readGPIO(self):
		
		value = self.wireReadRegister(self.SX1502_REGDATA_ADDR)
		return value

	def writeGPIO(self, value):
		self.wireWriteRegister(self.SX1502_REGDATA_ADDR, value )
		return value


  	def setDirectionGPIOChannel(self, channel, direction):
    
    		if (direction == self.SX1502_INPUT):
        		value = self.SX1502_direction | channel
        
        
    		else:
        		# assume output
        		value = self._SX1502_direction & ((~channel) &0xFF) 
        
    
   		self._SX1502_direction = value
    
    		self.wireWriteRegister(self.SX1502_REGDIR_ADDR, value)
    
    		# print("GPIO Direction=",value)
    
    		return self._SX1502_direction



  	
	def setPullupGPIOChannel(self, channel, state):
    
		if (state == self.SX1502_OFF):
        		value = self._SX1502_pullup & ((~channel) &0xFF) 
    		else:
        		# assume output
        		value = self._SX1502_pullup | channel
        
    
    
    		self._SX1502_pullup = value;
    		self.wireWriteRegister(self.SX1502_REGPULLUP_ADDR, value);
    		#print("GPIO Pullup=",value)
    
    		return self._SX1502_pullup;


  	def setPulldownGPIOChannel(self, channel, state):  

    
   		if (state == self.SX1502_OFF):
        		value = self._SX1502_pulldown & ((~channel) &0xFF) 
    		else:
        		# assume output
        		value = self._SX1502_pulldown | channel
        
    
   		self._SX1502_pulldown = value;
    		self.wireWriteRegister(self.SX1502_REGPULLDOWN_ADDR, value)
    		#print("GPIO Pulldown=",value)
    
    		return self._SX1502_pulldown;

  	def setInterruptMaskGPIOChannel(self, channel, state):
    		
		if (state == self.SX1502_OFF):
        		value = self._SX1502_interruptmask & ((~channel) &0xFF) 
    		else:
        		# assume output
        		value = self._SX1502_interruptmask | channel
        
    
    
    		self._SX1502_interruptmask = value
    		self.wireWriteRegister(self.SX1502_INTERRUPTMASK_ADDR, value)
    		#print("GPIO Interrupt Mask=",value)
    
    		return self._SX1502_interruptmask;




 	def wireWriteRegister(self, reg, value):

        	#print "addr =0x%x register = 0x%x data = 0x%x " % (self._SX1502_i2caddr, reg, value)
		self._bus.write_byte_data(self._SX1502_i2caddr, reg, value)

    
	def wireReadRegister(self, reg ):

		returndata = self._bus.read_byte_data(self._SX1502_i2caddr, reg)
        	#print "addr = 0x%x data = 0x%x %i returndata = 0x%x " % (self._SX1502_i2caddr, reg, reg, returndata)
        	return returndata

