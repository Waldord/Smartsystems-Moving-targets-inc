import cv2 as cv

video = cv.VideoCapture(0)
#this function will activate and run the camera on which ever computer this script runs on
#it can utilize several cameras at once, with "(0)" indicating that I only have one camera right now
scope = cv.createBackgroundSubtractorMOG2(20, 40)
#this is to create the scope for what the program will filter out
#numbers are manipulated based users preferences


#this loop will analyze the video feed frame by frame based on the scope set
while True:

    ret, frame = video.read()

    if ret:
        mask = scope.apply(frame)
        cv.imshow('Mask', mask)

        if cv.waitKey(5) == ord('X'):
            #if the user presses shift + x the program will close
            break

cv.destroyAllWindows()
video.release()