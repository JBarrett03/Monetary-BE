from pymongo import MongoClient

secret_key = 'mysecret'

client = MongoClient("mongodb://127.0.0.1:27017")
db = client.monetary    # Select the database
users = db.users        # Select the collection
accounts = db.accounts
transactions = db.transactions
blacklist = db.blacklist