import time
import board
import busio
import numpy as np
import matplotlib.pyplot as plt
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from scipy.interpolate import interp1d

i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)


chanPosY = AnalogIn(ads, ADS.P0)
chanPosX = AnalogIn(ads, ADS.P1)  #big external EM
chanNegY = AnalogIn(ads, ADS.P2)  # one of the 4 coil config Em
chanNegX = AnalogIn(ads, ADS.P3)


'''
lets say for example 
negative maximum = 13076
zeroed = 20358
positive maximum = 27851
'''


def readFIELD(channel, arr, low, high):
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
    arr.append(VAL)
    low = min(arr)
    high = max(arr)
    m = interp1d([low,high],[100,0])
    print([VAL,low,high, int(m(VAL))])
    

posXarr, lowPX, highPX = [],0,0
negYarr, lowNY, highNY = [],0,0

while True:
    readFIELD(chanNegY, negYarr, lowNY, highNY)
    

