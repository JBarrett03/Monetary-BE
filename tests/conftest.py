import pytest
from flask import Flask
from flask_cors import CORS
import mongomock
import globals

from blueprints.accounts.accounts import accounts_bp
from blueprints.users.users import users_bp

@pytest.fixture
def db(monkeypatch):
    client = mongomock.MongoClient()
    test_db = client["test_db"]
    
    monkeypatch.setattr(globals, "db", test_db)
    
    yield test_db
    
@pytest.fixture
def app(db):
    app = Flask(__name__)
    CORS(app)
        
    app.register_blueprint(accounts_bp)
    app.register_blueprint(users_bp)
    
    return app

@pytest.fixture
def client(app):
    return app.test_client()
