from datetime import UTC, datetime
from flask import Flask, jsonify, make_response, request

app = Flask(__name__)

users = [
    {
    "id": 1,
    "firstName": "John",
    "lastName": "Doe",
    "email": "john.doe@example.com",
    "password": "password",
    "phone": "123-456-7890",
    "address": "123 Main St, Anytown, USA",
    "DOB": "1990-01-01",
    "emailVerified": True,
    "phoneVerified": False,
    "status": "active",
    "createdAt": "2025-01-22T10:00:00Z",
    "lastLoginAt": "2025-01-22T10:00:00Z"
    },
    {
    "id": 2,
    "firstName": "Jane",
    "lastName": "Smith",
    "email": "jane.smith@example.com",
    "password": "password",
    "phone": "123-456-7890",
    "address": "123 Main St, Anytown, USA",
    "DOB": "1990-01-01",
    "emailVerified": True,
    "phoneVerified": True,
    "status": "active",
    "createdAt": "2025-01-22T10:00:00Z",
    "lastLoginAt": "2025-01-22T10:00:00Z"
    },
    {
    "id": 3,
    "firstName": "Bob",
    "lastName": "Johnson",
    "email": "bob.johnson@example.com",
    "password": "password",
    "phone": "123-456-7890",
    "address": "123 Main St, Anytown, USA",
    "DOB": "1990-01-01",
    "emailVerified": False,
    "phoneVerified": True,
    "status": "active",
    "createdAt": "2025-01-22T10:00:00Z",
    "lastLoginAt": "2025-01-22T10:00:00Z"
    }
]

@app.route("/api/v1.0/users", methods=["GET"])
def getUsers():
    return make_response(jsonify(users), 200)

@app.route("/api/v1.0/users/<int:id>", methods=["GET"])
def getUser(id):
    data_to_return = [user for user in users if user["id"] == id]
    return make_response(jsonify(data_to_return), 200)

@app.route("/api/v1.0/users", methods=['POST'])
def createUser():
    next_id = users[-1]["id"] + 1
    new_user = {
        "id": next_id,
        "firstName": request.json["firstName"],
        "lastName": request.json["lastName"],
        "email": request.json["email"],
        "password": request.json["password"],
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
    users.append(new_user)
    return make_response(jsonify(new_user), 201)

@app.route("/api/v1.0/users/<int:id>", methods=['PUT'])
def updateUser(id):
    for user in users:
        if user["id"] == id:
            user["firstName"] = request.json["firstName"]
            user["lastName"] = request.json["lastName"]
            user["email"] = request.json["email"]
            user["phone"] = request.json["phone"]
            user["address"] = request.json["address"]
            user["DOB"] = request.json["DOB"]
            break
    return make_response(jsonify(user), 200)

@app.route("/api/v1.0/users/<int:id>", methods=['DELETE'])
def deleteUser(id):
    for user in users:
        if user["id"] == id:
            users.remove(user)
            break
    return make_response(jsonify(users), 200)

if __name__ == '__main__':
    app.run(debug=True)