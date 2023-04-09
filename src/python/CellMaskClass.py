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
        device = "cpu"
        sam = sam_model_registry[model_type](checkpoint=sam_checkpoint)
        sam.to(device=device)

        self.predictor = SamPredictor(sam)

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

        self.mask_list = []
        self.reference_point = [0,0]
        self.final_mask = None
        self.cell_count = 0
   

    
    def mouse_points(self,event,x,y,flags,params):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.cell_count +=1
            self.reference_point = [x,y]
            if self.cell_count >0:
                self.mask_list.append(params["msks"])
     

    def main(self, file):

        frame = cv2.imread(file)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        print("Setting image predictor ...")
        self.predictor.set_image(frame)
        print("Image predictor set!")   
         
        cv2.namedWindow("img")  # name of CV2 window
        cv2.setMouseCallback("img", self.mouse_points)

        print("finding all masks...")
        #all_masks = self.mask_generator_2.generate(frame)
        print("done")

        #for i in range(1,len(all_masks)):
        #    bwmask = all_masks[i]["segmentation"]
        #    self.mask_list.append(bwmask)
        
        

        while True:
            #for i in range(len(all_masks)):
            #    bwmask = all_masks[i]["segmentation"].astype(np.uint8)
            #    bwmask*=255
            #    cnts, _ = cv2.findContours(bwmask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            #    cv2.drawContours(frame, cnts, -1,(0,255,0), 3)

            if self.cell_count >0:
                input_point = np.array([self.reference_point])
                input_label = np.array([1])

                #create mask
                masks, scores, logits = self.predictor.predict(
                                            point_coords=input_point,
                                            point_labels=input_label,
                                            multimask_output=True,
                                            )
                #convert to cv2 format
                best_mask = masks[np.argmax(scores)]
                params = {"msks": best_mask}

                #create black and white mask
                bwmask = best_mask.astype(np.uint8)
                cv2.setMouseCallback("img", self.mouse_points, params)

                bwmask*=255


                cnts, _ = cv2.findContours(bwmask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                cv2.drawContours(frame, cnts, -1,(0,255,0), 3)
            
            cv2.imshow("img",frame)

            if cv2.waitKey(500) & 0xFF == ord('q'):
                break

        cv2.destroyAllWindows()


        self.final_mask = self.mask_list[0].astype(np.uint8)

        for i in range(len(self.mask_list)):
            self.final_mask += self.mask_list[i].astype(np.uint8)

        self.final_mask *= 255
        cv2.imshow("img2",self.final_mask)

        if cv2.waitKey(0) & 0xFF == ord('q'):
            cv2.imwrite("cellmask.png", self.final_mask)
            cv2.destroyAllWindows()
        

        
    

if __name__ == "__main__":
    file = "/Users/bizzarohd/Desktop/Screen Shot 2023-04-08 at 6.57.24 PM.png"
    detector = MAXS_SAM()
    detector.main(file)
