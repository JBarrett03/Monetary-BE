from flask import jsonify, make_response, request
import jwt
from functools import wraps
import globals

def get_blacklist():
    return globals.db.blacklist

def jwt_required(func):
    @wraps(func)
    def jwt_required_wrapper(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        
        try:
            data = jwt.decode(token, globals.secret_key, algorithms='HS256')
        except:
            return make_response(jsonify({ "message": "Token is invalid" }), 401)
        bl_token = get_blacklist().find_one({ "token": token })
        if bl_token is not None:
            return make_response(jsonify({ "message": "Token has been cancelled" }), 401)
        return func(*args, **kwargs)
    return jwt_required_wrapper