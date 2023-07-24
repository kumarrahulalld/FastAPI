from publisher import publish
from subscriber import subscribe
from threading import Thread

publisher_count = 2
subscriber_count_for_topic = 3
thread_list = list()
topics = list()
for i in range(0, publisher_count):
    topicname = f'topic-{i}'
    topics.append(topicname)
    thread_list.append(Thread(target=publish, args=(i, topicname)))
    print(topicname)

for i in range(0, subscriber_count_for_topic):
    for topic in topics:
        username = f'user-{i}-{topic}'
        thread_list.append(Thread(target=subscribe, args=(topic, username)))
        print('subscribed -', topic, username)

for thread in thread_list:
    thread.start()
    print('running thread', thread)

