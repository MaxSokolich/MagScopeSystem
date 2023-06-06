from queue import Empty
from ControllerClass import Controller
from ArduinoHandler import ArduinoHandler
from MotorStageClass import MotorStage

from multiprocessing import Process, Queue, Event
#from src.python.AcousticClass import AcousticClass
import time



class MyController(Controller):

    def __init__(self, **kwargs):
        Controller.__init__(self, **kwargs)


if __name__ == "__main__":
    #create instance of motor stage class
    stage = MotorStage()

    #create instance and connect to arduino module
    PORT = "/dev/ttyACM0"
    arduino = ArduinoHandler()
    arduino.connect(PORT)
    
    #create queue to handle joystick commands
    joystick_q = Queue(1)
    controller = MyController(joystick_q=joystick_q,interface="/dev/input/js0", connecting_using_ds4drv=False)
    
    joystick_process = Process(target = controller.listen, args = (joystick_q,))
    joystick_process.start()

    while True:
        try:
            actions = joystick_q.get(0)
            if actions == False:
                break
            else:
                arduino.send(actions)
        except Empty:
            pass
 

    joystick_process.join()
    stage.stop()


