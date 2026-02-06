from flask import Flask
from blueprints.users.users import users_bp
from blueprints.accounts.accounts import accounts_bp
from blueprints.transactions.transactions import transactions_bp
from blueprints.auth.auth import auth_bp

app = Flask(__name__)
app.register_blueprint(users_bp)
app.register_blueprint(accounts_bp)
app.register_blueprint(transactions_bp)
app.register_blueprint(auth_bp)

if __name__ == '__main__':
    app.run(debug=True)