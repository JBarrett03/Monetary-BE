from flask import Blueprint, jsonify, make_response, request
from datetime import datetime
import globals
import jwt
import bcrypt
import globals

auth_bp = Blueprint('auth_bp', __name__)
users = globals.db.users
blacklist = globals.db.blacklist

@auth_bp.route("/api/v1.0/login", methods=['GET'])
def login():
    auth = request.authorization
    
    if auth:
        user = users.find_one({ "username": auth.username })
        if user is not None:
            if bcrypt.checkpw(bytes(auth.password, 'UTF-8'), user["password"]):
                token = jwt.encode({
                    'user': auth.username,
                    'admin': user['admin'],
                    'exp': datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=30)
                    },
                    globals.secret_key,
                    algorithm='HS256')
                return make_response(jsonify({ "token": token }), 200)
            else:
                return make_response(jsonify({ "message": "Bad password" }), 401)
        else:
            return make_response(jsonify({ "message": "Bad username" }), 401)
    return make_response(jsonify({ "message": "Authentication required..." }), 401)

@auth_bp.route("/api/v1.0/logout", methods=['GET'])
def logout():
    token = request.headers['x-access-token']
    blacklist.insert_one({ "token": token })
    return make_response(jsonify({ "message": "Logout successful" }), 200)
