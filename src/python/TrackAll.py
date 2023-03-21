import cv2
import numpy as np
from collections import deque
import matplotlib.pyplot as plt
import EasyPySpin
from typing import List, Tuple, Union
from tkinter import Tk
from tkinter import *
from src.python.FPSCounter import FPSCounter
from src.python.RobotClass import Robot
from src.python.Velocity import Velocity
from src.python.ContourProcessor import ContourProcessor
import time 

class AllTracker:
    def __init__(
        self,
        main_window: Tk,
        textbox: Tk,
        control_params: dict,
        camera_params: dict,
        status_params: dict,
        use_cuda: bool = False
        
    ):
        self.control_params = control_params
        self.camera_params = camera_params
        self.status_params = status_params

        self.width = 0  # width of cv2 window
        self.height = 0  # height of cv2 window

        self.main_window = main_window
        self.textbox = textbox

        self.num_bots = 0
        self.robot_list = []

        self.cp = ContourProcessor(self.control_params,use_cuda)



    def get_fps(self, fps: FPSCounter, frame: np.ndarray):
        """
        Compute and display average FPS up to this frame

        Args:
            fps: FPSCounter object for updating current fps information
            frame: np array representation of the current video frame read in
            resize_scale:   scaling factor for resizing a GUI element
            pix2_metric = 0.0964 pixels / 1um @ 1x
        Returns:
            None
        """

        # display information to the screen

        w = frame.shape[0]
        h = frame.shape[1]
        
        #fps
        cv2.putText(frame,str(int(fps.get_fps())),
            (int(w / 40),int(h / 30)),
            cv2.FONT_HERSHEY_COMPLEX,
            0.5,
            (255, 0, 0),
            1,
        )

        # scale bar
        cv2.putText(frame,"100 um",
            (int(w / 40),int(h / 18)),
            cv2.FONT_HERSHEY_COMPLEX,
            0.5,
            (255, 0, 0),
            1,
        )
        cv2.line(
            frame, 
            (int(w / 40),int(h / 14)),
            (int(w / 40) + int(100 * (self.pix_2metric)),int(h / 14)), 
            (255, 0, 0), 
            3
        )

    def display_hud(self, frame: np.ndarray,fps: FPSCounter):
        """
        Display dragon tails (bot trajectories) and other HUD graphics

        Args:
            frame: np array representation of the current video frame read in
        Returns:
            None
        """
        self.get_fps(fps, frame)

        if len(self.robot_list) > 0:
            color = plt.cm.rainbow(np.linspace(0, 1, self.num_bots)) * 255
            self.get_fps
            # bot_ids = [i for i in range(self.num_bots)]
            for (
                bot_id,
                bot_color,
            ) in zip(range(self.num_bots), color):

                x = int(self.robot_list[bot_id].cropped_frame[-1][0])
                y = int(self.robot_list[bot_id].cropped_frame[-1][1])
                w = int(self.robot_list[bot_id].cropped_frame[-1][2])
                h = int(self.robot_list[bot_id].cropped_frame[-1][3])

                # display dragon tails
                pts = np.array(self.robot_list[bot_id].position_list, np.int32)
                cv2.polylines(frame, [pts], False, bot_color, 2)
                

                #display target positions
                targets = self.robot_list[bot_id].trajectory
                if len(targets) > 0:
                    pts = np.array(self.robot_list[bot_id].trajectory, np.int32)
                    cv2.polylines(frame, [pts], False, (1, 1, 255), 2)


                    tar = targets[-1]
                    cv2.circle(frame,
                        (int(tar[0]), int(tar[1])),
                        4,
                        (bot_color),
                        -1,
                    )

                
                blur = round(self.robot_list[bot_id].blur_list[-1],2) if len(self.robot_list[bot_id].blur_list) > 0 else 0
                dia = round(np.sqrt(4*self.robot_list[bot_id].avg_area/np.pi),1)
                text = "robot {}: {} um | {} blur".format(bot_id+1,dia,blur)
                
                #cv2.putText(frame, "robot {}".format(bot_id+1), (x, y-10), 
                #            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,0), 1)
                #cv2.putText(frame, "~ {}um".format(dia), (x, y+h+20), 
                #            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1)
                            
                #cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 1)
                
                # if there are more than 10 velocities recorded in the robot, get
                # and display the average velocity
                if len(self.robot_list[bot_id].velocity_list) > 10:
                    # a "velocity" list is in the form of [x, y, magnitude];
                    # get the magnitude of the 10 most recent velocities, find their
                    # average, and display it on the tracker
                    vmag = [v.mag for v in self.robot_list[bot_id].velocity_list[-10:]]
                    vmag_avg = round(sum(vmag) / len(vmag),2)
                    
                    #cv2.putText(frame, f'{vmag_avg:.1f} um/s', (x, y +h + 40), 
                    #        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1)
                    
                    text = "robot {}: {} um | {} um/s | {} blur".format(bot_id+1,dia,vmag_avg,blur)
                
                #cv2.putText(
                #    frame,
                #    text,
                #    (0, 170 + bot_id * 20),
                #    cv2.FONT_HERSHEY_COMPLEX,
                #    0.5,
                #    bot_color,
                #    1,
                #)
                

       
    def main(self,filepath: Union[str, None]):
        
        
        if filepath is None:
            try:
                cam = EasyPySpin.VideoCapture(0)
            except EasyPySpin.EasyPySpinWarning:
                self.textbox.insert(END,"EasyPySpin camera not found, using standard camera\n")
                self.textbox.see("end")
            # cam = cv2.VideoCapture(0)
        else:
            # Use when reading in a video file
            cam = cv2.VideoCapture(filepath)

        self.width = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))


        


        start = time.time()
        fps_counter = FPSCounter()

        frame_count = 0
        cv2.namedWindow("im")  # name of CV2 window
        while True:
            fps_counter.update()
            
            # Read a frame from the camera
            ret, frame = cam.read()
            if not ret:
                break
            
           

            # Set exposure of camera
            cam.set(cv2.CAP_PROP_EXPOSURE, self.camera_params["exposure"])
            cam.set(cv2.CAP_PROP_FPS, self.camera_params["framerate"])
            # resize output based on the chosen ratio
            resize_scale = self.camera_params["resize_scale"]
            resize_ratio = (
                self.width * resize_scale // 100,
                self.height * resize_scale // 100,
            )

            frame = cv2.resize(frame, resize_ratio, interpolation=cv2.INTER_AREA)
        
            self.pix_2metric = ((resize_ratio[1]/106.2)  / 100) * self.camera_params["Obj"] *2

            lower = self.control_params["lower_thresh"]
            upper = self.control_params["upper_thresh"]
            thresh = self.control_params["tracking_frame"]* 10
            
            

            contours, blur = self.cp.get_contours(frame, self.control_params)
            
            for cnt in contours:
                area = cv2.contourArea(cnt)* (1/self.pix_2metric**2)
                dia = round(np.sqrt(4*area/np.pi),1)
                if dia > self.control_params["avg_bot_size"] /2   and   dia < self.control_params["avg_bot_size"] * 2  :
                    cv2.drawContours(frame, [cnt], -1, (0, 255, 255),1)
                    x, y, w, h = cv2.boundingRect(cnt)
                    
                    # Calculate the centroid of the contour
                    centroid_x = x + w // 2
                    centroid_y = y + h // 2
                
                    # Check if the centroid is close to an existing robot
                    found = False
                    for bot in range(len(self.robot_list)):
                        if abs(self.robot_list[bot].position_list[-1][0]- centroid_x) < thresh and abs(self.robot_list[bot].position_list[-1][1] - centroid_y) < thresh:
                            #if its close ad that bots pos
                            self.robot_list[bot].add_position([centroid_x,centroid_y])
                            self.robot_list[bot].add_crop([x,y,w,h])
                            self.robot_list[bot].add_area(area)
                            avg_global_area = sum(self.robot_list[bot].area_list) / len(self.robot_list[bot].area_list)
                            self.robot_list[bot].set_avg_area(avg_global_area)
                            self.robot_list[bot].add_blur(blur)
                            self.robot_list[bot].add_frame(frame_count)

                            if len(self.robot_list[bot].position_list) > 0:
                                velx = (
                                    (centroid_x - self.robot_list[bot].position_list[-2][0])
                                    / (self.pix_2metric)
                                    * (fps_counter.get_fps())
                                )

                                vely = (
                                    (centroid_y  - self.robot_list[bot].position_list[-2][1])
                                    / (self.pix_2metric)
                                    * (fps_counter.get_fps())
                                    
                                )

                                vel = Velocity(velx, vely, 0)
                                self.robot_list[bot].add_velocity(vel)
                            
                            found = True
                            # Append the current position and velocity to the trajectory and velocity lists
                            break
                
                    # If the centroid is not close to any existing robot, add a new robot
                    if not found:
                
                        self.num_bots += 1
                        robot = Robot()
                        robot.add_position([centroid_x,centroid_y])
                        robot.add_crop([x,y,w,h])
                        robot.add_area(area)
                        avg_global_area = sum(robot.area_list) / len(robot.area_list)
                        robot.set_avg_area(avg_global_area)
                        #robot.add_blur(blur)
                        self.robot_list.append(robot)
                  
            self.display_hud(frame, fps_counter)
            
            cv2.imshow('im', frame)
            
            frame_count +=1

            #handle frame rate adjustment
            if filepath is None:
                delay = 1
            else:
                delay = int(((1/self.camera_params["framerate"])-(1/75))*1000)
            k = cv2.waitKey(delay)


            # Exit the loop if the 'q' key is pressed
            self.main_window.update()
            if k & 0xFF == ord('q'):
                break


        cam.release()
        cv2.destroyAllWindows()

        return self.robot_list

       