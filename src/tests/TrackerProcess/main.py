#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module containing the Tracker class

@authors: Max Sokolich, Brennan Gallamoza, Luke Halko, Trea Holley,
          Alexis Mainiero, Cameron Thacker, Zoe Valladares
"""

import time
from typing import List, Tuple, Union
import numpy as np
import cv2
import matplotlib.pyplot as plt
from tkinter import Tk
from tkinter import *
from RobotClass import Robot
from ContourProcessor import ContourProcessor
from Velocity import Velocity

from FPSCounter import FPSCounter


#import EasyPySpin
import warnings

warnings.filterwarnings("error")
class Tracker:
    """
    Tracker class for tracking microbots. Creates an interactable interface using OpenCV for
    tracking the trajectories of microbots on a video input (either through a live camera
    or a video file).

    Args:
        control_params: dict containing modifiable controller variables in the GUI
        camera_params: dict containing modifiable camera variables in the GUI
        status_params: dict containing modifiable status variables in the GUI
    """

    def __init__(
        self,
        control_params: dict,
        camera_params: dict,
        status_params: dict,
        
    ):
    
        self.start = time.time()
        self.draw_trajectory = False  # determines if trajectory is manually being drawn
        self.robot_list = []  # list of actively tracked robots
        # self.raw_frames = []
        # self.bot_loc = None
        # self.target = None
        self.curr_frame = np.array([])
        self.num_bots = 0  # current number of bots
        self.frame_num = 0  # current frame count
        self.elapsed_time = 0  # time elapsed while tracking
        # self.fps_list = []  # Store the self.fps at the current frame

        self.width = 0  # width of cv2 window
        self.height = 0  # height of cv2 window
        
        #self.pix2metric = 1#((resize_ratio[1]/106.2)  / 100) * self.camera_params["Obj"] 
        
        self.control_params = control_params
        self.camera_params = camera_params
        self.status_params = status_params


        self.cp = ContourProcessor(self.control_params,False)


  

    


    def mouse_points(self, event: int, x: int, y: int, flags, params):
        """
        CV2 mouse callback function. This function is called when the mouse is
        clicked in the cv2 window. A new robot instance is initialized on each
        mouse click.

        Params:
            self: the class itself
            event:  an integer enum in cv2 representing the type of button press
            x:  x-coord of the mouse
            y:  y-coord of the mouse
            flags:  additional callback func args; unused
            params: additional callback func args; unused
        Returns:
            None
        """

        # Left button mouse click event; creates a RobotClass instance
        if event == cv2.EVENT_LBUTTONDOWN:
            # click on bot and create an instance of a mcirorobt
            # CoilOn = False
            bot_loc = [x, y]

            #create upper and lower bounds from point click color
            pixel_color = cv2.cvtColor(params["frame"],cv2.COLOR_BGR2HSV)[y,x]
            print(pixel_color)
            
            #print([x,y])
            '''
            hl = max(min(h_-20,180),0)
            sl = max(min(s_-50,255),0)
            vl = max(min(v_-50,255),0)
            hu = max(min(h_+20,180),0)
            su = max(min(s_+50,255),0)
            vu = max(min(v_+50,255),0)
            self.control_params["lower_thresh"] = np.array([hl,sl,vl])
            self.control_params["upper_thresh"] = np.array([hu,su,vu])
            print(self.control_params["lower_thresh"],self.control_params["upper_thresh"])'''

            #generate original bounding box
            x_1 = int(x - self.control_params["initial_crop"] / 2)
            y_1 = int(y - self.control_params["initial_crop"] / 2)
            w = self.control_params["initial_crop"]
            h = self.control_params["initial_crop"]



            robot = Robot()  # create robot instance
            robot.add_position(bot_loc)  # add position of the robot
            robot.add_crop([x_1, y_1, w, h])
            self.robot_list.append(robot)

            # add starting point of trajectory
            self.robot_list[-1].add_trajectory(bot_loc)
            self.num_bots += 1

        

        # Right mouse click event; allows you to draw the trajectory of the
        # most currently added microbot, so long as the button is held
        elif event == cv2.EVENT_MBUTTONDOWN:
            # draw trajectory
            target = [x, y]
            # create trajectory
            self.robot_list[-1].add_trajectory(target)
            self.draw_trajectory = True  # Target Position

        # Works in conjunction with holding down the right button for drawing
        # the trajectory
        elif event == cv2.EVENT_MOUSEMOVE:
            if self.draw_trajectory:
                target = [x, y]
                self.robot_list[-1].add_trajectory(target)

        # When right click is released, stop drawing trajectory
        elif event == cv2.EVENT_RBUTTONUP:
            self.draw_trajectory = False

        # Middle mouse; CLEAR EVERYTHING AND RESTART ANALYSIS
        elif event == cv2.EVENT_RBUTTONDOWN:
            #reset algorothms i.e. set node back to 0
            
            #other
            self.num_bots = 0
            del self.robot_list[:]
    



    def track_robot_position(
        self,
        avg_area: float,
        bot: Robot,
        cropped_frame: np.ndarray,
        new_pos: Tuple[int, int],
        current_pos: int,
        blur: float,
        max_dim: Tuple[int, int],
        fps: FPSCounter,
        pix_2metric: float
    ):
        """
        Calculate and display circular marker for a bot's position. Uses the bot's positional data,
        average area, cropped frames, and maximum dimensions of its contours to make calculations.

        If contours were found from the previous step, calculate the area of the contours and
        append it to the Robot class. Then, update global average running list of areas.

        Based on the current position calculate above, adjust cropped area dimensions for
        next frame, and finally update Robot class with new cropped dimension, position,
        velocity, and area.

        Args:
            avg_area:   average contour area of bot
            bot:    the Robot class being tracked
            cropped_frame:  cropped frame img containing the microbot
            new_pos:    tuple containing the starting X and Y position of bot
            current_pos:    current position of bot in the form of [x, y]
            max_dim:  tuple with maximum width and height of all contours
            pix_2metric:  (pix/um )conversion factor from pixels to um: depends on rsize scale and objective

        Returns:
            None
        """
        # calcuate and analyze contours areas
        bot.add_area(avg_area)
        avg_global_area = sum(bot.area_list) / len(bot.area_list)
        bot.set_avg_area(avg_global_area)
        # update cropped region based off new position and average area

        x_1, y_1 = new_pos
        max_width, max_height = max_dim
        x_1_new = x_1 + current_pos[0] - max_width
        y_1_new = y_1 + current_pos[1] - max_height
        x_2_new = 2* max_width
        y_2_new = 2* max_height
        new_crop = [int(x_1_new), int(y_1_new), int(x_2_new), int(y_2_new)]
        
       

        # calculate velocity based on last position and self.fps
        #print(pix_2metric)
        if len(bot.position_list) > 0:
            velx = (
                (current_pos[0] + x_1 - bot.position_list[-1][0])
                / (pix_2metric)
                * (fps.get_fps())
            )

            vely = (
                (current_pos[1] + y_1 - bot.position_list[-1][1])
                / (pix_2metric)
                * (fps.get_fps())
                
            )

            velz = 0
            if len(bot.blur_list) > 0:
                velz = (bot.blur_list[-1] - blur)    #This needs to be scaled or something (takes the past 5th blur value to get a rate)
            vel = Velocity(velx, vely, 0)
            bot.add_velocity(vel)
          
        # update robots params
        bot.add_crop(new_crop)
        bot.add_position([current_pos[0] + x_1, current_pos[1] + y_1])
        bot.add_blur(blur)
        bot.add_frame(self.frame_num)
        bot.add_time(round(time.time()-self.start,2))
        

    def detect_robot(self, frame: np.ndarray, fps: FPSCounter, pix_2metric: float):
        """
        For each robot defined through clicking, crop a frame around it based on initial
        left mouse click position, then:
            - apply mask and find contours
            - from contours draw a bounding box around the contours
            - find the centroid of the bounding box and use this as the robots current position

        Args:
            frame: np array representation of the current video frame read in
        Returns:
            None
        """
        for bot in range(len(self.robot_list)):

            # crop the frame based on initial ROI dimensions
            x_1, y_1, x_2, y_2 = self.robot_list[bot].cropped_frame[-1]
            
            max_width = 0  # max width of the contours
            max_height = 0  # max height of the contours

            x_1 = max(min(x_1, self.width), 0)
            y_1 = max(min(y_1, self.height), 0)
         
        
            cropped_frame = frame[y_1 : y_1 + y_2, x_1 : x_1 + x_2]
            
            contours, blur = self.cp.get_contours(cropped_frame, self.control_params)
            
            #blur =1
            #crop_mask = cv2.cvtColor(cropped_frame, cv2.COLOR_BGR2HSV)
            #lower_thresh =  CONTROL_PARAMS["lower_thresh"]#np.array([control_params["lower_thresh"], control_params["lower_thresh"], control_params["lower_thresh"]]) 
            #upper_thresh = CONTROL_PARAMS["upper_thresh"]#np.array([control_params["upper_thresh"],control_params["upper_thresh"],control_params["upper_thresh"]])
            #crop_mask = cv2.inRange(crop_mask, lower_thresh, upper_thresh)
            #contours, _ = cv2.findContours(crop_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
            if len(contours) !=0:
               
                max_cnt = contours[0]
                for contour in contours:
                    # alcualte max_contour
                   
                    if cv2.contourArea(contour) > cv2.contourArea(max_cnt): 
                        max_cnt = contour

                #record area of contour
                area = cv2.contourArea(max_cnt)* (1/pix_2metric**2)
                
                x, y, w, h = cv2.boundingRect(max_cnt)
                current_pos = [(x + x + w) / 2, (y + y + h) / 2]
                # track the maximum width and height of the contours
                if w > max_width:
                    max_width = w*self.control_params["tracking_frame"]
                if h > max_height:
                    max_height = h*self.control_params["tracking_frame"]
                #cv2.rectangle(cropped_frame, (x, y), (x + w, y + h), (255, 0, 0), 1)
                cv2.drawContours(cropped_frame, [max_cnt], -1, (0, 255, 255), 1)

                
                #print(ch,cs,cv)
                
                self.track_robot_position(
                    area,
                    self.robot_list[bot],
                    cropped_frame,
                    (x_1, y_1),
                    current_pos,
                    blur,
                    (max_width, max_height),
                    fps,
                    pix_2metric
                )
        


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
        #cv2.putText(frame,str(int(fps.get_fps())),(int(w / 40),int(h / 30)),cv2.FONT_HERSHEY_COMPLEX,0.5,(255, 255, 255),1,)

        # scale bar
        #cv2.putText(frame,"100 um",(int(w / 40),int(h / 18)),cv2.FONT_HERSHEY_COMPLEX,0.5,(255, 255, 255),1,)
        #cv2.line(frame, (int(w / 40),int(h / 14)),(int(w / 40) + int(100 * (self.pix_2metric)),int(h / 14)), (255, 255, 255), 3)


        

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
                #cv2.polylines(frame, [pts], False, bot_color, 2)
                

                #display target positions
                targets = self.robot_list[bot_id].trajectory
                if len(targets) > 0:
                    pts = np.array(self.robot_list[bot_id].trajectory, np.int32)
                    #cv2.polylines(frame, [pts], False, (1, 1, 255), 2)


                    tar = targets[-1]
                    #cv2.circle(frame,(int(tar[0]), int(tar[1])),4,(bot_color),-1,)

                
                blur = round(self.robot_list[bot_id].blur_list[-1],2) if len(self.robot_list[bot_id].blur_list) > 0 else 0
                dia = round(np.sqrt(4*self.robot_list[bot_id].avg_area/np.pi),1)
                text = "robot {}: {} um | {} blur".format(bot_id+1,dia,blur)
                
                #cv2.putText(frame, "robot {}".format(bot_id+1), (x, y-10), 
                            #cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,0), 1)
                #cv2.putText(frame, "~ {}um".format(dia), (x, y+h+20), 
                            #cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1)
                            
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 1)
                
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
                #cv2.putText(frame,text,(0, 170 + bot_id * 20),cv2.FONT_HERSHEY_COMPLEX,0.5,bot_color,1,)
                
                


    def main(
        self,
        filepath: Union[str, None],
        output_name: str = "",
    ):
        """
        Connect to a camera or video file and perform real time tracking and analysis of microbots
        through a separate OpenCV window

        Args:
            filepath:   filepath to video file to be analyzed

        Returns:
            None
        """
        #create robot window
     
        #self.robot_window.title("Robot Status")


        # Use when using EasyPySpin camera, an FLIR mahcine vision camera python API
        # global self.BFIELD
        
        # Use when reading in a video file
        cam = cv2.VideoCapture(filepath)

        # Get the video input's self.width, self.height, and self.fps
        self.width = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))
     
        cam_fps = cam.get(cv2.CAP_PROP_FPS)
        


        #params = {"arduino": arduino}
        cv2.namedWindow("im")  # name of CV2 window
        #cv2.setMouseCallback("im", self.mouse_points, params)  # set callback func

        # %%
        rec_start_time = None
        result = None
        start = time.time()
        fps_counter = FPSCounter()

        # Continously read and preprocess frames until end of video or error
        # is reached

        
        while True:
            fps_counter.update()
            success, frame = cam.read()
            params = {"frame":frame}
            cv2.setMouseCallback("im", self.mouse_points, params)



            self.curr_frame = frame
            if not success or frame is None:
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

            #calculate pixel to metric for varying res
            #106.2 um = 1024 pixels  @ 50%  resize and 100 x
            self.pix_2metric = ((resize_ratio[1]/106.2)  / 100) * self.camera_params["Obj"] *2 #divide by 2 cuz did scale calc on .5x adapter
            
            self.frame_num += 1  # increment frame

            if self.num_bots > 0:
                # DETECT ROBOTS AND UPDATE TRAJECTORY
                self.detect_robot(frame, fps_counter,self.pix_2metric)

                # APPLY SELECTED CONTROL ALGORITHM
              
                #print(self.robot_list[-1].tracks)

              
            # UPDATE AND DISPLAY HUD ELEMENTS
            self.display_hud(frame, fps_counter)
            
            # add videos a seperate list to save space and write the video afterwords
            if self.status_params["record_status"]:
                output_name = output_name + str(int(time.time()-start))
                if rec_start_time is None:
                    rec_start_time = time.time()

                if result is None:
                    result = cv2.VideoWriter(
                        output_name + ".mp4",
                        cv2.VideoWriter_fourcc(*"mp4v"),
                        30,    
                        resize_ratio,
                        
                    )  #int(fps.get_fps()) False for gray
              
                    

                
                #cv2.putText(frame,"time (s): " + str(np.round(time.time() - rec_start_time, 2)),(int((self.width * resize_scale / 100) * (7 / 10)),
                #        int((self.height * resize_scale / 100) * (9.9 / 10)),),cv2.FONT_HERSHEY_COMPLEX,0.5,(255, 255, 255),1)
                result.write(frame)

            elif result is not None and not self.status_params["record_status"]:
                result.release()
                rec_start_time = None 
                result = None
       

        
   
            cv2.imshow("im", frame)

            
            if filepath is None:
                delay = 1
            else:
                delay = int(((1/self.camera_params["framerate"])  -(1/75) )*1000)
            k = cv2.waitKey(delay)
                
            
            # Exit
       
            if k & 0xFF == ord("q"):
                break
            

        
        cam.release()
        
        cv2.destroyAllWindows()
      


        return self.robot_list
            
      

CONTROL_PARAMS = {
    "lower_thresh": np.array([0,0,0]),  #HSV
    "upper_thresh": np.array([180,255,130]),  #HSV   #130/150 -->black on upper value
    "blur_thresh": 100,
    "initial_crop": 100,       #intial size of "screenshot" cropped frame 
    "tracking_frame": 3,            #cropped frame dimensions mulitplier
    "avg_bot_size": 5,
    "field_strength": 1,
    "rolling_frequency": 10,
    "arrival_thresh": 10,
    "gamma": 90,
    "memory": 15,
}

CAMERA_PARAMS = {
    "resize_scale": 100, 
    "framerate": 1, 
    "exposure": 6000,   #6000
    "Obj": 50}

STATUS_PARAMS = {
    "rolling_status": 0,
    "orient_status": 0,
    "multi_agent_status": 0,
    "PID_status": 0,
    "algorithm_status": False,
    "record_status": True,
}

ACOUSTIC_PARAMS = {
    "acoustic_freq": 0,
    "acoustic_amplitude": 0
}

MAGNETIC_FIELD_PARAMS = {
    "PositiveY": 0,
    "PositiveX": 0,
    "NegativeY": 0,
    "NegativeX": 0,
}


if __name__ == "__main__":
    
    tracker = Tracker(CONTROL_PARAMS,CAMERA_PARAMS,STATUS_PARAMS)
        #self.tracker = tracker

    video_name = "/Users/bizzarohd/Desktop/Vid_7.mp4"

    output_name = "/Users/bizzarohd/Desktop/Vid_7_Annotated.mp4"
    
    

    tracker.main(video_name,output_name)
