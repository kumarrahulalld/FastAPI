# Using OpenCV for video handl
import cv2

# Using Redis for Pub/Sub
import redis


# Open a Video capture for your webcam.
def publish(cameraId, topicName):
    video = cv2.VideoCapture(cameraId)

    # Resizing parameters
    height = int(video.get(4) / 2)
    width = int(video.get(3) / 2)

    # Open a Redis connection to be used as publisher
    server = redis.Redis()

    # While video camera is on...
    while video.isOpened():

        # Read a frame from the camera. Frame is a 2D array of pixels.
        ret, frame = video.read()
        if ret:
            frame = cv2.resize(frame, (width, height))

            # Publish the frame (message packet) to a channel named user_1
            server.publish(topicName, frame.tobytes())

    video.release()
