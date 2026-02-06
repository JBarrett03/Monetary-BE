from flask import Flask, jsonify, make_response

app = Flask(__name__)

users = [
    {
    "_id": {
        "$oid": "697540596bd2ce0e5cf96566"
    },
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
    "_id": {
        "$oid": "697540596bd2ce0e5cf96567"
    },
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
    "_id": {
        "$oid": "697540596bd2ce0e5cf96568"
    },
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

if __name__ == '__main__':
    app.run(debug=True)