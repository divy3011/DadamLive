import cv2

windowName="Video Capturing"

def captureVideo():
    cv2.namedWindow(windowName)
    videoCapturing = cv2.VideoCapture(0)

    if videoCapturing.isOpened():
        rval, frame = videoCapturing.read()
    else:
        rval = False

    while rval:
        cv2.imshow(windowName, frame)
        rval, frame = videoCapturing.read()
        key = cv2.waitKey(20)
        if key == 27: # exit on ESC
            break

def destroyVideo():
    cv2.destroyWindow(windowName)

if __name__ == "__main__":
    captureVideo()
    destroyVideo()