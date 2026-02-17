import random
from flask import make_response, jsonify, request, Blueprint
from datetime import datetime, UTC, timedelta
from bson import ObjectId
import globals

accounts_bp = Blueprint('accounts_bp', __name__)

def get_accounts():
    return globals.db.accounts

def get_users():
    return globals.db.users

def generate_sort_code():
    return f"{random.randint(0,99):02d}-{random.randint(0,99):02d}-{random.randint(0,99):02d}"

def generate_unique_sort_code():
    while True:
        sort_code = generate_sort_code()
        if not get_accounts().find_one({ "sortCode": sort_code }):
            return sort_code

def generate_card_number():
    card_number = ''.join([str(random.randint(0, 9)) for _ in range(16)])
    formatted = f"{card_number[0:4]} {card_number[4:8]} {card_number[8:12]} {card_number[12:16]}"
    return formatted

@accounts_bp.route("/api/v1.0/users/<string:userId>/accounts", methods=['GET'])
def getAllUserAccounts(userId):
    if not ObjectId.is_valid(userId):
        return make_response(jsonify({ "error": "Invalid User Id" }), 400)
    
    user_object_id = ObjectId(userId)
    
    data_to_return = []
    for account in get_accounts().find({"userId": user_object_id, "status": { "$ne": "archived" }}).sort("order", 1):
        account["_id"] = str(account["_id"])
        account["userId"] = str(account["userId"])
        data_to_return.append(account)
        
    return make_response(jsonify(data_to_return), 200)

@accounts_bp.route("/api/v1.0/users/<string:userId>/accounts/<string:accountId>", methods=['GET'])
def getUserAccount(userId, accountId):
    if not ObjectId.is_valid(userId) or not ObjectId.is_valid(accountId):
        return make_response(jsonify({ "error": "Invalid user Id or Account Id" }), 400)
    
    account = get_accounts().find_one({"_id": ObjectId(accountId), "userId": ObjectId(userId)})
    
    if account is None:
        return make_response(jsonify({ "error": "Account not found" }), 404)
    
    account["_id"] = str(account["_id"])
    account["userId"] = str(account["userId"])
    
    if account.get("budget"):
        
        budget = account["budget"]
        
        start_budget = datetime.fromisoformat(budget["startDate"])
        end_budget = datetime.fromisoformat(budget["endDate"])
        
        transactions = list(globals.db.transactions.find({
            "accountId": ObjectId(accountId),
            "userId": ObjectId(userId),
            "type": "debit"
        }))
        
        total_spent = 0.00
        
        for transaction in transactions:
            if "createdAt" in transaction:
                created_at = datetime.fromisoformat(transaction["createdAt"].replace("Z", "+00:00"))
                if start_budget <= created_at <= end_budget:
                    total_spent += float(transaction["amount"])
        
        remaining_budget = float(budget["amount"]) - total_spent
        
        if remaining_budget < 0:
            remaining_budget = 0.00
            
        account["budgetSpent"] = total_spent
        account["budgetRemaining"] = remaining_budget
        
    return make_response(jsonify(account), 200)

@accounts_bp.route("/api/v1.0/users/<string:userId>/accounts", methods=['POST'])
def addAccount(userId):
    if not ObjectId.is_valid(userId):
        return make_response(jsonify({ "error": "Invalid User Id" }), 400)
    
    user = get_users().find_one({"_id": ObjectId(userId)})
    if not user:
        return make_response(jsonify({ "error": "User not found" }), 404)
    
    data = request.get_json()
    
    if not data:
        return make_response(jsonify({ "error": "Request body must be JSON" }), 400)
    
    accountType = data.get("accountType")
    currency = data.get("currency")
    
    if not accountType or not currency:
        return make_response(jsonify({ "error": "accountType and currency are required fields" }), 400)
    
    accountType = accountType.lower()
    
    if accountType not in ["savings", "checking"]:
        return make_response(jsonify({ "error": "Invalid account type. Must be 'savings' or 'checking'" }), 400)
    
    account_order = get_accounts().count_documents({ "userId": ObjectId(userId) })
        
    new_account = {
        "userId": ObjectId(userId),
        "accountType": accountType,
        "currency": currency,
        "balance": 0.00,
        "availableBalance": 0.00,
        "budget": None,
        "status": "active",
        "accountNumber": generate_card_number(),
        "sortCode": generate_unique_sort_code(),
        "isDefault": False,
        "order": account_order,
        "openedAt": datetime.now(UTC).isoformat() + "Z",
        "updatedAt": datetime.now(UTC).isoformat() + "Z"
    }
    
    result = get_accounts().insert_one(new_account)
    new_account["_id"] = str(result.inserted_id)
    new_account["userId"] = str(new_account["userId"])
    return make_response(jsonify(new_account), 201)

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
    
    account = get_accounts().find_one({ "_id": ObjectId(accountId), "userId": ObjectId(userId) })
    if not account:
        return make_response(jsonify({ "error": "Account not found" }), 404)
    
    new_balance = round(float(account.get("balance", 0)) + amount, 2)
    
    get_accounts().update_one(
        { "_id": ObjectId(accountId) },
        {
            "$set": {
                "balance": new_balance,
                "availableBalance": new_balance,
                "updatedAt": datetime.now(UTC).isoformat() + "Z"
            }
        }
    )
    
    new_transaction = {
        "userId": ObjectId(userId),
        "accountId": ObjectId(accountId),
        "type": "credit",
        "amount": amount,
        "status": "completed",
        "description": "Balance Top-Up",
        "merchant": "Monetary App",
        "category": "Deposit",
        "balanceAfter": new_balance,
        "createdAt": datetime.now(UTC).isoformat() + "Z"
    }
    
    transaction_result = globals.db.transactions.insert_one(new_transaction)
    
    return make_response(jsonify({ "newBalance": new_balance }), 200)

@accounts_bp.route("/api/v1.0/users/<string:userId>/accounts/order-accounts", methods=['PUT'])
def saveAccountOrder(userId):
    if not ObjectId.is_valid(userId):
        return make_response(jsonify({ "error": "Invalid User Id" }), 400)
    
    data = request.get_json()
    
    for item in data:
        get_accounts().update_one(
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
    
    result = get_accounts().update_one(
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
    
    archived_account = list(get_accounts().find({
        "userId": ObjectId(userId),
        "status": "archived"
    }))
    
    for account in archived_account:
        account["_id"] = str(account["_id"])
        account["userId"] = str(account["userId"])
        
    return make_response(jsonify(archived_account), 200)

@accounts_bp.route("/api/v1.0/users/<string:userId>/accounts/<string:accountId>/restore", methods=['PUT'])
def restoreAccount(userId, accountId):
    if not ObjectId.is_valid(userId) or not ObjectId.is_valid(accountId):
        return make_response(jsonify({ "error": "Invalid User Id or Account Id" }), 400)
    
    result = get_accounts().update_one(
        {
            "_id": ObjectId(accountId),
            "userId": ObjectId(userId)
        },
        {
            "$set": {
                "status": "active",
                "updatedAt": datetime.now(UTC).isoformat() + "Z"
            }
        }
    )
    
    if result.matched_count == 1:
        return make_response(jsonify({ "message": "Account restored successfully" }), 200)
    else:
        return make_response(jsonify({ "error": "Account not found" }), 404)
    
@accounts_bp.route("/api/v1.0/users/<string:userId>/accounts/<string:accountId>/budget", methods=['POST'])
def setBudget(userId, accountId):
    if not ObjectId.is_valid(userId) or not ObjectId.is_valid(accountId):
        return make_response(jsonify({ "error": "Invalid User Id or Account Id" }), 400)
    
    account = get_accounts().find_one({
        "_id": ObjectId(accountId),
        "userId": ObjectId(userId)
    })
    
    if not account:
        return make_response(jsonify({ "error": "Account not found" }), 404)
    
    if account["accountType"] != "savings":
        return make_response(jsonify({ "error": "Budgets can only be set for savings accounts" }), 400)
    
    data = request.get_json()
    
    amount = data.get("amount")
    budget_period = data.get("period")
    custom_start =  data.get("startDate")
    custom_end = data.get("endDate")
    
    if amount is None or not budget_period:
        return make_response(jsonify({ "error": "Amount and type are required fields" }), 400)
    
    now = datetime.now(UTC)
    
    if budget_period == 'weekly':
        start = now - timedelta(days=now.weekday())
        end = start + timedelta(days=6)
        
    elif budget_period == 'monthly': 
        start = now.replace(day=1)
        next_month = start.replace(day=28) + timedelta(days=4)
        end = next_month.replace(day=1) - timedelta(days=1)
        
    elif budget_period == 'annual':
        start = now.replace(month=1, day=1)
        end = now.replace(month=12, day=31)
        
    elif budget_period == 'custom':
        if not custom_start or not custom_end: 
            return make_response(jsonify({ "error": "Start and end dates are required for custom budget period" }), 400)
        
        start = datetime.fromisoformat(custom_start)
        end = datetime.fromisoformat(custom_end)
    
    else:
        return make_response(jsonify({ "error": "Invalid budget period type" }), 400)
    
    budget = {
        "amount": float(amount),
        "period": budget_period,
        "startDate": start.isoformat(),
        "endDate": end.isoformat()
    }
    
    get_accounts().update_one(
        {
            "_id": ObjectId(accountId),
            "userId": ObjectId(userId)
        },
        {
            "$set": {
                "budget": budget, 
                "updatedAt": datetime.now(UTC).isoformat() + "Z"
            }
        }
    )
    
    return make_response(jsonify({ "message": "Budget set successfully" }), 200)

@accounts_bp.route("/api/v1.0/users/<string:userId>/accounts/by-number/<string:accountNumber>", methods=['GET'])
def getAccountByNumber(userId, accountNumber):
    
    if not ObjectId.is_valid(userId):
        return make_response(jsonify({ "error": "Invalid User Id" }), 400)
    
    normalized_account_number = accountNumber.replace(" ", "")
    normalized_sort_code = request.args.get("sortCode")
    
    user_accounts = get_accounts().find({ "userId": ObjectId(userId) })
    
    for account in user_accounts:
        if account["accountNumber"].replace(" ", "") == normalized_account_number and account.get("sortCode") == normalized_sort_code:
            account["_id"] = str(account["_id"])
            account["userId"] = str(account["userId"])
            return make_response(jsonify(account), 200)
    
    return make_response(jsonify({ "error": "Account not found" }), 404)

@accounts_bp.route("/api/v1.0/users/<string:userId>/accounts/<string:accountId>/set-default", methods=['PUT'])
def setDefaultAccount(userId, accountId):
    if not ObjectId.is_valid(userId) or not ObjectId.is_valid(accountId):
        return make_response(jsonify({ "error": "Invalid User Id or Account Id" }), 400)
        
    get_accounts().update_many(
        {
            "userId": ObjectId(userId)
        },
        {
            "$set": {
                "isDefault": False,
                "updatedAt": datetime.now(UTC).isoformat() + "Z"
            }
        }
    )
    
    result = get_accounts().update_one(
        {
            "_id": ObjectId(accountId),
            "userId": ObjectId(userId)
        },
        {
            "$set": {
                "isDefault": True,
                "updatedAt": datetime.now(UTC).isoformat() + "Z"
            }
        }
    )
    
    if result.matched_count == 1:
        return make_response(jsonify({ "message": "Default Account Set" }), 200)
    else:
        return make_response(jsonify({ "error": "Account not found" }), 404)
    
@accounts_bp.route("/api/v1.0/users/<string:userId>/accounts/default", methods=['GET'])
def getDefaultAccount(userId):
    if not ObjectId.is_valid(userId):
        return make_response(jsonify({ "error": "Invalid User Id" }), 400)
    
    default_account = get_accounts().find_one({ "userId": ObjectId(userId), "isDefault": True, "status": { "$ne": "archived" } })
    
    if not default_account:
        return make_response(jsonify({ "error": "Default account not found" }), 404)
    
    default_account["_id"] = str(default_account["_id"])
    default_account["userId"] = str(default_account["userId"])
    
    return make_response(jsonify(default_account), 200)