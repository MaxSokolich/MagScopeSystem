#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#I changed the code so that instead of re-calculating the mapped angle, it saves all of them and takes an average. This
#should allow for a lower memory to be used while not having to worry as much about noise. Also it means that it can 
#update the magnetic field angle on every frame, once it initially captures memory number of frames, so it should be more
#responsive. 
import cv2
import numpy as np
import time
from src.python.ArduinoHandler import ArduinoHandler

class Orient_Algorithm:
    def __init__(self):
        #every time middle mouse button is pressed, it will reinitiate this classe
        self.node = 0
        self.robot_list = []
        self.control_params = None
        self.start = time.time()

        self.B_vec = np.array([1,0])
        self.T_R = 1
        
#         self.costheta_maps = np.array([])#added this so that we store the mapped angles
#         self.sintheta_maps = np.array([])#added this so that we store the mapped angles
         self.theta_maps = np.array([])#added this so that we store the mapped angles


    def control_trajectory(self, frame: np.ndarray, arduino: ArduinoHandler, robot_list, control_params):
        """
        Used for real time closed loop feedback on the jetson nano to steer a microrobot along a
        desired trajctory created with the right mouse button. Does so by:
            -defining a target position
            -displaying the target position
            -if a target position is defined, look at most recently clicked bot and display its trajectory

        In summary, moves the robot to each node in the trajectory array.
        If the error is less than a certain amount, move on to the next node

        Args:
            frame: np array representation of the current video frame read in
            start: start time of the tracking
        Return:
            None
        """
        self.robot_list = robot_list
        self.control_params = control_params

        if len(self.robot_list[-1].trajectory) > 1:
            #logic for arrival condition
            if self.node == len(self.robot_list[-1].trajectory):
                typ = 4
                input1 = 0
                input2 = 0
                input3 = 0
                print("arrived")


            #closed loop algorithm 
            else:
                #define target coordinate
                targetx = self.robot_list[-1].trajectory[self.node][0]
                targety = self.robot_list[-1].trajectory[self.node][1]

                #define robots current position
                robotx = self.robot_list[-1].position_list[-1][0]
                roboty = self.robot_list[-1].position_list[-1][1]
                
                #calculate error between node and robot
                direction_vec = [targetx - robotx, targety - roboty]
                error = np.sqrt(direction_vec[0] ** 2 + direction_vec[1] ** 2)
                self.alpha = np.arctan2(-direction_vec[1], direction_vec[0])


                #draw error arrow
                cv2.arrowedLine(
                    frame,
                    (int(robotx), int(roboty)),
                    (int(targetx), int(targety)),
                    [0, 0, 0],
                    3,
                )
                if error < 10:
                    self.node += 1

    
                # OUTPUT SIGNAL
                bot = self.robot_list[-1]
                if len(bot.velocity_list) >= self.control_params["memory"]:
                    
                    #find the velocity avearge over the last memory number of frames to mitigate noise: 
                    vx = np.mean(np.array([v.x for v in bot.velocity_list[-self.control_params["memory"]:]]))
                    vy = np.mean(np.array([v.y for v in bot.velocity_list[-self.control_params["memory"]:]]))
                    
                    vel_bot = np.array([vx, vy])  # current velocity of self propelled robot
                    vd = np.linalg.norm(vel_bot)
                    bd = np.linalg.norm(self.B_vec)

                    costheta = np.dot(vel_bot, self.B_vec) / (vd * bd)
                    sintheta = (vel_bot[0] * self.B_vec[1] - vel_bot[1] * self.B_vec[0]) / (vd * bd)
                    theta = np.arctan2(sintheta,costheta)
                

                    if not np.isnan(vd):
                        #this takes the average of cosine and sine, but I changed it to just average theta since that might make more sense
#                         np.append(self.costheta_maps,costheta)
#                         np.append(self.sintheta_maps,sintheta)
            
#                         costhetaNew = np.median(self.costheta_maps)#take the average, or median, so that the mapped angle is robust to noise
#                         sinthetaNew = np.median(self.sintheta_maps)
#                         normFactor = costhetaNew**2 + sinthetaNew**2
#                         costhetaNew = costhetaNew/normFactor
#                         sinthetaNew = sinthetaNew/normFactor #this makes sure that the sin**2+cos**2 = 1 while not changing the angle itself

                        np.append(self.theta_maps,theta)
                        if len(self.theta_maps) > 150:
                            self.theta_maps = self.theta_maps[-150:len(theta_maps)]#this makes sure that we only look at the latest 150 frames of data to keep it adaptable. It should be bigger if there's a lot of noise (slow bot) and smaller if its traj is well defined (fast bot) 
                        thetaNew = np.median(self.theta_maps)#take the average, or median, so that the mapped angle is robust to noise                        
                        self.T_R = np.array([[np.cos(thetaNew), -np.sin(thetaNew)], [np.sin(thetaNew), np.cos(thetaNew)]])
                     
                        #self.T_R = np.array([[costhetaNew, -sinthetaNew], [sinthetaNew, costhetaNew]])

                self.B_vec = np.dot(self.T_R, direction_vec)

                #OUTPUT SIGNAL      
                
                Bx = self.B_vec[0] / np.sqrt(self.B_vec[0] ** 2 + self.B_vec[1] ** 2)
                By = self.B_vec[1] / np.sqrt(self.B_vec[0] ** 2 + self.B_vec[1] ** 2)
                Bz = 0
                self.alpha = np.arctan2(By, Bx)
                
                typ = 2
                input1 = Bx
                input2 = By
                input3 = Bz
                try:
                    start_arrow = (100, 150 + (self.num_bots - 1) * 20)
                    end_arrow = (
                        int(start_arrow[0] + Bx * 15),
                        int(start_arrow[1] + By * 15),
                    )
                    cv2.arrowedLine(
                        frame, start_arrow, end_arrow, [255, 255, 255], 2
                    )
                except:
                    pass
                
                self.robot_list[-1].add_track(
                error,
                [robotx, roboty],
                [targetx, targety],
                self.alpha,
                self.control_params["rolling_frequency"],
                time.time()-self.start,
                "Orient",
            )
            print([typ,input1,input2,input3])
            arduino.send(typ,input1,input2,input3)

            


# In[ ]:


# This might be even better: use the above algorithm to initially set the angle each time a new node is set,
#then use the PID to make fine adjustments after that. You'll need to allow it to keep saving the mapped angles
#though even while the PID part is running. We could write that all as one code but first we should test each one
#first to make sure they're working

