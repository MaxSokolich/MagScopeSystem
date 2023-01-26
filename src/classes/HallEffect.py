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
from multiprocessing import Process, Queue, Event

class HallEffect:
    """
    Class for managing the Hall Effect sensors via i2c
    Args:
        None
    """

    def __init__(self):
        #set up sensor I2C
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.ads = ADS.ADS1115(self.i2c)
        
        self.chanPosY = AnalogIn(self.ads, ADS.P0)
        self.chanPosX = AnalogIn(self.ads, ADS.P1)  #big external EM
        self.chanNegY = AnalogIn(self.ads, ADS.P2)  # one of the 4 coil config Em
        self.chanNegX = AnalogIn(self.ads, ADS.P3)

        #set up queue and exit condition
        self.exit = Event()

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
    
    def showFIELD(self,q):
        """
        continously updates queue with sensor value from mulitprocssing.Process
        Args:
            q: Queue 
        Returns:
            None
        """             
        posY = self.createBounds() #create bounds for positive Y EM sensor
        posX = self.createBounds() #create bounds for positive X EM sensor
        negY = self.createBounds() #create bounds for negative Y EM sensor
        negX = self.createBounds() #create bounds for negative X EM sensor
        while not self.exit.is_set():
            
            #print("\nsensor1:", self.readFIELD(self.chanPosY, posY))
            #print("sensor2: ",self.readFIELD(self.chanPosX, posX))
            #print("sensor3: ",self.readFIELD(self.chanNegY, negY))
            #print("sensor4: ",self.readFIELD(self.chanNegX, negX))

            s1 = self.readFIELD(self.chanPosY, posY)
            s2 = self.readFIELD(self.chanPosX, posX)
            s3 = self.readFIELD(self.chanNegY, negY)
            s4 = self.readFIELD(self.chanNegX, negX)

            q.put([s1,s2,s3,s4])
        print(" -- Sensor Process Terminated -- ")

    def start(self,q):
        sensor_process = Process(target = self.showFIELD, args = (q,))
        sensor_process.start()

    def shutdown(self):
        self.exit.set()

"""
if __name__ == "__main__":
    Sense = HallEffect()
    Sense.showFIELD(None)
"""

