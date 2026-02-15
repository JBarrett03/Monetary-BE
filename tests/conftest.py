import pytest
from flask import Flask
from flask_cors import CORS
import mongomock
import globals

from blueprints.accounts.accounts import accounts_bp

@pytest.fixture
def app():
    app = Flask(__name__)
    CORS(app)
    
    globals.db = mongomock.MongoClient().db
    
    app.register_blueprint(accounts_bp)
    
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def db():
    return globals.db