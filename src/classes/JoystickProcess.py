
import time
import numpy as np
from multiprocessing import Process, Queue, Event
from src.classes.JoystickClass import Joystick



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

        #exit event
        self.exit = Event()        

    def handle_joystick(self, joystick_q):
        while not self.exit.is_set():

            #A Button Function --> Acoustic Module Toggle
            self.button_state = self.joy.A()
            if self.button_state != self.last_state:
                if self.button_state == True:
                    self.counter +=1
            self.last_state = self.button_state
            if self.counter %2 != 0 and self.switch_state !=0:
                self.switch_state = 0
                #self.AcousticModule.start(ACOUSTIC_PARAMS["acoustic_freq"])
                print("acoustic: on")
            elif self.counter %2 == 0 and self.switch_state !=1:
                self.switch_state = 1
                #self.AcousticModule.stop()
                print("acoustic: off")

            #Left Joystick Function --> Orient
            elif not self.joy.leftX() == 0 or not self.joy.leftY() == 0:
                Bxl = round(self.joy.leftX(),2)
                Byl = round(self.joy.leftY(),2)
                self.typ = 2
                self.input1 = Bxl
                self.input2 = Byl
                
            
            #Right Joystick Function --> Roll
            elif not self.joy.rightX() == 0 or not self.joy.rightY() == 0:
                Bxr = round(self.joy.rightX(),2)
                Byr = round(self.joy.rightY(),2)
                    
                angle = np.arctan2(Bxr,Byr)
                freq = 20#CONTROL_PARAMS["rolling_frequency"]
                gamma = 90#CONTROL_PARAMS["gamma"]
                self.typ = 1
                self.input1 = angle
                self.input2 = freq
                self.input3 = gamma
            
            #Right Trigger Function --> Positive Z
            elif self.joy.rightTrigger() > 0:
                self.typ = 2
                self.input3 = self.joy.rightTrigger()
                

            #Left Trigger Function --> Negative Z
            elif self.joy.leftTrigger() > 0:
                self.typ = 2
                self.input3 = -self.joy.leftTrigger()

            else:
                self.typ = 4
                self.input1 = 0
                self.input2 = 0
                self.input3 = 0
            
            #update qeueu
            actions = [self.typ,self.input1, self.input2, self.input3]
            #print(actions)
            joystick_q.put([self.typ,self.input1, self.input2, self.input3])
            time.sleep(10/1000)
        
        self.joy.close()
        print(" -- Joystick Process Terminated -- ")
    
        
    def start(self,joystick_q):
        joystick_process = Process(target = self.handle_joystick, args = (joystick_q,))
        joystick_process.start()

    def shutdown(self):
        self.exit.set()
        

      
'''if __name__ == "__main__":
    joystick_q = Queue()
    joystick_q.cancel_join_thread()
    JP = JoystickProcess()
    JP.start(joystick_q)'''
    