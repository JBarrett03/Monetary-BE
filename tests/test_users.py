# Test cases for getting user information
   
def test_get_user_invalid_id(client, db):
    user_id = db.users.insert_one({
        "email": "testuser@example.com",
        "admin": False,
    }).inserted_id
    
    response = client.get(f"/api/v1.0/users/{user_id}")
    
    assert response.status_code == 200
    
    data = response.get_json()
    
    assert data["email"] == "testuser@example.com"
    assert data["_id"] == str(user_id)
    
def test_get_user_not_found(client):
    fake_id = "64b8f0c2e1d2f9a1b2c3d4e5"
    
    response = client.get(f"/api/v1.0/users/{fake_id}")
    
    assert response.status_code == 404
    assert response.get_json() == { "error": "Invalid user ID" }
    
def test_get_user_without_password(client, db):
    user_id = db.users.insert_one({
        "email": "testuser@example.com",
        "admin": False,
    }).inserted_id
    
    response = client.get(f"/api/v1.0/users/{user_id}")
    
    assert response.status_code == 200
    assert "password" not in response.get_json()