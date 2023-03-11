"""
Module containing the DigitalPot class

@authors: Max Sokolich
"""
import RPi.GPIO as GPIO
import time 
GPIO.setmode(GPIO.BOARD)

class DigitalPot:
    def __init__(self):
        '''
        Digital Potentiamter Class that enables use of the X9C104 100K Pot Module

        Args:
            None
        '''
        
        self.CS = 11 #11
        self.UD = 13  #13
        self.INC = 15  #15

        GPIO.setup(self.CS, GPIO.OUT) # C/S
        GPIO.setup(self.UD, GPIO.OUT) # U/D
        GPIO.setup(self.INC, GPIO.OUT) # INC

        GPIO.output(self.CS, GPIO.HIGH)
        GPIO.output(self.INC, GPIO.HIGH)
        GPIO.output(self.UD, GPIO.LOW)

        #keep track of total amplitude
        self.count = 0 
    
    def activate(self):
        GPIO.output(self.CS, GPIO.LOW)
        time.sleep(0.000001)

    def set(self,flag):
        """
        sets the direction of increment: 
        1: inrease
        2: decrease
        """
        if flag == 1:
            GPIO.output(self.UD, GPIO.HIGH)
        elif flag == 0:
            GPIO.output(self.UD, GPIO.LOW)
        time.sleep(0.000005)

    def move(self,flag,step):
        """
        outputs the correct signals to either increase or decrease the module
        """
        self.set(flag)
        for i in range(step):
            GPIO.output(self.INC, GPIO.LOW)
            time.sleep(0.0001)
            GPIO.output(self.INC, GPIO.HIGH)
            time.sleep(0.000002)

    def apply(self, amplitude):
        """
        directly sets the resitance value 0-30
        """
        if amplitude >= self.count:
            actual_amp = amplitude - self.count
            self.move(1,actual_amp)
            self.count = amplitude
        elif amplitude < self.count:
            actual_amp = self.count - amplitude
            self.move(0, actual_amp)
            self.count = amplitude
    
    def reset(self):
        """
        Resets DP to zero 
        """
        self.move(1, 99)
        self.move(0,99)

    def exit(self):
        """
        deactivates the DP
        """
        GPIO.output(self.INC, GPIO.HIGH)
        GPIO.output(self.CS, GPIO.HIGH)
        GPIO.cleanup()
        

"""
max step = 30
we want a reading from 0 V to voltage maximum
~0 Volts is max on resistance

map(low_resistance, high resistance, high voltage, low voltage)
"""

if __name__ == "__main__":

    P = DigitalPot()
    P.activate()
    for i in range(30):
        print(i)
        P.apply(i)
        time.sleep(.1)
    for i in reversed(range(30)):
        print(i)
        P.apply(i)
        time.sleep(.1)

    P.reset()
    P.exit()
