import boto3

sqs = boto3.client('sqs')
message = 'Hello World'
queue_url = None
if_queue_exists = sqs.list_queues(QueueNamePrefix='Rahul_Mishra')
print(if_queue_exists)
if (if_queue_exists['ResponseMetadata']['HTTPStatusCode'] == 200) and (if_queue_exists.get('QueueUrls') is not None):
    print('Queue Exists')
    queue_url = if_queue_exists['QueueUrls'][0]
else:
    response = sqs.create_queue(
        QueueName='Rahul_Mishra',
        Attributes={
            'DelaySeconds': '1000',
            'MessageRetentionPeriod': '10000'
        }
    )
    queue_url = response['QueueUrl']
if queue_url is not None:
    for i in range(0, 10):
        message = f'Message {i}'
        send_response = sqs.send_message(QueueUrl=queue_url,
                                         DelaySeconds=0, MessageBody=message);
        if send_response['ResponseMetadata']['HTTPStatusCode'] == 200:
            print(f'Message {message} Sent Successfully')

        receive_response = sqs.receive_message(QueueUrl=queue_url);
        if receive_response['ResponseMetadata']['HTTPStatusCode'] == 200:
            print(f'Message {receive_response["Messages"][0]["Body"]} Received Successfully')
            sqs.delete_message(QueueUrl=queue_url,
                               ReceiptHandle=receive_response['Messages'][0]['ReceiptHandle'])
else:
    print('Some Issue Occurred During Queue Creation')
