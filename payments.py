from flask import Blueprint, jsonify, request
import stripe
import os

payments_bp = Blueprint('payments_bp', __name__)

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

@payments_bp.route("/api/v1.0/payments/create-intent", methods=['POST'])
def create_payment_intent():
    data = request.get_json()
    amount = data.get("amount")
    
    if not amount:
        return jsonify({ "error": "Amount is required" }), 400
    
    intent = stripe.PaymentIntent.create(
        amount = amount,
        currency = 'eur',
        automatic_payment_methods = { "enabled": True }
    )
    
    return jsonify({ "clientSecret": intent.client_secret })

@payments_bp.route("/webhooks/stripe", methods=['POST'])
def stripe_webhook():
    payload = request.data
    sig = request.headers.get("Stripe-Signature")
    
    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig,
            os.getenv("STRIPE_WEBHOOK_SECRET")
        )
    except Exception as e:
        return "", 400
    
    if event["type"] == "payment_intent.succeeded":
        intent = event["data"]["object"]
        
    return "", 200