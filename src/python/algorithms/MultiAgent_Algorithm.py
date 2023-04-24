import numpy as np
import time as time
from src.python.ArduinoHandler import ArduinoHandler
from src.python.RobotClass import Robot
from src.python.Velocity import Velocity




class Multi_Agent_Algorithm:
    def __init__(self):
        #every time middle mouse button is pressed, it will reinitiate this class
        self.robot_list = []
        self.control_params = None
        self.start = time.time()


        self.alpha=None
        
        self.A_MATRIX = []  #matrix list to store velocites at each freqiencu. it contains sublists of the average velocity of each microbot at freqnecy n. 
                            # example for 3 robots and 4 frequencies:   
                            #             [ [robot1_v@freq1, robot2_v@freq1, robot3_v@freq1]
                            #               [robot1_v@freq2, robot2_v@freq2, robot3_v@freq2]
                            #               [robot1_v@freq3, robot2_v@freq3, robot3_v@freq3]
                            #               [robot1_v@freq4, robot2_v@freq4, robot3_v@freq4]
                            #                                                               ]

        self.freq = 1    #initlize the first freq at 1
        self.count = 0   #initilze frame counter at 0
        self.N = 5      #number of frames to calulate velocities at each frequencies
        self.max_freq = 2   #maximum frequency to find velcoities to
        self.step1 = True   # boolean to define when we are in step1 or not (constructing A matrix)

    
    
    def control_trajectory(self, frame, arduino, robot_list, control_params):
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
        if self.step1 == True:
            typ = 1
            input1 = (self.freq*90) *0.017 #angle radians
            input2  = self.freq
            input3 = self.control_params["gamma"] #should be 90
            arduino.send(typ,input1,input2,input3)

            #incremient frame counter
            self.count += 1 
        
            if self.count == self.N:  
                """
                once N frames have passed, create vels list to store the new vels for each robot.
                then, append this list to a global list and increment the frequency.
                """
                print("added velcoites from each bot at {} Hz".format(self.freq))
                vels_list = []
                for bot in range(len(self.robot_list)):
                        bot_vel  = np.array([v.mag for v in self.robot_list[bot].velocity_list[-self.N:]])   # grab the past 50 frames worth instant velcoties
                        bot_vel_avg = round(sum(bot_vel) / len(bot_vel),2)                               # take the avg of these
                        vels_list.append(bot_vel_avg)
            
                self.A_MATRIX.append(vels_list) #add this iterations of velocities to new list
                
                self.freq += 1  #increase frequency and redo
                self.count = 0  #reset frame count for the next iteration of frequencies.
        
            elif self.freq == self.max_freq+1: # stop training after max freq has been achieved
                
                self.step1 = False
                print(self.A_MATRIX, "\n")
                self.freq = 0
                self.alpha = 0


        print([typ, input1, input2, input3])

        #step 2: optimize or choose A_MATRIX PRIME
        """
        A in the form:
        A =  [[v1(f1), v2(f1)], [v1(f2), v2(f2)]] 
        A =  [[v1(f1), vj(f1)], [v1(fi), vj(fi)]] 
        """
        A_PRIME = []
        for i in range(len(self.A_MATRIX)):
            for j in range(len(self.A_MATRIX)):
                ej = self.A_MATRIX[j]
        


        
    
        
        """A_PRIME = [v1(f1), 0, v1(f2), 0, v1(f3), 0; 
                    0   v1(f1), 0, v1(f2), 0, v1(f3); 
                   v2(f1), 0, v2(f2), 0, v2(f3), 0; 
                    0   v2(f1), 0, v2(f2), 0, v2(f3);
                   v3(f1), 0, v3(f2), 0, v3(f3), 0; 
                    0   v3(f1), 0, v3(f2), 0, v3(f3)]"""
        
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




"""

import sys
p = "/Users/bizzarohd/Desktop/MagScopeSystem/src/python"
sys.path.insert(1, p)

from Velocity import Velocity
from ArduinoHandler import ArduinoHandler
from typing import List, Tuple, Union


class Robot:
    def __init__(self):
        self.velocity_list = []  # stores bot velocities per frame

    def add_velocity(self, velocity: Velocity):
        self.velocity_list.append(velocity)





if __name__ == "__main__":

    control_params = {
        "lower_thresh": np.array([0,0,0]),  #HSV
        "upper_thresh": np.array([180,255,95]),  #HSV
        "blur_thresh": 100,
        "initial_crop": 100,       #intial size of "screenshot" cropped frame 
        "tracking_frame": 1,            #cropped frame dimensions mulitplier
        "avg_bot_size": 5,
        "field_strength": 1,
        "rolling_frequency": 10,
        "arrival_thresh": 10,
        "gamma": 90,
        "memory": 15,
        "PID_params": None,
    }



    Multi_Agent_Robot = Multi_Agent_Algorithm()
    arduino = ArduinoHandler()    
    arduino.connect("/dev/ttyACM0")

    frame = 0
    robot_list = []

    robot1 = Robot()
    robot2 = Robot()

    robot_list.append(robot1)
    robot_list.append(robot2)
    while True: #simulate 200 frames

        #update each robot with random velocity
        for i in range(len(robot_list)):
            bot = robot_list[i]
            velx = np.random.randint(5)
            vely = np.random.randint(5)
            vel = Velocity(velx, vely, 0)
            bot.add_velocity(vel)


        Multi_Agent_Robot.control_trajectory(frame, arduino, robot_list, control_params)
        
        frame+=1

        time.sleep(1)"""