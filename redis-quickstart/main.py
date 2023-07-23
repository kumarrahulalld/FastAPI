import redis

r = redis.Redis(host='127.0.0.1', port=6379, decode_responses=True)
r.set('greeting', 'Hello World')
print(r.get('greeting'))
print(r.lpush('mylist', '1 2 3 4 5','4 5 6','7 8 9'))
print(r.lrange('mylist',0,-1))

