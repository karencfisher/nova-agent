import cv2
import numpy as np

class dnn_detect():
    
    def __init__(self, prototxt, model):
        self.prototxt = prototxt
        self.model = model
        self.net = cv2.dnn.readNetFromCaffe(prototxt, model)
        
    def detect(self, image):
        
        # get dimensions of image and create blob from it
        (h, w) = image.shape[:2]
        blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)), 1.0,
                                     (300, 300), (104.0, 177.0, 123.0))
        
        # process blob through net to find detections
        self.net.setInput(blob)
        detections = self.net.forward()
        
        # obtain dimensions of ROIs
        boxes = []
        for i in range(0, detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            
            if confidence > 0.5:
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                rect = box.astype("int")
                rect[2] = rect[2] - rect[0]
                rect[3] = rect[3] - rect[1]
                boxes.append(rect)
            
        return boxes
    
    
