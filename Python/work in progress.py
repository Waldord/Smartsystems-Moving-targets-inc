"""Made by the only one"""


import cv2
import threading
from gpiozero import Servo
from time import sleep

#Initialize servos to GPIO pins
panServo = Servo(17)
tiltServo = Servo(18)

#Servo angle constraints
panMin, panMax = 0, 180
tiltMin, tiltMax = 0, 180

#Map angle to servo position
#Angle = 0-180, Position = -1 to +1
def angleToServoPos(angle):
    return (angle / 180) * 2 - 1

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

#Processing Thread
def processingThread():
    global latestFrame, stopThreads
    while not stopThreads:
        with frameLock:
            if latestFrame is None:
                continue
            frame = latestFrame.copy()
        
        #Convert frame to grayscale
        #Not obligatory, but can improve performance
        grayscale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        #Detect humans in frame
        boxes, _ = hog.detectMultiScale(grayscale, winStride=(8, 8), scale=1.05)

        if len(boxes) > 0:
            #Select one target, this chooses the first person it detects
            primaryBox = boxes[0]

            #Initialize the tracker
            tracker = cv2.TrackerCRST_create()
            tracker.init(frame, tuple(primaryBox))

            #Lock on the target
            primaryTargetLocked = True

            #Draw rectangle around the person
            x, y, w, h = primaryBox
            cv2.rectangle(frame, (x,y), (x + w, y + h), (0, 255, 0), 2)

        else:
            #Make the tracker follow the primary target
            success, box = tracker.update(frame)

            if success:
                x, y, w, h = map(int, box)
                #Draw a rectangle on the person when in tracking mode
                cv2.rectangle(frame, (x,y), (x + w, y + h), (255, 0, 0), 2)
            else:
                #When target moves out of frame, reset the tracker
                primaryTargetLocked = False
                tracker = None

            #Get coordinates of the detected person
            x, y, w, h = boxes[0]
            personCenterX = x + w // 2
            personCenterY = y + h // 2

            #Convert coordinates to servo angles
            panAngle = int(panMin + (personCenterX / frameWidth) * (panMax - panMin))
            tiltAngle = int(tiltMin + (personCenterY / frameHeight) * (tiltMax - tiltMin))

            #Move servos to position 
            panServo.value = angleToServoPos(panAngle)
            tiltServo.value = angleToServoPos(tiltAngle)
            print(f"Pan: {panAngle}, Tilt: {tiltAngle}")

        #Display video
        cv2.imshow("Frame", frame)
        if cv2.waitKey(1) & 0xFF == ord('X'):
            stopThreads = True
        

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


