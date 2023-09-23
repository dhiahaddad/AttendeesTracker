import cv2 as cv

class CameraFeed:
    def __init__(self):
        self.cam = cv.VideoCapture(0)   # change the camera port
        # Check if the camera was opened successfully
        if self.cam.isOpened():
            print("Camera is detected and opened.")
        else:
            print("Camera not detected or cannot be opened.")
        
    def get_image(self): 
        camera_is_found, image = self.cam.read() # read the camera image
        return camera_is_found, image