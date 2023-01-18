#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module containing the GUI class

@authors: Max Sokolich, Brennan Gallamoza, Luke Halko, Trea Holley,
          Alexis Mainiero, Cameron Thacker, Zoe Valladares
"""

from typing import Union
from tkinter import *
from tkinter import Tk
from tkinter import filedialog
from src.classes.Custom2DTracker import Tracker
from src.classes.ArduinoHandler import ArduinoHandler
from src.classes.Brightness import Brightness

# from pyspin import PySpin
# import EasyPySpin

CONTROL_PARAMS = {
    "lower_thresh": 0,
    "upper_thresh": 130,
    "bounding_length": 10,
    "area_filter": 3,
    "field_strength": 1,
    "rolling_frequency": 10,
    "gamma": 90,
    "memory": 50,
}

# pix = 1936 x 1464
# maxframerate = 130
# exptime = 10us - 30s
# iamge buffer = 240 MB
CAMERA_PARAMS = {"resize_scale": 50, "framerate": 20, "exposure": 5000, "Obj": 10}

STATUS_PARAMS = {
    "rolling_status": False,
    "orient_status": False,
    "record_status": False,
    "joystick_status":False,
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

        # Tkinter widget attributes
        self.text_box = Text(master, width=22, height=1)
        self.scroll_bar = Scrollbar(
            master, command=self.text_box.yview, orient="vertical"
        )
        self.text_box.configure(yscrollcommand=self.scroll_bar.set)

        # Tracker-related attributes
        self.arduino = arduino
        self.external_file = None

        coil_roll_button = Button(
            master, text="Rotate On", command=self.coil_roll, height=1, width=20
        )

        coil_orient_button = Button(
            master, text="Orient On", command=self.coil_orient, height=1, width=20
        )

        coil_joystick_button = Button(
            master, text="Joystick On", command=self.coil_joystick, height=1, width=20
        )

        savepickle = IntVar(master=master, name="savepickle_var")
        savepickle_box = Checkbutton(
            master, name = "savepickle",text="Save Pickle File", variable=savepickle, onvalue=1, offvalue=0
        )

        savepickle_box.var = savepickle

        closed_loop_params_button = Button(
            master,
            text="Edit Control Params",
            command=self.edit_closed_loop_params,
            height=1,
            width=20,
        )

        cam_params_button = Button(
            master,
            text="Edit Camera Params",
            command=self.edit_camera_params,
            height=1,
            width=20,
        )

        Label(master, text="Video Name").grid(row=2, column=3)
        vid_name = Button(
            master,
            name="vid_name",
            text="Choose Video",
            command=self.upload_vid,
            height=1,
            width=10,
        )

        Label(master, text="Output Name").grid(row=3, column=3)
        output_name = Entry(master, name="output_name")
        output_name.insert(10, "")

        record_button = Button(
            master, text="Record", command=self.record, height=1, width=10
        )

        stop_record_button = Button(
            master, text="Stop Record", command=self.stop_record, height=1, width=10
        )

        live_button = Button(master, text="Live", command=self.live, height=1, width=20)
        track_button = Button(
            master, text="Track", command=self.track, height=1, width=20
        )

        status_button = Button(
            master, text="Stop", command=self.status, height=1, width=10
        )

        show_b_button = Button(
            master, text="Show BFields (mT)", command=self.show_b, height=1, width=20
        )
        close_button = Button(master, text="Exit", width=5, height=1, command=self.exit)

        cuda_var = IntVar(master=master, name="cuda_var")

        cuda_button = Checkbutton(
            master,
            name="cuda_checkbox",
            text="Use CUDA?",
            variable=cuda_var,
            onvalue=1,
            offvalue=0,
        )

        cuda_button.var = cuda_var

        live_var = IntVar(master=master, name="live_var")

        livecam_button = Checkbutton(
            master,
            name="live_checkbox",
            text="Use Live Cam for Tracking?",
            variable=live_var,
            onvalue=1,
            offvalue=0,
        )

        livecam_button.var = live_var
        
        trackall_var = IntVar(master=master, name="trackall_var")

        trackall_button = Checkbutton(
            master,
            name="trackall_checkbox",
            text="TRACK ALL",
            variable=trackall_var,
            onvalue=1,
            offvalue=0,
        )

        trackall_button.var = trackall_var
        # WINDOW 1: GUI MAINFRAME
        closed_loop_params_button.grid(row=0, column=0)
        cam_params_button.grid(row=1, column=0)
        show_b_button.grid(row=2, column=0)
        live_button.grid(row=1, column=2)
        coil_roll_button.grid(row=1, column=1)
        coil_orient_button.grid(row=0, column=1)
        coil_joystick_button.grid(row=3, column=1)
        record_button.grid(row=2, column=1)
        stop_record_button.grid(row=2, column=2)
        vid_name.grid(row=2, column=4)
        savepickle_box.grid(row=0, column=4)
        track_button.grid(row=1, column=3)
        status_button.grid(row=1, column=4)
        close_button.grid(row=3, column=5)
        livecam_button.grid(row=2, column=5)
        self.text_box.grid(row=0, column=5, rowspan=2, sticky="nwse")
        output_name.grid(row=3, column=4)
        cuda_button.grid(row=3, column=0)
        trackall_button.grid(row=0,column= 3)

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

    def coil_joystick(self):
        """
        Flips the state of joystick_Status to True when "joystick On" is clicked

        Args:
            None
        Returns:
            None
        """
        STATUS_PARAMS["joystick_status"] = True

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
            CONTROL_PARAMS["bounding_length"] = int(bounding_length_slider.get())
            CONTROL_PARAMS["area_filter"] = int(area_filter_slider.get())
            CONTROL_PARAMS["field_strength"] = float(field_strength_slider.get())
            CONTROL_PARAMS["rolling_frequency"] = int(rolling_freq_slider.get())
            CONTROL_PARAMS["gamma"] = int(gamma_slider.get())
            CONTROL_PARAMS["memory"] = int(memory_slider.get())

            self.main_window.update()

        lower_thresh = DoubleVar()
        upper_thresh = DoubleVar()
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
            to=100,
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
        bounding_length_slider.set(CONTROL_PARAMS["bounding_length"])
        area_filter_slider.set(CONTROL_PARAMS["area_filter"])
        field_strength_slider.set(CONTROL_PARAMS["field_strength"])
        rolling_freq_slider.set(CONTROL_PARAMS["rolling_frequency"])
        gamma_slider.set(CONTROL_PARAMS["gamma"])
        memory_slider.set(CONTROL_PARAMS["memory"])

        lower_thresh_slider.pack()
        upper_thresh_slider.pack()
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
            to=130,
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
            to=50,
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

    def live(self):
        """
        Opens and window for the live or pre-recorded screen of the microbots.

        Args:
            None

        Returns:
            None
        """

        self.track(use_live_button=True, enable_tracking=False)

    def track(self, use_live_button: bool = False, enable_tracking: bool = True):
        """
        Initiates a Tracker instance for microbot tracking

        Args:
            None

        Returns:
            None
        """
        tracker = Tracker(
            CONTROL_PARAMS,
            CAMERA_PARAMS,
            STATUS_PARAMS,
            self.get_widget(self.main_window, "cuda_checkbox").var.get(),
        )
        if (
            use_live_button
            or self.get_widget(self.main_window, "live_checkbox").var.get()
        ):
            video_name = None
        else:
            video_name = self.external_file

        output_name = str(self.get_widget(self.main_window, "output_name").get())
        
        #track all robots if the widget is checked(true)
        if self.get_widget(self.main_window, "trackall_checkbox").var.get():
            tracker.create_robotlist(video_name)

        tracker.single_bot_thread(
            video_name, self.arduino, self.main_window, enable_tracking, output_name
        )

        if self.get_widget(self.main_window, "savepickle").var.get():
    
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
        STATUS_PARAMS["joystick_status"] = False
        print(" -- Orient OFF -- ")
        print(" -- Roll OFF -- ")
        print(" -- Joystick OFF -- ")
        self.text_box.insert(END, "Zeroed\n")
        self.text_box.see("end")

    def show_b(self):
        """
        Creates a new window for XYZ and -X-Y-Z terminal inputs.

        Args:
            None

        Returns:
            None
        """
        global Yfield_Entry, Xfield_Entry, Zfield_Entry, nYfield_Entry, nXfield_Entry, nZfield_Entry
        window5 = Toplevel(self.main_window)
        window5.title("Bfields")

        Xfield_label = Label(master=window5, text="X", width=10)
        Xfield_label.grid(row=0, column=0)
        Xfield_Entry = Entry(master=window5, width=5)
        Xfield_Entry.grid(row=0, column=1)

        Yfield_label = Label(master=window5, text="Y", width=10)
        Yfield_label.grid(row=1, column=0)
        Yfield_Entry = Entry(master=window5, width=5)
        Yfield_Entry.grid(row=1, column=1)

        Zfield_label = Label(master=window5, text="Z", width=10)
        Zfield_label.grid(row=2, column=0)
        Zfield_Entry = Entry(master=window5, width=5)
        Zfield_Entry.grid(row=2, column=1)

        nXfield_label = Label(master=window5, text="-X", width=10)
        nXfield_label.grid(row=3, column=0)
        nXfield_Entry = Entry(master=window5, width=5)
        nXfield_Entry.grid(row=3, column=1)

        nYfield_label = Label(master=window5, text="-Y", width=10)
        nYfield_label.grid(row=4, column=0)
        nYfield_Entry = Entry(master=window5, width=5)
        nYfield_Entry.grid(row=4, column=1)

        nZfield_label = Label(master=window5, text="-Z", width=10)
        nZfield_label.grid(row=5, column=0)
        nZfield_Entry = Entry(master=window5, width=5)
        nZfield_Entry.grid(row=5, column=1)

        self.main_window.update()

    def exit(self):
        """
        Quits the main window (self.main_window) and quits the ardunio connection
            exit()

        Args:
            None

        Returns:
            None
        """
        self.main_window.quit()
        self.main_window.destroy()
        self.arduino.close()

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

    def main(self) -> None:
        """
        Starts the tkinter GUI by opening up the main window

        Args:
            None

        Returns:
            None
        """
        self.main_window.mainloop()
