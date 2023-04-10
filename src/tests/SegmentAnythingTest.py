import matplotlib.pyplot as plt
import torch
import torchvision
import cv2
import numpy as np
from segment_anything import sam_model_registry, SamAutomaticMaskGenerator, SamPredictor

print("PyTorch version:", torch.__version__)
print("Torchvision version:", torchvision.__version__)
print("CUDA is available:", torch.cuda.is_available())





def show_anns(anns):
    if len(anns) == 0:
        return
    sorted_anns = sorted(anns, key=(lambda x: x['area']), reverse=True)
    ax = plt.gca()
    ax.set_autoscale_on(False)
    polygons = []
    color = []
    for ann in sorted_anns:
        m = ann['segmentation']
        img = np.ones((m.shape[0], m.shape[1], 3))
        color_mask = np.random.random((1, 3)).tolist()[0]
        for i in range(3):
            img[:,:,i] = color_mask[i]
        ax.imshow(np.dstack((img, m*0.35)))



sam_checkpoint = "/home/max/Desktop/sam_vit_h_4b8939.pth"

device = "cuda"
model_type = "default"


sam = sam_model_registry[model_type](checkpoint=sam_checkpoint)
sam.to(device=device)

mask_generator = SamAutomaticMaskGenerator(sam)


file = "/home/max/Desktop/MagScopeSystem/src/imgs/initialimg.png"
frame = cv2.imread(file)
masks = mask_generator.generate(frame)
print(len(masks))
#cv2.imshow(frame)
#show_anns(masks)

if cv2.waitKey(0) & 0xFF == ord("q"):
    cv2.destroyAllWindows()


