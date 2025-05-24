import base64
import numpy as np
import cv2
from tensorflow.keras.models import load_model
import tools.dnn_detect as dnn


class FaceExpression:
   
    def __base64_to_cv2(self, base64_string):
        # Convert the base64 string to a numpy array
        decoded_data = base64.b64decode(base64_string)
        np_data = np.frombuffer(decoded_data, np.uint8)
            
        img = cv2.imdecode(np_data, cv2.IMREAD_COLOR)
        return img

    def __preprocess_img(self, img):
         # And convert to grayscale
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Resize the image to 48x48 pixels
        img = cv2.resize(img, (48, 48))
        
        # Add a new axis to the image
        img = np.expand_dims(img, axis=0)
        img = np.expand_dims(img, axis=-1)
        
        # Normalize the image
        img = img / 255.0
        return img

    def infer_emotions(self, base64_img):
        # Load the pre-trained model
        try:
            model = load_model('tools\\best_model2.h5')
        except Exception as e:
            print(f"Error loading model: {e}")
            return None
        
        # Setup face detection 
        models = 'tools\\res10_300x300_ssd_iter_140000.caffemodel'
        detector = dnn.dnn_detect('tools\\deploy.prototxt.txt', models)

        img = self.__base64_to_cv2(base64_img)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        
        # Detect faces in the image
        faces = detector.detect(img)
        
        # If no faces are detected, return None
        if len(faces) == 0:
            print("No faces detected in the image")
            return None
        
        # Get the face with the largest area
        x, y, w, h = max(faces, key=lambda face: face[2] * face[3])     
        
        # Crop the face from the image
        padding = (h - w) // 2
        face = img[y:y+h, x-padding:x+w+padding]
        
        # Preprocess the image
        face = self.__preprocess_img(face)
        
        # Get the emotion prediction
        prediction = model.predict(face)
        
        # Get the emotion distribution
        emotion_labels = ['Neutral', 'Happy', 'Surprise', 'Sad', 'Angry', 'Disgust', 'Fear']
        results = list(zip(emotion_labels, prediction[0]))
        results.sort(key=lambda x: x[1], reverse=True)
        emotions = {emotion: str(prob) for emotion, prob in results}
        return emotions
