import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import style
plt.style.use('dark_background')
obj = pd.read_pickle("/home/max/Documents/MagScopeSystem/.pickle")


Vel_list = []
Size_list = []

bots = []
cm_subsection = np.linspace(0,len(obj),100)
color = [plt.cm.jet(x) for x in cm_subsection]
fig, ax = plt.subplots(3,1)



for i,c in zip(range(len(obj)),color):
    robot = obj[i]
    time = robot["Times"]
    print(time)
    frames = robot["Frame"]
    X = robot["PositionX"]
    Y = robot["PositionY"]
    VX = robot["VelX"]
    VY = robot["VelY"]
    VZ = robot["VelZ"]
    Vmag = robot["VMag"]
    Area = robot["Avg Area"]
    Size = np.sqrt(4*Area/np.pi)
    
    if len(Vmag) != 0:
        Vel = sum(Vmag)/len(Vmag)
        print(Vel)
        Vel_list.append(Vel)
        Size_list.append(Size)
    
        ax[0].plot(X,Y,color =c,linewidth = 4)
        ax[1].bar(i,Vel,color =c)
        ax[2].bar(i, Size,color =c)



ax[0].set_title("trajectories")
ax[0].invert_yaxis()
ax[0].set_xlabel("X")
ax[0].set_xlabel("Y")


ax[1].set_title("average velocity: {}um/s".format(round(np.mean(Vel_list),2)))
ax[1].set_xlabel("MR")
ax[1].axhline(np.mean(Vel_list), color = "w", linewidth=4)

ax[2].set_title("average size:{}um".format(round(np.mean(Size_list),2)))
ax[2].set_xlabel("MR")
ax[2].axhline(np.mean(Size_list), color = "w", linewidth = 4)

plt.show()
