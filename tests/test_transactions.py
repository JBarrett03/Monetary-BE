# Test cases for retrieving a transaction by ID

def test_get_transaction_success(client, db):
    user_id = db.users.insert_one({
        "email": "testuser@example.com"
    }).inserted_id
    
    account_id = db.accounts.insert_one({
        "userId": user_id
    }).inserted_id
    
    transaction_id = db.transactions.insert_one({
        "accountId": account_id,
        "amount": 100.00,
        "type": "credit",
    }).inserted_id
    
    response = client.get(f"/api/v1.0/users/{user_id}/accounts/{account_id}/transactions/{transaction_id}")
    
    assert response.status_code == 200
    
    data = response.get_json()
    assert data["_id"] == str(transaction_id)
    assert data["accountId"] == str(account_id)
    assert data["amount"] == 100.00
    assert data["type"] == "credit"
    
def test_get_transaction_invalid_id(client):
    response = client.get("/api/v1.0/users/invalidUserId/accounts/invalidAccountId/transactions/invalidTransactionId")
    assert response.status_code == 400
    assert response.get_json() == { "error": "Invalid User Id, Account Id or Transaction Id" }

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
    
def test_get_all_transactions(client, db):
    user_id = db.users.insert_one({
        "email": "testuser@example.com"
    }).inserted_id

    account_id = db.accounts.insert_one({
        "userId": user_id
    }).inserted_id
    
    db.transactions.insert_many([
        { "accountId": account_id, "amount": 50.00 },
        { "accountId": account_id, "amount": 150.00 }
    ])
    
    response = client.get(f"/api/v1.0/users/{user_id}/accounts/{account_id}/transactions")
    
    assert response.status_code == 200
    assert len(response.get_json()) == 2
    