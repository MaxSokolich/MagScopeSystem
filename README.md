# MagScopeSystem
a repository consisting of all scripts neccesary to use the mag scope system. The magscope system is an edge computing platform and custom device capable of a variety of microrobotic manipulation operations. The device consists of a single board computer (Jetson Xavier NX) with a python GUI used to control various manipulation setups. 
These setups include:
1) 3D Helmholtz Coils
2) 3D UV LED array
3) Acoustic Piezoelectric Transducers
4) 2D/3D Magnetic Tweezers

# To Add:
Overall:
- Electrical Schematic
- CAD Models and Figures
- Bill of Materials.
- Continue on Bugs.
- Custom Microscope and Coil Files


Code Specific:
-test 3D tracking, add Z position, improve z tracking, figure out blur with new hsv 
-maybe get ps5 controller working. need to figure out how to read it from usb
-fix acoustic digitial potentiameter mapping
-try and record video on seperate CPU/process using file in tests folder
-add error_threshold param slider for algorthms

# Instructions for initial installation of system components:
1) need to configure nvme ssd using nvidia sdkmanager:  
    - https://developer.nvidia.com/embedded/learn-get-started-jetson-agx-orin-devkit

2) need to build opencv with cuda support: 
    - https://github.com/mdegans/nano_build_opencv.git

3) need to add permissions in order to read and write to the arduino port: 
    - add this to /etc/rc.local to execute on boot: $ chmod 666 /dev/ttyACM0
3.5)  need to install qt5
    - sudo apt install qtbase5-dev qtchooser qt5-qmake qtbase5-dev-tools  

4) need to install Spinnaker FLIR camera SDK and python API: 
    - https://flir.app.boxcn.net/v/SpinnakerSDK/file/1093743440079
    - may need: sudo apt-mark manual qtbase5-dev qtchooser qt5-qmake qtbase5-dev-tools for spinview 

5) need to install all python dependencies
    - python3.8 -m pip install -r JetsonOrinReqs.txt

6) need to add "self.cam.PixelFormat.SetValue(PySpin.PixelFormat_BGR8)" above self.cam.BeginAcquistion() line in $ .local/lib/python3.8/site-packages/EasyPySpin.videocapture.py

7) need to install xboxdrv and jstest-gtk for joystick implimentation 
        $ sudo apt-get install -y xboxdrv         
        "https://github.com/FRC4564/Xbox"
    


**MagScope Electrical System Components** 
![alt text](https://github.com/MaxSokolich/MagScopeSystem/blob/main/src/imgs/MagScopeBox2.png?raw=true)

**Example Analysis**
--Example analysis plot from custom tracking algorithm. Displays selected robot trajectories, individial robot velocties and robot sizes--
![alt text](https://github.com/MaxSokolich/MagScopeSystem/blob/main/src/imgs/ExampleDataPlot.png?raw=true)


Max Sokolich - 2023
