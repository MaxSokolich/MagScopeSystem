#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module containing the Robot class

@authors: Max Sokolich, Brennan Gallamoza, Luke Halko, Trea Holley,
          Alexis Mainiero, Cameron Thacker, Zoe Valladares
"""

from typing import List, Tuple, Union
import numpy as np
from Velocity import Velocity



class Robot:
    """
    Robot class to store and ID all new robots currently being tracked.

    Args:
        None
    """

    def __init__(self):
        self.velocity_list = []  # stores bot velocities per frame
        self.position_list = []  # stores bot positions per frame
        self.blur_list = []  # stores calculated blur values per frame (AKA z-value)
        self.frame_list = []  # unused? stores frames
        self.area_list = []  # stores the cropped areas
        self.cropped_frame = []  # cropped section of a frame representing the bot
        self.avg_area = 0  # current average area of the bot in this frame
        self.avg_blur = 0  # current average blur of the bot in this frame
        self.tracks = []  # adds frame info on bot's error from manual track
        self.trajectory = []  # track points from manual pathing
        self.times = []  #time step per frame in seconds
 


    def add_area(self, area: float):
        """
        Add area value to the bot's area_list

        Args:
            area:   area float value to be added

        Returns:
            None
        """
        self.area_list.append(area)

    def add_blur(self, blur: float):
        """
        Add area value to the bot's blur

        Args:
            blur:   blur float value to be added

        Returns:
            None
        """
        self.blur_list.append(blur)

    def add_velocity(self, velocity: Velocity):
        """
        Add velocity to the bot's velocity_list

        Args:
            velocity:   class containing the bot's x-velocity,
                        y-velocity, and z-velocity

        Returns:
            None
        """
        self.velocity_list.append(velocity)

    def add_position(self, position: List[float]):
        """
        Add the position values to the bot's position_list

        Args:
            position:   list containing the bot's current x and y position

        Returns:
            None
        """
        self.position_list.append(position)
    

    def add_frame(self, frame: int):
        """
        Add frame number to the bot's frame list

        Args:
            frame:  current number frame to be added

        Returns:
            None
        """
        self.frame_list.append(frame)

    def add_crop(self, crop: List[int]):
        """
        Add crop coordinates to the bot's cropped_frame list

        Args:
            crop:   list containing the bot's cropping coords, in the form of:
                    [x0, y0, x1, y1]

        Returns:
            None
        """
        self.cropped_frame.append(crop)

    def set_avg_area(self, avg_area: float):
        """
        Set the bot's average area attribute

        Args:
            avg_area:   the bot's average cropped area as of the most current frame

        Returns:
            None
        """
        self.avg_area = avg_area

    def add_trajectory(self, traj: List[int]):
        """
        Add current intended trajectory for the bot to fllow

        Args:
            traj:   list of coords in the form of [x, y]

        Returns:
            None
        """
        self.trajectory.append(traj)

    def add_track(
        self,
        error: float,
        actual_tracks: List[int],
        desired_tracks: List[int],
        alpha: float,
        freq:float,
        time: float,
        control_param: Union[str, None],
    ):
        """
        Adds current frame's track information to the bot's tracks list

        Args:
            frame:  current number frame to be added
            error:  euclidean distance between the microbot's position and
                    the intended position
            actual_tracks:  list of true [x,y] coords
            desired_tracks: list of intended [x,y] coords
            alpha:  alpha parameter
            time:   current time as of track addition
            control_param:  TBD

        Returns:
            None
        """
        self.tracks.append(
            [error, actual_tracks, desired_tracks, alpha,freq, time, control_param]
        )

    def add_time(self, time):
        self.times.append(time)

    def as_dict(self) -> dict:
        """
        Convert's the bot's current frame and position information into a
        readable dictionary

        Args:
            None

        Returns:
            dictionary of the bot's current position and frame information
        """
        pos_x = np.array(self.position_list)[:, 0]
        pos_y = np.array(self.position_list)[:, 1]
        vel_x = np.array([v.x for v in self.velocity_list])
        vel_y = np.array([v.y for v in self.velocity_list])
        vel_z = np.array([v.z for v in self.velocity_list])
        v_mag = np.array([v.mag for v in self.velocity_list])
        if len(self.trajectory) > 1:
            traj_x = np.array(self.trajectory)[:, 0]
            traj_y = np.array(self.trajectory)[:, 1]
        else:
            traj_x,traj_y = None,None
        mydict = {
            "Frame": self.frame_list,
            "Times": self.times,
            "PositionX": pos_x,
            "PositionY": pos_y,
            "VelX": vel_x,
            "VelY": vel_y,
            "VelZ": vel_z,
            "VMag": v_mag,
            "Area": self.area_list,
            "Cropped Frame Dim": self.cropped_frame,
            "Avg Area": self.avg_area,
            "Track_Params(frame,error,current_pos,target_pos,alpha,freq,time)": self.tracks,
            "TrajectoryX": traj_x,
            "TrajectoryY": traj_y,
        }

        return mydict
