from time import sleep
from pySerialTransfer import pySerialTransfer as txfer
import time as time
import numpy as np
import math

link = txfer.SerialTransfer('/dev/ttyACM0')
link.open()
sleep(1)


arr = [float(4.0) ,float(50.5),float(0.367)]
sendSize = link.tx_obj(arr)
link.send(sendSize)
print("sent", arr)
sleep(2)


arr = [float(1.0) ,float(50.5),float(1)]
sendSize = link.tx_obj(arr)
link.send(sendSize)
print("sent", arr)
sleep(3)



   
arr = [float(4.0) ,float(50.5),float(0.367)] 
sendSize = link.tx_obj(arr)
link.send(sendSize)
print("sent", arr)
sleep(2)


arr = [float(2.0) ,float(50.5),float(1)] 
sendSize = link.tx_obj(arr)
link.send(sendSize)
print("sent", arr)
sleep(1)



arr = [float(4.0) ,float(50.5),float(0.367)] 
sendSize = link.tx_obj(arr)
link.send(sendSize)
print("sent", arr)
    
    
link.close()