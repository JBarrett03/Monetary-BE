import re
from blueprints.accounts.accounts import generate_card_number
from tests.conftest import db

# Test cases for the generate_card_number function

def test_generate_card_number_length():
    card_number = generate_card_number()
    assert len(card_number) == 19
    
def test_generate_card_number_format():
    card_number = generate_card_number()
    pattern = r"^\d{4} \d{4} \d{4} \d{4}$"
    assert re.match(pattern, card_number)
    
def test_generate_card_number_uniqueness():
    card_numbers = set()
    for _ in range(1000):
        card_number = generate_card_number()
        assert card_number not in card_numbers
        card_numbers.add(card_number)
        
def test_generate_card_number_digits_only():
    card_number = generate_card_number()
    cleaned_number = card_number.replace(" ", "")
    assert cleaned_number.isdigit()
    assert len(cleaned_number) == 16

# Test cases for getting all accounts for a user in the accounts blueprint

def test_get_accounts_invalid_user_id(client):
    response = client.get("/api/v1.0/users/invalidUserId/accounts")
    assert response.status_code == 400
    assert response.get_json() == { "error": "Invalid User Id" }
    
def test_get_accounts_no_accounts(client, db):
    userId = db.users.insert_one({
        "email": "testuser@example.com"
    }).inserted_id
    
    response = client.get(f"/api/v1.0/users/{userId}/accounts")
    assert response.status_code == 200
    assert response.get_json() == []
    
def test_get_accounts_multiple_accounts(client, db):
    userId = db.users.insert_one({
        "email": "testuser@example.com"
    }).inserted_id
    
    account1 = db.accounts.insert_one({
        "userId": userId,
        "accountType": "savings",
        "currency": "USD",
        "balance": 100.0,
        "availableBalance": 100.0,
        "status": "active"
    }).inserted_id
    
    account2 = db.accounts.insert_one({
        "userId": userId,
        "accountType": "checking",
        "currency": "USD",
        "balance": 200.0,
        "availableBalance": 200.0,
        "status": "active"
    }).inserted_id
    
    response = client.get(f"/api/v1.0/users/{userId}/accounts")
    assert response.status_code == 200
    accounts = response.get_json()
    assert len(accounts) == 2
    assert any(account["_id"] == str(account1) for account in accounts)
    assert any(account["_id"] == str(account2) for account in accounts)
    
def test_get_accounts_archived_accounts_excluded(client, db):
    userId = db.users.insert_one({
        "email": "testuser@example.com"
    }).inserted_id
    
    active_account = db.accounts.insert_one({
        "userId": userId,
        "accountType": "savings",
        "currency": "USD",
        "balance": 100.0,
        "availableBalance": 100.0,
        "status": "active"
    }).inserted_id
    
    archived_account = db.accounts.insert_one({
        "userId": userId,
        "accountType": "checking",
        "currency": "USD",
        "balance": 200.0,
        "availableBalance": 200.0,
        "status": "archived"
    }).inserted_id
    
    response = client.get(f"/api/v1.0/users/{userId}/accounts")
    assert response.status_code == 200
    accounts = response.get_json()
    assert len(accounts) == 1
    assert accounts[0]["_id"] == str(active_account)  

def test_get_accounts_sorted_by_order(client, db):
    userId = db.users.insert_one({
        "email": "testuser@example.com"
    }).inserted_id

    account1 = db.accounts.insert_one({
        "userId": userId,
        "accountType": "savings",
        "status": "active",
        "order": 2
    }).inserted_id

    account2 = db.accounts.insert_one({
        "userId": userId,
        "accountType": "checking",
        "status": "active",
        "order": 1
    }).inserted_id

    response = client.get(f"/api/v1.0/users/{userId}/accounts")

    assert response.status_code == 200
    accounts = response.get_json()

    assert accounts[0]["_id"] == str(account2)
    assert accounts[1]["_id"] == str(account1)

# Test cases for getting a specific account for a user in the accounts blueprint

# Test cases for creating a new account for a user in the accounts blueprint

# Test cases for updating an account for a user in the accounts blueprint

# Test cases for archiving an account for a user in the accounts blueprint
    
# Test cases for setting a card as default in the accounts blueprint

def test_set_default_account(client, db):
    
    userId = db.users.insert_one({
        "email": "testuser@example.com"
    }).inserted_id
    
    firstAccount = db.accounts.insert_one({
        "userId": userId,
        "isDefault": False,
        "status": "active"
    }).inserted_id
    
    secondAccount = db.accounts.insert_one({
        "userId": userId,
        "isDefault": False,
        "status": "active"
    }).inserted_id
    
    response = client.put(f"/api/v1.0/users/{userId}/accounts/{firstAccount}/set-default")
    
    assert response.status_code == 200
    
    updatedFirstAccount = db.accounts.find_one({ "_id": firstAccount})
    assert updatedFirstAccount["isDefault"] is True
    
    updatedSecondAccount = db.accounts.find_one({ "_id": secondAccount})
    assert updatedSecondAccount["isDefault"] is False