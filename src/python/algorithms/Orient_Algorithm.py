
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
                if len(bot.velocity_list) % self.control_params["memory"] == 0:
                    # only update every memory frames


                    vx = np.mean(np.array([v.x for v in bot.velocity_list[-self.control_params["memory"]:]]))
                    vy = np.mean(np.array([v.y for v in bot.velocity_list[-self.control_params["memory"]:]]))
                    
                    
                    
                    vel_bot = np.array([vx, vy])  # current velocity of self propelled robot
                    vd = np.linalg.norm(vel_bot)
                    bd = np.linalg.norm(self.B_vec)

                    costheta = np.dot(vel_bot, self.B_vec) / (vd * bd)
                    sintheta = (vel_bot[0] * self.B_vec[1] - vel_bot[1] * self.B_vec[0]) / (vd * bd)
                

                    if not np.isnan(vd):
                        self.T_R = np.array([[costheta, -sintheta], [sintheta, costheta]])

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

            