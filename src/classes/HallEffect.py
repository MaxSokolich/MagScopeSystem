"""
Note: Both HallEffect.py and AcousticHandler.py must be have the same pinmode 
configuration. i.e. GPIO.BOARD, BCM, TEGRA_SOC, or CVM. 

What I found is compatible with adafruit is BOARD. User must change line 8 
in python3.8/site-packages/adafruit_blinka/microcontroller/tegra/t194/pin.py
to:

Jetson.GPIO.setmode(GPIO.BOARD)
"""

import board
import busio
import numpy as np
import matplotlib.pyplot as plt
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from scipy.interpolate import interp1d


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

    def createBounds(self):
        """
        creates initial bounds to be updated when field is being read
        Args:
            none
        Returns:
            list of min max bounds
        """
        #call this in readField maybe
        neg_max = float("inf")
        pos_max = -float("inf")
        return [neg_max, pos_max]
   
    def readFIELD(self, channel,bound):
        """
        reads hall effect sensor field data given an analog obejct
        Args:
            channel:   AnalogIN channel object 1-4
            bound: class object that stores the min and max bounds generated from sensor
        Returns:
            mapped_field: scaled field value -100 to 100
        """
        VAL = channel.value
        if VAL < bound[0]:
            bound[0] = VAL
        if VAL > bound[1]:
            bound[1] = VAL
        m = interp1d([bound[0],bound[1]],[-100,100])
        mapped_field = int(m(VAL))
        return mapped_field
        


if __name__ == "__main__":
    Sense = HallEffect()
    posY = Sense.createBounds() #create bounds for positive Y EM sensor
    posX = Sense.createBounds() #create bounds for positive X EM sensor
    negY = Sense.createBounds() #create bounds for negative Y EM sensor
    negX = Sense.createBounds() #create bounds for negative X EM sensor
    
    while True:
        XFIELD = Sense.readFIELD(Sense.chanPosX, posX)
        print(XFIELD)
        print(posX)


