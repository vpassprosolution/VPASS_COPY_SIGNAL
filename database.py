import psycopg2

# PostgreSQL Database URL
DB_URL = "postgresql://postgres:vVMyqWjrqgVhEnwyFifTQxkDtPjQutGb@interchange.proxy.rlwy.net:30451/railway"

# Function to connect to the database
def connect_db():
    return psycopg2.connect(DB_URL)

# Function to add a new user subscription
def add_subscription(user_id, group_id, signal_format):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO telegram_subscriptions (user_id, group_id, signal_format) VALUES (%s, %s, %s) "
        "ON CONFLICT (user_id) DO UPDATE SET group_id=%s, signal_format=%s",
        (user_id, group_id, signal_format, group_id, signal_format)
    )
    conn.commit()
    conn.close()

# Function to check if a user is subscribed
def is_user_subscribed(user_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT group_id, signal_format FROM telegram_subscriptions WHERE user_id = %s", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result  # Returns (group_id, signal_format) if found, else None

# Function to remove a user subscription
def remove_subscription(user_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM telegram_subscriptions WHERE user_id = %s", (user_id,))
    conn.commit()
    conn.close()
