# Using OpenCV for video handl
import cv2

# Using Redis for Pub/Sub
import redis


# Open a Video capture for your webcam.
def publish(cameraId, topicName):
    video = cv2.VideoCapture(cameraId)

    # Resizing parameters
    height = int(video.get(4))
    width = int(video.get(3))
    print('width', width)
    print('height', height)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(f'output{cameraId}-{topicName}.avi', fourcc, 20.0, (640, 480))
    # Open a Redis connection to be used as publisher
    server = redis.Redis(host='127.0.0.1', port=6379)
    count =0
    # While video camera is on...
    while video.isOpened():

        # Read a frame from the camera. Frame is a 2D array of pixels.
        ret, frame = video.read()
        if ret:
            frame = cv2.resize(frame, (width, height))
            if count < 100:
                out.write(frame)
                count = count+1
            else:
                out.release()
            # Publish the frame (message packet) to a channel named user_1
            server.publish(topicName, frame.tobytes())

    video.release()

