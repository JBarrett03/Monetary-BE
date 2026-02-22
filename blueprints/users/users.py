from flask import Blueprint, jsonify, make_response, request
from datetime import UTC, datetime
from bson import ObjectId
import bcrypt
import globals

users_bp = Blueprint('users_bp', __name__)

def get_users():
    return globals.db.users

@users_bp.route("/api/v1.0/users/<string:id>", methods=["GET"])
def getUser(id):
    user = get_users().find_one({ "_id": ObjectId(id) })
    if user is not None:
        user["_id"] = str(user["_id"])
        user.pop("password", None)
        return make_response(jsonify(user), 200)
    else:
        return make_response(jsonify({ "error": "Invalid user ID" }), 404)

@users_bp.route("/api/v1.0/users", methods=["GET"])
def getUsers():
    data_to_return = []
    for user in get_users().find():
        user["_id"] = str(user["_id"])
        user.pop("password", None)
        data_to_return.append(user)
    return make_response(jsonify(data_to_return), 200)

@users_bp.route("/api/v1.0/users", methods=['POST'])
def createUser():
    data = request.get_json()
    email = data["email"].strip().lower()
    
    required_fields = [
        "firstName",
        "lastName",
        "email",
        "password",
        "phone",
        "address",
        "DOB"
    ]
    
    if not all(field in data for field in required_fields):
        return make_response(jsonify({ "error": "Missing required fields..." }), 400)
    
    if get_users().find_one({ "email": email }):
        return make_response(jsonify({ "error": "Email already exists..." }), 409)
    
    new_user = {
        "firstName": data["firstName"],
        "lastName": data["lastName"],
        "email": email,
        "password": bcrypt.hashpw(bytes(data["password"], 'UTF-8'), bcrypt.gensalt()),
        "phone": data["phone"],
        "address": data["address"],
        "DOB": data["DOB"],
        "admin": False,
        "emailVerified": False,
        "phoneVerified": False,
        "createdAt": datetime.now(UTC).isoformat() + "Z",
        "lastLogin": datetime.now(UTC).isoformat() + "Z"
    }
    
    result = get_users().insert_one(new_user)
    return make_response(jsonify({ "id": str(result.inserted_id), "message": "User created successfully" }), 201)
    
@users_bp.route("/api/v1.0/users/<string:id>", methods=['PUT'])
def updateUser(id):
    if not ObjectId.is_valid(id):
        return make_response(jsonify({ "error": "Invalid user ID" }), 400)
    
    data = request.get_json()
    
    allowed_fields = ["firstName", "lastName", "email", "password", "phone", "address", "DOB"]
    updated_fields = {}
    
    for field in allowed_fields:
        if field in data:
            if field == "email":
                updated_fields["email"] = data["email"].strip().lower()
            elif field == "password":
                updated_fields["password"] = bcrypt.hashpw(bytes(data["password"], 'UTF-8'), bcrypt.gensalt())
            else:
                updated_fields[field] = data[field]
    
    if not updated_fields:
        return make_response(jsonify({ "error": "No valid fields to update" }), 400)
    
    result = get_users().update_one({ "_id": ObjectId(id) }, { "$set": updated_fields })
    
    if result.matched_count == 1:
        return make_response(jsonify({ "message": "User updated successfully" }), 200)
    else:
        return make_response(jsonify({ "error": "User not found" }), 404)
    
    
@users_bp.route("/api/v1.0/users/<string:id>", methods=['DELETE'])
def deleteUser(id):
    result = get_users().delete_one({ "_id": ObjectId(id) })
    if result.deleted_count == 1:
        return make_response(jsonify( {} ), 204)
    else:
        return make_response(jsonify({ "error": "Invalid user ID" }), 404)