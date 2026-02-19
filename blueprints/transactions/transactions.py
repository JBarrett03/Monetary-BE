from flask import make_response, jsonify, request, Blueprint
from datetime import datetime, UTC
from bson import ObjectId
import globals
from category_rules import CATEGORY_RULES

transactions_bp = Blueprint('transactions_bp', __name__)

def get_transactions():
    return globals.db.transactions

def get_accounts():
    return globals.db.accounts

def get_users():
    return globals.db.users

@transactions_bp.route("/api/v1.0/users/<string:userId>/accounts/<string:accountId>/transactions", methods=['GET'])
def getAllTransactions(userId, accountId):
    if not ObjectId.is_valid(userId) or not ObjectId.is_valid(accountId):
        return make_response(jsonify({ "error": "Invalid User Id or Account Id" }), 400)
        
    transactions = get_transactions().find({
        "accountId": ObjectId(accountId),
        "userId": ObjectId(userId)
    }).sort("createdAt", -1)
    
    data_to_return = []
    
    for transaction in transactions:
        transaction["_id"] = str(transaction["_id"])
        transaction["accountId"] = str(transaction["accountId"])
        transaction["userId"] = str(transaction["userId"])
        data_to_return.append(transaction)
        
    return make_response(jsonify(data_to_return), 200)

@transactions_bp.route("/api/v1.0/users/<string:userId>/accounts/<string:accountId>/transactions/<string:transactionId>", methods=['GET'])
def getTransaction(userId, accountId, transactionId):
    if not ObjectId.is_valid(userId) or not ObjectId.is_valid(accountId) or not ObjectId.is_valid(transactionId):
        return make_response(jsonify({ "error": "Invalid User Id, Account Id or Transaction Id" }), 400)
    
    transaction = get_transactions().find_one({
        "_id": ObjectId(transactionId), 
        "accountId": ObjectId(accountId),
        "userId": ObjectId(userId)
    })
    
    if transaction is None:
        return make_response(jsonify({ "error": "Transaction not found" }), 404)
    
    transaction["_id"] = str(transaction["_id"])
    transaction["accountId"] = str(transaction["accountId"])
    transaction["userId"] = str(transaction["userId"])
    
    return make_response(jsonify(transaction), 200)

@transactions_bp.route("/api/v1.0/users/<string:userId>/accounts/<string:accountId>/transactions", methods=['POST'])
def addTransaction(userId, accountId):
    if not ObjectId.is_valid(userId) or not ObjectId.is_valid(accountId):
        return make_response(jsonify({ "error": "Invalid User Id or Account Id" }), 400)
    
    user = get_users().find_one({ "_id": ObjectId(userId) })
    if not user:
        return make_response(jsonify({ "error": "User not found" }), 404)
    
    account = get_accounts().find_one({
        "_id": ObjectId(accountId), 
        "userId": ObjectId(userId) 
    })
    if not account:
        return make_response(jsonify({ "error": "Account not found" }), 404)
    
    data = request.get_json()
    if not data:
        return make_response(jsonify({ "error": "Request body must be JSON" }), 400)
    
    try:
        amount = float(data.get("amount"))
    except (KeyError, ValueError):
        return make_response(jsonify({ "error": "invalid or missing amount" }), 400)
    
    if amount <= 0:
        return make_response(jsonify({ "error": "Amount must be greater than zero" }), 400)
    
    transaction_direction = data.get("direction")
    transaction_type = data.get("type", "unknown")
    merchant = data.get("merchant", "")
    description = data.get("description", "")
    
    if transaction_direction not in ["in", "out"]:
        return make_response(jsonify({ "error": "Direction must be 'in' or 'out'" }), 400)
    
    balance = float(account.get("balance", 0))
    
    if transaction_direction == "out":
        new_balance = round(balance - amount, 2)
    else:
        new_balance = round(balance + amount, 2)
    
    if new_balance < 0:
        return make_response(jsonify({ "error": "Insufficient funds" }), 400)
    
    get_accounts().update_one(
        { "_id": ObjectId(accountId) },
        {
            "$set": {
                "balance": new_balance,
                "availableBalance": new_balance,
                "updatedAt": datetime.now(UTC)
            }
        }
    )
    
    category = autoCategoriseTransaction(merchant, description)
    
    new_transaction = {
        "accountId": ObjectId(accountId),
        "userId": ObjectId(userId),
        "direction": transaction_direction,
        "type": transaction_type,
        "amount": amount,
        "status": "completed",
        "description": description,
        "merchant": merchant,
        "category": category,
        "balanceAfter": new_balance,
        "createdAt": datetime.now(UTC).isoformat()
    }
    
    result = get_transactions().insert_one(new_transaction)
    
    return make_response(jsonify({ "transactionId": str(result.inserted_id), "newBalance": new_balance }), 201)

def autoCategoriseTransaction(merchant: str, description: str) -> str:
    text = f"{merchant} {description}".lower()
    
    for category, keywords in CATEGORY_RULES.items():
        for keyword in keywords:
            if keyword in text:
                return category
    
    return "Miscellaneous"