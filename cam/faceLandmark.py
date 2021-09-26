import time

import numpy as np
import cv2
import dlib
from collections import OrderedDict
import imutils

# initialize dlib's face detector (HOG-based) and then create
# the facial landmark predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('./data/shape_predictor_68_face_landmarks.dat')

# find face part
# image : original image
# isDot : draw facial landmark
# part : face part(Eyebrow, Mouth, Eyes)
def findFaceLandmark(image, part, isDot) :
    height, width, channel = image.shape
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    #return gray, {}
    rects = detector(gray, 1)
    for (i, rect) in enumerate(rects):

        # determine the facial landmarks for the face region, then
        # convert the landmark (x, y)-coordinates to a NumPy array
        shape = predictor(gray, rect)
        shape = shape_to_numpy_array(shape)

        output, landmarks  = visualize_facial_landmarks(image, shape, part)
        if isDot :
            output = drawDot(output, landmarks)
        
        return output, landmarks
    return image, {}


# FACIAL_LANDMARKS_INDEXES = OrderedDict([
#     #("Mouth", (48, 68)),
#     ("Mouth", (48, 59)),
#     ("Right_Eyebrow", (17, 22)),
#     ("Left_Eyebrow", (22, 27)),
#     ("Right_Eye", (36, 42)),
#     ("Left_Eye", (42, 48)),
#     ("Nose", (27, 35)),
#     ("Jaw", (0, 17))
# ])

FACIAL_LANDMARKS_INDEXES = {
    "Mouth" : [(48, 59), (59, 68)],
    "Eyebrow" : [(17, 22),(22, 27)],
    "Eye" : [(36, 42), (42, 48)]
}

def shape_to_numpy_array(shape, dtype="int"):
    coordinates = np.zeros((68, 2), dtype=dtype)
    #coordinates = np.zeros((59, 2), dtype=dtype)
    
    
    for i in range(0, 68):
    #for i in range(0, 59):
        coordinates[i] = (shape.part(i).x, shape.part(i).y)
        
        
    return coordinates
    
    
def visualize_facial_landmarks(image, shape, part):
    if part not in FACIAL_LANDMARKS_INDEXES :
        return image, {}
        
    overlay = image.copy()
    output = image.copy()
    outline = []
    
    height, width, _ = image.shape
    #paper = np.ones((height, width, channel), dtype=np.uint8) * 255
    
    facial_features_cordinates = []
        # grab the (x, y)-coordinates associated with the
        # face landmark
    # (j, k) = FACIAL_LANDMARKS_INDEXES[name]

    # facial_features_cordinates[name] = shape[j:k]

    # if isDot == True :
    #     for dot in pts:
    #         cv2.line(output, dot, dot, (0,0,255), 2)
    # return output, facial_features_cordinates

    for (i, j) in FACIAL_LANDMARKS_INDEXES[part] :
        facial_features_cordinates.append(shape[i:j])

    return output, facial_features_cordinates

def drawDot(image, landmarks) :
    output = image.copy()
    for landmark in landmarks :
        for dot in landmark :
            output = cv2.line(output, dot, dot, (0,0,255), 2)
    return output


