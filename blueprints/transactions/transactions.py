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
    
    data_to_return = []
    for transaction in get_transactions().find({"accountId": ObjectId(accountId)}):
        transaction["_id"] = str(transaction["_id"])
        transaction["accountId"] = str(transaction["accountId"])
        data_to_return.append(transaction)
        
    return make_response(jsonify(data_to_return), 200)

@transactions_bp.route("/api/v1.0/users/<string:userId>/accounts/<string:accountId>/transactions/<string:transactionId>", methods=['GET'])
def getTransaction(userId, accountId, transactionId):
    if not ObjectId.is_valid(userId) or not ObjectId.is_valid(accountId) or not ObjectId.is_valid(transactionId):
        return make_response(jsonify({ "error": "Invalid User Id, Account Id or Transaction Id" }), 400)
    
    transaction = get_transactions().find_one({"_id": ObjectId(transactionId), "accountId": ObjectId(accountId)})
    
    if transaction is None:
        return make_response(jsonify({ "error": "Transaction not found" }), 404)
    
    transaction["_id"] = str(transaction["_id"])
    transaction["accountId"] = str(transaction["accountId"])
    return make_response(jsonify(transaction), 200)

@transactions_bp.route("/api/v1.0/users/<string:userId>/accounts/<string:accountId>/transactions", methods=['POST'])
def addTransaction(userId, accountId):
    if not ObjectId.is_valid(userId) or not ObjectId.is_valid(accountId):
        return make_response(jsonify({ "error": "Invalid User Id or Account Id" }), 400)
    
    user = get_users().find_one({ "_id": ObjectId(userId) })
    if not user:
        return make_response(jsonify({ "error": "User not found" }), 404)
    
    account = get_accounts().find_one({ "_id": ObjectId(accountId), "userId": ObjectId(userId) })
    if not account:
        return make_response(jsonify({ "error": "Account not found" }), 404)
    
    amount = float(request.form["amount"])
    new_balance = round(float(account["balance"]) - amount, 2)
    merchant = request.form["merchant"]
    description = request.form["description"]
    category = autoCategoriseTransaction(merchant, description)
    
    get_accounts().update_one(
        { "_id": ObjectId(accountId) },
        {
            "$set": {
                "balance": new_balance,
                "availableBalance": new_balance,
                "updatedAt": datetime.now(UTC).isoformat()
            }
        }
    )
    
    new_transaction = {
        "accountId": ObjectId(accountId),
        "type": request.form["type"],
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