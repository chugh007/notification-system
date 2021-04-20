import os
import json
from pymongo import MongoClient
from redis import Redis
from flask import Flask, request, Response
from flask_executor import Executor
import copy

app = Flask(__name__)
executor = Executor(app)

MONGO_INITDB_ROOT_USERNAME = os.environ.get('MONGO_INITDB_ROOT_USERNAME','root')
MONGO_INITDB_ROOT_PASSWORD = os.environ.get('MONGO_INITDB_ROOT_PASSWORD','root')
MONGO_INITDB_DATABASE = os.environ.get('MONGO_INITDB_DATABASE','test')
MONGO_HOST = os.environ['MONGO_HOST']
REDIS_HOST = os.environ['REDIS_HOST']
REDIS_PORT= int(os.environ.get('REDIS_PORT',6379))
COLLECTION=os.environ.get('MONGO_COLLECTION','my-collection')
ADDING_TO_REDIS_QUEUE = "ADDING TO REDIS QUEUE"
PUSHED_TO_REDIS_QUEUE = "PUSHED TO REDIS QUEUE"
redis = Redis(REDIS_HOST,REDIS_PORT,db=0)
REDIS_CHANNEL = os.environ.get('REDIS_CHANNEL','NOTIFICATION')

def get_mongo_client():
    client = MongoClient(
        MONGO_HOST,
        27017,
        username=MONGO_INITDB_ROOT_USERNAME,
        password=MONGO_INITDB_ROOT_PASSWORD
    )
    return client

def add_to_db(payload,status,entity):
    client = get_mongo_client()
    db = client[MONGO_INITDB_DATABASE]
    collection = db[COLLECTION]
    json_payload = copy.deepcopy(payload)
    json_payload['status'] = status
    json_payload['entity'] = entity
    inserted_id = collection.insert_one(json_payload).inserted_id
    return inserted_id

def publish_to_redis(payload,db_id):
    json_payload = copy.deepcopy(payload)
    json_payload['id'] = db_id
    redis.publish(REDIS_CHANNEL,json_payload)

def post_message_to_entity(entity,request):
    res = Response()
    res.content_type = 'application/json'
    res.status_code = 200
    res.data = 'SUCCESS'
    error_msg = 'Please send user and message either in query parameters or as json payload.'
    if request.is_json:
        payload = request.get_json()
        user = payload.get('user',None)
        if user and payload.get('message',None):
            db_id = add_to_db(payload,ADDING_TO_REDIS_QUEUE,entity)
            executor.submit(publish_to_redis,payload,db_id)
            res.data=str(db_id)
        else:
            res.data= error_msg
            res.status_code = 404
    else:
        user = request.args.get('user',None)
        message=request.args.get('message',None)
        if user and message :
            payload = {
                'user':user,
                'message': message
            }
            db_id = add_to_db(payload,ADDING_TO_REDIS_QUEUE,entity)
            executor.submit(publish_to_redis,payload,db_id)
            res.data=str(db_id)
            
        else:
            res.data = error_msg
            res.status_code=404
    
    return res
    

@app.route("/",methods=["GET"])
def alive():
    response = Response()
    response.status_code = 200
    response.data = 'alive'
    response.content_type = 'text/plain'
    return response

@app.route("/post_on_slack",methods=["POST"])
def post_message_on_slack():
    """
    user: ldap name
    message
    """
    return post_message_to_entity("SLACK",request)

@app.route("/post_on_email",methods=["POST"])
def post_message_on_email():
    """
    user: ldap name
    message
    """
    return post_message_to_entity("EMAIL",request)

@app.route("/check_status/<id>",methods=["GET"])
def check_status(id):
    res = Response()
    res.content_type = 'application/json'
    res.status_code = 200
    res.data = 'SUCCESS'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000', debug=True)


