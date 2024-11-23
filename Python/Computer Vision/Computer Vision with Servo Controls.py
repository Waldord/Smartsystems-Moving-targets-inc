import cv2
from gpiozero import Servo
from time import sleep

#Intilalizes servos to GPIO pins
panServo = Servo(17)
tiltServo = Servo(18)

#Servo angle constraints
panMin, panMax = 0, 180
tiltMin, tiltMax = 0, 180

#Function to map the angle (0-180) to the servo position (-1 to +1)
def angleToServoPos(angle):
    return (angle / 180) * 2 - 1

#Initialize the camera
videocapture = cv2.VideoCapture(0)

#Setting camera resolution
frameWidth, frameHeight = 640, 480
videocapture.set(cv2.CAP_PROP_FRAME_WIDTH, frameWidth)
videocapture.set(cv2.CAP_PROP_FRAME_HEIGHT, frameHeight)

#Load in the HOG Descriptor for human detection
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())


try:
    while True:
        ret, frame = videocapture.read()
        if not ret:
            print("Failed to capture")
            break
        
        #Convert frames to grayscale
        #Not necessary, but can speed up processing
        gray = cv2.cvtcolor(frame, cv2.COLOR_BGR2GRAY)

        #Detect humans in frame
        boxes, _ = hog.detectMultiScale(gray, winStride=(8, 8), scale=1.05)

        if len(boxes) > 0:
            #Get coordinates of detected person
            x, y, w, h = boxes[0]
            personCenterX = x + w // 2
            personCenterY = y + h // 2

            #Map the center coordinates to servo angle
            panAngle = int(panMin + (personCenterX / frameWidth) * (panMax - panMin))
            tiltAngle = int(tiltMin + (personCenterY / frameHeight) * (tiltMax - tiltMin))

            #Move servos to calculated position
            panServo.value = angleToServoPos(panAngle)
            tiltServo.value = angleToServoPos(tiltAngle)
            print(f"Pan: {panAngle}, Tilt: {tiltAngle}")

        #Display the frame
        #Can be disabled to improve performance
        cv2.imshow("Frame", frame)

        #Stop the program
        if cv2.waitKey(1) & 0xFF == ord('X'):
            break

finally:
    videocapture.release()
    cv2.destroyAllWindows()
    print("Program closed")