import cv2 as cv

class CameraFeed:
    def __init__(self):
        self.cam = cv.VideoCapture(0)   # change the camera port
        
    def get_image(self): 
        camera_is_found, image = self.cam.read() # read the camera image
        return camera_is_found, image