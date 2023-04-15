import cv2
import numpy as np

# Define the HSV color range to detect (in this case, blue)


lower_color = np.array([35, 100, 100])
upper_color = np.array([75, 255, 255])
# Initialize the video capture object
cap = cv2.VideoCapture("/Users/bizzarohd/Desktop/Media1.mp4")

while True:
    # Capture the current frame
    ret, frame = cap.read()

    # Convert the frame to the HSV color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Create an HSV mask for the target color range
    mask = cv2.inRange(hsv, lower_color, upper_color)
    #mask2 = cv2.inRange(hsv, lower_color1, upper_color1)
    #mask = mask1 + mask2


    # Find the contours of the mask
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Draw a bounding box around the largest contour
    #if len(contours) > 0:
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Display the resulting frame
    cv2.imshow('frame', frame)

    # Check for quit command
    if cv2.waitKey(1000) & 0xFF == ord('q'):
        break

# Release the video capture object and close the windows
cap.release()
cv2.destroyAllWindows()
