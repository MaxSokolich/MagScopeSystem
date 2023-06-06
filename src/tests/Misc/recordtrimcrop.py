import cv2
#import PySpin
#import EasyPySpin
import time
import numpy as np

'''
BFS-U3-50S5C-Color
2448x2048
35 fps

NOTE: need to add cam.PixelFormat.SetValue(PySpin.PixelFormat_BGR8) above self.cam.BeginAcquistion() line in Easypyspin videocapture
'''
global count


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


def mouse_points(event,x,y,flags,params):
    global b
    if event == cv2.EVENT_LBUTTONDOWN:
        print(count)
        b = [x,y]


            
b = [0,0]
fps = count_fps()       
cam = cv2.VideoCapture("/Users/bizzarohd/Desktop/BubblePropped0.mp4")
width = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))




cv2.namedWindow("img")  # name of CV2 window
cv2.setMouseCallback("img", mouse_points)  # set callback func
start = time.time()
count = 0
resize_scale =100
resize_ratio = (
                width * resize_scale // 100,
                height * resize_scale // 100,
            )

result = cv2.VideoWriter(
                        "/Users/bizzarohd/Desktop/BubblePropelled.mov",
                        cv2.VideoWriter_fourcc(*"mp4v"),
                        50,    
                        (410,454),
                        
                    ) 

while True:
    fps.update()
    suc, frame = cam.read()
    if not suc:
        print("error")
        break
    #click object on half resd image
    #find coords of obj in
    #do contouring based on full res img


    resize_scale =100
    resize_ratio = (
                width * resize_scale // 100,
                height * resize_scale // 100,
            )
    
    x,y = b[0], b[1]
    frame = cv2.resize(frame, resize_ratio, interpolation=cv2.INTER_AREA)
  
    frame = frame[:, :]
    print(frame.shape)
    #cv2.circle(frame,(x,y),10, (255,255,0),-1)


    


    
    cv2.putText(
            frame,
            str(round(time.time()-start,2))+" s",
            (
                int((width * resize_scale / 100) / 40),
                int((height * resize_scale / 100) / 20),
            ),
            cv2.FONT_HERSHEY_COMPLEX,
            1,
            (0, 255, 0),
            2,
        )
    cv2.imshow("img",frame)
    
    if count == 250:
        cv2.imwrite("/Users/bizzarohd/Desktop/img{}.png".format(count), frame)
        print("saved")
    
    elif count == 500:
        cv2.imwrite("/Users/bizzarohd/Desktop/img{}.png".format(count), frame)
    elif count == 700:
        cv2.imwrite("/Users/bizzarohd/Desktop/img{}.png".format(count), frame)
    
    elif count == 940:
        cv2.imwrite("/Users/bizzarohd/Desktop/img{}.png".format(count), frame)
    
    elif count == 50:
        cv2.imwrite("/Users/bizzarohd/Desktop/img{}.png".format(count), frame)
    
    elif count == 142:
        cv2.imwrite("/Users/bizzarohd/Desktop/img{}.png".format(count), frame)
    """
    elif count == 260:
        cv2.imwrite("img{}.png".format(count), frame)"""

        
    result.write(frame)
    

  


        
  

    fps.get_fps()
    count+=1
    print(count)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        #Send(arduino,0,0,4)
    
        break




result.release()
cv2.destroyAllWindows()
cam.release()

