# Open CV to display incoming frame
import cv2
# Redis to subscribe
import redis
# Numpy to convert message packet to 2D array of pixels.
import numpy as np


def subscribe(topic, userId):
    client = redis.Redis(host='127.0.0.1', port=6379)
    print(topic, userId)
    client_channel = client.pubsub()
    # Let's subscribe to other user's channel.
    client_channel.subscribe(topic)

    # Listening to messages in the channel
    for item in client_channel.listen():
        if item["type"] != "message":
            continue

        # For every message received in the channel, converting the bytes to a 2D array.
        frame = np.frombuffer(item["data"], dtype="uint8").reshape(240, 320, 3)

        # Displaying this frame back to the User client.
        cv2.imshow(f'{userId}', frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    client_channel.unsubscribe()
    cv2.destroyAllWindows()
