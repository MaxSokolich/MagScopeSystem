import numpy as np
import time as time
from src.python.ArduinoHandler import ArduinoHandler


class Multi_Agent_Algorithm:
    def __init__(self):
        #every time middle mouse button is pressed, it will reinitiate this classe
        self.node = 0
        self.robot_list = []
        self.control_params = None
        self.start = time.time()

        self.frequencies = [1,10,30]
        self.alpha=None
    
    def control_trajectory(self, frame: np.ndarray, arduino: ArduinoHandler, robot_list, control_params):
        """_
        apply mutli agent algorithm from paper. 
        The idea is you click on a robot with left mouse button. 
        Then you click on a goal position with right mouse button.

        This function will be applied every time a frame is read. so each robots positions are 
        updated continously in the custom tracker while loop.

        execution tree:
                    Custom2DTracker.main()  --->  AlgorithmHandler.run()  --->  Multi_Agent_Algorithm.control_trajectory()
        Args:
            None
        Returns:
            action commands to be sent to arduino. these will be typ 1 commands

            step1: loop through freqencies 1-20 (5 seconds for each) and calculate speeds for each frequency
            step2: choose 3 frequencies (2,10,28 say). construct matrix A
            step3: apply algorithm / find t vector
        """
        self.robot_list = robot_list
        self.control_params = control_params

        #step1
        
        for i in range(1,20):
            
            typ = 1
            input1 = 0 #alpha angle
            input2 = i #rolling frequency
            input3 = self.control_params["gamma"] #should be 90

            robot1_pos0 = self.robot_list.position_list[0]
            robot2_pos0 = self.robot_list.position_list[1]
            robot3_pos0 = self.robot_list.position_list[2]
        
            arduino.send(typ,input1,input2,input3)

            velocity = 0
            time.sleep(5) 

            robot1_pos1 = self.robot_list.position_list[0]
            robot2_pos1 = self.robot_list.position_list[1]
            robot3_pos1 = self.robot_list.position_list[2]

            
           


        current_positions = []  #create a list of every selected bots current position
        goal_positions = []     #create a list of every selected bots goal position
        for bot in range(len(self.robot_list)):
            pos = self.robot_list[bot].position_list[-1]
            goal= self.robot_list[bot].trajectory[-1]

            current_positions.append(pos)
            goal_positions.append(goal)

    
        #generate the action
        for f in self.frequencies:
            t1 = -1 * np.sum((np.array([position[0] for position in current_positions]) - np.array([position[0] for position in goal_positions])) *np.array(f))
            t2 = -1 * np.sum((np.array([position[1] for position in current_positions]) - np.array([position[1] for position in goal_positions])) *np.array(f))
            
            norm_f = np.linalg.norm(f)
            t1 /= (norm_f **2)
            t1 /= (norm_f **2)


            self.alpha = np.arctan2(t2,t1)
            application_time = np.sqrt(t1**2+t2**2)  #best way to apply?
            frequency = f        
           
            #apply the action 
            typ = 1
            input1 = self.alpha
            input2 = self.control_params["rolling_frequency"]
            input3 = self.control_params["gamma"] #should be 90
        
            arduino.send(typ,input1,input2,input3)
