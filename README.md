# MagScopeSystem
a repository consisting of all scripts neccesary to use the mag scope system. The magscope system is an edge computing platform and custom device capable of a variety of microrobotic manipulation operations. The device consists of a single board computer (Jetson Xavier NX) with a python GUI used to control various manipulation setups. 
These setups include:
1) 3D Helmholtz Coils
2) 3D UV LED array
3) Acoustic Piezoelectric Transducers
4) 2D/3D Magnetic Tweezers

TO ADD:
- Electrical Schematic
- CAD Models and Figures
- Code Flowcharts
- Bill of Materials
- Updated Reqs.txt
- Continue on Bugs.

Instructions for initial installation of all modules:
- need to add permissions to the arduino port. add this to /etc/rc.local to execute on boot: $ chmod 666 /dev/ttyACM0
- need to add "self.cam.PixelFormat.SetValue(PySpin.PixelFormat_BGR8)" above self.cam.BeginAcquistion() line in $ .local/lib/python3.8/site-packages/EasyPySpin.videocapture.py
- need to install Spinnaker FLIR camera SDK and python API: https://flir.app.boxcn.net/v/SpinnakerSDK/file/1093743440079
- need to install xboxdrv and jstest-gtk for joystick implimentation $ sudo apt-get install -y xboxdrv         "https://github.com/FRC4564/Xbox"
               also needed for jstest-gtk $ sudo apt-get install libcanberra-gtk-module
- need sudo apt-mark manual qtbase5-dev qtchooser qt5-qmake qtbase5-dev-tools for spinview 

--Example analysis plot from custom tracking algorithm. Displays selected robot trajectories, individial robot velocties and robot sizes--
![alt text](https://github.com/MaxSokolich/MagScopeSystem/blob/main/src/imgs/ExampleDataPlot.png?raw=true)




Max Sokolich
