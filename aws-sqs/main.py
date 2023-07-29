import boto3

sqs = boto3.client('sqs')
message = 'Hello World'
queue_url = None
if_queue_exists = sqs.list_queues(QueueNamePrefix='Rahul_Mishra')
if if_queue_exists['QueueUrls']:
    queue_url = if_queue_exists['QueueUrls'][0]
else:
    response = sqs.create_queue(
        QueueName='Rahul_Mishra',
        Attributes={
            'DelaySeconds': '60',
            'MessageRetentionPeriod': '86400'
        }
    )
    queue_url = response['QueueUrl']
if queue_url is not None:
    send_response = sqs.send_message(QueueUrl=queue_url,
                                     DelaySeconds=10, MessageBody=message);
    if send_response['ResponseMetadata']['HTTPStatusCode'] == 200:
        print(f'Message {message} Sent Successfully')

    receive_response = sqs.receive_message(QueueUrl=queue_url);
    if receive_response['ResponseMetadata']['HTTPStatusCode'] == 200:
        print(f'Message {receive_response["Messages"][0]["Body"]} Received Successfully')
else:
    print('Some Issue Occurred During Queue Creation')
