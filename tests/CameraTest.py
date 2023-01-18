import cv2
import EasyPySpin
import time
import numpy as np

'''
BFS-U3-50S5C-Color
2448x2048
35 fps
'''

class count_fps:
    t0 = 0
    t1 = 0
    fps =0
    def __init__(self):
        self.t0 = time.time()
        self.t1 = self.t0
    def update(self):
        self.t1 = time.time()
        self.fps = 1/(self.t1-self.t0)
        self.t0 = self.t1
    def get_fps(self):
        return self.fps




fps = count_fps()       
cam = EasyPySpin.VideoCapture(0)
width = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))
cam.set(cv2.CAP_PROP_FPS,30)
print(cam.get(cv2.CAP_PROP_FPS))
resize_scale =50


while True:
    fps.update()
    suc, frame = cam.read()
    
    
    resize_ratio = (
                width * resize_scale // 100,
                height * resize_scale // 100,
            )
    frame = cv2.resize(frame, resize_ratio, interpolation=cv2.INTER_AREA)
    #frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #frame = cv2.demosaicing(frame,cv2.COLOR_BayerBG2BGR)
    print(frame.shape)
    cv2.putText(
            frame,
            str(int(fps.get_fps())),
            (
                int((width * resize_scale / 100) / 40),
                int((height * resize_scale / 100) / 20),
            ),
            cv2.FONT_HERSHEY_COMPLEX,
            0.5,
            (0, 255, 0),
            1,
        )
    cv2.putText(
            frame,
            str(
                [
                    int((width * resize_scale / 100)),
                    int((height * resize_scale / 100)),
                ]
            ),
            (
                int((width * resize_scale / 100) / 40),
                int((height * resize_scale / 100) / 60),
            ),
            cv2.FONT_HERSHEY_COMPLEX,
            0.5,
            (0, 255, 0),
            1,
        )
    cv2.imshow("im",frame)
  

    fps.get_fps()
    if cv2.waitKey(1) & 0xFF == ord('q'):
        #Send(arduino,0,0,4)
        break
    

cv2.destroyAllWindows()
cam.release()