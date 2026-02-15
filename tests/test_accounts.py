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