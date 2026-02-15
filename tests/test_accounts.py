import re
from blueprints.accounts.accounts import generate_card_number

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