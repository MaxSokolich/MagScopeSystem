
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

        self.acoustic_status = 0

        #exit event
        self.exit = Event()        

    def handle_joystick(self, joystick_q):
        while not self.exit.is_set():
            # A Button --> Acoustic Module Toggle
            self.acoustic_status = self.joy.A()

            #Left Joystick Function --> Orient
            if not self.joy.leftX() == 0 or not self.joy.leftY() == 0:
                Bxl = round(self.joy.leftX(),2)
                Byl = round(self.joy.leftY(),2)
                self.typ = 2
                self.input1 = Bxl
                self.input2 = Byl
                
            
            #Right Joystick Function --> Roll
            elif not self.joy.rightX() == 0 or not self.joy.rightY() == 0:
                Bxr = round(self.joy.rightX(),2)
                Byr = round(self.joy.rightY(),2)
                    
                angle = np.arctan2(Byr,Bxr)
                self.typ = 1
                self.input1 = angle
               
            
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
            
            #update queue
            actions = [self.typ,self.input1, self.input2, self.input3, self.acoustic_status]
            joystick_q.put(actions)
            time.sleep(50/1000)  #need some sort of delay to not flood queue
        
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
    