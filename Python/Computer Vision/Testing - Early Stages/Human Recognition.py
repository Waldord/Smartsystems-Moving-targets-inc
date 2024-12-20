import cv2

# Initializes the HOG descriptor
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

# Enables a direct video feed from the computer webcam
videocapture = cv2.VideoCapture(1)

while True:
    # Analyse every individual frame from feed
    ret, frame = videocapture.read()

    # Break the loop if no video is available for analysis
    if not ret:
        print("Failed to capture video")
        break

    # Detects if there are any humans in the frame
    boxes, weights = hog.detectMultiScale(frame, winStride=(16, 16))

    # Where humans are detected, draw a rectangle around the bodies
    for (x, y, w, h) in boxes:
        cv2.rectangle(frame, (x,y), (x + w, y + h), (0, 0, 255), 2)

    # Display the video feed on screen
    cv2.imshow('Human Detection', frame)
    # When "shift + x" is pressed, stop the code
    if cv2.waitKey(1) & 0xFF == ord('X'):
        break


videocapture.release()
cv2.destroyAllWindows()