import cv2
import numpy as np
from collections import deque
import matplotlib.pyplot as plt
import EasyPySpin
from typing import List, Tuple, Union
from tkinter import Tk
from tkinter import *
from src.python.FPSCounter import FPSCounter
import time 

class AllTracker:
    def __init__(
        self,
        main_window: Tk,
        control_params: dict,
        camera_params: dict,
        status_params: dict,
        
    ):
        self.control_params = control_params
        self.camera_params = camera_params
        self.status_params = status_params

        self.width = 0  # width of cv2 window
        self.height = 0  # height of cv2 window

        self.main_window = main_window



    def get_fps(self, fps: FPSCounter, frame: np.ndarray, pix_2metric: float):
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
            (255, 255, 255),
            1,
        )

        # scale bar
        cv2.putText(frame,"100 um",
            (int(w / 40),int(h / 18)),
            cv2.FONT_HERSHEY_COMPLEX,
            0.5,
            (255, 255, 255),
            1,
        )
        cv2.line(
            frame, 
            (int(w / 40),int(h / 14)),
            (int(w / 40) + int(100 * (pix_2metric)),int(h / 14)), 
            (255, 255, 255), 
            3
        )

       
    def main(self,filepath: Union[str, None]):
        
        
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


        # Define the lower and upper bounds of the black color
        lower_black = np.array([0, 0, 0])
        upper_black = np.array([30, 30, 30])


        thresh = 50


        # Define a dictionary to store the robots and their identifiersq
        robots = {}


        # Initialize the identifier counter
        id_count = 0


        # Define lists to store the trajectory and velocity of each robot
        trajectories = {}
        velocities = {}

        start = time.time()
        fps_counter = FPSCounter()

        count = 0
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
            #calculate pixel to metric for varying res
            #106.2 um = 1024 pixels  @ 50%  resize and 100 x
            self.pix_2metric = ((resize_ratio[1]/106.2)  / 100) * self.camera_params["Obj"] 

            # Convert the frame to grayscale and blur it to reduce noise
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Threshold the image to find black regions
            mask = cv2.inRange(frame, lower_black, upper_black)
            
            # Find contours in the black regions
            contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            
            # Process each contour
            for cnt in contours:
                x, y, w, h = cv2.boundingRect(cnt)
                
                # Calculate the centroid of the contour
                centroid_x = x + w // 2
                centroid_y = y + h // 2
                
                # Check if the centroid is close to an existing robot
                found = False
                for id, robot in robots.items():
                    if abs(robot['centroid_x'] - centroid_x) < thresh and abs(robot['centroid_y'] - centroid_y) < thresh:
                        # Calculate the velocity of the robot
                        vel_x = centroid_x - robot['centroid_x']
                        vel_y = centroid_y - robot['centroid_y']
                        velocity = np.sqrt(vel_x**2 + vel_y**2)
                        # Update the previous position of the robot
                        robot['prev_x'] = robot['centroid_x']
                        robot['prev_y'] = robot['centroid_y']
                        # Update the current position of the robot
                        robot['centroid_x'] = centroid_x
                        robot['centroid_y'] = centroid_y
                        found = True
                        # Append the current position and velocity to the trajectory and velocity lists
                        trajectories[id]['x'].append(centroid_x)
                        trajectories[id]['y'].append(centroid_y)
                        velocities[id].append(velocity)
                        break
                
                # If the centroid is not close to any existing robot, add a new robot
                if not found:
            
                    id_count += 1
                    robots[id_count] = {'centroid_x': centroid_x, 'centroid_y': centroid_y}
                    # Initialize the trajectory and velocity lists for the new robot
                    trajectories[id_count] = {'x': [centroid_x], 'y': [centroid_y]}
                    velocities[id_count] = []
            
            # Draw bounding boxes and identifiers for each robot
            for id, robot in robots.items():
                x = robot['centroid_x'] - 20
                y = robot['centroid_y'] - 20
                # Draw a bounding box around the robot
                cv2.rectangle(frame, (x, y), (x + 40, y + 40), (0, 255, 0), 2)

                # Draw the identifier for the robot
                cv2.putText(frame, f'Robot {id}', (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

                # Draw the trajectory of the robot
                if len(trajectories[id]['x']) > 1:
                    for i in range(1, len(trajectories[id]['x'])):
                        x1 = trajectories[id]['x'][i-1]
                        y1 = trajectories[id]['y'][i-1]
                        x2 = trajectories[id]['x'][i]
                        y2 = trajectories[id]['y'][i]
                        cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)

                # Draw the velocity of the robot
                if velocities[id]:
                    velocity = np.mean(velocities[id])
                    cv2.putText(frame, f'Velocity: {velocity:.2f} pixels/frame', (x, y + 45), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

                # Update the trajectory and velocity lists for robots that were not detected in the current frame
                for id, trajectory in trajectories.items():
                    if id not in robots:
                        trajectory['x'].append(trajectory['x'][-1])
                        trajectory['y'].append(trajectory['y'][-1])
                        velocities[id].append(0)

            # Display the frame
            self.get_fps(fps_counter,frame, self.pix_2metric)
            cv2.imshow('frame', frame)
            count +=1

            #handle frame rate adjustment
            if filepath is None:
                delay = 1
            else:
                delay = int((1/self.camera_params["framerate"])*1000)
            k = cv2.waitKey(delay)


            # Exit the loop if the 'q' key is pressed
            self.main_window.update()
            if k & 0xFF == ord('q'):
                break


        cam.release()
        cv2.destroyAllWindows()

        ''' 
        fig, ax = plt.subplots()
        ax.set_xlim(0, 2448)
        ax.set_ylim(0, 2048)
        ax.set_title('Robot Trajectories')
        ax.set_xlabel('X Position')
        ax.set_ylabel('Y Position')
        for id, trajectory in trajectories.items():
            x = trajectory['x']
            y = trajectory['y']
            ax.plot(x, y, label=f'Robot {id}')
            ax.legend()
        plt.show()

        fig, ax = plt.subplots()
        ax.set_title('Robot Velocities')
        ax.set_xlabel('Time (frames)')
        ax.set_ylabel('Velocity (pixels/frame)')
        for id, velocity in velocities.items():
            ax.plot(velocity, label=f'Robot {id}')
            ax.legend()
        plt.show()'''