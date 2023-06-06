from threading import Thread
import cv2
import EasyPySpin
import multiprocessing


class VideoWritingThreading(object):
    def __init__(self, src=0):
        # Create a VideoCapture object
        self.capture = EasyPySpin.VideoCapture(src)
        self.framenum = 0
        # Default resolutions of the frame are obtained (system dependent)
        self.frame_width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # Set up codec and output video settings
        self.codec = cv2.VideoWriter_fourcc('M','J','P','G')
        self.output_video = cv2.VideoWriter('testing.mp4', cv2.VideoWriter_fourcc(*"mp4v"), 20, (self.frame_width, self.frame_height))


        # Start the thread to read frames from the video stream
        self.thread = Thread(target=self.update, args=())
        #self.thread = multiprocessing.Process(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()

    def update(self):
        # Read the next frame from the stream in a different thread
        while True:
            if self.capture.isOpened():
                (self.status, self.frame) = self.capture.read()

    def show_frame(self):
        # Display frames in main program
        if self.status:
            cv2.imshow('frame', self.frame)
        self.framenum+=1
        print(self.framenum)

        # Press Q on keyboard to stop recording
        key = cv2.waitKey(1)
        if key == ord('q'):
            self.capture.release()
            self.output_video.release()
            cv2.destroyAllWindows()
            exit(1)

    def save_frame(self):
        # Save obtained frame into video output file
        self.output_video.write(self.frame)

if __name__ == '__main__':
    capture_src = 0
    video_writing = VideoWritingThreading(capture_src)
    while True:
        try:
            video_writing.show_frame()
            video_writing.save_frame()
        except AttributeError:
            pass
