# Test cases for retrieving a transaction by ID
    
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
    
