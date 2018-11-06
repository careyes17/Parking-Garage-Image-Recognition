import cv2
from imutils.video.pivideostream import PiVideoStream
import math
import imutils
import time
import numpy as np
import mysql.connector

class VideoCamera(object):
    def __init__(self, flip = False):
        self.mydb = mysql.connector.connect(
            host="#################",
            user="#################",
            passwd="#################",
            database="################"
        )
        self.carsarray = []
        self.vs = PiVideoStream().start()
        self.flip = flip
        time.sleep(2.0)

    def __del__(self):
        self.vs.stop()

    def flip_if_needed(self, frame):
        if self.flip:
            return np.flip(frame, 0)
        return frame

    def get_frame(self):
        frame = self.flip_if_needed(self.vs.read())
        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()
    
    def get_object(self, classifier):
        found_objects = False
        frame = self.flip_if_needed(self.vs.read()).copy() 
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        objects = classifier.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(15, 15),
            flags=cv2.CASCADE_SCALE_IMAGE
        )

        if len(objects) > 0:
            found_objects = True

        # Draw a rectangle around the objects
        numofcars = 0
        for (x, y, w, h) in objects:
            numofcars = numofcars + 1
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            #print (numofcars)
        print ("Analyzing...")
        self.carsarray.append(numofcars)
        cv2.imshow('video', frame)
        cv2.waitKey(50)
        if len(self.carsarray) > 9:
            avginimage = math.ceil(sum(self.carsarray) / 10)
            print (avginimage)
            mycursor = self.mydb.cursor()
            #sql = "UPDATE cars SET Cars =%s%s"
            #val = (" ", avginimage)
            mycursor.execute("UPDATE cars SET Cars = %s" % (avginimage))
            self.mydb.commit()
            self.carsarray = []
        ret, jpeg = cv2.imencode('.jpg', frame)
        return (jpeg.tobytes(), found_objects)


