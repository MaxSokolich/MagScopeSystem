from matplotlib_scalebar.scalebar import ScaleBar
import cv2
import EasyPySpin
import matplotlib.pyplot as plt
scalebar = ScaleBar(0.08, "um", length_fraction = 0.25)


s = plt.add__artist(scalebar)
print(type(s))
cam = EasyPySpin.VideoCapture(0)


cv2.imshow(scalebar)


while True:
 
    suc, frame = cam.read()
    
    r = .5
    size = (int(frame.shape[1]*r), int(frame.shape[0]*r))
    frame = cv2.resize(frame,size,interpolation = cv2.INTER_AREA)
    print(frame.shape)
    height = int(frame.shape[0])
    print(height)
    pix_2metric = (106.2 / height / 100) * 10
    print(pix_2metric)
    
    
   
    

    #send actions to arduino
    #Send(arduino,typ,angle,rolling_frequency)
    
    cv2.add
    
    cv2.imshow("im",frame)
  


    if cv2.waitKey(10) & 0xFF == ord('q'):# or BUTTON == ["b",1]:
        break
cam.release()
cv2.destroyAllWindows()
