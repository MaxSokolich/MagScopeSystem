
import numpy as np
import matplotlib.pyplot as plt
import pickle
from tqdm import tqdm
import pandas as pd
from mpl_toolkits import mplot3d
plt.style.use('dark_background')


class Analysis:
    def __init__(self,
                 control_params: dict,
                 camera_params: dict,
                 status_params: dict,
                 robot_list):
        self.control_params = control_params
        self.camera_params = camera_params
        self.status_params = status_params
        self.robot_list = robot_list


        self.width = 2448
        self.height = 2048
        self.resize_scale = self.camera_params["resize_scale"]
        self.resize_ratio = (
                self.width * self.resize_scale // 100,
                self.height * self.resize_scale // 100,
            )
        self.pix2metric = ((self.resize_ratio[1]/106.2)  / 100) * self.camera_params["Obj"] 

    def convert2pickle(self, filename: str):
            """
            Converts recorded microbot tracking info into a pickle file for storage.

            Args:
                filename:   name of output file

            Returns:
                None
            """
            
            pickles = []
            print(" --- writing robots ---")
            for bot in tqdm(self.robot_list):
                if len(bot.area_list) > 1:
                    pickles.append(bot.as_dict())
            filename = "src/data/"+filename
            print(" -- writing pickle --")
            with open(filename + ".pickle", "wb") as handle:
                pickle.dump(pickles, handle, protocol=pickle.HIGHEST_PROTOCOL)
            print(" -- ({}.pickle) DONE -- ".format(filename))



    def plot(self):
            """
            ##ADD 3D PLOT of TRAJECTORIES
            Plot all trajectories from each robot using matplotlib

            Args:
                self: the class itself
            Returns:
                None
            """
            print(" -- PLOTTING -- ")
            color = plt.cm.rainbow(np.linspace(0, 1, len(self.robot_list)))
          

            _, ax = plt.subplots(3,1, figsize=(5, 8))
            _,ax2 = plt.subplots(1,1, figsize=(8, 8))
            ax2 = plt.axes(projection = '3d')
            #xx, yy = np.meshgrid(range(400), range(400))
            #zz = yy*0
            #ax2.plot_surface(xx, yy, zz)


            Vel_list = []
            Size_list= [1]
            max_z = 0
            global_max_vel = 0
            for i, c in zip(range(len(self.robot_list)), color):
                bot = self.robot_list[i]
                if len(bot.frame_list) > 10:

                    #ADD 2D PLOT
                    X = np.array(bot.position_list)[1:, 0] /self.pix2metric
                    Y = np.array(bot.position_list)[1:, 1] /self.pix2metric
                    if len(bot.trajectory) > 1:
                        GoalX = np.array(bot.trajectory)[:,0]/self.pix2metric
                        GoalY = np.array(bot.trajectory)[:,1]/self.pix2metric
                        ax[0].plot(GoalX, GoalY, color =c * .7,linewidth = 1 )
                    ax[0].plot(X,Y,color =c,linewidth = 1 )
                    


                    #ADD 3D PLOT
                    Z = np.array(bot.blur_list)[:]    #need to fix scal, will also need to normalize this
                    Z = Z - np.min(Z)

                    #Z = ((Z - np.min(Z)) / (np.max(Z) - np.min(Z))) #normalize
                    rolling_avgZ = pd.DataFrame(Z).rolling(30).mean().values
                    avgZ = [i[0] for i in rolling_avgZ]
                    
                    if max(Z) > max_z: #for plot z max limit
                        max_z = max(Z)
                        
                    ax2.plot3D(X,Y,avgZ,color =c,linewidth = 1)



                    #ADD SIZE PLOT
                    Area_list = np.array(bot.area_list)
                    areas_rolling = pd.DataFrame(Area_list).rolling(30).mean().values
                    dia_list = [np.sqrt(4*j[0] /np.pi) for j in areas_rolling]
                   
                    avg_area = round(bot.avg_area,3)
                    avg_dia = np.sqrt(4*avg_area/np.pi)
                    #if avg_area != 0:
                    #    Size_list.append(avg_dia)
                    #    b = ax[2].bar(i,avg_dia, color =c,label = "{}um".format(round(avg_dia,2)))
                    #    ax[2].bar_label(b, label_type='center') 


                    #ADD VELOCITY PLOT
                    VX = np.array([v.x for v in bot.velocity_list])
                    VY = np.array([v.y for v in bot.velocity_list])
                    VZ = np.array([v.z for v in bot.velocity_list])
                    Vmag = np.array([v.mag for v in bot.velocity_list])
                    #print(Vmag)        
                    #if len(Vmag) > 0:
                    Vmax = max(Vmag)
                    if Vmax > global_max_vel:
                         global_max_vel = Vmax
                    #if Vmin == 0:
                    #    Vmag = Vmag[Vmag != 0]
                    #else:
                    #    pass

                    #filter out extreams and when the microrobot is at rest (Vmag =0)
                    Vmag = Vmag[Vmag<Vmax*1]
                
                    Vel = round(sum(Vmag)/len(Vmag),2)
                    Vel_list.append(Vel)
                    rolling_avg = pd.DataFrame(Vmag).rolling(20).median()
        
                    ax[1].plot(rolling_avg,color =c, label = "{}um/s".format(Vel))
                
                
            
            #2D
            ax[0].set_title("2D Trajectories")
            ax[0].invert_yaxis()
            ax[0].set_xlabel("X (um)")
            ax[0].set_ylabel("Y (um)")
            ax[0].set_xlim([0,(self.width * self.resize_scale // 100) /self.pix2metric])
            ax[0].set_ylim([(self.height * self.resize_scale // 100) /self.pix2metric, 0])
            
            #VEL
            ax[1].set_title("average velocity: {}um/s".format(round(np.median(Vel_list),2)))
            ax[1].set_xlabel("Frame")
            ax[1].set_ylim([0, max(Vel_list)*2]) #([0,global_max_vel*2])
            ax[1].legend()
            ax[1].axhline(np.mean(Vel_list), color = "w", linewidth=4)

            #SIZE
            ax[2].set_title("average size:{}um".format(round(np.mean(Size_list),2)))
            ax[2].set_xlabel("MR")
            ax[2].axhline(np.mean(Size_list), color = "w", linewidth = 4)
            ax[2].legend()
            
            #3D
            ax2.set_title("3D Trajectories")
            ax2.axes.set_xlim3d(left=0, right=(self.width * self.resize_scale // 100) /self.pix2metric) 
            ax2.axes.set_ylim3d(bottom=(self.height * self.resize_scale // 100) /self.pix2metric, top=0) 
            ax2.axes.set_zlim3d(bottom= 0, top=max_z*2 if max_z>0 else 1) 

            ax2.set_xlabel("X (um)")
            ax2.set_ylabel("Y (um)")
            ax2.set_zlabel("Z (contrast units)")
    
            plt.show()