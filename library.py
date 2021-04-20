import os
import logging
import json
from pymongo import MongoClient
from redis import Redis
import copy
from bson.objectid import ObjectId  

MONGO_INITDB_ROOT_USERNAME = os.environ.get('MONGO_INITDB_ROOT_USERNAME','root')
MONGO_INITDB_ROOT_PASSWORD = os.environ.get('MONGO_INITDB_ROOT_PASSWORD','root')
MONGO_INITDB_DATABASE = os.environ.get('MONGO_INITDB_DATABASE','test')
MONGO_HOST = os.environ['MONGO_HOST']
REDIS_HOST = os.environ['REDIS_HOST']
REDIS_PORT= int(os.environ.get('REDIS_PORT',6379))
COLLECTION=os.environ.get('MONGO_COLLECTION','my-collection')
ADDING_TO_REDIS_QUEUE = "ADDING TO REDIS QUEUE"
PUSHED_TO_REDIS_QUEUE = "PUSHED TO REDIS QUEUE"
REDIS_CHANNEL = os.environ.get('REDIS_CHANNEL','NOTIFICATION')
redis=None
mongo_client = None
pubsub = None

def init_redis_client():
    global redis
    global pubsub
    redis = Redis(REDIS_HOST,REDIS_PORT,db=0)
    pubsub = redis.pubsub(ignore_subscribe_messages=True)

def setup_logging(log_dir="/tmp/", log_file="/tmp/app.log"):
    from logging.handlers import RotatingFileHandler
    """ Sets up global logging """
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    logging.basicConfig(handlers=[RotatingFileHandler(log_file, maxBytes=100000, backupCount=10), logging.StreamHandler()],
                        level = logging.INFO,
                        format = '%(asctime)s:%(processName)-10s:%(filename)s:%(funcName)s:%(lineno)04d:%(levelname)s:%(message)s',
                        datefmt = '%Y-%m-%d %H:%M:%S')


def init_mongo_client():
    global mongo_client
    mongo_client = MongoClient(
        MONGO_HOST,
        27017,
        username=MONGO_INITDB_ROOT_USERNAME,
        password=MONGO_INITDB_ROOT_PASSWORD
    )

def add_to_db(payload,status,entity):
    db = mongo_client[MONGO_INITDB_DATABASE]
    collection = db[COLLECTION]
    json_payload = copy.deepcopy(payload)
    json_payload['status'] = status
    json_payload['entity'] = entity
    inserted_id = collection.insert_one(json_payload).inserted_id
    return inserted_id

def publish_to_redis(payload,db_id,entity):
    json_payload = copy.deepcopy(payload)
    json_payload['id'] = str(db_id)
    json_payload['entity'] = entity
    redis.publish(REDIS_CHANNEL,json.dumps(json_payload,indent=2))

def subscribe_channel(channel_name=REDIS_CHANNEL,handler=None):
    if handler:
        pubsub.subscribe(**{channel_name: handler})    
    else:
        pubsub.subscribe(channel_name)

def redis_channel_get_message():
    pubsub.get_message()

def mongo_update(id,status,result_payload = ''):
    myquery = {"_id" : ObjectId(id)}
    new_values = {"$set": {'status' : status , 'result_payload' : result_payload}}
    db = mongo_client[MONGO_INITDB_DATABASE]
    collection = db[COLLECTION]
    collection.update_one(myquery,new_values)