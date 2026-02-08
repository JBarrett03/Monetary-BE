import random
from flask import make_response, jsonify, request, Blueprint
from datetime import datetime, UTC
from bson import ObjectId
import globals

accounts_bp = Blueprint('accounts_bp', __name__)
accounts = globals.db.accounts
users = globals.db.users

@accounts_bp.route("/api/v1.0/users/<string:userId>/accounts", methods=['GET'])
def getAllUserAccounts(userId):
    if not ObjectId.is_valid(userId):
        return make_response(jsonify({ "error": "Invalid User Id" }), 400)
    
    user_object_id = ObjectId(userId)
    
    data_to_return = []
    for account in accounts.find({"userId": user_object_id, "status": { "$ne": "archived" }}).sort("order", 1):
        account["_id"] = str(account["_id"])
        account["userId"] = str(account["userId"])
        data_to_return.append(account)
        
    return make_response(jsonify(data_to_return), 200)

@accounts_bp.route("/api/v1.0/users/<string:userId>/accounts/<string:accountId>", methods=['GET'])
def getUserAccount(userId, accountId):
    if not ObjectId.is_valid(userId) or not ObjectId.is_valid(accountId):
        return make_response(jsonify({ "error": "Invalid user Id or Account Id" }), 400)
    
    account = accounts.find_one({"_id": ObjectId(accountId), "userId": ObjectId(userId)})
    
    if account is None:
        return make_response(jsonify({ "error": "Account not found" }), 404)
    
    account["_id"] = str(account["_id"])
    account["userId"] = str(account["userId"])
    return make_response(jsonify(account), 200)

@accounts_bp.route("/api/v1.0/users/<string:userId>/accounts", methods=['POST'])
def addAccount(userId):
    if not ObjectId.is_valid(userId):
        return make_response(jsonify({ "error": "Invalid User Id" }), 400)
    
    user = users.find_one({"_id": ObjectId(userId)})
    if not user:
        return make_response(jsonify({ "error": "User not found" }), 404)
    
    account_order = accounts.count_documents({ "userId": ObjectId(userId) })
        
    new_account = {
        "userId": ObjectId(userId),
        "accountType": request.form["accountType"],
        "currency": request.form["currency"],
        "balance": 0.00,
        "availableBalance": 0.00,
        "status": "active",
        "accountNumber": str(random.randint(10000000, 99999999)),
        "order": account_order,
        "openedAt": datetime.now(UTC).isoformat() + "Z",
        "updatedAt": datetime.now(UTC).isoformat() + "Z"
    }
    
    result = accounts.insert_one(new_account)
    new_account_link = f"http://localhost:5000/api/v1.0/users/{userId}/accounts/{result.inserted_id}"
    return make_response(jsonify({"url": new_account_link}), 201)

@accounts_bp.route("/api/v1.0/users/<string:userId>/accounts/<string:accountId>", methods=['POST'])
def addBalance(userId, accountId):
    if not ObjectId.is_valid(userId) or not ObjectId.is_valid(accountId):
        return make_response(jsonify({ "error": "Invalid User Id or Account Id" }), 400)
    
    amount = request.form.get("amount")
    if amount is None:
        return make_response(jsonify({ "error": "Amount is required" }), 400)
    
    try:
        amount = float(amount)
    except ValueError:
        return make_response(jsonify({ "error": "Invalid amount format" }), 400)
    
    account = accounts.find_one({ "_id": ObjectId(accountId), "userId": ObjectId(userId) })
    if not account:
        return make_response(jsonify({ "error": "Account not found" }), 404)
    
    new_balance = account.get("balance", 0) + amount
    
    accounts.update_one(
        { "_id": ObjectId(accountId) },
        {
            "$set": {
                "balance": new_balance,
                "availableBalance": new_balance,
                "updatedAt": datetime.now(UTC).isoformat() + "Z"
            }
        }
    )
    
    return make_response(jsonify({ "newBalance": new_balance }), 200)

@accounts_bp.route("/api/v1.0/users/<string:userId>/accounts/order-accounts", methods=['PUT'])
def saveAccountOrder(userId):
    if not ObjectId.is_valid(userId):
        return make_response(jsonify({ "error": "Invalid User Id" }), 400)
    
    data = request.get_json()
    
    for item in data:
        accounts.update_one(
            {
                "_id": ObjectId(item["accountId"]),
                "userId": ObjectId(userId)
            },
            {
                "$set": {
                    "order": item["order"],
                    "updatedAt": datetime.now(UTC).isoformat() + "Z"
                }
            }
        )
    
    return make_response(jsonify({ "message": "Account order updated successfully" }), 200)

@accounts_bp.route("/api/v1.0/users/<string:userId>/accounts/<string:accountId>", methods=['PUT'])
def archiveAccount(userId, accountId):
    if not ObjectId.is_valid(userId) or not ObjectId.is_valid(accountId):
        return make_response(jsonify({ "error": "Invalid User Id or Account Id" }), 400)
    
    result = accounts.update_one(
        {
            "_id": ObjectId(accountId),
            "userId": ObjectId(userId)
        },
        {
            "$set": {
                "status": "archived",
                "updatedAt": datetime.now(UTC).isoformat() + "Z"
            }
        }
    )
    
    if result.matched_count == 1:
        return make_response(jsonify({ "message": "Account archived successfully" }), 200)
    else:
        return make_response(jsonify({ "error": "Account not found" }), 404)
    
@accounts_bp.route("/api/v1.0/users/<string:userId>/accounts/archived", methods=['GET'])
def getArchivedAccounts(userId):
    if not ObjectId.is_valid(userId):
        return make_response(jsonify({ "error": "Invalid User Id" }), 400)
    
    archived_account = list(accounts.find({
        "userId": ObjectId(userId),
        "status": "archived"
    }))
    
    for account in archived_account:
        account["_id"] = str(account["_id"])
        account["userId"] = str(account["userId"])
        
    return make_response(jsonify(archived_account), 200)