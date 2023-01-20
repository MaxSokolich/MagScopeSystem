import cv2
import EasyPySpin
import time
import numpy as np
from pySerialTransfer import pySerialTransfer as txfer
import os, struct, array
from fcntl import ioctl
from JoystickClass import *#READ_JS, LSTICK,RSTICK,BUTTON

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
print("-- Connected to Joystick --")

#ARDUINO
arduino  = txfer.SerialTransfer('/dev/ttyACM0')
arduino.open()
print("-- Connected to Arduino --")

#CAMERA
fps = count_fps()       
cam = EasyPySpin.VideoCapture(0)
print("-- Connected to Camera --")
cam.set(cv2.CAP_PROP_FPS,30)
print(cam.get(cv2.CAP_PROP_FPS))
r =.5

    
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
    LSTICK,RSTICK,BUTTON = READ_JS()
    #print(BUTTON, LSTICK, RSTICK)
     
     

    x = LSTICK[0]
    y = LSTICK[1]
    mag = np.sqrt(x**2+y**2)
    print(mag)
    if mag > .01:
        angle = np.arctan2(y, x) - np.pi/2#*180/np.pi
        #angle = (angle+ 360) % 360
        rolling_frequency = int(mag*20)
        typ = 1
    else:
        angle = 0
        rolling_frequency = 0
        typ = 4
                         
   
    

    #send actions to arduino
    Send(arduino,typ,angle,rolling_frequency)
    

    cv2.putText(frame,str(int(fps.get_fps())),(int(40),int(70)), cv2.FONT_HERSHEY_COMPLEX,.5,(0,255,0),1)
    cv2.imshow("im",frame)
  

    fps.get_fps()
    if cv2.waitKey(10) & 0xFF == ord('q'):# or BUTTON == ["b",1]:
        Send(arduino,4,0,0)
        break
    

cv2.destroyAllWindows()
cam.release()  #close camera
arduino.close() #close arduino
#jsdev.close() #close joystick