#!/usr/bin/env python
#   SDL_Arduino_SDL_Pi_GroveDigitalExtender Library
#   SDL_Arduino_SDL_Pi_GroveDigitalExtender.py Raspberry Pi Drivers
#   Version 1.1
#   SwitchDoc Labs   August 3, 2015


import smbus
from datetime import datetime

class SDL_Pi_GroveDigitalExtender():

	# This board is based on the SX1502 I2C 8 Bit GPIO 
	################
	# SDL_Pi_GroveDigitalExtender Code
	################
	#I2C ADDRESS/BITS
	#   -----------------------------------------------------------------------
	SDL_Pi_GroveDigitalExtender_ADDRESS                         =    (0x20)    # 0x21 (Addr=VDD)
	
	#=========================================================================
	
	#=========================================================================
	#    REGISTERS (R/W)
	#    -----------------------------------------------------------------------
	
	SDL_Pi_GroveDigitalExtender_REGDATA_ADDR                   =    (0x00) # RegData
	SDL_Pi_GroveDigitalExtender_REGDIR_ADDR                    =    (0x01) # Direction
	SDL_Pi_GroveDigitalExtender_REGPULLUP_ADDR                 =    (0x02) # Pullups
	SDL_Pi_GroveDigitalExtender_REGPULLDOWN_ADDR               =    (0x03) # Pulldowns
  	 
	SDL_Pi_GroveDigitalExtender_INTERRUPTMASK_ADDR             =    (0x05) # Interrupt Mask
	SDL_Pi_GroveDigitalExtender_SENSEHIGH_ADDR                 =    (0x06) # Interrupt direction 7-4
	SDL_Pi_GroveDigitalExtender_SENSELOW_ADDR                  =    (0x07) # Interrupt direction 3-0
  	 
	SDL_Pi_GroveDigitalExtender_INTERRUPTSOURCE_ADDR           =    (0x08) # Interrupt Source 
	SDL_Pi_GroveDigitalExtender_EVENTSTATUS_ADDR               =    (0x09) # Event Status of I/Os
  	 
	SDL_Pi_GroveDigitalExtender_REGPLDMODE_ADDR                =    (0x10) # PLD Mode  
	SDL_Pi_GroveDigitalExtender_REGPLDPLDTABLE0_ADDR           =    (0x11) # PLD Truth Table 
	SDL_Pi_GroveDigitalExtender_REGPLDPLDTABLE1_ADDR           =    (0x12) # PLD Truth Table  
	SDL_Pi_GroveDigitalExtender_REGPLDPLDTABLE2_ADDR           =    (0x13) # PLD Truth Table  
	SDL_Pi_GroveDigitalExtender_REGPLDPLDTABLE3_ADDR           =    (0x14) # PLD Truth Table  
	SDL_Pi_GroveDigitalExtender_REGPLDPLDTABLE4_ADDR           =    (0x15) # PLD Truth Table  
	 
	SDL_Pi_GroveDigitalExtender_REGADVANCED_ADDR               =    (0xAB) # Advanced Settings
  	 
	
  	 
	#---------------------------------------------------------------------
	SDL_Pi_GroveDigitalExtender_CONFIG_RESET                    =    (0x8000)  # Reset Bit
		
	SDL_Pi_GroveDigitalExtender_REG_IO7                     =    (0x80)  # Channel IO7 
	SDL_Pi_GroveDigitalExtender_REG_IO6                     =    (0x40)  # Channel IO6 
	SDL_Pi_GroveDigitalExtender_REG_IO5                     =    (0x20)  # Channel IO5 
	SDL_Pi_GroveDigitalExtender_REG_IO4                     =    (0x10)  # Channel IO4 
	SDL_Pi_GroveDigitalExtender_REG_IO3                     =    (0x08)  # Channel IO3 
	SDL_Pi_GroveDigitalExtender_REG_IO2                     =    (0x04)  # Channel IO2 
	SDL_Pi_GroveDigitalExtender_REG_IO1                     =    (0x02)  # Channel IO1 
	SDL_Pi_GroveDigitalExtender_REG_IO0                     =    (0x01)  # Channel IO0 
  	 
	INPUT                       =    (0x01)  # 1 means input
	OUTPUT                      =    (0x00)  # 0 means output
  	 
	SDL_Pi_GroveDigitalExtender_OFF                         =    (0x00)  # 0 means off
	SDL_Pi_GroveDigitalExtender_ON                          =    (0x01)  # 1 means on
  	 
   	
	SDL_Pi_GroveDigitalExtender_REG_SENS_NONE              =    (0x0)  # None - Interrupt Edge Sensitivity
	SDL_Pi_GroveDigitalExtender_REG_SENS_RISING            =    (0x1)  # Rising - Interrupt Edge Sensitivity
	SDL_Pi_GroveDigitalExtender_REG_SENS_FALLING           =    (0x2)  # Falling - Interrupt Edge Sensitivity
	SDL_Pi_GroveDigitalExtender_REG_SENS_BOTH              =    (0x3)  # None - Interrupt Edge Sensitivity
	
    


	def __init__(self, twi=1, addr=SDL_Pi_GroveDigitalExtender_ADDRESS):
		self._bus = smbus.SMBus(twi)
		self._SDL_Pi_GroveDigitalExtender_i2caddr = addr
		
		# variables
    		self.wireWriteRegister(self.SDL_Pi_GroveDigitalExtender_REGDIR_ADDR, 0xFF)
		self._SDL_Pi_GroveDigitalExtender_direction = 0xFF
        	self._SDL_Pi_GroveDigitalExtender_pullup = 0
        	self._SDL_Pi_GroveDigitalExtender_pulldown = 0
		self._SDL_Pi_GroveDigitalExtender_interruptmask = 0
    


			

	def readGPIOByte(self):
		
		value = self.wireReadRegister(self.SDL_Pi_GroveDigitalExtender_REGDATA_ADDR)
		return value

	def writeGPIOByte(self, value):
		self.wireWriteRegister(self.SDL_Pi_GroveDigitalExtender_REGDATA_ADDR, value )
		return value


	def readGPIO(self, channel):
		
		value = self.wireReadRegister(self.SDL_Pi_GroveDigitalExtender_REGDATA_ADDR)
		mask = 1 << channel 
		if ((mask & value) == 0):
			return 0
		else:
			return 1

	def writeGPIO(self, channel, value):
		
		# clear channel bits except lsb
		value = value & 0x01
		value = value << channel
		channelMask = 1 << channel
	        oldValue = self.wireReadRegister(self.SDL_Pi_GroveDigitalExtender_REGDATA_ADDR)
		newValue = (oldValue & ((~channelMask) & 0xFF)) + value
		self.wireWriteRegister(self.SDL_Pi_GroveDigitalExtender_REGDATA_ADDR, newValue )
		return value


  	def setDirectionGPIOChannel(self, channel, direction):

		channel = 1 << channel
   		#print "setDirect channel = 0x%X" % channel 
		oldDirectionReg = self.wireReadRegister(self.SDL_Pi_GroveDigitalExtender_REGDIR_ADDR)
		#print "oldDirectionReg= 0x%x" % oldDirectionReg
		
    		if (direction == self.INPUT):
        		value = oldDirectionReg | channel
        
        
    		else:
        		# assume output
        		value = oldDirectionReg & ((~channel) &0xFF) 
        
    
   		self._SDL_Pi_GroveDigitalExtender_direction = value
    
    		self.wireWriteRegister(self.SDL_Pi_GroveDigitalExtender_REGDIR_ADDR, value)
    
    		# print("GPIO Direction=",value)
		newDirectionReg = self.wireReadRegister(self.SDL_Pi_GroveDigitalExtender_REGDIR_ADDR)
		#print "newDirectionReg= 0x%x" % newDirectionReg
    
    		return  newDirectionReg



  	
	def setPullupGPIOChannel(self, channel, state):
		
		channel = 1 << channel
    
		if (state == self.SDL_Pi_GroveDigitalExtender_OFF):
        		value = self._SDL_Pi_GroveDigitalExtender_pullup & ((~channel) &0xFF) 
    		else:
        		# assume output
        		value = self._SDL_Pi_GroveDigitalExtender_pullup | channel
        
    
    
    		self._SDL_Pi_GroveDigitalExtender_pullup = value;
    		self.wireWriteRegister(self.SDL_Pi_GroveDigitalExtender_REGPULLUP_ADDR, value);
    		#print("GPIO Pullup=",value)
    
    		return self._SDL_Pi_GroveDigitalExtender_pullup;


  	def setPulldownGPIOChannel(self, channel, state):  

		channel = 1 << channel
    
   		if (state == self.SDL_Pi_GroveDigitalExtender_OFF):
        		value = self._SDL_Pi_GroveDigitalExtender_pulldown & ((~channel) &0xFF) 
    		else:
        		# assume output
        		value = self._SDL_Pi_GroveDigitalExtender_pulldown | channel
        
    
   		self._SDL_Pi_GroveDigitalExtender_pulldown = value;
    		self.wireWriteRegister(self.SDL_Pi_GroveDigitalExtender_REGPULLDOWN_ADDR, value)
    		#print("GPIO Pulldown=",value)
    
    		return self._SDL_Pi_GroveDigitalExtender_pulldown;

  	def setInterruptMaskGPIOChannel(self, channel, state):
		
		channel = 1 << channel
    		
		if (state == self.SDL_Pi_GroveDigitalExtender_OFF):
        		value = self._SDL_Pi_GroveDigitalExtender_interruptmask & ((~channel) &0xFF) 
    		else:
        		# assume output
        		value = self._SDL_Pi_GroveDigitalExtender_interruptmask | channel
        
    
    
    		self._SDL_Pi_GroveDigitalExtender_interruptmask = value
    		self.wireWriteRegister(self.SDL_Pi_GroveDigitalExtender_INTERRUPTMASK_ADDR, value)
    		#print("GPIO Interrupt Mask=",value)
    
    		return self._SDL_Pi_GroveDigitalExtender_interruptmask;




 	def wireWriteRegister(self, reg, value):

        	#print "addr =0x%x register = 0x%x data = 0x%x " % (self._SDL_Pi_GroveDigitalExtender_i2caddr, reg, value)
		self._bus.write_byte_data(self._SDL_Pi_GroveDigitalExtender_i2caddr, reg, value)

    
	def wireReadRegister(self, reg ):

		returndata = self._bus.read_byte_data(self._SDL_Pi_GroveDigitalExtender_i2caddr, reg)
        	#print "addr = 0x%x data = 0x%x %i returndata = 0x%x " % (self._SDL_Pi_GroveDigitalExtender_i2caddr, reg, reg, returndata)
        	return returndata

