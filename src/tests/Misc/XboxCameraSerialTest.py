import cv2
import EasyPySpin
import time
import numpy as np
from pySerialTransfer import pySerialTransfer as txfer
import os, struct, array
from fcntl import ioctl
from JoystickClass import Joystick
import HallEffect

class count_fps:
    t0 = 0
    t1 = 0
    fps =0
    def __init__(self):
        self.t0 = time.time()
        self.t1 = self.t0
    def update(self):
        self.t1 = time.time()
        self.fps = 1/(self.t1-self.t0)
        self.t0 = self.t1
    def get_fps(self):
        return self.fps

#JOYSTICK
joy = Joystick()
print("-- Connected to Joystick --")

#ARDUINO
arduino  = txfer.SerialTransfer('/dev/ttyACM0')
arduino.open()
print("-- Connected to Arduino --")

#CAMERA
fps = count_fps()       
cam = cv2.VideoCapture("/home/max/Documents/MagScopeSystem/videos/mickyroll1.mp4")
print("-- Connected to Camera --")
cam.set(cv2.CAP_PROP_FPS,30)
print(cam.get(cv2.CAP_PROP_FPS))
r =.5

#SENSOR
sensor = HallEffect.Sensor()
posY = sensor.createBounds() #create bounds for positive Y EM sensor
posX = sensor.createBounds() #create bounds for positive X EM sensor
negY = sensor.createBounds() #create bounds for negative Y EM sensor
negX = sensor.createBounds() #create bounds for negative X EM sensor
    
def Send(arduino,typ,alpha,freq):
    message = arduino.tx_obj([float(typ),float(alpha),float(freq)]) #float(0) => Rolling
    arduino.send(message)
    print("sent:", [typ,alpha,freq])


    
    
while True:
    fps.update()
    suc, frame = cam.read()
    size = (int(frame.shape[1]*r), int(frame.shape[0]*r))
    frame = cv2.resize(frame,size,interpolation = cv2.INTER_AREA)
    
    
    #read joystick
    #evbuf = jsdev.read(8)
    #if evbuf is not None:
    
    #print(BUTTON, LSTICK, RSTICK)
    print(joy.leftX())
     
    print("sensor1: ",sensor.readFIELD(sensor.chanPosY, posY))
    print("sensor2: ",sensor.readFIELD(sensor.chanPosX, posX))
    print("sensor3: ",sensor.readFIELD(sensor.chanNegY, negY))
    print("sensor4: ",sensor.readFIELD(sensor.chanNegX, negX))

                         
   
    

    #send actions to arduino
    #Send(arduino,typ,angle,rolling_frequency)
    

    cv2.putText(frame,str(int(fps.get_fps())),(int(40),int(70)), cv2.FONT_HERSHEY_COMPLEX,.5,(0,255,0),1)
    cv2.imshow("im",frame)
  

    fps.get_fps()
    if cv2.waitKey(10) & 0xFF == ord('q'):# or BUTTON == ["b",1]:
        Send(arduino,4,0,0)
        joy.close()
        break
    

cv2.destroyAllWindows()
cam.release()  #close camera
arduino.close() #close arduino
#jsdev.close() #close joystick