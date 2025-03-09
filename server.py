from flask import Flask, request, jsonify
from database import add_subscription, remove_subscription, get_subscriptions

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "VPASS COPY SIGNAL API is running!"})

@app.route('/subscribe', methods=['POST'])
def subscribe():
    """API to handle user subscriptions."""
    data = request.json
    user_id = data.get("user_id")
    group_link = data.get("group_link")
    signal_format = data.get("signal_format")

    if not user_id or not group_link or not signal_format:
        return jsonify({"error": "Missing required parameters"}), 400

    result = add_subscription(user_id, group_link, signal_format)

    if "error" in result:
        return jsonify(result), 400

    return jsonify(result), 200

@app.route('/webhook', methods=['POST'])
def receive_webhook():
    """Receive and process webhook data."""
    data = request.json

    if not data:
        return jsonify({"error": "No data received"}), 400

    return jsonify({"message": "Webhook received!", "data": data}), 200



@app.route('/unsubscribe', methods=['POST'])
def unsubscribe():
    """API to handle user unsubscriptions."""
    data = request.json
    user_id = data.get("user_id")
    group_id = data.get("group_id")

    if not user_id or not group_id:
        return jsonify({"error": "Missing required parameters"}), 400

    result = remove_subscription(user_id, group_id)
    return jsonify(result), 200

@app.route('/get_subscriptions', methods=['POST'])
def get_user_subscriptions():
    """API to return all subscribed groups for a user."""
    data = request.json
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400

    subscriptions = get_subscriptions(user_id)

    if not subscriptions:
        return jsonify({"message": "No active subscriptions"}), 200

    return jsonify({"subscriptions": subscriptions}), 200

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))  # Use Railway's assigned PORT
    app.run(host='0.0.0.0', port=port)
