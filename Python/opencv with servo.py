"""This code uses the openCV library to control servo movements"""
"""The HOG descriptor is used to recognize humans in the frames provided by the camera"""
"""Once the descriptor has identified the player, a CRST tracker takes over to reduce load on RPI"""
"""The player is then tracked with a blue rectangle around their body profile"""
"""A function finds the middle point of this rectangle"""
"""This center point is converted to coordinates of a grid system"""
"""These coordinates are then converted to servo angles"""
"""The servos will then follow the center point around when the player moves"""
"""The code runs the camera operation and detection operation on two threads"""
"""This is done to optimize performance on the RPI's limited resources"""
"""Made by Eirik"""

import cv2
import threading
from time import sleep
from adafruit_servokit import ServoKit
import time
from math import floor

#Initialize servos to GPIO pins
kit = ServoKit(channels=16)
kit.servo[0].actuation_range = 90
kit.servo[1].actuation_range = 90
kit.servo[0].angle = 55
kit.servo[1].angle = 45


#Servo angle constraints
panMin, panMax = 0, 90
tiltMin, tiltMax = 40, 65

oldValueX = 0
oldValueY = 0

#Map angle to servo position
#Angle = 0-180, Position = -1 to +1
def angleToServoPos(angle):
    return (angle - 1)
#Camera settings
frameWidth, frameHeight = 640, 480
latestFrame = None
frameLock = threading.Lock()

#Initialize the camera
videocapture = cv2.VideoCapture(0)
videocapture.set(cv2.CAP_PROP_FRAME_WIDTH, frameWidth)
videocapture.set(cv2.CAP_PROP_FRAME_HEIGHT, frameHeight)

#Load HOG Descriptor
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

#Initialize tracker
tracker = None
primaryTargetLocked = False

#Flag to control threads
stopThreads = False

#Camera Thread
def cameraThread():
    global latestFrame, stopThreads
    while not stopThreads:
        ret, frame = videocapture.read()
        if not ret:
            print("Failed to capture")
            break
        #Update latest frame with locking for thread safety
        with frameLock:
            latestFrame = frame.copy()

# Processing Thread
def processingThread():
    global latestFrame, stopThreads, tracker, primaryTargetLocked, oldValueY, oldValueX
    confirmFrames = 10 #Amount of frames used to confirm tracking
    detectHistory = []
    while not stopThreads:
        with frameLock:
            if latestFrame is None:
                continue
            frame = latestFrame.copy()

        #HOG only runs if tracker is not active
        if not primaryTargetLocked:
            # Convert frame to grayscale (optional for performance)
            grayscale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # Detect humans in frame
            boxes, _ = hog.detectMultiScale(grayscale, winStride=(8, 8), scale=1.05)

            if len(boxes) > 0:
                # Select one target, e.g., the first detected person
                primaryBox = boxes[0]
                detectHistory.append(primaryBox)

                #If detection history contains more frames than neeeded for confirmation, delete them
                if len(detectHistory) > confirmFrames:
                    detectHistory.pop(0)
                
                #Check that the marked target stays consistent trough several frames
                if len(detectHistory) == confirmFrames and all(
                    abs(detectHistory[0][0] - box[0]) < 10 and
                    abs(detectHistory[0][1] - box[1]) < 10 and
                    abs(detectHistory[0][2] - box[2]) < 10 and
                    abs(detectHistory[0][3] - box[3]) < 10
                    for box in detectHistory
                ):
                    time.sleep(2)

                    # Initialize the tracker
                    tracker = cv2.TrackerCSRT_create()
                    tracker.init(frame, tuple(primaryBox))

                    # Lock on the target
                    primaryTargetLocked = True
                    #Once target is found, detection is no longer necessary
                    detectHistory.clear()

                    # Draw rectangle around the person
                    x, y, w, h = primaryBox
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        else:
            # Make the tracker follow the primary target
            success, box = tracker.update(frame)
            
            if success:
                x, y, w, h = map(int, box)
                # Draw a rectangle on the person when in tracking mode
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                
            else:
                # Reset tracker if the target is lost
                primaryTargetLocked = False
                tracker = None
                
            #Get coordinates of the detected person
            x, y, w, h = boxes[0]
            personCenterX = box[0] + w // 2
            personCenterY = box[1] + h // 2
            
            #Convert coordinates to servo angles
            panAngle = 90-int(panMin + (personCenterX / frameWidth) * (panMax - panMin))
            tiltAngle = 90-int(tiltMin + (personCenterY / frameHeight) * (tiltMax - tiltMin))
            
            #Move servos to position 
            kit.servo[1].angle = (floor(angleToServoPos(panAngle)))
            kit.servo[0].angle = (floor(angleToServoPos(tiltAngle)))
            print(f"Pan: {panAngle}, Tilt: {tiltAngle}")

        # Display video
        cv2.imshow("Frame", frame)
        if cv2.waitKey(1) & 0xFF == ord('X'):
            stopThreads = True
            break

        
#Start the threads
cameraT = threading.Thread(target = cameraThread, daemon = True)
processingT = threading.Thread(target = processingThread, daemon = True)

cameraT.start()
processingT.start()

#Wait for the threads to complete
try:
    while not stopThreads:
        sleep(0.1) #Keeps main thread alive
finally:
    #Signal the threads to stop and release resources
    stopThreads = True
    cameraT.join()
    processingT.join()
    videocapture.release()
    cv2.destroyAllWindows()
    print("Program stopped!")

#Coding Sources
# HOG Descriptor: https://medium.com/@dnemutlu/hog-feature-descriptor-263313c3b40d
# OpenCV Course: https://opencv.org/university/free-opencv-course/?utm_source=opcv&utm_medium=gsopcv
# HOG Descriptor: https://docs.opencv.org/3.4/d5/d33/structcv_1_1HOGDescriptor.html
# People Detection: https://www.youtube.com/watch?v=UQRW4B4_nmU
# People Detection: https://www.youtube.com/watch?v=zyKam8pNjJ4
# People Detection: https://www.youtube.com/watch?v=cvGEWBO0Vho
# Threads: https://www.youtube.com/watch?v=IEEhzQoKtQU
# OpenCV CSRT Tracker: https://stackoverflow.com/questions/65545311/how-to-use-the-csrt-tracker-correctly-to-track-objects-in-opencv 