#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module containing the ContourProcessor class

@authors: Max Sokolich, Brennan Gallamoza, Luke Halko, Trea Holley,
          Alexis Mainiero, Cameron Thacker, Zoe Valladares
"""

import os
from typing import List, Tuple, Union
import numpy as np
import matplotlib.pyplot as plt
import cv2

DEFAULT_IMG = str(os.path.dirname(os.path.abspath(__file__))) + "/../imgs/initialimg.png"

class ContourProcessor:
    '''
    Tracker class for tracking microbots. Creates an interactable interface using OpenCV for
    tracking the trajectories of microbots on a video input (either through a live camera 
    or a video file).

    NOTE: USING CONTRAST IN PLACE OF BLUR FOR A ARTIFICAL Z VALUE

    Args:
        use_cuda: boolean specifying whether CUDA preprocessing should be performed
        baseline_blur_img: path to the "standard image" of an in-focus microbot
    '''

    def __init__(self,control_params: dict,use_cuda: bool=False, baseline_blur_img: str=DEFAULT_IMG):
        self.kernel_size = 3
        self.base_brightness = 0
        self.control_params = control_params
        self.baseline_blur = 0#self.calculate_blur(cv2.imread(baseline_blur_img), True)
        self.counter = 0
        if use_cuda and cv2.cuda.getCudaEnabledDeviceCount() > 0:
            self.use_cuda = True
        else:
            if use_cuda:
                print("No CUDA devices were found, disabling CUDA for current Tracker")
            self.use_cuda = False


    def calculate_blur(self, cropped_frame: np.ndarray, apply_grayscale=False) -> float:
        """
        Applies the Laplacian operator to an image (in the form of an np.ndarray), then
        takes the resulting variance as a measure of the image's blur.

        Arg:
            cropped_frame:  np.ndarray representing an image containing a microbot
            apply_grayscale:    converts cropped_frame to grayscale;
                                optional param for testing purposes
        Returns:
            float value representing the variance of the image after applying the
            Laplacian operator.
        """
        #grab the original blur value after 6 frames from clicking on a bot
        
        if self.counter == 0:
            self.blur_baseline = cv2.Laplacian(cropped_frame, cv2.CV_64F).var()

        if apply_grayscale:
            cropped_frame = cv2.cvtColor(cropped_frame, cv2.COLOR_BGR2GRAY)
        #print(cv2.Laplacian(cropped_frame, cv2.CV_64F).var())
        return cv2.Laplacian(cropped_frame, cv2.CV_64F).var()

    def get_blur_kernel(self, blur: float) -> Union[Tuple[float, float], None]:
        """
        Calculates the Gaussian blur kernel that should be used in cv2.GaussianBlur
        prior to identifying contours. Calculation based on the ContourProcessor's
        blur_thresh, where modification of the base kernel size is done if the blur
        level drops below the threshold.

        Args:
            blur:  float representing the Laplacian blur variance of an image
        Returns:
            A Gaussian kernel size in the form of a 2-tuple (height, width). May also
            return None if no blur kernel should be applied.
        """
        self.blur_thresh = self.control_params["blur_thresh"] 
        kernel = self.kernel_size
        if blur < self.blur_thresh:
            blur_reduction = blur / self.blur_thresh
            kernel = int(kernel * blur_reduction)
            if kernel % 2 == 0:
                kernel += 1
        
        if kernel == 0:
            return None
        else:
            return (kernel, kernel)
    
    def get_brightness_and_contrast(self, blur: float) -> Tuple[int, int]:
        """
        Calculate the brightness and contrast to be used on a cropped image for
        preprocessing. The higher the blur, the more contrast and brightnening is
        applied to the image, allowing for contours to be found.

        Args:
            blur:  float representing the Laplacian blur variance of an image
        Returns:
            A 2-tuple containing the brightness and contrast to be used on the
            image, respectively
        """
        brightness = 0
        contrast = 0
        if blur != 0 and blur < self.blur_thresh:
            contrast = (self.blur_thresh*8) / blur
      
        #print(blur , " < ", self.blur_thresh)
        return brightness, contrast


    def apply_brightness_contrast(
            self,
            cropped_frame: np.ndarray,
            brightness: float,
            contrast: float
        )-> np.ndarray:
        """
        Takes an np.ndarray image and applies contrast and brightness alterations with
        the following formula:

        `new_image = (old_image) * (contrast/127 + 1) - contrast + brightness`

        **formula described by OpenCV documentation here:
            https://docs.opencv.org/4.x/d3/dc1/tutorial_basic_linear_transform.html

        Args:
            blur:  float representing the Laplacian blur variance of an image
        Returns:
            A Gaussian kernel size in the form of a 2-tuple (height, width). May also
            return None if no blur kernel should be applied.
        """
        # if abs(brightness) > 127 or abs(contrast) > 127:
        #     raise ValueError("Brightness and Contrast must be integers between -127 to 127")
        
        img = np.int16(cropped_frame)
        img = img * (contrast/127 + 1) - contrast + brightness
        img = np.clip(img, 0, 255)
        img = np.uint8(img)
        return img

    

    def apply_pipeline(
            self,
            cropped_frame: np.ndarray,
            control_params: dict,
            bot_blur_list: Union[List[float], None]=None,
            debug_mode=False
        ) -> np.ndarray:
        """
        Applies a pipeline of preprocessing to a cropped frame in the form of:
            Grayscale -> Gaussian Blur -> Brightness/Contrast Adjustment -> InRange threshold

        Also calculates the blur variance of a cropped image

        Args:
            cropped_frame:  cropped frame img containing the microbot, indicated by list of coords
            bot_blur_list:  list of previous blur values from each frame, originally contained=
                            in a Robot class
            debug_mode: Optional debugging boolean; if True, debugging information is printed
        Returns:
            masked image + blur value
        """
        # Apply preprocessing pipeline to cropped image
        # convert to grayscale
        crop_mask = cv2.cvtColor(cropped_frame, cv2.COLOR_BGR2HSV)  #[hue, saturation, vlue]
        #crop_mask = cropped_frame
        # get blur after grayscale is applied

        blur = self.calculate_blur(crop_mask)

        # get the avg blur based on the current blur and last 5 other frames
        if bot_blur_list:
            avg_blur = (blur + (sum(bot_blur_list[-3:]))) / 3
            #print(avg_blur)
            
        if debug_mode:
            print("BLUR:\t", blur)

        # apply gaussian blur based on avg_blur
        kernel = self.get_blur_kernel(blur)   # dynamic kernel
        if kernel is not None:
            crop_mask = cv2.GaussianBlur(crop_mask, kernel, 0)

        # apply brightness/contrast based on avg_blur
        brightness, contrast = self.get_brightness_and_contrast(blur)
        crop_mask = self.apply_brightness_contrast(crop_mask, brightness, contrast)
        self.lower_thresh =  control_params["lower_thresh"]#np.array([control_params["lower_thresh"], control_params["lower_thresh"], control_params["lower_thresh"]]) 
        self.upper_thresh = control_params["upper_thresh"]#np.array([control_params["upper_thresh"],control_params["upper_thresh"],control_params["upper_thresh"]])
        crop_mask = cv2.inRange(crop_mask, self.lower_thresh, self.upper_thresh)
        #cv2.imshow("3",crop_mask)

        # Return the preprocessed cropping and the blur value of the current frame
        return crop_mask, contrast   #switched from blur

    def apply_cuda_pipeline(self, cropped_frame: np.ndarray,control_params: dict,):
        """
        Applies a pipeline of preprocessing on the GPU to a cropped frame in the form of:
            Grayscale -> InRange threshold

        Also calculates the blur variance of a cropped image

        Args:
            cropped_frame:  cropped frame img containing the microbot, indicated by list of coords
            bot_blur_list:  list of previous blur values from each frame, originally contained=
                            in a Robot class
            debug_mode: Optional debugging boolean; if True, debugging information is printed
        Returns:
            List of contours
        """

        gpu_frame = cv2.cuda_GpuMat()
        gpu_frame.upload(cropped_frame)
        gpu_frame = cv2.cuda.cvtColor(gpu_frame, cv2.COLOR_BGR2HSV)

        # Gaussian and Brightness/Contrast performed on CPU; currently inefficient due to
        # overhead of uploading/downloading twice, must be optimized with CUDA Python
        crop_mask = gpu_frame.download()
        blur = self.calculate_blur(crop_mask)
        # apply gaussian blur based on avg_blur
        kernel = self.get_blur_kernel(blur)   # dynamic kernel
        if kernel is not None:
            crop_mask = cv2.GaussianBlur(
                crop_mask, kernel, 0)

        # apply brightness/contrast based on avg_blur
        brightness, contrast = self.get_brightness_and_contrast(blur)
        crop_mask = self.apply_brightness_contrast(crop_mask, brightness, contrast)

        gpu_frame.upload(crop_mask)

        h,s,v = cv2.cuda.split(gpu_frame)
        reth, h = cv2.cuda.threshold(h, control_params["lower_thresh"][0], control_params["upper_thresh"][0], cv2.THRESH_BINARY)
        rets, s = cv2.cuda.threshold(s, control_params["lower_thresh"][1], control_params["upper_thresh"][1], cv2.THRESH_BINARY)
        retv, v = cv2.cuda.threshold(v, control_params["lower_thresh"][2], control_params["upper_thresh"][2], cv2.THRESH_BINARY)
        temp = cv2.cuda.bitwise_and(h,s)
        gpu_frame = cv2.cuda.bitwise_and(temp,v)
        crop_mask = gpu_frame.download()

        return crop_mask, contrast  #switched from blur

    def get_contours(
            self,
            cropped_frame: np.ndarray,
            control_params: dict, 
            bot_blur_list: Union[List[float], None]=None,
            debug_mode=False,
        ) -> Tuple[List, float]:
        """
        Applies a pipeline of preprocessing to a cropped frame, then gets the contours from the
        cropped, preprocesed image.

        Args:
            cropped_frame:  cropped frame img containing the microbot, indicated by list of coords
            bot_blur_list:  list of previous blur values from each frame, originally contained=
                            in a Robot class
            debug_mode: Optional debugging boolean; if True, debugging information is printed
        Returns:
            List of contours
        """

        if self.use_cuda:
            crop_mask, contrast = self.apply_cuda_pipeline(cropped_frame,control_params)
        else:
            crop_mask, contrast = self.apply_pipeline(cropped_frame, control_params, bot_blur_list, debug_mode)

       
        # find contours and areas of contours
        contours, _ = cv2.findContours(crop_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Return the contours and the blur value of the current frame
        
        self.counter+=1
        return contours, contrast#blur - self.baseline_blur

    def plot_contours(self, contours: Tuple[np.ndarray]):
        """
        Print out contour coordinates and plot the points on a scatterplot.

        Args:
            contours:   output of cv2.findContours(); results in a tuple containing
                        a np.ndarray of X, Y coordinates for each contour point
        Returns:
            None
        """
        num_contours = contours[0].shape[0]
        contours = contours[0].reshape(num_contours, 2)

        print("CONTOURS:\n", contours)

        plt.figure(figsize=(8,8))
        plt.scatter(x=[x[0] for x in contours], y=[y[1] for y in contours])
        plt.show()