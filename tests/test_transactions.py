def test_get_transaction_not_found(client, db):
    user_id = db.users.insert_one({
        "email": "testuser@example.com",
    }).inserted_id
    
    account_id = db.accounts.insert_one({
        "userId": user_id
    }).inserted_id
    
    fake_transaction_id = "64b8f0c2e1d2f9a1b2c3d4e7"
    
    response = client.get(f"/api/v1.0/users/{user_id}/accounts/{account_id}/transactions/{fake_transaction_id}")
    
    assert response.status_code == 404
    assert response.get_json() == { "error": "Transaction not found" }
    
def test_get_transaction_invalid_id(client):
    response = client.get("/api/v1.0/users/invalid/accounts/invalid/transactions/invalid")
    
    assert response.status_code == 400
    
def test_get_transaction(client, db):
    user_id = db.users.insert_one({ "email": "testuser2@example.com" }).inserted_id
    account_id = db.accounts.insert_one({ "userId": user_id }).inserted_id
    transaction_id = db.transactions.insert_one({ "userId": user_id, "accountId": account_id, "amount": 100, "status": "completed" }).inserted_id
    
    response = client.get(f"/api/v1.0/users/{user_id}/accounts/{account_id}/transactions/{transaction_id}")
    data = response.get_json()
    
    assert response.status_code == 200
    assert data["amount"] == 100
    
def test_get_all_transactions(client, db):
    user_id = db.users.insert_one({ "email": "testuser2@example.com" }).inserted_id
    account_id = db.accounts.insert_one({ "userId": user_id }).inserted_id
    transaction_id = db.transactions.insert_one({ "userId": user_id, "accountId": account_id, "amount": 100, "status": "completed" })
    
    response = client.get(f"/api/v1.0/users/{user_id}/accounts/{account_id}/transactions")
    
    assert response.status_code == 200
    assert len(response.get_json()) == 1
    
def test_add_transaction(client, db):
    user_id = db.users.insert_one({ "email": "testuser2@example.com" }).inserted_id
    account_id = db.accounts.insert_one({
        "userId": user_id, 
        "balance": 200, 
        "accountType": 'savings' 
    }).inserted_id
    
    response = client.post(f"/api/v1.0/users/{user_id}/accounts/{account_id}/transactions", json={
        "amount": 150,
        "direction": "out",
        "merchant": "Test Merchant",
        "description": "Test Description"
    })
    
    assert response.status_code == 201
    
def test_transactions_summary(client, db):
    user_id = db.users.insert_one({ "email": "testuser2@example.com" }).inserted_id
    
    db.transactions.insert_one({
        "userId": user_id,
        "direction": "out",
        "status": "completed",
        "amount": 100
    })
    
    response = client.get(f"/api/v1.0/users/{user_id}/transactions/summary?direction=out")
    
    data = response.get_json()
    
    assert response.status_code == 200
    assert data["totalAmount"] == 100
    
def test_add_transaction_insufficient_funds(client, db):
    user_id = db.users.insert_one({ "email": "testuser2@example.com" }).inserted_id
    account_id = db.accounts.insert_one({
        "userId": user_id, 
        "balance": 50, 
        "accountType": 'savings' 
    }).inserted_id
    
    response = client.post(f"/api/v1.0/users/{user_id}/accounts/{account_id}/transactions", json={
        "amount": 100,
        "direction": "out"
    })
    
    assert response.status_code == 400