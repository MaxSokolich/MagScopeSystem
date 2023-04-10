import numpy as np
import torch
import matplotlib.pyplot as plt
import cv2
import time
from segment_anything import sam_model_registry, SamAutomaticMaskGenerator, SamPredictor

class MAXS_SAM:
    def __init__(self):
        #create SAM object
        print("Loading SAM ...")
        sam_checkpoint = "/Users/bizzarohd/Desktop/segment-anything/sam_vit_h_4b8939.pth"
        model_type = "vit_h"
        device = None

        sam = sam_model_registry[model_type](checkpoint=sam_checkpoint)
        sam.to(device=device)

        self.mask_generator = SamAutomaticMaskGenerator(sam)

        self.mask_generator_2 = SamAutomaticMaskGenerator(
            model=sam,
            points_per_side=32,
            pred_iou_thresh=0.86,
            stability_score_thresh=0.92,
            crop_n_layers=1,
            crop_n_points_downscale_factor=2,
            min_mask_region_area=100,  # Requires open-cv to run post-processing
        )
        print("SAM loaded successfully!")

    def main(self,file):
        frame = cv2.imread(file)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) 

        masks = self.mask_generator_2.generate(frame)
        
        final_mask = masks[0]["segmentation"].astype(np.uint8)
        
        for i in range(1,len(masks)):
            #bounding boxes
            #bbx = masks[i]["bbox"]
            #cv2.rectangle(frame,(bbx[0], bbx[1]), (bbx[0]+bbx[2], bbx[1]+bbx[3]),(0,255,0),2)

            #mask
            bwmask = masks[i]["segmentation"].astype(np.uint8)
            
            final_mask+=bwmask
            
        final_mask += 255
        #result = result.clip(0, 255).astype("uint8")

        cv2.imshow("mask",final_mask)
        cv2.imshow("img",frame)
        cv2.imwrite("cellmask.png", final_mask)

        if cv2.waitKey(0) & 0xFF == ord('q'):

            cv2.destroyAllWindows()
        
    

if __name__ == "__main__":
    img = '/Users/bizzarohd/Desktop/Screen Shot 2023-04-08 at 2.28.23 PM.png'
    detector = MAXS_SAM()
    detector.main(img)
