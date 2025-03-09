import psycopg2

# Database connection settings
DATABASE_URL = "postgresql://postgres:vVMyqWjrqgVhEnwyFifTQxkDtPjQutGb@interchange.proxy.rlwy.net:30451/railway"

def connect_db():
    """Connect to the PostgreSQL database."""
    return psycopg2.connect(DATABASE_URL, sslmode="require")

def add_subscriber(chat_id, instrument, group_link=None):
    """Subscribe a user to an instrument with an optional group link."""
    conn = connect_db()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO subscribers (chat_id, instrument, group_link)
            VALUES (%s, %s, %s)
            ON CONFLICT (chat_id, instrument) DO UPDATE 
            SET group_link = EXCLUDED.group_link;
        """, (chat_id, instrument, group_link))
        conn.commit()
    finally:
        cur.close()
        conn.close()

def remove_subscriber(chat_id, instrument):
    """Unsubscribe a user from an instrument."""
    conn = connect_db()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM subscribers WHERE chat_id = %s AND instrument = %s;", (chat_id, instrument))
        conn.commit()
    finally:
        cur.close()
        conn.close()

def get_subscribers(instrument):
    """Retrieve all subscribers for a specific instrument."""
    conn = connect_db()
    cur = conn.cursor()
    try:
        cur.execute("SELECT chat_id, group_link FROM subscribers WHERE instrument = %s;", (instrument,))
        subscribers = cur.fetchall()
        return subscribers
    finally:
        cur.close()
        conn.close()

def is_subscribed(chat_id, instrument):
    """Check if a user is subscribed to an instrument."""
    conn = connect_db()
    cur = conn.cursor()
    try:
        cur.execute("SELECT 1 FROM subscribers WHERE chat_id = %s AND instrument = %s;", (chat_id, instrument))
        return cur.fetchone() is not None
    finally:
        cur.close()
        conn.close()
