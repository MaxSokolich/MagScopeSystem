import numpy as np
import time as time
from src.python.ArduinoHandler import ArduinoHandler


class Multi_Agent_Algorithm:
    def __init__(self):
        #every time middle mouse button is pressed, it will reinitiate this class
        self.robot_list = []
        self.control_params = None
        self.start = time.time()


        self.alpha=None
        
        self.A_MATRIX = []

        self.freq = 1    #initlize the first freq at 1
        self.count = 0   #initilze frame counter at 0
        self.N = 50      #number of frames to calulate velocities at each frequencies

    
    
    def control_trajectory(self, frame: np.ndarray, arduino: ArduinoHandler, robot_list, control_params):
        """
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
        """
        self.robot_list = robot_list
        self.control_params = control_params


        #step1: loop through frequencies and get velocities at each frequency
        #apply output action
        typ = 1
        input1 = 0
        input2  = self.freq
        input3 = self.control_params["gamma"] #should be 90
        arduino.send(typ,input1,input2,input3)

        #incremient frame counter
        self.count += 1 
        
        
        if self.count == self.N:  
            print(self.count)
            """
            once N frames have passed, create vels list to store the new vels for each robot.
            then, append this list to a global list and increment the frequency.
            """
            vels_list = []
            for bot in range(len(self.robot_list)):
                
                    bot_vel  = np.array([v.mag for v in self.robot_list[bot].velocity_list[-self.N:]])   # grab the past 50 frames worth instant velcoties
                    bot_vel_avg = round(sum(bot_vel) / len(bot_vel),2)                               # take the avg of these

                    vels_list = bot_vel_avg
            
            self.A_MATRIX.append(vels_list) #add this iterations of velocities to new list
            
            self.freq += 1  #increase frequency and redo
            self.count = 0  #reset frame count for the next iteration of frequencies.


        
        #step 2: optimize or choose A_MATRIX PRIME

        #setp 3: find t (below...)

        '''
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
        
            arduino.send(typ,input1,input2,input3)'''
