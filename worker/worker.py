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
from post_message import Slack,Email
import traceback

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
    entity = data_payload['entity']
    db_id = data_payload['id']
    status = "{} SUCCESSFUL".format(entity)
    result_payload=''
    try:
        if entity.lower() == "slack":
            slack = Slack()
            slack.sendMessage(user,text)
        elif entity.lower() == "email":
            email = Email()
            email.sendMessage(user,text)
    except Exception as e:
        logging.error("Error occurred {} {}".format(e,traceback.format_exc()))
        status = "{} FAILED".format(entity)
        result_payload = str(e)
    finally:
        executor.submit(mongo_update,db_id,status,result_payload=result_payload)


def main():
    subscribe_channel(handler=message_handler)
    while True:
        redis_channel_get_message()
        time.sleep(0.001)


if __name__ == '__main__':
    main()


