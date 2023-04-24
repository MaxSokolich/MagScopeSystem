#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module containing the GUI class

@authors: Max Sokolich, Brennan Gallamoza, Luke Halko, Trea Holley,
          Alexis Mainiero, Cameron Thacker, Zoe Valladares
pix = 1936 x 1464 mono
maxframerate = 130 (actually ~60)
exptime = 10us - 30s
iamge buffer = 240 MB

or 

pix - 2448 x 2048 color
maxframerate = 35 (actually 24)
"""
import colorsys
from queue import Empty
import multiprocessing
import time as time
import numpy as np
from typing import Union
from tkinter import *
from tkinter import Tk
from tkinter import filedialog

from src.python.AcousticClass import AcousticClass
from src.python.HallEffect import HallEffect
from src.python.Custom2DTracker import Tracker
from src.python.ArduinoHandler import ArduinoHandler
from src.python.Brightness import Brightness
from src.python.JoystickProcess import JoystickProcess
from src.python.AnalysisClass import Analysis
from src.python.TrackAll import AllTracker


# with jetson orin, cam can get up to 35 fps

PID_PARAMS = {
    "Iframes": 100,
    "Dframes": 10,
    "Kp": 0.1,
    "Ki": 0.01,
    "Kd": 0.01,
}

CONTROL_PARAMS = {
    "lower_thresh": np.array([0,0,0]),  #HSV
    "upper_thresh": np.array([180,255,140]),  #HSV   #130/150
    "blur_thresh": 100,
    "initial_crop": 100,       #intial size of "screenshot" cropped frame 
    "tracking_frame": 1,            #cropped frame dimensions mulitplier
    "avg_bot_size": 5,
    "field_strength": 1,
    "rolling_frequency": 10,
    "arrival_thresh": 10,
    "gamma": 90,
    "memory": 15,
    "PID_params": PID_PARAMS,
}

CAMERA_PARAMS = {
    "resize_scale": 50, 
    "framerate": 24, 
    "exposure": 6000,   #6000
    "Obj": 50}

STATUS_PARAMS = {
    "rolling_status": 0,
    "orient_status": 0,
    "multi_agent_status": 0,
    "PID_status": 0,
    "algorithm_status": False,
    "record_status": False,
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



class GUI:
    """
    Handles the Tkinter GUI actions for the microbot tracking user interface,
    including global adjustments to the tracker, file input and output, CUDA
    toggling, and other features

    Args:
        master: Tk window acting as the main window of the GUI
        arduino: ArduinoHandler object containing arduino connection information
    """

    def __init__(self, master: Tk, arduino: ArduinoHandler):
        # Tkinter window attributes
        self.main_window = master
        self.screen_width = self.main_window.winfo_screenwidth()
        self.screen_height = self.main_window.winfo_screenheight()
        self.x, self.y = 0, 0
        self.w, self.h = (
            self.main_window.winfo_reqwidth(),
            self.main_window.winfo_reqheight(),
        )

        #update sensor process/queue
        self.sensor = None
        self.sense_q = multiprocessing.Queue(1)
        #self.sense_q.cancel_join_thread()
        self.checksensor = None
        #self.main_window.after(10, self.CheckSensorPoll, self.sense_q)

        #update joystick process/queue
        self.joystick = None
        self.joystick_q =  multiprocessing.Queue(1)
        #self.joystick_q.cancel_join_thread()
        self.checkjoy = None
        #self.main_window.after(10, self.CheckJoystickPoll, self.joystick_q)
          
          
        # Tracker-related attributes
        self.arduino = arduino
        self.external_file = None

        
        #define instance of acoustic module
        self.AcousticModule = AcousticClass()
        self.AcousticModule.dp_activate()

        #acoustic conditioning/logic
        self.button_state = 0
        self.last_state = 0
        self.counter = 0
        self.switch_state = 0

        # Tkinter widget attributes
        self.text_box = Text(master, width=22, height=4)
        self.scroll_bar = Scrollbar(
            master, 
            command=self.text_box.yview, 
            orient="vertical"
        )
        self.text_box.configure(yscrollcommand=self.scroll_bar.set)
        self.text_box.grid(row=7, column=2, columnspan =2,sticky="nwse")


        coil_joystick_button = Button(
            master, 
            text="Joystick On", 
            command=self.joy_proc, 
            height=1, 
            width=18,
            bg = 'magenta',
            fg= 'white'
        )

        sensor_button = Button(
            master, 
            text="Sensor On", 
            command=self.sensor_proc, 
            height=1, 
            width=18,
            bg = 'black',
            fg= 'white'
        )

        closed_loop_params_button = Button(
            master,
            text="Edit Control Params",
            command=self.edit_closed_loop_params,
            height=1,
            width=20,
            bg = 'green',
            fg= 'black'
        )

        cam_params_button = Button(
            master,
            text="Edit Camera Params",
            command=self.edit_camera_params,
            height=1,
            width=20,
            bg = 'yellow',
            fg= 'black'
        )

        acoustic_params_button = Button(
            master,
            text="Edit Acoustic Params",
            command=self.edit_acoustic_params,
            height=1,
            width=20,
            bg = 'cyan',
            fg= 'black'
        )

        pid_params_button = Button(
            master,
            text="Edit PID Params",
            command=self.edit_pid_params,
            height=1,
            width=18,
            bg = 'black',
            fg= 'white'
        )

        closed_loop_params_button.grid(row=0, column=0)
        cam_params_button.grid(row=1, column=0)
        acoustic_params_button.grid(row=2, column=0)
        pid_params_button.grid(row=2,column=3)


        #VIDEO RECORD FRAME
        self.video_record_frame = Frame(master = master)
        self.video_record_frame.grid(row=3,column=3,rowspan = 2)


        output_name = Entry(master=self.video_record_frame, name="output_name")
        output_name.insert(10, "")

        record_button = Button(
            self.video_record_frame, 
            text="Record", 
            command=self.record, 
            height=1, 
            width=10,
            bg = 'red',
            fg= 'black'
        )

        stop_record_button = Button(
            self.video_record_frame, 
            text="Stop Record", 
            command=self.stop_record, 
            height=1, 
            width=10,
            bg = 'white',
            fg= 'black'
        )

        Label(master = self.video_record_frame, text="Output Name").grid(row=0, column=0)
        output_name.grid(row=1, column=0)
        record_button.grid(row=2, column=0)
        stop_record_button.grid(row=3, column=0)
        

        
        #2 ALGORITHM FRAME
        self.algorithm_frame = Frame(master = master)
        self.algorithm_frame.grid(row=0,column=2,rowspan = 3)
        
        Label(master = self.algorithm_frame, text="--Algorithm List--").grid(row=0, column=0)

        AlgoRoll = IntVar(master=master, name="roll")
        AlgoRoll_box = Checkbutton(
            master=self.algorithm_frame, 
            name = "roll",
            text="Roll", 
            command = self.coil_roll,
            variable=AlgoRoll, 
            onvalue=1, 
            offvalue=0
        )
        AlgoRoll_box.var = AlgoRoll

        AlgoOrient = IntVar(master=master, name="orient")
        AlgoOrient_box = Checkbutton(
            master=self.algorithm_frame, 
            name = "orient",
            text="Orient", 
            command = self.coil_orient,
            variable=AlgoOrient, 
            onvalue=1, 
            offvalue=0
        )
        AlgoOrient_box.var = AlgoOrient

        AlgoMulti = IntVar(master=master, name="multi")
        AlgoMulti_box = Checkbutton(
            master=self.algorithm_frame, 
            name = "multi",
            text="Multi-Agent", 
            command = self.coil_multi_agent,
            variable=AlgoMulti, 
            onvalue=1, 
            offvalue=0
        )
        AlgoMulti_box.var = AlgoMulti

        AlgoPID = IntVar(master=master, name="pid")
        AlgoPID_box = Checkbutton(
            master=self.algorithm_frame, 
            name = "pid",
            text="PID", 
            command = self.coil_PID,
            variable=AlgoPID, 
            onvalue=1, 
            offvalue=0
        )
        AlgoPID_box.var = AlgoPID


        AlgoRoll_box.grid(row=1, column=0)
        AlgoOrient_box.grid(row=2, column=0)
        AlgoMulti_box.grid(row=3, column=0)
        AlgoPID_box.grid(row=4, column=0)




        #3 CHECKBOXES FRAME
        self.checkboxes_frame = Frame(master = master)
        self.checkboxes_frame.grid(row=6,column=1,rowspan = 2)

        savepickle = IntVar(master=master, name="savepickle_var")
        
        savepickle_box = Checkbutton(
            master=self.checkboxes_frame, 
            name = "savepickle",
            text="Save Pickle File", 
            variable=savepickle, 
            onvalue=1, 
            offvalue=0
        )

        savepickle_box.var = savepickle

        cuda_var = IntVar(master=master, name="cuda_var")

        cuda_button = Checkbutton(
            master=self.checkboxes_frame,
            name="cuda_checkbox",
            text="Use CUDA?",
            variable=cuda_var,
            onvalue=1,
            offvalue=0,
        )

        cuda_button.var = cuda_var
    
        savepickle_box.grid(row=0, column=0)
        cuda_button.grid(row=1, column=0)
       




        
        #4 CHOOSE VIDEO FRAME
        self.video_option_frame = Frame(master = master)
        self.video_option_frame.grid(row=3,column=2,rowspan = 2)


        run_algo_button = Button(
            self.video_option_frame,
            text="Run Algo", 
            command=self.run_algo, 
            height=1, 
            width=10,
            bg = 'yellow',
            fg= 'black'
        )
       

        vid_name = Button(
            self.video_option_frame,
            name="vid_name",
            text="Choose Video",
            command=self.upload_vid,
            height=1,
            width=10,
            bg = 'red',
            fg= 'black'
        )
        
        live_var = IntVar(master=master, name="live_var")

        livecam_button = Checkbutton(
            self.video_option_frame,
            name="live_checkbox",
            text="Use Live Cam for \nTracking?",
            variable=live_var,
            onvalue=1,
            offvalue=0,
        )
        livecam_button.var = live_var

        run_algo_button.grid(row=0, column=0)
        vid_name.grid(row=1, column=0)
        livecam_button.grid(row=2, column=0)



        #5 BIG BUTTONS

        Big_button_frame = Frame(master = master)
        Big_button_frame.grid(row=0,column=1,rowspan = 7)

        status_button = Button(
            Big_button_frame, 
            text="Stop:\nZero All Signals", 
            command=self.status, 
            height=5, 
            width=20,
            bg = 'red',
            fg= 'white'
        )

        track_button = Button(
            Big_button_frame, 
            text="Track", 
            command=self.track, 
            height=4, 
            width=20,
            bg = 'blue',
            fg= 'white'
        )

        trackall_button = Button(
            Big_button_frame, 
            text="Track All", 
            command=self.trackall, 
            height=1, 
            width=20,
            bg = "#40E0D0",
            fg= 'white'
        )


        close_button = Button(master, 
            text="Exit", 
            width=10, 
            height=4, 
            command=self.exit, 
            bg = 'black',
            fg= 'white')

        status_button.grid(row=0, column=1,rowspan =3)
        track_button.grid(row=3, column=1,rowspan=2)
        trackall_button.grid(row=5, column=1)

        close_button.grid(row=7, column=0)

        #6 GUI MAINFRAME: OTHER
        Label(master, text="---Robot List---").grid(row=0, column=4)
        

        
        coil_joystick_button.grid(row=0, column=3,rowspan =1)
        sensor_button.grid(row=1, column=3,rowspan =1)
        
        
        
        
       
        

    
        #BFIELD FRAME
        Bfield_frame = Frame(master = master)
        Bfield_frame.grid(row=3,column=0,rowspan = 2)

        Yfield_label = Label(master=Bfield_frame, text="Y", width=10)
        Yfield_label.grid(row=0, column=0)
        self.Yfield_Entry = Entry(master=Bfield_frame, width=5)
        self.Yfield_Entry.grid(row=0, column=1)
        
        Xfield_label = Label(master=Bfield_frame, text="X", width=10)
        Xfield_label.grid(row=1, column=0)
        self.Xfield_Entry = Entry(master=Bfield_frame, width=5)
        self.Xfield_Entry.grid(row=1, column=1)

        nYfield_label = Label(master=Bfield_frame, text="-Y", width=10)
        nYfield_label.grid(row=2, column=0)
        self.nYfield_Entry = Entry(master=Bfield_frame, width=5)
        self.nYfield_Entry.grid(row=2, column=1)

        nXfield_label = Label(master=Bfield_frame, text="-X", width=10)
        nXfield_label.grid(row=3, column=0)
        self.nXfield_Entry = Entry(master=Bfield_frame, width=5)
        self.nXfield_Entry.grid(row=3, column=1)

        


    def upload_vid(self):
        """
        Helper function for uploading a video to be tracked

        Args:
            None
        Returns:
            None
        """
        filename = filedialog.askopenfilename()
        self.text_box.insert(END,"Loaded: {}\n".format(filename))
        self.text_box.see("end")
        self.external_file = filename

    def coil_roll(self):
        """
        Flips the state of Rolling_Status to True when "Roll" is clicked

        Args:
            None
        Returns:
            None
        """
        STATUS_PARAMS["rolling_status"] = self.get_widget(self.algorithm_frame, "roll").var.get()
        
    def coil_orient(self):
        """
        Flips the state of Orient_Status to True when "Orient" is clicked

        Args:
            None
        Returns:
            None
        """
        STATUS_PARAMS["orient_status"] = self.get_widget(self.algorithm_frame, "orient").var.get()

    def coil_multi_agent(self):
        """
        Flips the state of "multi_agent_status" to True when "Multi-Agent" is clicked

        Args:
            None
        Returns:
            None
        """
        STATUS_PARAMS["multi_agent_status"] = self.get_widget(self.algorithm_frame, "multi").var.get()

    def coil_PID(self):
        """
        Flips the state of "pid_status" to True when "PID is clicked

        Args:
            None
        Returns:
            None
        """
        STATUS_PARAMS["PID_status"] = self.get_widget(self.algorithm_frame, "pid").var.get()


    def run_algo(self):
        """
        Flips the state of algorthm status to True when "run_algo" is clicked

        Args:
            None
        Returns:
            None
        """
        STATUS_PARAMS["algorithm_status"] = True


    def edit_closed_loop_params(self):
        """
        Creates a new window for
            Lower and Upper Threshold,
            Bounding length, Area Filter,
            Field Strength,
            Rolling Frequency,
            gamma,
            and memory

        All of the widgets and sliders are initialized here when the Edit CLosed
        Loop Paramater buttons is clicked.

        Args:
            None
        Return:
            None

        """
        window3 = Toplevel(self.main_window)
        window3.title("ControlParams")

        #cretae a frame to keep track of upper and low HSV bounds
        detection_thresh = Frame(master = window3)
        detection_thresh.pack()

        #lower
        Label(master = detection_thresh,text= "Lower Threshold (HSV)").grid(row=0,column=0,columnspan=3)
        Lower_H_Ent = Entry(master=detection_thresh, width=5)
        Lower_H_Ent.grid(row=1, column=0)
        Lower_H_Ent.delete(0,END)
        Lower_H_Ent.insert(0,(str(CONTROL_PARAMS["lower_thresh"][0])))
        Lower_S_Ent = Entry(master=detection_thresh, width=5)
        Lower_S_Ent.grid(row=1, column=1)
        Lower_S_Ent.delete(0,END)
        Lower_S_Ent.insert(0,(str(CONTROL_PARAMS["lower_thresh"][1])))
        Lower_V_Ent = Entry(master=detection_thresh, width=5)
        Lower_V_Ent.grid(row=1, column=2)
        Lower_V_Ent.delete(0,END)
        Lower_V_Ent.insert(0,(str(CONTROL_PARAMS["lower_thresh"][2])))
        
        lrgb = tuple(round(c * 255) for c in colorsys.hsv_to_rgb(int(Lower_H_Ent.get())/180, int(Lower_S_Ent.get())/255, int(Lower_V_Ent.get())/255))
       
        lower_col = Canvas(master = detection_thresh,width=20,height = 20,bg ="#%02x%02x%02x"%lrgb)
        lower_col.grid(row=1,column=3)

        #upper thresh
        Label(master = detection_thresh,text= "Upper Threshold (HSV)").grid(row=2,column=0,columnspan=3)
        Upper_H_Ent = Entry(master=detection_thresh, width=5)
        Upper_H_Ent.grid(row=3, column=0)
        Upper_H_Ent.delete(0,END)
        Upper_H_Ent.insert(0,(str(CONTROL_PARAMS["upper_thresh"][0])))
        Upper_S_Ent = Entry(master=detection_thresh, width=5)
        Upper_S_Ent.grid(row=3, column=1)
        Upper_S_Ent.delete(0,END)
        Upper_S_Ent.insert(0,(str(CONTROL_PARAMS["upper_thresh"][1])))
        Upper_V_Ent = Entry(master=detection_thresh, width=5)
        Upper_V_Ent.grid(row=3, column=2)
        Upper_V_Ent.delete(0,END)
        Upper_V_Ent.insert(0,(str(CONTROL_PARAMS["upper_thresh"][2])))

        urgb = tuple(round(c * 255) for c in colorsys.hsv_to_rgb(int(Upper_H_Ent.get())/180, int(Upper_S_Ent.get())/255, int(Upper_V_Ent.get())/255))
        upper_col = Canvas(master = detection_thresh,width=20,height = 20,bg = "#%02x%02x%02x"%urgb)
        upper_col.grid(row=3,column=3)


        def apply_thresh():
            CONTROL_PARAMS["lower_thresh"] = np.array([int(Lower_H_Ent.get()),int(Lower_S_Ent.get()),int(Lower_V_Ent.get())])
            CONTROL_PARAMS["upper_thresh"] = np.array([int(Upper_H_Ent.get()),int(Upper_S_Ent.get()),int(Upper_V_Ent.get())])

            lrgb = tuple(round(c * 255) for c in colorsys.hsv_to_rgb(int(Lower_H_Ent.get())/180, int(Lower_S_Ent.get())/255, int(Lower_V_Ent.get())/255))
            lower_col.config(bg ="#%02x%02x%02x"%lrgb)

            urgb = tuple(round(c * 255) for c in colorsys.hsv_to_rgb(int(Upper_H_Ent.get())/180, int(Upper_S_Ent.get())/255, int(Upper_V_Ent.get())/255))
            upper_col.config(bg = "#%02x%02x%02x"%urgb)
           

    

        #apply thresh
        apply_thresh_but = Button(detection_thresh, 
            text="Apply", 
            width=10, 
            height=1, 
            command=apply_thresh, 
            bg = 'black',
            fg= 'white')
        
        apply_thresh_but.grid(row=4,column=0,columnspan = 3)

        
        
        
        #handle sliders
        def update_loop_slider_values(event):
            """
            Constantly updates control_params when the sliders are used.

            Params:
                event

            Returns:
                None
            """

            #CONTROL_PARAMS["lower_thresh"] = int(lower_thresh_slider.get())
            #CONTROL_PARAMS["upper_thresh"] = int(upper_thresh_slider.get())
            CONTROL_PARAMS["blur_thresh"] = int(blur_thresh_slider.get())
            CONTROL_PARAMS["initial_crop"] = int(initial_crop_slider.get())
            CONTROL_PARAMS["tracking_frame"] = int(tracking_frame_slider.get())
            CONTROL_PARAMS["avg_bot_size"] = int(avg_bot_size_slider.get())
            CONTROL_PARAMS["field_strength"] = float(field_strength_slider.get())
            CONTROL_PARAMS["rolling_frequency"] = int(rolling_freq_slider.get())
            CONTROL_PARAMS["arrival_thresh"] = int(arrival_thresh_slider.get())
            CONTROL_PARAMS["gamma"] = int(gamma_slider.get())
            CONTROL_PARAMS["memory"] = int(memory_slider.get())

            self.main_window.update()

        #lower_thresh = DoubleVar()
        #upper_thresh = DoubleVar()
        blur_thresh = DoubleVar()
        initial_crop = DoubleVar()
        avg_bot_size = DoubleVar()
        tracking_frame = DoubleVar()
        field_strength = DoubleVar()
        rolling_frequency = DoubleVar()
        arrival_thresh = DoubleVar()
        gamma = DoubleVar()
        memory = DoubleVar()

        blur_thresh_slider = Scale(
            master=window3,
            label="blur_thresh",
            from_=1,
            to=250,
            resolution=1,
            variable=blur_thresh,
            width=20,
            length=200,
            orient=HORIZONTAL,
            command=update_loop_slider_values,
        )
        initial_crop_slider = Scale(
            master=window3,
            label="initial crop length",
            from_=10,
            to=200,
            resolution=5,
            variable=initial_crop,
            width=20,
            length=200,
            orient=HORIZONTAL,
            command=update_loop_slider_values,
        )
        tracking_frame_slider = Scale(
            master=window3,
            label="tracking frame size",
            from_=1,
            to=5,
            resolution=1,
            variable=tracking_frame,
            width=20,
            length=200,
            orient=HORIZONTAL,
            command=update_loop_slider_values,
        )
        avg_bot_size_slider = Scale(
            master=window3,
            label="~ avg size (um)",
            from_=1,
            to=200,
            resolution=1,
            variable=avg_bot_size,
            width=20,
            length=200,
            orient=HORIZONTAL,
            command=update_loop_slider_values,
        )
        field_strength_slider = Scale(
            master=window3,
            label="Field Strength",
            from_=0,
            to=1,
            digits=4,
            resolution=0.1,
            variable=field_strength,
            width=20,
            length=200,
            orient=HORIZONTAL,
            command=update_loop_slider_values,
        )
        rolling_freq_slider = Scale(
            master=window3,
            label="Rolling Frequency",
            from_=1,
            to=20,
            digits=4,
            resolution=0.5,
            variable=rolling_frequency,
            width=20,
            length=200,
            orient=HORIZONTAL,
            command=update_loop_slider_values,
        )
        arrival_thresh_slider = Scale(
            master=window3,
            label="Arrival Threshold",
            from_=1,
            to=50,
            digits=1,
            resolution=1,
            variable=arrival_thresh,
            width=20,
            length=200,
            orient=HORIZONTAL,
            command=update_loop_slider_values,
        )
        gamma_slider = Scale(
            master=window3,
            label="gamma",
            from_=0,
            to=180,
            resolution=5,
            variable=gamma,
            width=20,
            length=200,
            orient=HORIZONTAL,
            command=update_loop_slider_values,
        )
        memory_slider = Scale(
            master=window3,
            label="memory",
            from_=1,
            to=100,
            resolution=1,
            variable=memory,
            width=20,
            length=200,
            orient=HORIZONTAL,
            command=update_loop_slider_values,
        )

        #lower_thresh_slider.set(CONTROL_PARAMS["lower_thresh"])
        #upper_thresh_slider.set(CONTROL_PARAMS["upper_thresh"])
        blur_thresh_slider.set(CONTROL_PARAMS["blur_thresh"])
        initial_crop_slider.set(CONTROL_PARAMS["initial_crop"])
        tracking_frame_slider.set(CONTROL_PARAMS["tracking_frame"])
        avg_bot_size_slider.set(CONTROL_PARAMS["avg_bot_size"])
        field_strength_slider.set(CONTROL_PARAMS["field_strength"])
        rolling_freq_slider.set(CONTROL_PARAMS["rolling_frequency"])
        arrival_thresh_slider.set(CONTROL_PARAMS["arrival_thresh"])
        gamma_slider.set(CONTROL_PARAMS["gamma"])
        memory_slider.set(CONTROL_PARAMS["memory"])

        #lower_thresh_slider.pack()
        #upper_thresh_slider.pack()
        blur_thresh_slider.pack()
        initial_crop_slider.pack()
        tracking_frame_slider.pack()
        avg_bot_size_slider.pack()
        field_strength_slider.pack()
        rolling_freq_slider.pack()
        arrival_thresh_slider.pack()
        gamma_slider.pack()
        memory_slider.pack()

    def edit_camera_params(self):
        """
        Creates a new window for Window Size, Frame Rate, exposure, and
        (Whatever Object slider does) The new window is defined, initialized,
        and opened when cam_params_button button is clicked

        Args:
            None

        Returns:
            None
        """
        window4 = Toplevel(self.main_window)
        window4.title("Camera Params")

        def update_loop_slider_values(event):
            """
            Constantly updates camera_params when the sliders are used.

            Params:
                event

            Returns:
                None
            """
            CAMERA_PARAMS["resize_scale"] = int(resize_scale_slider.get())
            CAMERA_PARAMS["framerate"] = int(frame_rate_slider.get())
            CAMERA_PARAMS["exposure"] = int(exposure_slider.get())
            # CAMERA_PARAMS["exposure"] = Brightness()
            CAMERA_PARAMS["Obj"] = int(obj_slider.get())

            self.main_window.update()

        resize_scale = DoubleVar()
        frame_rate = DoubleVar()
        exposure = DoubleVar()
        obj = DoubleVar()

        resize_scale_slider = Scale(
            master=window4,
            label="Resize Scale",
            from_=1,
            to=100,
            resolution=1,
            variable=resize_scale,
            width=20,
            length=200,
            orient=HORIZONTAL,
            command=update_loop_slider_values,
        )
        frame_rate_slider = Scale(
            master=window4,
            label="Frame Rate",
            from_=1,
            to=24,
            resolution=1,
            variable=frame_rate,
            width=20,
            length=200,
            orient=HORIZONTAL,
            command=update_loop_slider_values,
        )
        exposure_slider = Scale(
            master=window4,
            label="exposure",
            from_=1,
            to=100000,
            resolution=10,
            variable=exposure,
            width=20,
            length=200,
            orient=HORIZONTAL,
            command=update_loop_slider_values,
        )
        obj_slider = Scale(
            master=window4,
            label="Obj x",
            from_=10,
            to=100,
            resolution=10,
            variable=obj,
            width=20,
            length=200,
            orient=HORIZONTAL,
            command=update_loop_slider_values,
        )

        resize_scale_slider.set(CAMERA_PARAMS["resize_scale"])
        frame_rate_slider.set(CAMERA_PARAMS["framerate"])
        exposure_slider.set(CAMERA_PARAMS["exposure"])
        obj_slider.set(CAMERA_PARAMS["Obj"])

        resize_scale_slider.pack()
        frame_rate_slider.pack()
        exposure_slider.pack()
        obj_slider.pack()



    
    def edit_acoustic_params(self):
        """
        Creates a new window to control the AD9850 Signal generator module. 
        genereates sinusoidal or square waveforms from 0-40 MHz

        Args:
            None

        Returns:
            None
        """
        window5 = Toplevel(self.main_window)
        window5.title("Acoustic Module")

        
        
        def apply_freq():
            self.AcousticModule.start(ACOUSTIC_PARAMS["acoustic_freq"],ACOUSTIC_PARAMS["acoustic_amplitude"])
            self.text_box.insert(END," -- waveform ON -- \n")
            self.text_box.see("end")
        
        def stop_freq():
            self.AcousticModule.stop()
            self.text_box.insert(END," -- waveform OFF -- \n")
            self.text_box.see("end")
        
        def test_freq():
            self.AcousticModule.start(int(10000),ACOUSTIC_PARAMS["acoustic_amplitude"])
            self.text_box.insert(END," -- 10kHz Test -- \n")
            self.text_box.see("end")
        
        def update_loop_slider_values(event):
            """
            Constantly updates acoustic params when the sliders are used.
            Params:
                event
            Returns:
                None
            """
            ACOUSTIC_PARAMS["acoustic_freq"] = int(acoustic_slider.get())
            ACOUSTIC_PARAMS["acoustic_amplitude"] = int(amplitude_slider.get())
            apply_freq()
            self.main_window.update()

        #create apply widget
        apply_button = Button(
            window5, 
            text="Apply", 
            command=apply_freq, 
            height=1, width=10,
            bg = 'blue',
            fg= 'white'
        )
        apply_button.pack()
        
        #create stop widget
        stop_button = Button(
            window5, 
            text="Stop", 
            command=stop_freq, 
            height=1, width=10,
            bg = 'red',
            fg= 'white'
        )
        stop_button.pack()

        #create test widget
        test_button = Button(
            window5, 
            text="Test 10kHz", 
            command=test_freq, 
            height=1, width=10,
            bg = 'green',
            fg= 'white'
        )

        test_button.pack()


        #create freq widget
        acoustic_frequency = DoubleVar()
        acoustic_slider = Scale(
            master=window5,
            label="Acoustic Frequency",
            from_=1000000,
            to=2000000,
            resolution=1000,
            variable=acoustic_frequency,
            width=50,
            length=1000,
            orient=HORIZONTAL,
            command=update_loop_slider_values,
        )
       
        acoustic_slider.set(ACOUSTIC_PARAMS["acoustic_freq"])        
        acoustic_slider.pack()
        
        #create amplitude widget
        acoustic_amplitude = DoubleVar()
        amplitude_slider = Scale(
            master=window5,
            label="Acoustic Amplitude",
            from_=0,
            to=5,
            resolution=.1,
            variable=acoustic_amplitude,
            width=50,
            length=1000,
            orient=HORIZONTAL,
            command=update_loop_slider_values,
        )
       
        amplitude_slider.set(ACOUSTIC_PARAMS["acoustic_amplitude"])        
        amplitude_slider.pack()
        
        def EXIT():
            self.AcousticModule.close()
            window5.destroy()
        window5.protocol("WM_DELETE_WINDOW",EXIT)
    

    def edit_pid_params(self):
        """
        Creates a new window for Window Size, Frame Rate, exposure, and
        (Whatever Object slider does) The new window is defined, initialized,
        and opened when cam_params_button button is clicked

        Args:
            None

        Returns:
            None
        """
        window6 = Toplevel(self.main_window)
        window6.title("PID Params")

        def update_pid_slider_values(event):
            """
            Constantly updates camera_params when the sliders are used.

            Params:
                event

            Returns:
                None
            """

            PID_PARAMS["Iframes"] = int(Iframes_slider.get())
            PID_PARAMS["Dframes"] = int(Dframes_slider.get())
            PID_PARAMS["Kp"] = int(Kp_slider.get())
            PID_PARAMS["Ki"] = int(Ki_slider.get())
            PID_PARAMS["Kd"] = int(Kd_slider.get())

            self.main_window.update()

        Iframes = DoubleVar()
        Dframes = DoubleVar()
        Kp = DoubleVar()
        Ki = DoubleVar()
        Kd = DoubleVar()

        Iframes_slider = Scale(
            master=window6,
            label="Iframes",
            from_=1,
            to=100,
            resolution=1,
            variable=Iframes,
            width=20,
            length=200,
            orient=HORIZONTAL,
            command=update_pid_slider_values,
        )
        Dframes_slider = Scale(
            master=window6,
            label="Dframes",
            from_=1,
            to=100,
            resolution=1,
            variable=Dframes,
            width=20,
            length=200,
            orient=HORIZONTAL,
            command=update_pid_slider_values,
        )
        Kp_slider = Scale(
            master=window6,
            label="Kp",
            from_=1,
            to=100,
            resolution=1,
            variable=Kp,
            width=20,
            length=200,
            orient=HORIZONTAL,
            command=update_pid_slider_values,
        )
        Ki_slider = Scale(
            master=window6,
            label="Ki",
            from_=1,
            to=100,
            resolution=1,
            variable=Ki,
            width=20,
            length=200,
            orient=HORIZONTAL,
            command=update_pid_slider_values,
        )
        Kd_slider = Scale(
            master=window6,
            label="Kd",
            from_=1,
            to=100,
            resolution=1,
            variable=Kd,
            width=20,
            length=200,
            orient=HORIZONTAL,
            command=update_pid_slider_values,
        )

        Iframes_slider.set(PID_PARAMS["Iframes"])
        Dframes_slider.set(PID_PARAMS["Dframes"])
        Kp_slider.set(PID_PARAMS["Kp"])
        Ki_slider.set(PID_PARAMS["Ki"])
        Kd_slider.set(PID_PARAMS["Kd"])

        Iframes_slider.pack()
        Dframes_slider.pack()
        Kp_slider.pack()
        Ki_slider.pack()
        Kd_slider.pack()


    def record(self):
        """
        Records and downloads mp4 file of tracking and live feed.

        Args:
            None

        Returns:
            None
        """
        STATUS_PARAMS["record_status"] = True

    def stop_record(self):
        """
        Stops the recording for the current video

        Args:
            None

        Returns:
            None
        """

        STATUS_PARAMS["record_status"] = False

    def track(self):
        """
        Initiates a Tracker instance for microbot tracking

        Args:
            None

        Returns:
            None
        """


        
        tracker = Tracker(self.main_window, self.text_box,
            CONTROL_PARAMS,
            CAMERA_PARAMS,
            STATUS_PARAMS,
            self.get_widget(self.checkboxes_frame, "cuda_checkbox").var.get(),
        )
        #self.tracker = tracker

        if (self.get_widget(self.video_option_frame, "live_checkbox").var.get()):
            video_name = None
        else:
            video_name = self.external_file

        output_name = str(self.get_widget(self.video_record_frame, "output_name").get())
        

        robot_list = tracker.main(video_name, self.arduino, output_name)


        
        if self.get_widget(self.checkboxes_frame, "savepickle").var.get():
            analyze = Analysis(CONTROL_PARAMS, CAMERA_PARAMS,STATUS_PARAMS,robot_list)
            analyze.convert2pickle(output_name)
            analyze.plot()

        


    def trackall(self):
        """
        Initiates a AllTracker instance for tracking all microrobots

        Args:
            None

        Returns:
            None
        """

        alltracker = AllTracker(self.main_window, self.text_box,
            CONTROL_PARAMS,
            CAMERA_PARAMS,
            STATUS_PARAMS,
            self.get_widget(self.checkboxes_frame, "cuda_checkbox").var.get()
        )
        if (self.get_widget(self.video_option_frame, "live_checkbox").var.get()):
            video_name = None
        else:
            video_name = self.external_file

        robot_list = alltracker.main(video_name)

        output_name = str(self.get_widget(self.video_record_frame, "output_name").get())

        if self.get_widget(self.checkboxes_frame, "savepickle").var.get():
            analyze = Analysis(CONTROL_PARAMS, CAMERA_PARAMS,STATUS_PARAMS,robot_list)
            analyze.convert2pickle(output_name)
            analyze.plot()


    def status(self):
        """
        Resets and zeros all status variables in tracker (i.e. zeros all outputs)

        Args:
            None

        Returns:
            None
        """
       

        STATUS_PARAMS["algorithm_status"] = False
        
        self.text_box.insert(END, "____ZEROED ____\n")
        self.text_box.see("end")

        #self.tracker.robot_window.destroy()
        self.arduino.send(4, 0, 0, 0)
        
        #shutdown hall sensor readings
        if self.sensor is not None:
            self.sensor.shutdown()
            self.main_window.after_cancel(self.checksensor)
          
        
        if self.joystick is not None:
            self.joystick.shutdown()
            self.main_window.after_cancel(self.checkjoy)
       
            

    

    def get_widget(self, window: Union[Tk, Toplevel], widget_name: str) -> Widget:
        """
        Gets a widget in the main window by name

        Args:
            widget_name:    name of the desired widget on the main window

        Returns:
            None
        """
        try:
            return window.nametowidget(widget_name)
        except KeyError:
            raise KeyError(f"Cannot find widget named {widget_name}")



    

    def joy_proc(self):
        """
        creates an instance of JoystickProcess class and starts a subprocess to read values

        Args:
            None
        Returns:
            None
        """
        self.joystick = JoystickProcess()
        self.joystick.start(self.joystick_q)
        self.checkjoy = self.main_window.after(10, self.CheckJoystickPoll, self.joystick_q)

    
    def CheckJoystickPoll(self,j_queue):
        """
        checks the joystick queue for incoming command values

        Args:
            c_queue: queue object
            joy_array: [typ, input1, input2, input3]
            input1(typ1 | typ2) = angle|  Bx
            input2(typ1 | typ2) = freq | By
            input3(typ1 | typ2) = gamma | Bz
        Returns:
            None
        """
        try:
            joy_array = j_queue.get(0) # [typ,input1,input2,input3]
            typ = joy_array[0]
            
            #Send arduino signal
            if typ == 1:
                #gamma toggle logic.
                if joy_array[3] == 0:
                    self.arduino.send(typ, joy_array[1], CONTROL_PARAMS["rolling_frequency"], joy_array[3]) #use gamma = 0
                else: 
                    self.arduino.send(typ, joy_array[1], CONTROL_PARAMS["rolling_frequency"], CONTROL_PARAMS["gamma"])
            else:
                self.arduino.send(typ, joy_array[1], joy_array[2], joy_array[3]) 
                
            #A Button Function --> Acoustic Module Toggle
            self.button_state = joy_array[4]
            if self.button_state != self.last_state:
                if self.button_state == True:
                    self.counter +=1
            self.last_state = self.button_state
            if self.counter %2 != 0 and self.switch_state !=0:
                self.switch_state = 0
                self.AcousticModule.start(ACOUSTIC_PARAMS["acoustic_freq"],ACOUSTIC_PARAMS["acoustic_amplitude"])
                self.text_box.insert(END, " -- waveform ON -- \n")
                self.text_box.see("end")
                #print("acoustic: on")
            elif self.counter %2 == 0 and self.switch_state !=1:
                self.switch_state = 1
                self.AcousticModule.stop()
                self.text_box.insert(END, " -- waveform OFF -- \n")
                self.text_box.see("end")

        except Empty:
            pass
        finally:
            self.main_window.after(10,self.CheckJoystickPoll, j_queue)


    def sensor_proc(self):
        """
        creates an instance of HallEffect class and starts a subprocess to read values

        Args:
            None
        Returns:
            None
        """
        self.sensor = HallEffect()
        self.sensor.start(self.sense_q)
        self.checksensor = self.main_window.after(10, self.CheckSensorPoll, self.sense_q)
    
    def CheckSensorPoll(self,s_queue):
        """
        checks the hall effect sensor queue for incoming sensors values

        Args:
            c_queue: queue object
        Returns:
            None
        """
        try:
            value_array = s_queue.get(0) # [s1,s2,s3,s4]
            
            #update Yfield
            self.Yfield_Entry.delete(0,END)
            self.Yfield_Entry.insert(0,"{}".format(value_array[0])) 

            #update Xfield
            self.Xfield_Entry.delete(0,END)
            self.Xfield_Entry.insert(0,"{}".format(value_array[1])) 

            #update nYfield
            self.nYfield_Entry.delete(0,END)
            self.nYfield_Entry.insert(0,"{}".format(value_array[2]))

            #update nXfield
            self.nXfield_Entry.delete(0,END)
            self.nXfield_Entry.insert(0,"{}".format(value_array[3]))
        except Empty:
            pass
        finally:
            self.main_window.after(10,self.CheckSensorPoll, s_queue)
    
   
    def exit(self):
        """
        Quits the main window (self.main_window) and quits the ardunio connection
            exit()

        Args:
            None

        Returns:
            None
        """
        self.AcousticModule.exit()
        self.main_window.quit()
        self.main_window.destroy()
        self.arduino.close()


    def main(self) -> None:
        """
        Starts the tkinter GUI by opening up the main window
        continously displays magnetic field values if checked

        Args:
            None

        Returns:
            None
        """
        self.main_window.mainloop()
