import psycopg2
import re

# Database connection settings
DATABASE_URL = "postgresql://postgres:vVMyqWjrqgVhEnwyFifTQxkDtPjQutGb@interchange.proxy.rlwy.net:30451/railway"

def connect_db():
    """Connect to the PostgreSQL database."""
    return psycopg2.connect(DATABASE_URL, sslmode="require")

def extract_group_id(group_link):
    """Extracts the group_id from the provided group link."""
    match = re.search(r"t\.me/([\w\d_]+)", group_link)
    if match:
        return match.group(1)  # Extract the group_id
    return None  # Return None if no valid group_id found

def add_subscription(user_id, group_link, signal_format):
    """Adds a new subscription for the user."""
    conn = connect_db()
    cur = conn.cursor()
    
    group_id = extract_group_id(group_link)  # Extract group_id from link
    if not group_id:
        return {"error": "Invalid group link format"}

    try:
        # Check if the user already has 3 subscriptions
        cur.execute("SELECT COUNT(*) FROM subscriptions WHERE user_id = %s;", (user_id,))
        count = cur.fetchone()[0]

        if count >= 3:
            return {"error": "You can only subscribe to a maximum of 3 groups. Please remove one before adding another."}

        # Insert the new subscription
        cur.execute("""
            INSERT INTO subscriptions (user_id, group_id, group_link, signal_format)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (user_id, group_id) DO NOTHING;
        """, (user_id, group_id, group_link, signal_format))

        conn.commit()
        return {"success": f"Subscribed to {group_link} with format {signal_format}"}

    finally:
        cur.close()
        conn.close()

def remove_subscription(user_id, group_id):
    """Removes a subscription for the user."""
    conn = connect_db()
    cur = conn.cursor()

    try:
        cur.execute("DELETE FROM subscriptions WHERE user_id = %s AND group_id = %s;", (user_id, group_id))
        conn.commit()
        return {"success": f"Unsubscribed from {group_id}"}

    finally:
        cur.close()
        conn.close()

def get_subscriptions(user_id):
    """Retrieves all subscriptions for a user."""
    conn = connect_db()
    cur = conn.cursor()

    try:
        cur.execute("SELECT group_id, group_link, signal_format FROM subscriptions WHERE user_id = %s;", (user_id,))
        subscriptions = cur.fetchall()
        return subscriptions

    finally:
        cur.close()
        conn.close()
