"""
Main script for performing microbot tracking

@authors: Max Sokolich, Brennan Gallamoza, Luke Halko, Trea Holley,
          Alexis Mainiero, Cameron Thacker, Zoe Valladares
"""
import time
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

    #initiate gui window
    gui = GUI(window, arduino)
   
    #start gui mainwindow
    gui.main()
 

 
    
