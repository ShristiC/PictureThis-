from json import dumps

from bson import ObjectId
from flask import Flask

from dotenv import load_dotenv
import os

from flask import jsonify
from flask import request
from flask_pymongo import pymongo

load_dotenv()

MONGO_DB_URL = "mongodb+srv://{}:{}@cluster0-prcpb.mongodb.net/test?retryWrites=true&w=majority" \
    .format(os.getenv("MONGO_USER"), os.getenv("MONGO_PASSWORD"))

app = Flask(__name__)

mongo_client = pymongo.MongoClient(MONGO_DB_URL)
mongo_db = mongo_client.get_database('sample_geospatial')
shipwrecks = mongo_db.get_collection('shipwrecks')


@app.route('/')
def index():
    return "Welcome to homepage"


@app.route('/loc/view/<user_id>')
def get_user(user_id):
    user = shipwrecks.find_one({'_id': ObjectId(user_id)})
    return dumps(user)


@app.route('/loc/add/', methods=['POST'])
def add_user():
    received = request.json
    username = received['username']
    email = received['email']

    if username and email and request.method == 'POST':
        entry_id = shipwrecks.insert({'username': username, 'email': email})

        response = jsonify("user {} added successfully".format(entry_id))
        response.status_code = 200
        return response
    else:
        response = jsonify("user creating failed")
        response.status_code = 500
        return response


@app.route('/loc/update/<user_id>', methods=['PUT'])
def update_user(user_id):
    received = request.json
    username = received['username']
    email = received['email']

    if username and email:
        mongo_client.db.users.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'username': username, 'email': email}}
        )

        response = jsonify("user updated successfully")
        response.status_code = 200
        return response

    else:
        not_found()


@app.route('/loc/delete/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    mongo_client.db.users.delete_one({'_id': ObjectId(user_id)})
    resp = jsonify("user deleted successfully")
    resp.status_code = 200
    return resp


@app.errorhandler(404)
def not_found(error=None):
    msg = {
        'status': 404,
        'message': 'Request not found ' + request.url
    }

    response = jsonify(msg)
    response.status_code = 404
    return response


if __name__ == '__main__':
    app.run()