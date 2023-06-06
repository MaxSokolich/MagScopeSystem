private repository: https://github.com/MaxSokolich/MagScopeSystem/
NOTE: a seperate repo is to be created that includes all scripts to control the custom 3D stage/microscope setup. 

# MagScope System
a repository consisting of all scripts neccesary to use the mag scope system. The magscope system is an edge computing platform and custom device capable of a variety of microrobotic manipulation operations. The device consists of a single board computer (Jetson AGX Orin) with a python GUI used to control various manipulation setups. The system is named MagScope which combines the words magnetic and microscope. 

These manipulation setups include:
1) 3D Helmholtz Coils
2) 3D UV LED array
3) Acoustic Piezoelectric Transducers
4) 2D/3D Magnetic Tweezers
5) Electro-Osmotic Pumps using Copper Tape

The overall cost of the system excluding a manipulation setup is around $6000 (see CAD_MODELS/Bill_of_Materials.txt) as opposed to $28,000 from a company named MangetobotIx out of Switzerland. Including their magnetic manipulation setup, the total cost for there system is $60,228. This number still excludes a microscope. 

If only trying to track microrobots or use the PS4Controller, see the seperate folders TrackerProcess and ControllerProcess

# To Add:
Overall:
- Electrical Schematic
- CAD Models and Figures
- Bill of Materials.
- Continue on Bugs.
- Custom Microscope and Coil Files

**MagScope Electrical System Components** 
![alt text](https://github.com/MaxSokolich/MagScopeSystem/blob/main/src/imgs/MagScopeBox2.png?raw=true)

**MagScope Control GUI**
![alt text](https://github.com/MaxSokolich/MagScopeSystem/blob/main/src/imgs/MicrorobotTrackingGui.png?raw=true)

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

4)  need to install qt5
    - sudo apt install qtbase5-dev qtchooser qt5-qmake qtbase5-dev-tools  
    - sudo apt install qt5-default

5) need to install Spinnaker FLIR camera SDK and python API: 
    - https://flir.app.boxcn.net/v/SpinnakerSDK/file/1093743440079
    - may need: sudo apt-mark manual qtbase5-dev qtchooser qt5-qmake qtbase5-dev-tools for spinview 

6) need to install all python dependencies
    - python3.8 -m pip install -r JetsonOrinReqs.txt

7) need to add "self.cam.PixelFormat.SetValue(PySpin.PixelFormat_BGR8)" above self.cam.BeginAcquistion() line in $ .local/lib/python3.8/site-packages/EasyPySpin.videocapture.py

8) need to change in lib/python3.8/site-packages/adafruit_blinka/microcontroller/tegra/t234/pin.py from "GPIO.setmode(GPIO.TEGRA_SOC)" to GPIO.setmode(GPIO.BOARD)
    - otherwise the acoustic class and hall effect class will clash

9) need to install xboxdrv and jstest-gtk for joystick implimentation 
        $ sudo apt-get install -y xboxdrv         
        "https://github.com/FRC4564/Xbox"
        
10) VSCode: https://github.com/JetsonHacksNano/installVSCode.git

11) optional: install arduino using jetsonhacks github and upload main.ino from src/arduino


    




**Example Analysis**
--Example analysis plot from custom tracking algorithm. Displays selected robot trajectories, individial robot velocties and robot sizes--
![alt text](https://github.com/MaxSokolich/MagScopeSystem/blob/main/src/imgs/ExampleDataPlot.png?raw=true)


Max Sokolich - 2023
