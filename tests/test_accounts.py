from mongomock import ObjectId

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
    
    db.accounts.insert_one({
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

def test_get_account_not_found(client, db):
    userId = db.users.insert_one({
        "email": "testuser@example.com"
    }).inserted_id
    valid_account_id = str(ObjectId())
    response = client.get(f"/api/v1.0/users/{userId}/accounts/{valid_account_id}")
    assert response.status_code == 404

def test_get_account_wrong_user(client, db):
    userId1 = db.users.insert_one({
        "email": "testuser1@example.com"
    }).inserted_id
    
    userId2 = db.users.insert_one({
        "email": "testuser2@example.com"
    }).inserted_id
    
    accountId = db.accounts.insert_one({
        "userId": userId1,
        "accountType": "savings",
        "currency": "USD",
        "balance": 100.0,
        "availableBalance": 100.0,
        "status": "active"
    }).inserted_id
    
    response = client.get(f"/api/v1.0/users/{userId2}/accounts/{accountId}")
    assert response.status_code == 404
       
def test_create_account_invalid_user_id(client):
    response = client.post("/api/v1.0/users/invalidUserId/accounts", json={
        "accountType": "savings",
        "currency": "USD"
    })
    assert response.status_code == 400
    
def test_create_account_missing_fields(client, db):
    userId = db.users.insert_one({
        "email": "testuser@example.com"
    }).inserted_id
    
    response = client.post(f"/api/v1.0/users/{userId}/accounts", json={
        "accountType": "savings"
    })
    assert response.status_code == 400
    
def test_create_account_success(client, db):
    userId = db.users.insert_one({
        "email": "testuser@example.com"
    }).inserted_id
    
    response = client.post(f"/api/v1.0/users/{userId}/accounts", json={
        "accountType": "savings",
        "currency": "USD"
    })
    assert response.status_code == 201
    response_data = response.get_json()
    assert response_data["accountType"] == "savings"
    assert response_data["currency"] == "USD"
    assert response_data["balance"] == 0.0
    assert response_data["status"] == "active"

def test_create_account_user_not_found(client):
    non_existent_user_id = str(ObjectId())
    response = client.post(f"/api/v1.0/users/{non_existent_user_id}/accounts", json={
        "accountType": "savings",
        "currency": "USD"
    })
    assert response.status_code == 404
    
def test_archive_account_not_found(client, db):
    userId = db.users.insert_one({
        "email": "testuser@example.com"
    }).inserted_id
    
    non_existent_account_id = str(ObjectId())
    response = client.put(f"/api/v1.0/users/{userId}/accounts/{non_existent_account_id}")
    assert response.status_code == 404

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