from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "VPASS COPY SIGNAL API is running!"})

@app.route('/subscribe', methods=['POST'])
def subscribe():
    data = request.json
    user_id = data.get("user_id")
    group_id = data.get("group_id")
    signal_format = data.get("signal_format")

    if not user_id or not group_id or not signal_format:
        return jsonify({"error": "Missing required parameters"}), 400

    from database import add_subscription
    add_subscription(user_id, group_id, signal_format)

    return jsonify({"message": f"User {user_id} subscribed to {group_id} for {signal_format} signals."})

@app.route('/unsubscribe', methods=['POST'])
def unsubscribe():
    data = request.json
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400

    from database import remove_subscription
    remove_subscription(user_id)

    return jsonify({"message": f"User {user_id} unsubscribed successfully."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
