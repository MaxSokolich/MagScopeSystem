import cv2
import multiprocessing as mp
import EasyPySpin

# Initialize the video capture object
cap = EasyPySpin.VideoCapture(0)

cap.set(cv2.CAP_PROP_FPS, 5)


w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
# Define the codec and create a VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('output.mp4', fourcc, 5, (w, h))

# Define the function to write frames to the output file
def write_frames(queue):
    while True:
        frame = queue.get()
        if frame is None:
            break
        out.write(frame)

# Create the queue and the process to write frames
queue = mp.Queue()
process = mp.Process(target=write_frames, args=(queue,))
process.start()



# Loop through the frames and put them in the queue
n=0
while cap.isOpened():
    ret, frame = cap.read()
    if ret:
        # Put the frame in the queue
        queue.put(frame)

        # Display the frame (optional)
        cv2.imshow('frame', frame)

        # Press 'q' to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break

# Put None in the queue to signal the end of frames
queue.put(None)


# Release the resources
process.join()
cap.release()
out.release()
print("release writer")
cv2.destroyAllWindows()
