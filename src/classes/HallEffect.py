import time
import board
import busio
import numpy as np
import matplotlib.pyplot as plt

i2c = busio.I2C(board.SCL, board.SDA)

import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

ads = ADS.ADS1115(i2c)
chanx = AnalogIn(ads, ADS.P0)
chany = AnalogIn(ads, ADS.P1)
chanz = AnalogIn(ads, ADS.P2)

chanxlist = []
chanylist = []
chanzlist = []

starttime = round(time.time(),2)
readtime = round(time.time(),2)
timelist = []

while readtime - starttime < 20:
    readtime = round(time.time(),2)
    print("time:",round(readtime-starttime,2),"x:",round(chanx.value-21273.88,2)," ","y:",round(chany.value-21032.99,2)," ","z:",round(chanz.value-20835.43,2)," ")
    timelist.append(readtime)
    chanxlist.append(round(chanx.value-21273.88,2))
    chanylist.append(round(chany.value-21032.99,2))
    chanzlist.append(round(chanz.value-20835.43,2))
    time.sleep(0.2)
    
chanx_zero = sum(chanxlist)/(len(chanxlist))
chany_zero = sum(chanylist)/(len(chanylist))
chanz_zero = sum(chanzlist)/(len(chanzlist))

print("x:",chanx_zero,"y:",chany_zero,"z:",chanz_zero)
plt.plot(timelist,chanxlist,timelist,chanylist,timelist,chanzlist)
plt.show()