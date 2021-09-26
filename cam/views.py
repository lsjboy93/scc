from django.shortcuts import render

from django.views.decorators import gzip
from django.views.decorators.csrf import csrf_exempt
from django.http import StreamingHttpResponse
import cv2
import numpy as np
import threading
#import cam.changer
import json

import cam.imgs as imgs
import cam.changer as c2

# Create your views here.


takePic = False
selectedPart = "Mouth"
selectedColor = "d27C7f"

class imageData():
    initImage = np.array([[[0,0,0]] * 120 for i in range(120)], dtype = np.uint8)
    beforeImage = np.array([[[0,0,0]] * 120 for i in range(120)], dtype = np.uint8)
    afterImage = np.array([[[0,0,0]] * 120 for i in range(120)], dtype = np.uint8)
    landmarks = []
    cvt = c2.converter()
    def __init__(self) :
        pass

    def setBeforeImage(self, image) :
        self.beforeImage = image

    def getBeforeImage(self) :
        return self.beforeImage

    def setAfterImage(self) :
        if takePic == False  :
            self.afterImage = self.initImage
        else :
            self.afterImage = self.beforeImage
        
        
    def getBeforeFrame(self) :
        #image = cv2.cvtColor(self.beforeImage, cv2.COLOR_BGR2HSV)
        image = self.beforeImage
        ret, jpeg = cv2.imencode('.jpg', image )
        return jpeg.tobytes()

    def getAfter(self) :
        global takePic
        global selectedPart
        global selectedColor

        isFace = self.cvt.setImage(self.afterImage)
        if isFace == False :
            ret, jpeg = cv2.imencode('.jpg', self.initImage)
            return jpeg.tobytes()
        else :
            isFace = self.cvt.setImage(self.afterImage)
            self.cvt.setPart(selectedPart)
            output = self.cvt.preview(selectedColor)
            ret, jpeg = cv2.imencode('.jpg', output)
            return jpeg.tobytes()


class VideoCamera3(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        self.video.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.video.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    
    def __del__(self):
        self.video.release()
    
    def get_frame(self):
        success, image = self.video.read()
        h, w, _ = image.shape
        image = cv2.flip(image, 1)
        image = image[:,int(w/3):int(w/3) * 2]
        data.setBeforeImage(image)
        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()

data = imageData()
getCam = VideoCamera3()




def home(request) :
    numbers = list([1,2,3,4,5])
    context = {
    	'numbers':numbers,
    }
    return render(request, 'home.html', context)

@csrf_exempt
def test(request) :
    global selectedPart
    colorRGB = ""
    if 'color' in request.POST :
        colorRGB = request.POST['color']
    if 'part' in request.POST :
        selectedPart = request.POST['part']
    
    print(colorRGB)
    itemColors = json.dumps(imgs.getItemColors()[selectedPart])
    itemNames = json.dumps(imgs.getItemNames()[selectedPart])
    #itemColors = imgs.getItemColors()[selectedPart]
    context = {
        "itemColors" : itemColors,
        "itemNames" : itemNames,
    }
    return render(request, 'test.html', context)

@csrf_exempt
def page(request) :
    global takePic
    global selectedPart
    global selectedColor
    colorRGB = ""
    if 'part' in request.POST :
        selectedPart = request.POST['part']
        print("selectedPart : ", selectedPart)
    if 'selectedColor' in request.POST :
        selectedColor = request.POST['selectedColor']
        print("selectedColor : ", selectedColor)
    if "takePic" in request.POST :
        if takePic == False :
            takePic = True
            data.setAfterImage()
        else :
            takePic = False
            data.setAfterImage()
        print(takePic)
     
    
    print(colorRGB)
    itemColors = json.dumps(imgs.getItemColors()[selectedPart])
    itemNames = json.dumps(imgs.getItemNames()[selectedPart])
    itemFileName = json.dumps(imgs.getItemFileNames()[selectedPart])
    context = {
    	'numbers':colorRGB,
        "selectedColor" : selectedColor,
        "selectedPart" : selectedPart,
        'itemColors' : itemColors,
        "itemNames" : itemNames,
        "itemFileName" : itemFileName
    }

    return render(request, 'page.html', context)






# class VideoCamera(object) :
#     def __init__(self) :
#         self.video = cv2.VideoCapture(0)
#         (self.grabbed, self.frame) = self.video.read()
#         threading.Thread(target = self.update, args=()).start()
#     def __del__(self) :
#         self.video.release()

#     def get_frame(self) : 
#         image = self.frame
#         _, jpeg = cv2.imencode('.jpg', image)
#         return jpeg.tobytes()

#     def update(self):
#         while True :
#             (self.grabbed, self.frame) = self.video.read()

# def gen(camera):
#     global image
#     while True:
#         print(len(image))
#         frame = camera.get_frame()
#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')




# class VideoCamera2(object):
#     def __init__(self):
#         # Using OpenCV to capture from device 0. If you have trouble capturing
#         # from a webcam, comment the line below out and use a video file
#         # instead.
#         self.video = cv2.VideoCapture(0)
#         # If you decide to use video.mp4, you must have this file in the folder
#         # as the main.py.
#         # self.video = cv2.VideoCapture('video.mp4')
    
#     def __del__(self):
#         self.video.release()
    
#     def get_frame(self):
#         success, image = self.video.read()
#         # We are using Motion JPEG, but OpenCV defaults to capture raw images,
#         # so we must encode it into JPEG in order to correctly display the
#         # video stream.
#         ret, jpeg = cv2.imencode('.jpg', image)
#         return jpeg.tobytes()


# def gen2():
#     while True:
#         #afterImage = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
#         frame = image.tobytes()
#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        
def gen3() :
    while True :
        frame = getCam.get_frame()
        yield (b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

def convertColor() :
    global takePic
    print(takePic)
    while True :
        frame = data.getAfter()
        yield (b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@gzip.gzip_page
def detectme(request) :
    #return render(request, 'home.html')
    try :
        #cam = VideoCamera2()
        #return StreamingHttpResponse(gen(cam), content_type='multipart/x-mixed-replace; boundary=frame')
        #return StreamingHttpResponse(gen(getCam), content_type='multipart/x-mixed-replace; boundary=frame')
        return StreamingHttpResponse(gen3(), content_type='multipart/x-mixed-replace; boundary=frame')
    except :
        print("Error")
        pass

@gzip.gzip_page
def after(request) :
    try :
        print("after")
        return StreamingHttpResponse(convertColor(), content_type='multipart/x-mixed-replace; boundary=frame')
    except :
        print("Error")
        pass