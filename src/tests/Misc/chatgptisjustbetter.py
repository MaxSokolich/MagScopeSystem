import cv2
import numpy as np
import matplotlib.pyplot as plt

# Initialize the camera
cap = cv2.VideoCapture("/Users/bizzarohd/Desktop/MagScopeSystem/src/videos/mickyroll1.mp4")


# Define the lower and upper bounds of the black color in HSV
lower_black = np.array([0, 0, 0])
upper_black = np.array([180, 255, 30])

# Initialize variables
robot_id = 0
trajectories = {}
velocities = {}
frame_counter = 0


while True:
    # Read a frame from the camera
    ret, frame = cap.read()

    if not ret:
        break

    # Convert the frame to HSV color space
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Create a mask based on the black color range
    black_mask = cv2.inRange(hsv_frame, lower_black, upper_black)

    # Apply a series of dilations and erosions to remove noise
    kernel = np.ones((5, 5), np.uint8)
    black_mask = cv2.dilate(black_mask, kernel, iterations=2)
    black_mask = cv2.erode(black_mask, kernel, iterations=2)

    # Find contours in the mask
    contours, _ = cv2.findContours(black_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Draw bounding boxes around the detected robots and assign unique IDs
    for contour in contours:
        area = cv2.contourArea(contour)

        # Ignore contours that are too small
        if area > 100:
            x, y, w, h = cv2.boundingRect(contour)

            # Draw a bounding box around the robot
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Check if a robot ID has already been assigned to the current bounding box
            robot_assigned = False
            for r_id, (prev_x, prev_y) in trajectories.items():
                if abs(x - prev_x[-1]) < 50 and abs(y - prev_y[-1]) < 50:
                    # The current bounding box is close enough to a previously detected robot
                    # Assign the same ID to the current bounding box
                    robot_id = r_id
                    robot_assigned = True
                    break

            if not robot_assigned:
                # Assign a new ID to the current bounding box
                robot_id += 1

            # Add the current position to the trajectory of the current robot
            if robot_id not in trajectories:
                trajectories[robot_id] = ([], [])
            trajectories[robot_id][0].append(x + w//2)
            trajectories[robot_id][1].append(y + h//2)

            # Calculate the velocity of the current robot
            if len(trajectories[robot_id][0]) > 10:
                x_diff = np.diff(trajectories[robot_id][0][-10:])
                y_diff = np.diff(trajectories[robot_id][1][-10:])
                velocity = np.mean(np.sqrt(x_diff ** 2 + y_diff ** 2))
                if robot_id not in velocities:
                    velocities[robot_id] = []
                velocities[robot_id].append(velocity)

    # Increment the frame counter
    frame_counter += 1
    
    # Show the frame
    cv2.imshow('frame', frame)
    
    # Exit if the 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Plot the trajectories and velocities of each robot
for i, (x, y) in trajectories.items():
    plt.plot(x, y, label=f'Robot {i}')
plt.legend()
plt.xlabel('X position (pixels)')
plt.ylabel('Y position (pixels)')
plt.title('Trajectories')
plt.show()

for i, v in velocities.items():
    plt.plot(v, label=f'Robot {i}')
plt.legend()
plt.xlabel('Frame')
plt.ylabel('Velocity (pixels/frame)')
plt.title('Velocities')
plt.show()
