import bcrypt

def test_login_missing_fields(client):
    response = client.post("/api/v1.0/login", json={})
    
    assert response.status_code == 400
    assert response.get_json() == {
        "error": "Email and Password are required..." 
    }
    
def test_login_invalid_credentials(client, db):
    hashed_password = bcrypt.hashpw("correctpassword".encode('utf-8'), bcrypt.gensalt())
    
    db.users.insert_one({
        "email": "testuser@example.com",
        "password": hashed_password
    })
    
    response = client.post("/api/v1.0/login", json={
        "email": "testuser@example.com",
        "password": "wrongpassword"
    })
    
    assert response.status_code == 401
    assert response.get_json() == { "error": "Invalid email or password..." }
    
def test_login(client, db):
    hashed_password = bcrypt.hashpw("correctpassword".encode('utf-8'), bcrypt.gensalt())
    
    user_id = db.users.insert_one({
        "email": "testuser@example.com",
        "password": hashed_password
    }).inserted_id
    
    response = client.post("/api/v1.0/login", json={
        "email": "testuser@example.com",
        "password": "correctpassword"
    })
    
    data = response.get_json()
    
    assert response.status_code == 200
    assert data["userId"] == str(user_id)
    assert "token" in data
    
def test_logout(client, db):
    token = "fake.jwt.token"
    
    response = client.get("/api/v1.0/logout", headers={ "x-access-token": token })
    
    assert response.status_code == 200
    assert response.get_json() == { "message": "Logout successful" }
    assert db.blacklist.find_one({ "token": token }) is not None