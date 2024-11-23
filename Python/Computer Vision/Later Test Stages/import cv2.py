import cv2

# Initialize the HOG descriptor/person detector
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

# Open the webcam (you can also provide a video file path)
cap = cv2.VideoCapture(0)  # Change 0 to 'your_video.mp4' for a video file

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    
    if not ret:
        print("Failed to capture video")
        break
    
    # Resize the frame for faster processing (optional)
    frame_resized = cv2.resize(frame, (640, 480))

    # Detect humans in the frame
    boxes, weights = hog.detectMultiScale(frame_resized, winStride=(8, 8))

    # Draw bounding boxes around detected humans
    for (x, y, w, h) in boxes:
        cv2.rectangle(frame_resized, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Display the resulting frame
    cv2.imshow('Human Detection', frame_resized)

    # Break the loop on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the capture and close any open windows
cap.release()
cv2.destroyAllWindows()
