from flask import Blueprint, jsonify, make_response, request
from datetime import UTC, datetime
from bson import ObjectId
import bcrypt
import globals

users_bp = Blueprint('users_bp', __name__)

users = globals.db.users

@users_bp.route("/api/v1.0/users/<string:id>", methods=["GET"])
def getUser(id):
    user = users.find_one({ "_id": ObjectId(id) })
    if user is not None:
        user["_id"] = str(user["_id"])
        user.pop("password", None)
        return make_response(jsonify(user), 200)
    else:
        return make_response(jsonify({ "error": "Invalid user ID" }), 404)

@users_bp.route("/api/v1.0/users", methods=["GET"])
def getUsers():
    data_to_return = []
    for user in users.find():
        user["_id"] = str(user["_id"])
        user.pop("password", None)
        data_to_return.append(user)
    return make_response(jsonify(data_to_return), 200)

@users_bp.route("/api/v1.0/users", methods=['POST'])
def createUser():
    data = request.get_json()
    
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
    
    # Prevent duplicate accounts
    if users.find_one({ "email": data["email"] }):
        return make_response(jsonify({ "error": "Email already exists..." }), 409)
    
    new_user = {
        "firstName": data["firstName"],
        "lastName": data["lastName"],
        "email": data["email"],
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
    
    result = users.insert_one(new_user)
    return make_response(jsonify({ "id": str(result.inserted_id), "message": "User created successfully" }), 201)
    
@users_bp.route("/api/v1.0/users/<string:id>", methods=['PUT'])
def updateUser(id):
    if "firstName" in request.json and "lastName" in request.json and "email" in request.json and "phone" in request.json and "address" in request.json and "DOB" in request.json:
        result = users.update_one({
            "_id": ObjectId(id)
        }, {
            "$set": {
                "firstName": request.json["firstName"],
                "lastName": request.json["lastName"],
                "email": request.json["email"],
                "phone": request.json["phone"],
                "address": request.json["address"],
                "DOB": request.json["DOB"]
            }
        })
        if result.matched_count == 1:
            edited_user_link = "http://localhost:5000/api/v1.0/users/" + id
            return make_response(jsonify({ "url": edited_user_link }), 200)
        else:
            return make_response(jsonify({ "error": "Invalid user ID" }), 404)
    else:
        return make_response(jsonify({ "error": "Missing required fields" }), 404)
    
@users_bp.route("/api/v1.0/users/<string:id>", methods=['DELETE'])
def deleteUser(id):
    result = users.delete_one({ "_id": ObjectId(id) })
    if result.deleted_count == 1:
        return make_response(jsonify( {} ), 204)
    else:
        return make_response(jsonify({ "error": "Invalid user ID" }), 404)