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
    if "firstName" in request.json and "lastName" in request.json and "username" in request.json and "password" in request.json and "phone" in request.json and "address" in request.json and "DOB" in request.json:
        new_user = {
            "firstName": request.json["firstName"],
            "lastName": request.json["lastName"],
            "username": request.json["username"],
            "password": bcrypt.hashpw(request.json["password"].encode(), bcrypt.gensalt()),
            "phone": request.json["phone"],
            "address": request.json["address"],
            "DOB": request.json["DOB"],
            "admin": False,
            "emailVerified": False,
            "phoneVerified": False,
            "status": "active",
            "createdAt": datetime.now(UTC).isoformat(),
            "lastLoginAt": datetime.now(UTC).isoformat()
        }
        new_user_id = users.insert_one(new_user)
        new_user_link = "http://localhost:5000/api/v1.0/users/" + str(new_user_id.inserted_id)
        return make_response(jsonify({ "url": new_user_link }), 201)
    else:
        return make_response(jsonify({ "error": "Missing required fields" }), 404)
    
@users_bp.route("/api/v1.0/users/<string:id>", methods=['PUT'])
def updateUser(id):
    if "firstName" in request.json and "lastName" in request.json and "username" in request.json and "phone" in request.json and "address" in request.json and "DOB" in request.json:
        result = users.update_one({
            "_id": ObjectId(id)
        }, {
            "$set": {
                "firstName": request.json["firstName"],
                "lastName": request.json["lastName"],
                "username": request.json["username"],
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