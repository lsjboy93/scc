import cv2
import numpy as np
import cam.faceLandmark as fl


DEFAULT_HEIGHT = 960
DEFAULT_WIDTH = 1280

def getPaper(color, height = DEFAULT_HEIGHT, width = DEFAULT_WIDTH) :
    return np.array([[color] * width for i in range(height)], dtype = np.uint8)

class converter() :
    def __init__(self) :
        self.image = []
        self.landmarks = []
        self.rect = []
        self.part = "Mouth"
        self.landmarkImage = []

    def setPart(self, part) :
        self.part = part

    def setImage(self, faceImage) :
        self.image = faceImage
        output, self.landmarks = fl.findFaceLandmark(self.image, self.part, isDot = True)
        self.landmarkImage = output
        if len(self.landmarks) < 1 :
            return False
        return True
        
    def preview(self, color) :
        output = cv2.cvtColor(self.image, cv2.COLOR_BGR2BGRA)
        if self.part == "Mouth" :
            mask, rect = getMouthMask(self.image, self.landmarks)
            #print(rect)
            output = output - mask
            mask = changeColor(mask, rect, color)
            
            #mask3 = cv2.addWeighted(mask, 0.8, mask2, 0.2, 0)
            #mask4 = cv2.addWeighted(mask, 0.2, mask2, 0.8, 0)
            #cv2.imshow("mask1", mask)
            #cv2.imshow("mask2", mask2)
            #cv2.imshow("mask3", mask3)
            #cv2.imshow("mask4", mask4)
            output += mask
        else :
            for landmark in landmarks :
                mask, rect =  getMask(self.image, self.part, landmark)
                output = output - mask
                mask = changeColor(mask, rect, color)
                
                #mask = cv2.addWeighted(mask, 0.2, mask2, 0.8, 0)
                output += mask
        #cv2.imshow("mask", output)
        output = cv2.cvtColor(output, cv2.COLOR_BGRA2BGR)
        #cv2.imshow("output", output)
        return output
        
def preview(image, part, color, landmarks) :
    print(image.shape)
    output = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
    if part == "Mouth" :
        mask, rect = getMouthMask(image, landmarks)
        output = output - mask
        mask = changeColor(mask, rect, color)
        output += mask
    output = cv2.cvtColor(output, cv2.COLOR_BGRA2BGR)
    return output

def convert(image, isLandmark, isPaint, color) :
    #print(isLandmark, isPaint, color)
    """
    1. get landmark
    2. get mask
    3. change mask color
    4. overlay
    """

    # get landmark
    output, landmarks = fl.findFaceLandmark(image, self.part, isLandmark)
    if len(landmarks) < 1 :
        return image, False
    #print("part", part)
    # get mask
    if isPaint :
        output = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
        if self.part == "Mouth" :
            mask, rect = getMouthMask(image, landmarks)
            #print(self.part)
            output = output - mask
            mask = changeColor(mask, rect, color)
            output += mask
            
        else :
            for landmark in landmarks :
                mask, rect =  getMask(image, self.part, landmark)
                output = output - mask
                mask = changeColor(mask, rect, color)
                output += mask
                
    return output, True



endpoint = {
        "Mouth" : (0, 6),
        "Eyebrow" : (0, 4),
        "Eye" : (0, 3)
    }


def getMouthMask(image, landmarks) :
    outline = []
    innerline = []

    landmark = landmarks[0]
    for i in range(len(landmark)) :
        el_count = len(landmark)
        currentPoint = landmark[i % el_count]
        nextPoint = landmark[(i + 1) % el_count]
        outline.append(currentPoint.tolist())

        width = nextPoint[0] - currentPoint[0] - 1

        # vertical line
        if width == 0 :
            pass

        else:
            move = int(width / abs(width))

            for col in range(currentPoint[0] + 1, nextPoint[0], move) :
                edge = []
                edge.append(col)
                edge.append(currentPoint[1] + int(float(nextPoint[1] - currentPoint[1]) * (col - currentPoint[0])/width))
                outline.append(edge)

    landmark = landmarks[1]
    for i in range(len(landmark)) :
        # find innerline
        el_count = len(landmark)
        currentPoint = landmark[i % el_count]
        nextPoint = landmark[(i + 1) % el_count]
        innerline.append(currentPoint.tolist())

        width = nextPoint[0] - currentPoint[0] - 1

        # vertical line
        if width == 0 :
            pass

        else:
            move = int(width / abs(width))

            for col in range(currentPoint[0] + 1, nextPoint[0], move) :
                edge = []
                edge.append(col)
                edge.append(currentPoint[1] + int(float(nextPoint[1] - currentPoint[1]) * (col - currentPoint[0])/width))
                innerline.append(edge)



    height, width, _ = image.shape

    rect = [0] * 4
    rect[0] = height
    rect[1] = outline[0][0]
    rect[2] = 0
    rect[3] = outline[int(len(outline)/2)][0] 
    
    # paper = mask
    # B G R + Alpha
    paper = getPaper([0,0,0,255], height, width)
  
    for i in range(1, int(len(outline)/2)) :
        for row in range (outline[i][1], outline[-i][1] + 1) :
            paper[row][outline[i][0]] = np.insert(image[row][outline[i][0]], 3, 1)

            if row < rect[0] :
                rect[0] = row
            if row > rect[2] :
                rect[2] = row

            paper[row][outline[i][0]] = np.insert(image[row][outline[i][0]], 3, 1)

    for i in range(1, int(len(outline)/2)) :
        for row in range (innerline[i][1], innerline[-i][1] + 1) :
            paper[row][innerline[i][0]] = [0,0,0,0]


    return paper, rect 


def getMask(image, part, landmark) : 
    outline = []

    for i in range(len(landmark)) :
        # find outline
        el_count = len(landmark)
        currentPoint = landmark[i % el_count]
        nextPoint = landmark[(i + 1) % el_count]
        outline.append(currentPoint.tolist())

        width = nextPoint[0] - currentPoint[0] - 1

        # vertical line
        if width == 0 :
            pass

        else:
            move = int(width / abs(width))

            for col in range(currentPoint[0] + 1, nextPoint[0], move) :
                edge = []
                edge.append(col)
                edge.append(currentPoint[1] + int(float(nextPoint[1] - currentPoint[1]) * (col - currentPoint[0])/width))
                outline.append(edge)


    height, width, _ = image.shape

    rect = [0] * 4
    rect[0] = height
    rect[1] = outline[0][0]
    rect[2] = 0
    rect[3] = outline[int(len(outline)/2)][0] 
    
    # paper = mask
    # B G R + Alpha
    #paper = np.array([[[0, 0, 0, 0]] * width for i in range(height)], dtype = np.uint8)
    paper = getPaper([0,0,0,0], height, width )
  
    for i in range(1, int(len(outline)/2)) :
        for row in range (outline[i][1], outline[-i][1] + 1) :
            paper[row][outline[i][0]] = np.insert(image[row][outline[i][0]], 3, 1)

            if row < rect[0] :
                rect[0] = row
            if row > rect[2] :
                rect[2] = row
            

    return paper, rect
   


def changeColor(mask, rect, color) :
    sampleWidth, sampleHeight = [300, 300]
    if isinstance(color, str) :
        color = int(color, 16)
    targetColor = []
    targetColor.append(color % 256)
    color = int(color / 256)
    targetColor.append(color % 256)
    color = int(color / 256)
    targetColor.append(color % 256)
    
    targetColorSample = getPaper(targetColor, 300, 300)
    
    height, width, _ = mask.shape
    
    u, l, d, r = rect
    #print(u,l,d,r)

    partOriginImage = mask[u:d+1, l:r+1]
    partImage = cv2.cvtColor(cv2.cvtColor(partOriginImage, cv2.COLOR_BGRA2BGR), cv2.COLOR_BGR2HSV)
    targetHSV = cv2.cvtColor(targetColorSample, cv2.COLOR_BGR2HSV)
    
    partImage[:,:,0] = targetHSV[0][0][0]

    partChangedImage = cv2.cvtColor(cv2.cvtColor(partImage, cv2.COLOR_HSV2BGR), cv2.COLOR_BGR2BGRA)
    
    partChangedImage[:,:,3] = partOriginImage[:,:,3]

    mask[u:d+1, l:r+1] = partChangedImage

    return mask
    