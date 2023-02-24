import cv2
import numpy as np

def resize(img):
    return cv2.resize(img,(800,450))

cap = cv2.VideoCapture(r'C:\Users\elva\Downloads\iros_speed\snowmanSmallerLobe_30Hz.mp4')
fps = cap.get(cv2.CAP_PROP_FPS)

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# creat BackgroundSubtractorMOG2 object
fgbg = cv2.createBackgroundSubtractorMOG2()

x_old, y_old, speed = 0, 0, 0

while True:
    ret, frame = cap.read()

    if not ret:
        break

    # extract the foreground mask
    fgmask = fgbg.apply(frame)

    # morphological processing of the foreground mask
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_OPEN, kernel)

    # find contours in the foreground mask
    contours, hierarchy = cv2.findContours(fgmask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # detect and find the largest contour
    if contours:
        cnt = contours[0]
        for contour in contours:
            if cv2.contourArea(contour)>cv2.contourArea(cnt):
                cnt = contour
        cv2.drawContours(frame, cnt, -1,(0,0,255),2)
    else:
        cnt = None
        
    # calculate its velocity and draw the rectangle
    x, y, w, h = cv2.boundingRect(cnt)
    x_new, y_new = x + w // 2, y + h // 2

    if x_old != 0 and y_old != 0:
        dist = np.sqrt((x_new - x_old) ** 2 + (y_new - y_old) ** 2)
        time_interval = 1 / fps
        speed = dist / time_interval
        print(speed*0.004)
        with open(r'C:\Users\elva\Downloads\iros_speed\snowmanSmallerLobe_30Hz.txt', 'a') as f:
            f.writelines(str(speed*0.004))
            f.write("\n")
        

    x_old, y_old = x_new, y_new
    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
    cv2.putText(frame, f"Resolution: {width*0.004}x{height*0.004}", (10, 50),
    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(frame, f"Speed: {speed*0.004}", (10, 100),
    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(frame, f"Size: {(x - w)*0.004}X{(y - h)*0.004}", (10, 150),
    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.imshow("frame",resize(frame))

    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()