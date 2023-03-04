#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module containing the GUI class

@authors: Max Sokolich, Brennan Gallamoza, Luke Halko, Trea Holley,
          Alexis Mainiero, Cameron Thacker, Zoe Valladares
pix = 1936 x 1464
maxframerate = 130
exptime = 10us - 30s
iamge buffer = 240 MB
"""
from queue import Empty
import multiprocessing
import time as time
import numpy as np
from typing import Union
from tkinter import *
from tkinter import Tk
from tkinter import filedialog
from src.classes.AcousticClass import AcousticClass
from src.classes.HallEffect import HallEffect
from src.classes.Custom2DTracker import Tracker
from src.classes.ArduinoHandler import ArduinoHandler
from src.classes.Brightness import Brightness
from src.classes.JoystickProcess import JoystickProcess



# from pyspin import PySpin
# import EasyPySpin

CONTROL_PARAMS = {
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

STATUS_PARAMS = {
    "rolling_status": False,
    "orient_status": False,
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
        self.sense_q = multiprocessing.Queue()
        self.sense_q.cancel_join_thread()
        self.main_window.after(10, self.CheckSensorPoll, self.sense_q)

        #update joystick process/queue
        self.joystick = None
        self.joystick_q =  multiprocessing.Queue()
        self.joystick_q.cancel_join_thread()
        self.main_window.after(10, self.CheckJoystickPoll, self.joystick_q)

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

        

        coil_roll_button = Button(
            master, 
            text="Rotate On", 
            command=self.coil_roll, 
            height=1, 
            width=18,
            bg = 'green2',
            fg= 'black'
        )

        coil_orient_button = Button(
            master, 
            text="Orient On", 
            command=self.coil_orient, 
            height=1, 
            width=18,
            bg = 'green4',
            fg= 'white'
        )

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
        

        
       

        #3 CHECKBOXES FRAME

        self.checkboxes_frame = Frame(master = master)
        self.checkboxes_frame.grid(row=7,column=1,rowspan = 2)

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
        
        trackall_var = IntVar(master=master, name="trackall_var")

        trackall_button = Checkbutton(
            master=self.checkboxes_frame,
            name="trackall_checkbox",
            text="TRACK ALL",
            variable=trackall_var,
            onvalue=1,
            offvalue=0,
        )

        trackall_button.var = trackall_var

        savepickle_box.grid(row=0, column=0)
        cuda_button.grid(row=1, column=0)
        trackall_button.grid(row=2,column= 0)




        
        #CHOOSE VIDEO FRAME
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
            bg = 'white',
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



        #3 BIG BUTTONS
        track_button = Button(
            master, 
            text="Track", 
            command=self.track, 
            height=5, 
            width=20,
            bg = 'blue',
            fg= 'white'
        )

        
        status_button = Button(
            master, 
            text="Stop:\nZero All Signals", 
            command=self.status, 
            height=5, 
            width=20,
            bg = 'red',
            fg= 'white'
        )

        close_button = Button(master, 
            text="Exit", 
            width=10, 
            height=4, 
            command=self.exit, 
            bg = 'black',
            fg= 'white')


        track_button.grid(row=3, column=1,rowspan=3)
        status_button.grid(row=0, column=1,rowspan =3)
        close_button.grid(row=7, column=0)

        # GUI MAINFRAME: OTHER
        Label(master, text="---Robot List---").grid(row=0, column=4)
        
        
        closed_loop_params_button.grid(row=0, column=0)
        cam_params_button.grid(row=1, column=0)
        acoustic_params_button.grid(row=2, column=0)

        
        
        coil_roll_button.grid(row=0, column=2)
        coil_orient_button.grid(row=1, column=2)
        coil_joystick_button.grid(row=0, column=3,rowspan =1)
        sensor_button.grid(row=1, column=3,rowspan =1)
        
        
        
        

        
       
        

    
        #BFIELD FRAME
        Bfield_frame = Frame(master = master)
        Bfield_frame.grid(row=3,column=0,rowspan = 3)

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
        print("Loaded:",filename)
        self.external_file = filename

    def coil_roll(self):
        """
        Flips the state of Rolling_Status to True when "Rotate On" is clicked

        Args:
            None
        Returns:
            None
        """
        STATUS_PARAMS["rolling_status"] = True

    def coil_orient(self):
        """
        Flips the state of Orient_Status to True when "Orient On" is clicked

        Args:
            None
        Returns:
            None
        """
        STATUS_PARAMS["orient_status"] = True

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
        window3.title("ClosedLoop Params")

        def update_loop_slider_values(event):
            """
            Constantly updates control_params when the sliders are used.

            Params:
                event

            Returns:
                None
            """

            CONTROL_PARAMS["lower_thresh"] = int(lower_thresh_slider.get())
            CONTROL_PARAMS["upper_thresh"] = int(upper_thresh_slider.get())
            CONTROL_PARAMS["blur_thresh"] = int(blur_thresh_slider.get())
            CONTROL_PARAMS["bounding_length"] = int(bounding_length_slider.get())
            CONTROL_PARAMS["area_filter"] = int(area_filter_slider.get())
            CONTROL_PARAMS["field_strength"] = float(field_strength_slider.get())
            CONTROL_PARAMS["rolling_frequency"] = int(rolling_freq_slider.get())
            CONTROL_PARAMS["gamma"] = int(gamma_slider.get())
            CONTROL_PARAMS["memory"] = int(memory_slider.get())

            self.main_window.update()

        lower_thresh = DoubleVar()
        upper_thresh = DoubleVar()
        blur_thresh = DoubleVar()
        bounding_length = DoubleVar()
        area_filter = DoubleVar()
        field_strength = DoubleVar()
        rolling_frequency = DoubleVar()
        gamma = DoubleVar()
        memory = DoubleVar()

        lower_thresh_slider = Scale(
            master=window3,
            label="lower_thresh",
            from_=1,
            to=255,
            resolution=1,
            variable=lower_thresh,
            width=20,
            length=200,
            orient=HORIZONTAL,
            command=update_loop_slider_values,
        )
        upper_thresh_slider = Scale(
            master=window3,
            label="upper_thresh",
            from_=1,
            to=255,
            resolution=1,
            variable=upper_thresh,
            width=20,
            length=200,
            orient=HORIZONTAL,
            command=update_loop_slider_values,
        )
        blur_thresh_slider = Scale(
            master=window3,
            label="blur_thresh",
            from_=50,
            to=250,
            resolution=1,
            variable=blur_thresh,
            width=20,
            length=200,
            orient=HORIZONTAL,
            command=update_loop_slider_values,
        )
        bounding_length_slider = Scale(
            master=window3,
            label="bounding length",
            from_=10,
            to=200,
            resolution=5,
            variable=bounding_length,
            width=20,
            length=200,
            orient=HORIZONTAL,
            command=update_loop_slider_values,
        )
        area_filter_slider = Scale(
            master=window3,
            label="area filter",
            from_=1,
            to=5,
            resolution=1,
            variable=area_filter,
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

        lower_thresh_slider.set(CONTROL_PARAMS["lower_thresh"])
        upper_thresh_slider.set(CONTROL_PARAMS["upper_thresh"])
        blur_thresh_slider.set(CONTROL_PARAMS["blur_thresh"])
        bounding_length_slider.set(CONTROL_PARAMS["bounding_length"])
        area_filter_slider.set(CONTROL_PARAMS["area_filter"])
        field_strength_slider.set(CONTROL_PARAMS["field_strength"])
        rolling_freq_slider.set(CONTROL_PARAMS["rolling_frequency"])
        gamma_slider.set(CONTROL_PARAMS["gamma"])
        memory_slider.set(CONTROL_PARAMS["memory"])

        lower_thresh_slider.pack()
        upper_thresh_slider.pack()
        blur_thresh_slider.pack()
        bounding_length_slider.pack()
        area_filter_slider.pack()
        field_strength_slider.pack()
        rolling_freq_slider.pack()
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
            print(" -- waveform ON --")
        
        def stop_freq():
            self.AcousticModule.stop()
            print(" -- waveform OFF --")
        
        def test_freq():
            self.AcousticModule.start(int(10000),ACOUSTIC_PARAMS["acoustic_amplitude"])
            print(" -- waveform TEST --")
        
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

    def track(self, enable_tracking: bool = True):
        """
        Initiates a Tracker instance for microbot tracking

        Args:
            None

        Returns:
            None
        """


        
        tracker = Tracker(
            self.main_window,
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
        
        #track all robots if the widget is checked(true)
        if self.get_widget(self.checkboxes_frame, "trackall_checkbox").var.get():
            tracker.create_robotlist(video_name)

        tracker.single_bot_thread(video_name, self.arduino, output_name)
        
        if self.get_widget(self.checkboxes_frame, "savepickle").var.get():
            tracker.convert2pickle(output_name)

        


        

    def status(self):
        """
        Resets and zeros all status variables in tracker (i.e. zeros all outputs)

        Args:
            None

        Returns:
            None
        """
       

        STATUS_PARAMS["rolling_status"] = False
        STATUS_PARAMS["orient_status"] = False
        STATUS_PARAMS["algorithm_status"] = False
        print(" -- Orient OFF -- ")
        print(" -- Roll OFF -- ")
        print(" -- Algorithm OFF --")
        
        self.text_box.insert(END, "Zeroed\n")
        self.text_box.see("end")

        #self.tracker.robot_window.destroy()
        
        #shutdown hall sensor readings
        if self.sensor is not None:
            self.sensor.shutdown()
        
        if self.joystick is not None:
            self.joystick.shutdown()
            

    

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
                self.text_box.insert(END, "acoustic on\n")
                self.text_box.see("end")
                #print("acoustic: on")
            elif self.counter %2 == 0 and self.switch_state !=1:
                self.switch_state = 1
                self.AcousticModule.stop()
                self.text_box.insert(END, "acoustic off\n")
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
