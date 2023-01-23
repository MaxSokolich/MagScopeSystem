#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module containing the Tracker class

@authors: Max Sokolich, Brennan Gallamoza, Luke Halko, Trea Holley,
          Alexis Mainiero, Cameron Thacker, Zoe Valladares
"""

import time
from typing import List, Tuple, Union
import pickle
import numpy as np
import cv2
import matplotlib.pyplot as plt
from tqdm import tqdm
from tkinter import Tk

from src.classes.RobotClass import Robot
from src.classes.ContourProcessor import ContourProcessor
from src.classes.Velocity import Velocity
from src.classes.ArduinoHandler import ArduinoHandler
from src.classes.FPSCounter import FPSCounter

import EasyPySpin
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
        use_cuda: bool = False,
    ):
        self.alpha = 1000

        self.draw_trajectory = False  # determines if trajectory is manually being drawn
        self.robot_list = []  # list of actively tracked robots
        # self.raw_frames = []
        # self.bot_loc = None
        # self.target = None
        self.curr_frame = np.array([])
        self.node = None  # index of node having their trajectory manually influenced
        self.num_bots = 0  # current number of bots
        self.frame_num = 0  # current frame count
        self.elapsed_time = 0  # time elapsed while tracking
        self.prev_frame_time = 0  # prev frame time, used for self.fps calcs
        self.new_frame_time = 0  # time of newest frame, used for self.fps calcs
        # self.fps_list = []  # Store the self.fps at the current frame
        self.pix_2metric = 3.45/camera_params["Obj"]  # pix/micron ratio #NEEDS FIXING
        self.width = 0  # width of cv2 window
        self.height = 0  # height of cv2 window

        self.control_params = control_params
        self.camera_params = camera_params
        self.status_params = status_params

        self.cp = ContourProcessor(self.control_params,use_cuda)

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
        

            x_1 = int(x - self.control_params["bounding_length"] / 2)
            y_1 = int(y - self.control_params["bounding_length"] / 2)
            w = self.control_params["bounding_length"]
            h = self.control_params["bounding_length"]



            robot = Robot()  # create robot instance
            robot.add_position(bot_loc)  # add position of the robot
            robot.add_crop([x_1, y_1, w, h])
            robot.add_blur(
                self.cp.calculate_blur(self.curr_frame[y_1 : y_1 + h, x_1 : x_1 + w])
            )
            self.robot_list.append(robot)

            # add starting point of trajectory
            self.node = 0
            self.robot_list[-1].add_trajectory(bot_loc)
            self.num_bots += 1

        # Right mouse click event; allows you to draw the trajectory of the
        # most currently added microbot, so long as the button is held
        elif event == cv2.EVENT_RBUTTONDOWN:
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
        elif event == cv2.EVENT_MBUTTONDOWN:
            del self.robot_list[:]
            self.num_bots = 0
            self.node = 0
            if params["arduino"].conn is not None:
                params["arduino"].send(4, 0, 0, 0)

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
        x_2_new = 2 * max_width
        y_2_new = 2 * max_height
        new_crop = [int(x_1_new), int(y_1_new), int(x_2_new), int(y_2_new)]

        # calculate velocity based on last position and self.fps
        if len(bot.position_list) > 5:
            velx = (
                (current_pos[0] + x_1 - bot.position_list[-1][0])
                * fps.get_fps()
                * (self.pix_2metric)
            )
            vely = (
                (current_pos[1] + y_1 - bot.position_list[-1][1])
                * fps.get_fps()
                * (self.pix_2metric)
            )
            velz = 0
            
            if len(bot.blur_list) > 0:
                velz = (bot.blur_list[-4] - blur)    #This needs to be scaled or something
            vel = Velocity(velx, vely, velz)
            bot.add_velocity(vel)
          
        # update robots params
        bot.add_crop(new_crop)
        bot.add_position([current_pos[0] + x_1, current_pos[1] + y_1])
        bot.add_frame(self.frame_num)

        # display
        cv2.circle(
            cropped_frame,
            (int(current_pos[0]), int(current_pos[1])),
            2,
            (1, 255, 1),
            -1,
        )

    def detect_robot(self, frame: np.ndarray, fps: FPSCounter):
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
        for bot in self.robot_list:

            # crop the frame based on initial ROI dimensions
            x_1, y_1, x_2, y_2 = bot.cropped_frame[-1]
            area_threshold = bot.avg_area / 20
            area_list = []  # store areas of microbots
            avg_area = None
            max_width = 0  # max width of the contours
            max_height = 0  # max height of the contours

            x_1 = max(min(x_1, self.width), 0)
            y_1 = max(min(y_1, self.height), 0)
         
        
            cropped_frame = frame[y_1 : y_1 + y_2, x_1 : x_1 + x_2]
            
            contours, blur = self.cp.get_contours(cropped_frame,self.control_params)
            bot.add_blur(blur)

            for contour in contours:
                # remove small elements by calcualting arrea
                area = cv2.contourArea(contour)

                if area > area_threshold:  # and area < 3000:# and area < 2000: #pixels
                    area_list.append(area)


                    #TRY USING CV2.MOMENTS TO FIND X,Y CENTROID
                    #M = cv2.moments(contour)
                    #cx = int(M["m10"] / M["m00"])
                    #cy = int(M["m01"] / M["m00"])
                    #current_pos = [cx,cy]
                    x, y, w, h = cv2.boundingRect(contour)
                    current_pos = [(x + x + w) / 2, (y + y + h) / 2]

                    # track the maximum width and height of the contours
                    if w > max_width:
                        max_width = w
                    if h > max_height:
                        max_height = h

                    #cv2.rectangle(cropped_frame, (x, y), (x + w, y + h), (255, 0, 0), 1)
                    # -1: draw all
                    cv2.drawContours(cropped_frame, [contour], -1, (0, 255, 255), 1)

            # interesting condition for when a robot splits
            if len(area_list) > 1:
                pass
                # print("bot split")

            # TRACK AND UPDATE ROBOT
            # %%
            if area_list:
                avg_area = sum(area_list) / len(area_list)  # record average area
                self.track_robot_position(
                    avg_area,
                    bot,
                    cropped_frame,
                    (x_1, y_1),
                    current_pos,
                    blur,
                    (max_width, max_height),
                    fps,
                )
            # else:
            #     pass
            # if when i click there is no detected area: delete the most recent robot instance

            # del self.robot_list[-1]
            # self.num_bots -=1
            # i also want to recent everything and clear the screen
    
    
    


    def control_trajectory(
        self, frame: np.ndarray, start: float, arduino: ArduinoHandler
    ):
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
        if len(self.robot_list[-1].trajectory) > 1:
            if self.node == len(self.robot_list[-1].trajectory):
                self.alpha = 1000  # can be any number not 0 - 2pi. indicates stop outpting current
                # define first node in traj array
                # define first node in traj array
                targetx = self.robot_list[-1].trajectory[-1][0]
                targety = self.robot_list[-1].trajectory[-1][1]

                # calcualte bots position
                # choose the last bot that was pressed for now
                robotx = self.robot_list[-1].position_list[-1][0]
                roboty = self.robot_list[-1].position_list[-1][1]

                error = np.sqrt((targetx - robotx) ** 2 + (targety - roboty) ** 2)
                print("arrived")
                unique_control_param = None
                if arduino.conn is not None:
                    arduino.send(4, 0, 0, 0)
            else:
                # non-linear closed loop
                # display trajectory
                # initialize a B_vec for orientation algorithm, not really used,
                # just needs to be defined for algorithm to work
                B_vec = np.array([1, 0])

                pts = np.array(self.robot_list[-1].trajectory, np.int32)
                cv2.polylines(frame, [pts], False, (1, 1, 255), 1)

                # define first node in traj array
                targetx = self.robot_list[-1].trajectory[self.node][0]
                targety = self.robot_list[-1].trajectory[self.node][1]

                # calcualte bots position
                # choose the last bot that was pressed for now
                robotx = self.robot_list[-1].position_list[-1][0]
                roboty = self.robot_list[-1].position_list[-1][1]

                # calcualte error
                cv2.arrowedLine(
                    frame,
                    (int(robotx), int(roboty)),
                    (int(targetx), int(targety)),
                    [0, 0, 0],
                    3,
                )
                error = np.sqrt((targetx - robotx) ** 2 + (targety - roboty) ** 2)

                if error < 20:
                    targetx = self.robot_list[-1].trajectory[self.node][0]
                    targety = self.robot_list[-1].trajectory[self.node][1]
                    direction_vec = [targetx - robotx, targety - roboty]
                    self.alpha = np.arctan2(direction_vec[1], direction_vec[0])

                    self.node += 1

                else:
                    direction_vec = [targetx - robotx, targety - roboty]
                    self.alpha = np.arctan2(direction_vec[1], direction_vec[0])

                # now update params and output to coils if True
                if (
                    self.status_params["rolling_status"]
                    and not self.status_params["orient_status"]
                ):
                    typ = 1
                    my_alpha = self.alpha - np.pi / 2
                    if arduino.conn is not None:
                        input1 = my_alpha
                        input2 = self.control_params["rolling_frequency"]
                        input3 = 90 #gamma
                        arduino.send(
                            typ,input1,input2,input3
                        )
                    unique_control_param = "Roll"

                elif (
                    self.status_params["orient_status"]
                    and not self.status_params["rolling_status"]
                    and self.robot_list[-1] > self.control_params["memory"] - 1
                ):
                    bot = self.robot_list[-1]
                    if len(bot.velocity_list) % self.control_params["memory"] == 0:
                        # only update every memory frames

                        vx = np.mean(
                            np.array(
                                bot.velocity_list[-self.control_params["memory"] :]
                            )[:, 0]
                        )  # taking the previous 10 velocities and avg to reduce noise
                        vy = np.mean(
                            np.array(
                                bot.velocity_list[-self.control_params["memory"] :]
                            )[:, 1]
                        )
                        vel_bot = np.array(
                            [vx, vy]
                        )  # current velocity of self propelled robot

                        vd = np.linalg.norm(vel_bot)
                        bd = np.linalg.norm(B_vec)

                        costheta = np.dot(vel_bot, B_vec) / (vd * bd)
                        sintheta = (vel_bot[0] * B_vec[1] - vel_bot[1] * B_vec[0]) / (
                            vd * bd
                        )
                      

                        if not np.isnan(vd):
                            # Text_Box.insert(tk.END, str(round(B_vec*180/np.pi,3))+"\n")
                            # Text_Box.see("end")

                            T_R = np.array(
                                [[costheta, -sintheta], [sintheta, costheta]]
                            )

                            B_vec = np.dot(T_R, direction_vec)

                            Bx = B_vec[0] / np.sqrt(B_vec[0] ** 2 + B_vec[1] ** 2)
                            By = B_vec[1] / np.sqrt(B_vec[0] ** 2 + B_vec[1] ** 2)
                            Bz = 0
                            # OUTPUT

                            self.alpha = np.arctan2(By, Bx)
                            typ = 2
                            if arduino.conn is not None:
                                input1 = Bx
                                input2 = By
                                input3 = Bz
                                arduino.send(
                                    typ,input1,input2,input3
                                )
                    unique_control_param = "Orient"

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
                else:
                    unique_control_param = None
                    if arduino.conn is not None:
                        arduino.send(4, 0, 0, 0)

            self.robot_list[-1].add_track(
                self.frame_num,
                error,
                [robotx, roboty],
                [targetx, targety],
                self.alpha,
                self.control_params["rolling_frequency"],
                time.time(),
                unique_control_param,
            )

    def get_fps(self, fps: FPSCounter, frame: np.ndarray, resize_scale: int):
        """
        Compute and display average FPS up to this frame

        Args:
            fps: FPSCounter object for updating current fps information
            frame: np array representation of the current video frame read in
            resize_scale:   scaling factor for resizing a GUI element
        Returns:
            None
        """

        # display information to the screen
        cv2.putText(
            frame,
            str(int(fps.get_fps())),
            (
                int((self.width * resize_scale / 100) / 40),
                int((self.height * resize_scale / 100) / 30),
            ),
            cv2.FONT_HERSHEY_COMPLEX,
            0.5,
            (0, 255, 0),
            1,
        )

        # scale bar
        cv2.line(
            frame, (75, 80), (int(100 * (1 / self.pix_2metric)), 80), (0, 0, 255), 3
        )

    def display_hud(self, frame: np.ndarray):
        """
        Display dragon tails (bot trajectories) and other HUD graphics

        Args:
            frame: np array representation of the current video frame read in
        Returns:
            None
        """
        #convert from gray to color
       
        color = plt.cm.rainbow(np.linspace(0, 1, self.num_bots)) * 255
        # bot_ids = [i for i in range(self.num_bots)]
        for (
            bot_id,
            bot_color,
        ) in zip(range(self.num_bots), color):

            # display dragon tails
            pts = np.array(self.robot_list[bot_id].position_list, np.int32)
            cv2.polylines(frame, [pts], False, bot_color, 1)

            # if there are more than 10 velocities recorded in the robot, get
            # and display the average velocity
            if len(self.robot_list[bot_id].velocity_list) > 10:
                # a "velocity" list is in the form of [x, y, magnitude];
                # get the magnitude of the 10 most recent velocities, find their
                # average, and display it on the tracker
                bot = self.robot_list[bot_id]
                vmag = [v.mag for v in bot.velocity_list[-10:]]
                vmag_avg = sum(vmag) / len(vmag)

                # blur = bot.blur_list[-1] if len(bot.blur_list) > 0 else 0
                blur = (
                    bot.blur_list[(len(bot.blur_list) - len(bot.blur_list) % 10) - 1]
                    if len(bot.blur_list) > 0
                    else 0
                )
                #Vz value calculated from blur
                vz = [v.z for v in bot.velocity_list[-10:]]
                vz_avg = sum(vz)/len(vz)
                cv2.putText(
                    frame,
                    f"{bot_id+1} - vmag: {int(vmag_avg)} blur: {round(blur, 2)}",
                    (0, 150 + bot_id * 20),
                    cv2.FONT_HERSHEY_COMPLEX,
                    0.5,
                    bot_color,
                    1,
                )

    def display_livestream_info(
        self, frame: np.ndarray, fps: FPSCounter, resize_scale: int
    ):
        """
        Displays non-tracking live-feed info to OpenCV window

        Args:
            frame: np array representation of the current video frame read in
            fps: FPSCounter object for updating current fps information
            resize_scale:   scaling factor for resizing a GUI element
        Returns:
            None
        """
        cv2.putText(
            frame,
            str(int(fps.get_fps())),
            (
                int((self.width * resize_scale / 100) / 40),
                int((self.height * resize_scale / 100) / 20),
            ),
            cv2.FONT_HERSHEY_COMPLEX,
            0.5,
            (0, 255, 0),
            1,
        )
        cv2.putText(
            frame,
            str(
                [
                    int((self.width * resize_scale / 100)),
                    int((self.height * resize_scale / 100)),
                ]
            ),
            (
                int((self.width * resize_scale / 100) / 40),
                int((self.height * resize_scale / 100) / 60),
            ),
            cv2.FONT_HERSHEY_COMPLEX,
            0.5,
            (0, 255, 0),
            1,
        )

    def single_bot_thread(
        self,
        filepath: Union[str, None],
        arduino: ArduinoHandler,
        main_window: Tk,
        enable_tracking: bool = True,
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

        # Use when using EasyPySpin camera, an FLIR mahcine vision camera python API
        # global self.BFIELD
        if filepath is None:
            try:
                cam = EasyPySpin.VideoCapture(0)
            except EasyPySpin.EasyPySpinWarning:
                print("EasyPySpin camera not found, using standard camera")
            # cam = cv2.VideoCapture(0)
        else:
            # Use when reading in a video file
            cam = cv2.VideoCapture(filepath)

        # Get the video input's self.width, self.height, and self.fps
        self.width = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cam_fps = cam.get(cv2.CAP_PROP_FPS)
        print(self.width, self.height, cam_fps)

        params = {"arduino": arduino}
        cv2.namedWindow("im")  # name of CV2 window
        cv2.setMouseCallback("im", self.mouse_points, params)  # set callback func

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
       
            self.curr_frame = frame
            if not success or frame is None:
                print("Game Over")
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

            if enable_tracking:
                self.frame_num += 1  # increment frame

                if self.num_bots > 0:
                    # DETECT ROBOTS AND UPDATE TRAJECTORY
                    self.detect_robot(frame, fps_counter)

                    # CONTROL LOOP FOR MANUALLY INFLUENCING TRAJECTORY OF MOST RECENT BOT
                    self.control_trajectory(frame, start, arduino)

                    # UPDATE AND DISPLAY HUD ELEMENTS
                    self.display_hud(frame)

                # Compute and record self.fps
                self.get_fps(fps_counter, frame, resize_scale)
            else:
                self.display_livestream_info(frame, fps_counter, resize_scale)
            
            #CONVERT BACK INTO RGB
            
            # add videos a seperate list to save space and write the video afterwords
            if self.status_params["record_status"]:
                if rec_start_time is None:
                    rec_start_time = time.time()

                if result is None:
                    result = cv2.VideoWriter(
                        output_name + ".mp4",
                        cv2.VideoWriter_fourcc(*"mp4v"),
                        20,
                        resize_ratio
                    )

                cv2.putText(
                    frame,
                    "time (s): " + str(np.round(time.time() - rec_start_time, 3)),
                    (
                        int((self.width * resize_scale / 100) * (7 / 10)),
                        int((self.height * resize_scale / 100) * (9.9 / 10)),
                    ),
                    cv2.FONT_HERSHEY_COMPLEX,
                    0.5,
                    (255, 255, 255),
                    1,
                )
                result.write(frame)
            elif result is not None and not self.status_params["record_status"]:
                result.release()
                result = None

            
            # display frame to CV2 window
            cv2.imshow("im", frame)

            
            if filepath is None:
                delay = 1
            else:
                delay = int((1/self.camera_params["framerate"])*1000)
            # Exit
            main_window.update()
            if cv2.waitKey(delay) & 0xFF == ord("q"):
                break
        
        
        cam.release()
        cv2.destroyAllWindows()
        arduino.send(4, 0, 0, 0)


        ''' 
        plt.figure()
        for i in self.robot_list:
            plt.plot(i.blur_list[20:])
            plt.title("blur")

        plt.figure()
        for i in self.robot_list:
            plt.plot(i.area_list[20:])
            plt.title("area")
        plt.show()
        '''

    def create_robotlist(self,filepath: Union[str, None]):
        #
        """
        begin by reading single frame and generating robot instances for all
        #detected contours
        Args:
            filepath: either FLIR camera or presaved video
        Returns:
            None
        """
        if filepath is None:
            try:
                cam = EasyPySpin.VideoCapture(0)
            except EasyPySpin.EasyPySpinWarning:
                print("EasyPySpin camera not found, using standard camera")
            # cam = cv2.VideoCapture(0)
        else:
            # Use when reading in a video file
            cam = cv2.VideoCapture(filepath)
            
        self.width = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))


        success,firstframe = cam.read()
        resize_scale = self.camera_params["resize_scale"]
        resize_ratio = (
                self.width * resize_scale // 100,
                self.height * resize_scale // 100,
            )
        firstframe = cv2.resize(firstframe, resize_ratio, interpolation=cv2.INTER_AREA)


        contours, blur = self.cp.get_contours(firstframe,self.control_params)
        area_threshold = 0    

        for contour in contours:
            # remove small elements by calcualting arrea
            area = cv2.contourArea(contour)

            if area > area_threshold:  # and area < 3000:# and area < 2000: #pixels


                x, y, w, h = cv2.boundingRect(contour)
                current_pos = [(x + x + w) / 2, (y + y + h) / 2]

                x,y = current_pos

                x_1 = int(x - self.control_params["bounding_length"] / 2)
                y_1 = int(y - self.control_params["bounding_length"] / 2)
                w = self.control_params["bounding_length"]
                h = self.control_params["bounding_length"]

                robot = Robot()  # create robot instance
                robot.add_position(current_pos)  # add position of the robot
                robot.add_crop([x_1, y_1, w, h])
                robot.add_blur(
                    self.cp.calculate_blur(firstframe[y_1 : y_1 + h, x_1 : x_1 + w])
                )
                self.robot_list.append(robot)

                # add starting point of trajectory
                self.num_bots += 1
        cv2.imwrite("initialimg.png",firstframe)
        cam.release()
       
   
        



    def plot(self):
        """
        Plot all trajectories from each robot using matplotlib

        Args:
            self: the class itself
        Returns:
            None
        """
        color = plt.cm.rainbow(np.linspace(0, 1, self.num_bots))

        plt.figure()
        plt.xlim((0, (1936 * self.camera_params["resize_scale"] / 100)))
        plt.ylim(((1440 * self.camera_params["resize_scale"] / 100), 0))
        plt.title("ALL TRAGECTORYS")
        for bot, bot_color in zip(self.num_bots, color):
            datax = []
            datay = []
            for i in bot.position_list:
                datax.append(i[0])
                datay.append(i[1])
                plt.plot(datax, datay, color=bot_color)

        plt.figure()
        plt.xlim((0, (1936 * self.camera_params["resize_scale"] / 100)))
        plt.ylim(((1440 * self.camera_params["resize_scale"] / 100), 0))
        plt.title("CONTROL LOOP TRAJECTORIES")
        for bot, bot_color in zip(self.num_bots, color):
            # calcualte desired tragectory

            # plt.plot(calc_trag[0][0], calc_trag[0][1], calc_trag[1][0],calc_trag[1][1], color=c,marker = "o")

            calcx = []
            calcy = []

            actual_x = []
            actual_y = []
            for track in bot.tracks:
                actual_x.append(track[2][0])
                actual_y.append(track[2][1])

            # ,markersize  = 3, marker = "*")
            plt.plot(actual_x, actual_y, color=bot_color, label="actual")

            for i in bot.trajectory:
                calcx.append(i[0])
                calcy.append(i[1])

            plt.plot(calcx, calcy, color=bot_color * 0.5, label="desired")

        plt.legend()
        plt.show()

    def convert2pickle(self, filename: str):
        """
        Converts recorded microbot tracking info into a pickle file for storage.

        Args:
            filename:   name of output file
            rolling_frequency:  Rolling frequency of video

        Returns:
            None
        """

        pickles = []
        print(" --- writing robots ---")
        for bot in tqdm(self.robot_list):
            if len(bot.area_list) > 1:
                pickles.append(bot.as_dict())

        #print(" --- writing frames ---")
        #cap = cv2.VideoCapture(filename + ".mp4")
        #length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        #raw = []

        #for i in tqdm(range(length)):
        #    _, frame = cap.read()
        #    raw.append(frame)

    

        print(" -- writing pickle --")
        with open(filename + ".pickle", "wb") as handle:
            pickle.dump(pickles, handle, protocol=pickle.HIGHEST_PROTOCOL)
        print(" -- DONE -- ")
