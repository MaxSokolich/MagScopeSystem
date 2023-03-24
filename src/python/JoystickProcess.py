
import time
import numpy as np
from multiprocessing import Process, Queue, Event
from src.python.JoystickClass import Joystick

#arduino signal: [typ, input1, input2, input3]
#typ =1 : spherical ---> Roll [1, alpha, freq, gamma]
#typ =2 : cartesian --> Orient [2, Bx, By, Bz]
#typ =3 : Tweezer [3, Direction, Amplitude, None] where directon = [1,2,3,4] = [Up,Right,Down,Left]

class JoystickProcess():
    def __init__(self):
        self.joy = Joystick()

        #acoustic conditioning
        self.button_state = 0
        self.last_state = 0
        self.counter = 0
        self.switch_state = 0

        #initlize actions
        self.typ = 4
        self.input1 = 0
        self.input2 = 0
        self.input3 = 0

        self.acoustic_status = 0
        self.amplitude = 0.9
        #exit event
        self.exit = Event()        

    def handle_joystick(self, joystick_q):
        while not self.exit.is_set():
            
            # A Button --> Acoustic Module Toggle
            self.acoustic_status = self.joy.A()

            #Y Button --> Magnetic Spinning
            if self.joy.Y():  #turn on spinning  
                self.typ = 1
                self.input3 = 0

            #Right Joystick Function --> Roll
            elif not self.joy.rightX() == 0 or not self.joy.rightY() == 0:
                Bxr = round(self.joy.rightX(),2)
                Byr = round(self.joy.rightY(),2)
                    
                angle = np.arctan2(Byr,Bxr)
                self.typ = 1
                self.input1 = angle+np.pi/2
                self.input2 = int(np.sqrt(Bxr**2 + Byr**2)*20)
                self.input3 = 90
                
                
                
            #Left Joystick Function --> Orient
            elif not self.joy.leftX() == 0 or not self.joy.leftY() == 0:
                Bxl = round(self.joy.leftX(),2)
                Byl = round(self.joy.leftY(),2)
                self.typ = 2
                self.input1 = Bxl
                self.input2 = Byl
            


            #Right Trigger Function --> Positive Z
            elif self.joy.rightTrigger() > 0:
                self.typ = 2
                self.input3 = self.joy.rightTrigger()
            
            #Left Trigger Function --> Negative Z
            elif self.joy.leftTrigger() > 0:
                self.typ = 2
                self.input3 = -self.joy.leftTrigger()
                
                

            #D-Pad --> Tweezer Quick Field
            elif self.joy.dpadUp() != 0:
                self.typ = 3
                self.input1 = 1 #Up
                self.input2 = self.amplitude
                self.input3 = 0
            elif self.joy.dpadRight() != 0:
                self.typ = 3
                self.input1 = 2 #Right
                self.input2 = self.amplitude
                self.input3 = 0
            elif self.joy.dpadDown() != 0:
                self.typ = 3
                self.input1 = 3 #Down
                self.input2 = self.amplitude
                self.input3 = 0
            elif self.joy.dpadLeft() != 0:
                self.typ = 3
                self.input1 = 4 #Left
                self.input2 = self.amplitude
                self.input3 = 0
                
            else:
                self.typ = 4
                self.input1 = 0
                self.input2 = 0
                self.input3 = 0
            
            #update queue
            actions = [self.typ, self.input1, self.input2, self.input3, self.acoustic_status]
            joystick_q.put(actions)
            #print(actions)
            time.sleep(40/1000)  #need some sort of delay to not flood queue
        
        #self.joy.close()
        print(" -- Joystick Process Terminated -- ")
    
        
    def start(self,joystick_q):
        joystick_process = Process(target = self.handle_joystick, args = (joystick_q,))
        joystick_process.start()

    def shutdown(self):

        self.joy.close()
        self.exit.set()

        
        
         
        

      
if __name__ == "__main__":
    joystick_q = Queue()
    joystick_q.cancel_join_thread()
    JP = JoystickProcess()
    JP.start(joystick_q)
    
    
    