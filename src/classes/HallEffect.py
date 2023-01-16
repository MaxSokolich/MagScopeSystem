import time
import board
import busio
import numpy as np
import matplotlib.pyplot as plt
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from scipy.interpolate import interp1d




'''
lets say for example 
negative maximum = 13076
zeroed = 20358
positive maximum = 27851
'''
class HallEffect:
    """
    Class for managing the Hall Effect sensors via i2c
    Args:
        None
    """

    def __init__(self):
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.ads = ADS.ADS1115(self.i2c)

        self.chanPosY = AnalogIn(self.ads, ADS.P0)
        self.chanPosX = AnalogIn(self.ads, ADS.P1)  #big external EM
        self.chanNegY = AnalogIn(self.ads, ADS.P2)  # one of the 4 coil config Em
        self.chanNegX = AnalogIn(self.ads, ADS.P3)

        self.min_val = float("inf")
        self.max_val = -float("inf")

    
    def createBounds(self):
        
        pass
        #return nmax,zero,pmax

    
    
    def readFIELD(self, channel):
        """
            reads hall effect sensor field data given an analog obejct
            need to figure out how to account for reverse polarity
            Args:
                channel:   AnalogIN channel object 1-4
                arr: list to append values to calculate min max from
                min, max: min and max raw values of sensor
            Returns:
                None
            """
        VAL = channel.value
        if VAL < self.min_val:
            self.min_val = VAL
        if VAL > self.max_val:
            self.max_val = VAL

        m = interp1d([self.min_val,self.max_val],[100,0])
        print([VAL,self.min_val,self.max_val, int(m(VAL))])
        


if __name__ == "__main__":

    Sense = HallEffect()
    while True:
        Sense.readFIELD(Sense.chanPosX)
    

