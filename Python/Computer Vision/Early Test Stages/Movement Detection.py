import cv2
import gradio as gr
import numpy as np
import matplotlib.pyplot as plt

cap = cv2.VideoCapture(0)
backSub = cv2.createBackgroundSubtractorMOG2()
if not cap.isOpened():
    print("Error opening video file")
    while cap.isOpened():
        # Capture frame-by-frame
          ret, frame = cap.read()
          if ret:
            # Apply background subtraction
            fg_mask = backSub.apply(frame)

# Find contours
contours, hierarchy = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
# print(contours)
frame_ct = cv2.drawContours(frame, contours, -1, (0, 255, 0), 2)
# Display the resulting frame
cv2.imshow('Frame_final', frame_ct)

# apply global threshold to remove shadows
retval, mask_thresh = cv2.threshold( fg_mask, 180, 255, cv2.THRESH_BINARY)

# set the kernal
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
# Apply erosion
mask_eroded = cv2.morphologyEx(mask_thresh, cv2.MORPH_OPEN, kernel)

min_contour_area = 500  # Define your minimum area threshold
large_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > min_contour_area]

frame_out = frame.copy()
for cnt in large_contours:
    x, y, w, h = cv2.boundingRect(cnt)
    frame_out = cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 200), 3)
 
# Display the resulting frame
cv2.imshow('Frame_final', frame_out)