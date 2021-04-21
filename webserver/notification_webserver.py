import os
import json
import sys
import logging
sys.path.append(".")
from library import *
from pymongo import MongoClient
from redis import Redis
from flask import Flask, request, Response
from flask_executor import Executor
from bson import json_util, ObjectId


app = Flask(__name__)
executor = Executor(app)
setup_logging()
logging.info("logger init")
init_redis_client()
init_mongo_client()

def post_message_to_entity(entity,request):
    res = Response()
    res.content_type = 'application/json'
    res.status_code = 200
    res.data = 'SUCCESS'
    error_msg = 'Please send user, message and owner either in query parameters or as json payload.'
    if request.is_json:
        payload = request.get_json()
        user = payload.get('user',None)
        if user and payload.get('message',None):
            db_id = add_to_db(payload,ADDING_TO_REDIS_QUEUE,entity)
            executor.submit(publish_to_redis,payload,db_id,entity)
            res.data=str(db_id)
        else:
            res.data= error_msg
            res.status_code = 404
    else:
        user = request.args.get('user',None)
        message=request.args.get('message',None)
        if user and message:
            payload = {
                'user':user,
                'message': message,
            }
            db_id = add_to_db(payload,ADDING_TO_REDIS_QUEUE,entity)
            executor.submit(publish_to_redis,payload,db_id,entity)
            #publish_to_redis(payload,db_id,entity)
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
    owner
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
    try:
        result = get_obj_by_id(id)
        res.data = json_util.dumps(result)
    except Exception as e:
        res.data = str(e)
        res.status_code = 404

    return res

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000', debug=True)


