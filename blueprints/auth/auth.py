from flask import Blueprint, jsonify, make_response, request
from datetime import datetime, UTC, timedelta
import globals
import jwt
import bcrypt
from pymongo import ReturnDocument
from decorators import limiter

auth_bp = Blueprint('auth_bp', __name__)

def get_users():
    return globals.db.users

def get_blacklist():
    return globals.db.blacklist

@auth_bp.route("/api/v1.0/login", methods=['POST'])
@limiter.limit("30 per minute")
def login():
    data = request.get_json()
    
    if not data or "email" not in data or "password" not in data:
        return make_response(jsonify({ "error": "Email and Password are required..." }), 400)
    
    email = data["email"].strip().lower()
    user = get_users().find_one({ "email": email })
    
    if not user:
        return make_response(jsonify({ "error": "Invalid email or password..." }), 401)
    
    date = datetime.utcnow()
    
    lock_until = user.get("lockUntil")
    if lock_until and date < lock_until:
        return make_response(jsonify({ "error": "Account is locked due to multiple failed login attempts. Please try again later..." }), 403)
    
    if not bcrypt.checkpw(data["password"].encode('utf-8'), user["password"]):
        
        attempts = user.get("failedAttempts", 0)
        incremented_attempts = attempts + 1
        
        if attempts >= 5:
            get_users().update_one(
                { "_id": user["_id"] },
                { "$set": {
                    "failedAttempts": 0,
                    "lockUntil": date + timedelta(minutes=1)
                }}
            )
        else:
            get_users().update_one(
                { "_id": user["_id"] },
                { "$set": { "failedAttempts": incremented_attempts }}
            )

        return make_response(jsonify({ "error": "Account is temporarily locked due to multiple failed login attempts. Please try again later..." }), 403)
    
    get_users().update_one(
        { "_id": user["_id"] },
        { "$set": {
            "failedAttempts": 0,
            "lockUntil": None,
            "lastLogin": date.isoformat() + "Z"
        }}
    )
    
    token = jwt.encode(
        {
            "userId": str(user["_id"]),
            "admin": user.get("admin", False),
            "exp": datetime.now(UTC) + timedelta(minutes=30)
        },
        globals.secret_key,
        algorithm='HS256'
    )
    return make_response(jsonify({ "userId": str(user["_id"]), "token": token }), 200)

@auth_bp.route("/api/v1.0/logout", methods=['GET'])
def logout():
    token = request.headers.get('x-access-token')
    
    if not token:
        return make_response(jsonify({ "error": "Token is missing..." }), 400)
    
    get_blacklist().insert_one({ "token": token })
    return make_response(jsonify({ "message": "Logout successful" }), 200)
