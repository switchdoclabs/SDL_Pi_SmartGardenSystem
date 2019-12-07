#utility programs
import state
################
# Unit Conversion
################
# 

def returnTemperatureCF(temperature):
    if (state.EnglishMetric == True):
        # return Metric 
        return temperature
    else:
        return (9.0/5.0)*temperature + 32.0

def returnTemperatureCFUnit():
    if (state.EnglishMetric == True):
        # return Metric 
        return "C"
    else:
        return  "F"

