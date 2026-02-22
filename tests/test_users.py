# Test cases for getting user information
   
from bson import ObjectId


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

# Test cases for creating a new user

def test_create_user_success(client, db):
    user_data = {
        "firstName": "John",
        "lastName": "Doe",
        "email": "johndoe@example.com",
        "password": "password123",
        "phone": "1234567890",
        "address": "123 Main St",
        "DOB": "1990-01-01"
    }
    
    response = client.post("/api/v1.0/users", json=user_data)
    
    assert response.status_code == 201
    
    data = response.get_json()
    assert "id" in data
    
    created_user = db.users.find_one({ "_id": ObjectId(data["id"]) })
    
    assert created_user["email"] == "johndoe@example.com"
    assert created_user["admin"] == False
    assert created_user["emailVerified"] is False
    assert created_user["phoneVerified"] is False
    assert "createdAt" in created_user
    assert "lastLogin" in created_user
    assert created_user["password"] != "password123"
    
def test_create_user_missing_fields(client):
    user_data = {
        "firstName": "John",
        "lastName": "Doe",
        "email": "johndoe@example.com",
        "password": "password123"
    }
    
    response = client.post("/api/v1.0/users", json=user_data)
    
    assert response.status_code == 400
    assert response.get_json() == { "error": "Missing required fields..." }
    
def test_create_user_duplicate_email(client, db):
    existing_user = {
        "firstName": "Jane",
        "lastName": "Smith",
        "email": "janesmith@example.com",
        "password": b"hashedpassword",
        "phone": "0987654321",
        "address": "456 Elm St",
        "DOB": "1992-02-02",
        "admin": False,
        "emailVerified": False,
        "phoneVerified": False,
        "createdAt": "2024-01-01T00:00:00Z",
        "lastLogin": "2024-01-01T00:00:00Z"
    }
    
    db.users.insert_one(existing_user)
    
    new_user = {
        "firstName": "Jane",
        "lastName": "Smith",
        "email": "janesmith@example.com",
        "password": "password123",
        "phone": "0987654321",
        "address": "456 Elm St",
        "DOB": "1992-02-02"
    }
    
    response = client.post("/api/v1.0/users", json=new_user)
    
    assert response.status_code == 409
    assert response.get_json() == { "error": "Email already exists..." }
    
# Test cases for updating user information

def test_update_user_success(client, db):
    user_id = db.users.insert_one({
        "firstName": "John",
        "lastName": "Doe",
        "email": "johndoe@example.com",
        "password": b"hashedpassword",
        "phone": "1234567890",
        "address": "123 Main St",
        "DOB": "1990-01-01",
        "admin": False,
        "emailVerified": False,
        "phoneVerified": False,
        "createdAt": "2024-01-01T00:00:00Z",
        "lastLogin": "2024-01-01T00:00:00Z"
    }).inserted_id
    
    update_data = {
        "firstName": "Johnny",
        "email": "johnnydoe@example.com"
    }
    
    response = client.put(f"/api/v1.0/users/{user_id}", json=update_data)
    
    assert response.status_code == 200
    
    updated_user = db.users.find_one({ "_id": ObjectId(user_id) })
    
    assert updated_user["firstName"] == "Johnny"
    assert updated_user["email"] == "johnnydoe@example.com"
    
def test_update_user_invalid_id(client):
    response = client.put("/api/v1.0/users/invalidId", json={
        "firstName": "Johnny"
    })
    
    assert response.status_code == 400
    assert response.get_json() == { "error": "Invalid user ID" }
    
def test_update_user_not_found(client):
    fake_id = str(ObjectId())
    
    response = client.put(f"/api/v1.0/users/{fake_id}", json={
        "firstName": "Johnny"
    })
    
    assert response.status_code == 404
    assert response.get_json() == { "error": "User not found" }
    
def test_update_user_no_valid_fields(client, db):
    user_id = db.users.insert_one({
        "firstName": "Jane",
        "email": "janedoe@example.com",
    }).inserted_id
    
    response = client.put(f"/api/v1.0/users/{user_id}", json={
        "admin": True
    })
    
    assert response.status_code == 400
    assert response.get_json() == { "error": "No valid fields to update" }
    
def test_update_user_single_field(client, db):
    user_id = db.users.insert_one({
        "firstName": "John",
        "lastName": "Doe",
        "email": "johndoe@example.com",
        "password": b"hashedpassword",
    }).inserted_id
    
    response = client.put(f"/api/v1.0/users/{user_id}", json={
        "firstName": "Johnny"
    })
    
    assert response.status_code == 200
    
    updated_user = db.users.find_one({ "_id": ObjectId(user_id) })
    assert updated_user["firstName"] == "Johnny"
    
def test_update_user_multiple_fields(client, db):
    user_id = db.users.insert_one({
        "firstName": "Jane",
        "lastName": "Smith",
        "email": "janesmith@example.com"
    }).inserted_id
    
    response = client.put(f"/api/v1.0/users/{user_id}", json={
        "firstName": "Janet",
        "lastName": "Doe",
        "email": "janetdoe@example.com"
    })
    
    assert response.status_code == 200
    
    updated_user = db.users.find_one({ "_id": ObjectId(user_id) })
    assert updated_user["firstName"] == "Janet"
    assert updated_user["lastName"] == "Doe"
    assert updated_user["email"] == "janetdoe@example.com"