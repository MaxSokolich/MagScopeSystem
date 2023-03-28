"""
reads all algoritgms from algorothm folder and assigns each one to the checkbox widget

"""
import numpy as np
from src.python.ArduinoHandler import ArduinoHandler
from src.python.algorithms.Roll_Algorithm import Roll_Algorithm
from src.python.algorithms.Orient_Algorithm import Orient_Algorithm
from src.python.algorithms.MultiAgent_Algorithm import Multi_Agent_Algorithm


class AlgorithmHandler:
    """
    Algorithm class for handleing new algorithms. You can import an algorithm from the 
    algorithm folder or create a new one.

    Instructions on how to create an algorithm:
    1 - use "robot_list" to extract real time data from each of the selected robots
    2 - use "frame" to display certain features about the algorithm. like direction arrow
    3 - use "arduino" to output the proper signals based on the following notation:

                spherical ---> Roll
                        typ = 1
                        input1 = alpha/polar angle
                        input2 = rolling frequency in Hz
                        input3 = gamma/azumethal angle

                        
                cartesian --> Orient
                        typ = 2
                        input1 = Bx
                        input2 = By
                        input3 = Bz

                tweezer --> [+y,+x,-y,-x]
                        typ = 3
                        input1 =  1=up,2=right,3=down,4=left
                        input2 = amplitude
                        input3 = None/0

                zero -->
                        typ = 4
                        input1 = 0
                        input2 = 0
                        input3 = 0


    Args:
        None
    """

    def __init__(self):
        #every time middle mouse button is pressed, it will reinitiate the following classes
        self.Roll_Robot = Roll_Algorithm()
        self.Orient_Robot = Orient_Algorithm()
        self.Multi_Agent_Robot = Multi_Agent_Algorithm()
        

    def run(self, 
            robot_list, 
            control_params, 
            camera_params, 
            status_params, 
            arduino: ArduinoHandler,
            frame: np.ndarray):
        

        if status_params["rolling_status"] == 1:
            self.Roll_Robot.control_trajectory(frame, arduino, robot_list, control_params)
        
        elif status_params["orient_status"] == 1:
            self.Orient_Robot.control_trajectory(frame, arduino, robot_list, control_params)
        
        elif status_params["multi_agent_status"] == 1:
            self.Multi_Agent_Robot.control_trajectory(frame, arduino, robot_list, control_params)

        else: 
            arduino.send(4, 0, 0, 0)
    
        