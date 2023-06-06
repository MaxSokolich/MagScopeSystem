import board
from adafruit_motorkit import MotorKit

import time


class MotorStage:
    def __init__(self):
        #green   =   motor1   = X
        #yellow  =   motor2   = Y
        #blue    =   motor3   = Z
        self.kit = MotorKit(i2c=board.I2C())
    
    def MoveX(self, direction):
        self.kit.motor1.throttle = direction
    
        
    def MoveY(self, direction):
        self.kit.motor3.throttle = direction
 
    
    def MoveZ(self, direction):
        self.kit.motor2.throttle = direction


    def stop(self):
        self.kit.motor1.throttle = 0
        self.kit.motor2.throttle = 0
        self.kit.motor3.throttle = 0


"""if __name__ == "__main__":
    stage = MotorStage()
    def on(stage):
        
        stage.stop()
        x = 0
        while x < 100:
            time.sleep(20/1000)
            stage.MoveX(1)
            stage.MoveY(1)
            stage.MoveZ(1)
            #if x % 50==0:
            #    print("startinggggggggggggggggggggggggggg")
            #    time.sleep(50/1000)
            #    print("startinggggggggggggggggggggggggggg")
            #    stage.MoveX(-1)
            #    stage.MoveY(-1)
            #    stage.MoveZ(-1)
            #    print("Backkkkkkkkkkkkkkkkkkkkkkkkkkkkk")
            
            time.sleep(1000/1000)
            #time.sleep(5)
            stage.MoveX(-1)
            stage.MoveY(-1)
            stage.MoveZ(-1)
            #time.sleep(5)
            print(x)
            x+=1
        stage.stop()

    def off(stage):
        stage.stop()

    #on(stage)
    off(stage)"""