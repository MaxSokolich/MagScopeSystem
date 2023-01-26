"""
Main script for performing microbot tracking

@authors: Max Sokolich, Brennan Gallamoza, Luke Halko, Trea Holley,
          Alexis Mainiero, Cameron Thacker, Zoe Valladares
"""

from tkinter import Tk
import asyncio
from src.classes.GUI import GUI
from src.classes.ArduinoHandler import ArduinoHandler
from src.classes.HallEffect import HallEffect
from multiprocessing import Process, Queue
#arduino signal: [typ, input1, input2, input3]
#typ =1 : spherical ---> Roll
#typ =2 : cartesian --> Orient

PORT = "/dev/ttyACM0"


if __name__ == "__main__":
    #gui window
    window = Tk()
    window.title("Microbot Tracking GUI")

    #arduino
    arduino = ArduinoHandler()
    arduino.connect(PORT)

    #hall effect
    sensor = HallEffect()

    #initiate Queue to store hall effect sensor variables
    q = Queue()
    q.cancel_join_thread()

    #initiate gui window
    gui = GUI(window, arduino,q)

    #start halleffect process
    p1 = Process(target = sensor.showFIELD, args = (q,))
    p1.start()
   
    #start gui mainwindow
    asyncio.run(gui.main())
    p1.join()
 
    
