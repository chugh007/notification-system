import os
import json
import logging
from redis import Redis
from redis.client import PubSub
import sys
sys.path.append(".")
from library import *
from concurrent.futures import ThreadPoolExecutor
import time

executor = ThreadPoolExecutor(5)
setup_logging()
init_redis_client() #access using redis
init_mongo_client() #access using mongo_client

def message_handler(message):
    data = message['data']
    logging.info("Recieved message from redis queue {}".format(data))
    data_payload = json.loads(data)
    user = data_payload['user']
    text = data_payload['message']
    owner = data_payload['owner']
    entity = data_payload['entity']
    db_id = data_payload['id']
    if entity.lower() == "slack":
        pass
    elif entity.lower() == "email":
        pass
        
    executor.submit(mongo_update,db_id,"{} SUCCESSFUL".format(entity),result_payload='test')


def main():
    subscribe_channel(handler=message_handler)
    while True:
        redis_channel_get_message()
        time.sleep(0.001)


if __name__ == '__main__':
    main()


