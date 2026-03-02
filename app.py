from flask import Flask, jsonify, make_response
from blueprints.users.users import users_bp
from blueprints.accounts.accounts import accounts_bp
from blueprints.transactions.transactions import transactions_bp
from blueprints.auth.auth import auth_bp
from payments import payments_bp
from flask_cors import CORS
from decorators import limiter

app = Flask(__name__)
CORS(app)
app.register_blueprint(users_bp)
app.register_blueprint(accounts_bp)
app.register_blueprint(transactions_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(payments_bp)

limiter.init_app(app)

@app.errorhandler(429)
def ratelimit_handler(e):
    return make_response(jsonify({
        "error": "Too many login attempts. Please try again in one minute..."
    }), 429)

if __name__ == '__main__':
    app.run(debug=True)