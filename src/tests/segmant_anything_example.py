import numpy as np
import torch
import matplotlib.pyplot as plt
import cv2
import time
from segment_anything import sam_model_registry, SamPredictor

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
    

class MAXS_SAM:
    def __init__(self):
        #create SAM object
        print("Loading SAM ...")
        sam_checkpoint = "/Users/bizzarohd/Desktop/segment-anything/sam_vit_h_4b8939.pth"
        model_type = "vit_h"
        device = None
        sam = sam_model_registry[model_type](checkpoint=sam_checkpoint)
        sam.to(device=device)
        self.predictor = SamPredictor(sam)
        print("SAM loaded successfully!")


        self.frame = None
        self.reference_point = [0,0]
        self.width = 0
        self.height = 0 
        self.resize_scale = 100

    def load_image(self, image):
        
        im = cv2.imread(image)
        im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
        print("Setting image predictor ...")
        self.predictor.set_image(im)
        print("Image predictor set!")   
        self.frame = im
        self.width = im.shape[1]
        self.height = im.shape[0]
      

    


    def create_mask(self, ref_point):
        #define reference point
        input_point = np.array([ref_point])
        input_label = np.array([1])

        #create mask
        masks, scores, logits = self.predictor.predict(
                                    point_coords=input_point,
                                    point_labels=input_label,
                                    multimask_output=True,
                                    )
        #convert to cv2 format
        best_mask = masks[np.argmax(scores)]
        bwmask = best_mask.astype(np.uint8)
        bwmask*=255

        contours, _ = cv2.findContours(bwmask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        return contours
    

        
    def mouse_points(self,event,x,y,flags,params):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.reference_point = [x,y]

    def main(self):
    
        fps = count_fps()  
        cv2.namedWindow("img")  # name of CV2 window
        cv2.setMouseCallback("img", self.mouse_points)  # set callback func
        
        while True:
            fps.update()
            cnts = self.create_mask(self.reference_point)
            cv2.drawContours(self.frame, cnts, -1,(0,255,0), 3)


            print(self.reference_point)
            cv2.putText(self.frame,str(int(fps.get_fps())),
                    (
                        int((self.width * self.resize_scale / 100) / 40),
                        int((self.height * self.resize_scale / 100) / 20),
                    ),
                    cv2.FONT_HERSHEY_COMPLEX,
                    0.5,
                    (0, 255, 0),
                    1,
                )
            
            cv2.imshow("img",self.frame)

            if cv2.waitKey(100) & 0xFF == ord('q'):
                break

        cv2.destroyAllWindows()
        
    

if __name__ == "__main__":
    img = '/Users/bizzarohd/Desktop/cancercells.png'
    detector = MAXS_SAM()
    detector.load_image(img)
    detector.main()
