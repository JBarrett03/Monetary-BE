from datetime import UTC, datetime
from flask import Flask, jsonify, make_response, request
import uuid, random

app = Flask(__name__)

users = {}

def generate_dummy_data():
    firstNames = ["John", "Jane", "Alice", "Bob", "Charlie"]
    lastNames = ["Doe", "Smith", "Johnson", "Brown", "Davis"]
    towns = [
        "Coleraine", "Banbridge", "Belfast", "Lisburn",
        "Ballymena", "Derry", "Newry", "Enniskillen",
        "Omagh", "Ballymoney"
    ]
    
    user_dict = {}
    
    for i in range(100):
        userId = str(uuid.uuid4())
        firstName = random.choice(firstNames)
        lastName = random.choice(lastNames)
        email = f"{firstName.lower()}.{lastName.lower()}@example.com"
        password = "password123"
        phone = f"+1-555-{random.randint(1000, 9999)}"
        address = f"{random.randint(1, 999)} {random.choice(towns)} Street"
        DOB = f"{random.randint(1950, 2000)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"
        admin = False
        emailVerified = random.choice([True, False])
        phoneVerified = random.choice([True, False])
        status = "active"
        createdAt = datetime.now(UTC).isoformat()
        lastLoginAt = datetime.now(UTC).isoformat()
        user_dict[userId] = {
            "id": userId,
            "firstName": firstName,
            "lastName": lastName,
            "email": email,
            "password": password,
            "phone": phone,
            "address": address,
            "DOB": DOB,
            "admin": admin,
            "emailVerified": emailVerified,
            "phoneVerified": phoneVerified,
            "status": status,
            "createdAt": createdAt,
            "lastLoginAt": lastLoginAt
        }
    return user_dict

users = generate_dummy_data()


@app.route("/api/v1.0/users", methods=["GET"])
def getUsers():
    return make_response(jsonify(users), 200)

@app.route("/api/v1.0/users/<string:id>", methods=["GET"])
def getUser(id):
    if id in users:
        return make_response(jsonify(users[id]), 200)
    return make_response(jsonify({ "error": "Invalid user ID" }), 404)
    
@app.route("/api/v1.0/users", methods=['POST'])
def createUser():
    if "firstName" in request.json and "lastName" in request.json and "email" in request.json and "password" in request.json and "phone" in request.json and "address" in request.json and "DOB" in request.json:
        next_id = str(uuid.uuid4())
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
        users[next_id] = new_user
        return make_response(jsonify({ next_id: new_user }), 201)
    else:
        return make_response(jsonify({ "error": "Missing required fields" }), 404)

@app.route("/api/v1.0/users/<string:id>", methods=['PUT'])
def updateUser(id):
    if id not in users:
        return make_response(jsonify({ "error": "Invalid user ID" }), 404)
    else:
        if "firstName" in request.json and "lastName" in request.json and "email" in request.json and "phone" in request.json and "address" in request.json and "DOB" in request.json:
            users[id]["firstName"] = request.json["firstName"]
            users[id]["lastName"] = request.json["lastName"]
            users[id]["email"] = request.json["email"]
            users[id]["phone"] = request.json["phone"]
            users[id]["address"] = request.json["address"]
            users[id]["DOB"] = request.json["DOB"]
            return make_response(jsonify({ id: users[id] }), 200)
        else:
            return make_response(jsonify({ "error": "Missing required fields" }), 404)


@app.route("/api/v1.0/users/<string:id>", methods=['DELETE'])
def deleteUser(id):
    if id in users:
        del users[id]
        return make_response(jsonify( {} ), 204)
    else:
        return make_response(jsonify({ "error": "Invalid user ID" }), 404)

if __name__ == '__main__':
    app.run(debug=True)