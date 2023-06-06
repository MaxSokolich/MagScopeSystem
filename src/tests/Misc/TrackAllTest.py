import EasyPySpin
import warnings

import pandas as pd
import time
from typing import List, Tuple, Union
import pickle
import numpy as np
import cv2
import matplotlib.pyplot as plt



control_params = {
    "lower_thresh": 0,
    "upper_thresh": 104,
    "blur_thresh": 100,
    "bounding_length": 100,       #intial size of "screenshot" cropped frame 
    "area_filter": 1,            #cropped frame dimensions mulitplier
    "field_strength": 1,
    "rolling_frequency": 10,
    "gamma": 90,
    "memory": 50,
}

CAMERA_PARAMS = {
    "resize_scale": 100, 
    "framerate": 24, 
    "exposure": 10000, 
    "Obj": 50}

def create_robotlist(filepath: Union[str, None]):
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
            
        width = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))


        success,firstframe = cam.read()
        resize_scale = CAMERA_PARAMS["resize_scale"]
        resize_ratio = (
                width * resize_scale // 100,
                height * resize_scale // 100,
            )
        firstframe = cv2.resize(firstframe, resize_ratio, interpolation=cv2.INTER_AREA)

        crop_mask = cv2.cvtColor(firstframe, cv2.COLOR_BGR2GRAY)
        crop_mask = cv2.GaussianBlur(crop_mask, (21,21), 0)
        crop_mask = cv2.inRange(crop_mask, control_params["lower_thresh"], control_params["upper_thresh"])
        contours, _ = cv2.findContours(crop_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        areas = []  
        
        
        for contour in contours: #treating each contour as a robot
            # remove small elements by calcualting arrea
            area = cv2.contourArea(contour)
            areas.append(area)

        print(areas)
        print(np.mean(np.array(areas)))

        frame = cv2.cvtColor(crop_mask, cv2.COLOR_GRAY2BGR)
        for contour in contours: #treating each contour as a robot
            # remove small elements by calcualting arrea
            area = cv2.contourArea(contour)

            if area >= np.mean(np.array(areas))/2:  # and area < 3000:# and area < 2000: #pixels


                x, y, w, h = cv2.boundingRect(contour)
                current_pos = [(x + x + w) / 2, (y + y + h) / 2]

                x,y = current_pos

                x_1 = int(x - control_params["bounding_length"] / 2)
                y_1 = int(y - control_params["bounding_length"] / 2)
                w = control_params["bounding_length"]
                h = control_params["bounding_length"]

                cv2.drawContours(frame, contour, -1, (0, 0, 255), 2)
     

                
                #create checkboxes for each robot
        
        #self.create_robot_checkbox(self.robot_window)
        
        cv2.imwrite("initialmask.png",frame)
        cam.release()
       
filepath = "/home/max/Documents/MagScopeSystem/videos/mickyroll1.mp4"
create_robotlist(None)