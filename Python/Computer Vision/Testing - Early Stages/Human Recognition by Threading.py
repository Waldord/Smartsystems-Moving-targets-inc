import cv2
import threading

class VideoStream:
    def __init__(self, src=0):
        self.stream = cv2.VideoCapture(src)
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.stream.set(cv2.CAP_PROP_FPS, 30)
        self.stream.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
        (self.grabbed, self.frame) = self.stream.read()
        self.stopped = False

    def start(self):
        threading.Thread(target=self.update, args=(), daemon=True).start()
        return self

    def update(self):
        while not self.stopped:
            if not self.grabbed:
                self.stop()
            else:
                (self.grabbed, self.frame) = self.stream.read()

    def read(self):
        return self.frame

    def stop(self):
        self.stopped = True
        self.stream.release()

# Initialize HOG descriptor for human detection
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

# Start video stream on a separate thread
vs = VideoStream(src=0).start()  # Change src to 1 if using an external webcam

frame_skip = 3
frame_counter = 0

while True:
    # Read the latest frame from the threaded video stream
    frame_counter += 1
    frame = vs.read()

    if frame is None:
        print("No frame captured")
        break

    # Get the frame's dimensions
    if frame_counter % frame_skip == 0:
        frame_height, frame_width = frame.shape[:2]

    # Define a central region of interest (ROI)
        center_x, center_y = frame_width // 2, frame_height // 2
        roi_width, roi_height = frame_width // 4, frame_height // 4  # Adjust the size of the central region

    # Detect humans in the frame
        boxes, weights = hog.detectMultiScale(frame, winStride=(8, 8))

    # Iterate over detected boxes
        for (x, y, w, h) in boxes:
        # Calculate the center of the current bounding box
            person_center_x = x + w // 2
            person_center_y = y + h // 2

        # Check if the person is within the central region
            if (center_x - roi_width // 2 < person_center_x < center_x + roi_width // 2 and
                center_y - roi_height // 2 < person_center_y < center_y + roi_height // 2):
            # Draw rectangle only if the person is in the center region
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Draw the central region for visual aid (optional)
        cv2.rectangle(frame, 
                      (center_x - roi_width // 2, center_y - roi_height // 2), 
                      (center_x + roi_width // 2, center_y + roi_height // 2), 
                      (255, 0, 0), 2)

    # Display the frame
    cv2.imshow('Human Detection', frame)

    # Exit if the 'X' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('x'):
        break

# Stop the video stream and close windows
vs.stop()
cv2.destroyAllWindows()
