"""
Main script for performing microbot tracking

@authors: Max Sokolich, Brennan Gallamoza, Luke Halko, Trea Holley,
          Alexis Mainiero, Cameron Thacker, Zoe Valladares
"""


import time
from tkinter import Tk
import asyncio
from src.python.GUI import GUI
from src.python.ArduinoHandler import ArduinoHandler
from src.python.HallEffect import HallEffect
from multiprocessing import Process, Queue
#arduino signal: [typ, input1, input2, input3]
#typ =1 : spherical ---> Roll 
#typ =2 : cartesian --> Orient
#typ =3 : tweezer --> [+y,+x,-y,-x]

#NOTE: VELZ SET AS 0



PORT = "/dev/ttyACM0"


if __name__ == "__main__":
    #gui window
    window = Tk()
    window.title("Microbot Tracking GUI")

    #arduino
    arduino = ArduinoHandler()
    arduino.connect(PORT)

    #initiate gui window
    gui = GUI(window, arduino)
   
    #start gui mainwindow
    asyncio.run(gui.main())
    #gui.main()
 

 #white [0,0,200]-> [180,255,255]
 #black [0,0,0] -> [180,255,30]
 #hematite [0,0,90] -> [180,25,180] 
 #gfp [35, 100, 100] -> [75, 255, 255]
    
