"""
Module containing the DigitalPot class

@authors: Max Sokolich
"""
import RPi.GPIO as GPIO
import time 


class DigitalPot:
    def __init__(self):
        '''
        Digital Potentiamter Class that enables use of the X9C104 100K Pot Module

        Args:
            None
        '''
        GPIO.setmode(GPIO.BOARD)

        self.CS = 11 #11
        self.UD = 13  #13
        self.INC = 15  #15

        GPIO.setup(self.CS, GPIO.OUT) # C/S
        GPIO.setup(self.UD, GPIO.OUT) # U/D
        GPIO.setup(self.INC, GPIO.OUT) # INC

        GPIO.output(self.CS, GPIO.HIGH)
        GPIO.output(self.INC, GPIO.HIGH)
        GPIO.output(self.UD, GPIO.LOW)
    
    def activate(self):
        GPIO.output(self.CS, GPIO.LOW)
        time.sleep(0.000001)
        print("chip activated")

    def set(self,flag):
        if flag == 1:
            GPIO.output(self.UD, GPIO.HIGH)
        elif flag == 0:
            GPIO.output(self.UD, GPIO.LOW)
        time.sleep(0.000005)
        print("wiper set to ", flag)

    def move(self,flag,step):
        self.set(flag)
        for i in range(step):
            GPIO.output(self.INC, GPIO.LOW)
            time.sleep(0.0001)
            GPIO.output(self.INC, GPIO.HIGH)
            time.sleep(0.0001)
        print("step end")
    
    def reset(self):
        self.move(1, 99)
        self.move(0,99)
        print("reset")

    def exit(self):
        GPIO.output(self.INC, GPIO.HIGH)
        GPIO.output(self.CS, GPIO.HIGH)
        print("exited")

            


'''if __name__ == "__main__":
    P = DigitalPot()
    P.activate()
    for i in range(9):
        P.move(1,i)
        print(i)
        time.sleep(.5)
    for j in reversed(range(9)):
        print(j)
        P.move(0,i)
        time.sleep(.5)

 
    P.reset()
    P.exit()'''
