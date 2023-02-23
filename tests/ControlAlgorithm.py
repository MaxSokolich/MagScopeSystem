#typ =1 : spherical ---> Roll [1, alpha, freq, gamma]

import cv2
import time
import numpy as np
from typing import List, Tuple, Union
from tkinter import Tk
import EasyPySpin
import matplotlib.pyplot as plt

from src.classes.Custom2DTracker import Tracker
from src.classes.Velocity import Velocity
from src.classes.ArduinoHandler import ArduinoHandler
from src.classes.FPSCounter import FPSCounter
from src.classes.RobotClass import Robot
from src.classes.ContourProcessor import ContourProcessor



class Algorithm:
    def __init__(self, main_window: Tk, 
                 arduino: ArduinoHandler,
                control_params: dict,
                camera_params: dict,
                status_params: dict,
                use_cuda: bool = False,
                ):


        self.arduino = arduino
        self.main_window = main_window
        self.control_params = control_params
        self.camera_params = camera_params
        self.status_params = status_params

        self.cp = ContourProcessor(self.control_params,use_cuda)

        self.start = time.time()
        self.draw_trajectory = False  # determines if trajectory is manually being drawn
        self.robot_list = []  # list of actively tracked robots
        self.curr_frame = np.array([])
        self.node = None  # index of node having their trajectory manually influenced
        self.num_bots = 0  # current number of bots
        self.frame_num = 0  # current frame count
        self.elapsed_time = 0  # time elapsed while tracking
        self.prev_frame_time = 0  # prev frame time, used for self.fps calcs
        self.new_frame_time = 0  # time of newest frame, used for self.fps calcs
        self.width = 0  # width of cv2 window
        self.height = 0  # height of cv2 window

    
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
            self.node = 1
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
        x_2_new = 2 * max_width
        y_2_new = 2 * max_height
        new_crop = [int(x_1_new), int(y_1_new), int(x_2_new), int(y_2_new)]
        
       

        # calculate velocity based on last position and self.fps
        #print(pix_2metric)
        if len(bot.position_list) > 5:
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
                velz = (bot.blur_list[-4] - blur)    #This needs to be scaled or something
            vel = Velocity(velx, vely, 0)
            bot.add_velocity(vel)
          
        # update robots params
        bot.add_crop(new_crop)
        bot.add_position([current_pos[0] + x_1, current_pos[1] + y_1])
        bot.add_frame(self.frame_num)
        bot.add_time(round(time.time()-self.start,2))

        # display
        cv2.circle(
            cropped_frame,
            (int(current_pos[0]), int(current_pos[1])),
            2,
            (1, 255, 1),
            -1,
        )

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
        for bot in self.robot_list:

            # crop the frame based on initial ROI dimensions
            x_1, y_1, x_2, y_2 = bot.cropped_frame[-1]
            
            max_width = 0  # max width of the contours
            max_height = 0  # max height of the contours

            x_1 = max(min(x_1, self.width), 0)
            y_1 = max(min(y_1, self.height), 0)
         
        
            cropped_frame = frame[y_1 : y_1 + y_2, x_1 : x_1 + x_2]
            
            #CSIC mask
            contours, blur = self.cp.get_contours(cropped_frame,self.control_params)
            bot.add_blur(blur)
            #test mask
            #fgmask = F.apply(cropped_frame)
            #kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (1, 1))
            #fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_OPEN, kernel)
            #contours, hierarchy = cv2.findContours(fgmask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            #blur = 0

            #area_thresh = bot.avg_area*2
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
                    max_width = w
                if h > max_height:
                    max_height = h
                cv2.rectangle(cropped_frame, (x, y), (x + w, y + h), (255, 0, 0), 1)
                #cv2.drawContours(cropped_frame, [max_cnt], -1, (0, 255, 255), 1)
   
                self.track_robot_position(
                    area,
                    bot,
                    cropped_frame,
                    (x_1, y_1),
                    current_pos,
                    blur,
                    (max_width, max_height),
                    fps,
                    pix_2metric
                )


    def get_fps(self, fps: FPSCounter, frame: np.ndarray, resize_scale: int, pix_2metric: float):
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
            frame, (75, 80), (75 + int(100 * (pix_2metric)),80), (0, 0, 255), 3
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
            cv2.polylines(frame, [pts], False, bot_color, 2)
            
            #display target positions
            targets = self.robot_list[bot_id].trajectory
            if len(targets) > 0:
                target = targets[-1]
                cv2.circle(frame,
                    (int(target[0]), int(target[1])),
                    4,
                    (bot_color),
                    -1,
                )

            # if there are more than 10 velocities recorded in the robot, get
            # and display the average velocity
            if len(self.robot_list[bot_id].velocity_list) > 10:
                bot = self.robot_list[bot_id]
                vmag = [v.mag for v in bot.velocity_list[-10:]]
                vmag_avg = sum(vmag) / len(vmag)
                #print(vmag_avg)

                # blur = bot.blur_list[-1] if len(bot.blur_list) > 0 else 0
                blur = (
                    bot.blur_list[(len(bot.blur_list) - len(bot.blur_list) % 10) - 1]
                    if len(bot.blur_list) > 0
                    else 0
                )
                #Vz value calculated from blur
                vz = [v.z for v in bot.velocity_list[-10:]]
                vz_avg = sum(vz)/len(vz)

                #average diamter of bot (calcuating from area of circle)
                dia = np.sqrt(4*bot.avg_area/np.pi)
                
                
                cv2.putText(
                    frame,
                    f"{bot_id+1} - vmag: {int(vmag_avg)}um/s. size: {round(dia, 2)}um",
                    (0, 150 + bot_id * 20),
                    cv2.FONT_HERSHEY_COMPLEX,
                    0.5,
                    bot_color,
                    1,
                )

    def algorithm(self, arduino):
        """
        
        

        Returns: actions
        """
        f = 1 #frequency
        pos_list = []
        target_list = []
        for bot in range(len(self.robot_list)):
            current_position = self.robot_list[bot].position_list[-1]
            target_position = self.robot_list[bot].trajectory[-1]
            past_position = self.robot_list[bot].position_list[-2]

        
        t1 = 1
        t2 = 2
        alpha = np.arctan2(t2,t1)
        application_time = np.sqrt(t1**2+t2**2)
        frequency = f        
        gamma = 90
        
        if arduino.conn is not None:            
            arduino.send(1,alpha,frequency,gamma)
        
     
        
    


    
    def run(
        self,
        filepath: Union[str, None],
        arduino: ArduinoHandler,
        main_window: Tk,
        output_name: str = "",
    ):
        """
        Runs the different algorithm custom tracker thread 

        Args:
            filepath:   filepath to video file to be analyzed

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

        # Get the video input's self.width, self.height, and self.fps
        self.width = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cam_fps = cam.get(cv2.CAP_PROP_FPS)
        print(self.width, self.height, cam_fps)

        params = {"arduino": arduino}
        cv2.namedWindow("im")  # name of CV2 window
        cv2.setMouseCallback("im", self.mouse_points, params)  # set callback func

        rec_start_time = None
        result = None
        fps_counter = FPSCounter()
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

            #calculate pixel to metric for varying res
            #106.2 um = 1024 pixels  @ 50%  resize and 100 x
            pix_2metric = ((resize_ratio[1]/106.2)  / 100) * self.camera_params["Obj"] 
            self.frame_num += 1  # increment frame

            if self.num_bots > 0:
                # DETECT ROBOTS AND UPDATE TRAJECTORY
                self.detect_robot(frame, fps_counter,pix_2metric)

                # UPDATE AND DISPLAY HUD ELEMENTS
                self.display_hud(frame)

                # RUN ALGORITHM
                #self.run(self.arduino)
              

            # Compute and record self.fps
            self.get_fps(fps_counter, frame, resize_scale, pix_2metric)
        

            
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

