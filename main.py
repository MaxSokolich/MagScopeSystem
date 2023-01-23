"""
Main script for performing microbot tracking

@authors: Max Sokolich, Brennan Gallamoza, Luke Halko, Trea Holley,
          Alexis Mainiero, Cameron Thacker, Zoe Valladares
"""

from tkinter import Tk
import asyncio
from src.classes.GUI import GUI
from src.classes.ArduinoHandler import ArduinoHandler

#arduino signal: [typ, input1, input2, input3]
#typ =1 : spherical ---> Roll
#typ =2 : cartesian --> Orient

PORT = "/dev/ttyACM0"

if __name__ == "__main__":
    arduino = ArduinoHandler()
    arduino.connect(PORT)

    window = Tk()
    window.title("Microbot Tracking GUI")
    gui = GUI(window, arduino)
    asyncio.run(gui.main())
 