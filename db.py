import sqlite3

# Open a connection to the db with foreign keys enforced
def get_connection_db(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

# Test the connection
def check_connection_db(conn):
    try:
        conn.execute("SELECT 1")
        return True
    except sqlite3.Error as e:
        print(f"db connection check failed: {e}")
        return False



# Init the db tables, create tables if they dont exist
def init_db(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS apps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            process_name TEXT NOT NULL UNIQUE,
            display_name TEXT,
            daily_limit_minutes INTEGER,
            created_at TEXT DEFAULT (datetime('now'))
        );
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS daily_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            app_id INTEGER NOT NULL REFERENCES apps(id),
            date TEXT NOT NULL,
            seconds_used REAL NOT NULL DEFAULT 0,
            UNIQUE(app_id, date)
        );
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS focused_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            app_id INTEGER NOT NULL REFERENCES apps(id),
            date TEXT NOT NULL,
            seconds_used REAL NOT NULL DEFAULT 0,
            UNIQUE(app_id, date)
        );
    """)
    conn.commit()



# Search for an app in the apps db
def get_app_db(conn, process_name):
    cur = conn.execute(
        "SELECT * FROM apps WHERE process_name = ?", (process_name,)
    )
    row = cur.fetchone()
    return dict(row) if row else None

def get_all_apps_db(conn):
    cur = conn.execute(
        "SELECT * FROM apps"
    )
    return [dict(row) for row in cur.fetchall()]   



# Add an app into the app table, no dupes
def add_app_db(conn, process_name, display_name=None, daily_limit_minutes=None):
    conn.execute("""
        INSERT INTO apps (process_name, display_name, daily_limit_minutes)
        VALUES (?, ?, ?)
        ON CONFLICT(process_name) DO NOTHING
    """, (process_name, display_name, daily_limit_minutes))
    conn.commit()



# Get the seconds used by an app on a given date, 0 if none.
def get_today_focused_usage_db(conn, process_name, date):
    cur = conn.execute("""
        SELECT u.seconds_used
        FROM focused_usage u
        JOIN apps a ON a.id = u.app_id
        WHERE a.process_name = ? AND u.date = ?
    """, (process_name, date))
    row = cur.fetchone()
    return row["seconds_used"] if row else 0

def get_today_usage_db(conn, process_name, date):
    cur = conn.execute("""
        SELECT u.seconds_used
        FROM daily_usage u
        JOIN apps a ON a.id = u.app_id
        WHERE a.process_name = ? AND u.date = ?
    """, (process_name, date))
    row = cur.fetchone()
    return row["seconds_used"] if row else 0

# Get the earliest date with any recorded usage, None if there's no data yet.
def get_earliest_usage_date_db(conn):
    cur = conn.execute("""
        SELECT MIN(date) as min_date FROM (
            SELECT date FROM daily_usage
            UNION
            SELECT date FROM focused_usage
        )
    """)
    row = cur.fetchone()
    return row["min_date"] if row and row["min_date"] else None



# Add the usage by seconds. Returns False (and warns) if process_name isn't registered in apps.
def add_focused_usage_db(conn, process_name, date, seconds):
    cur = conn.execute("""
        INSERT INTO focused_usage (app_id, date, seconds_used)
        SELECT id, ?, ? FROM apps WHERE process_name = ?
        ON CONFLICT(app_id, date) DO UPDATE SET
            seconds_used = seconds_used + excluded.seconds_used
    """, (date, seconds, process_name))
    conn.commit()

    if cur.rowcount == 0:
        print(f"warning: '{process_name}' is not registered in apps, focused usage not recorded")
        return False
    return True

def add_daily_usage_db(conn, process_name, date, seconds):
    cur = conn.execute("""
        INSERT INTO daily_usage (app_id, date, seconds_used)
        SELECT id, ?, ? FROM apps WHERE process_name = ?
        ON CONFLICT(app_id, date) DO UPDATE SET
            seconds_used = seconds_used + excluded.seconds_used
    """, (date, seconds, process_name))
    conn.commit()

    if cur.rowcount == 0:
        print(f"warning: '{process_name}' is not registered in apps, usage not recorded")
        return False
    return True



# Update the display name in the db
def update_display_name_db(conn, process_name, display_name):
    cur = conn.execute("""
        UPDATE apps SET display_name = ? WHERE process_name = ?
    """, (display_name, process_name))
    conn.commit()

    if cur.rowcount == 0:
        print(f"warning: '{process_name}' not found, display name not updated")
        return False
    return True

# Update the daily limit (in minutes) in the db. Pass None to clear the limit.
def update_daily_limit_db(conn, process_name, daily_limit_minutes):
    cur = conn.execute("""
        UPDATE apps SET daily_limit_minutes = ? WHERE process_name = ?
    """, (daily_limit_minutes, process_name))
    conn.commit()

    if cur.rowcount == 0:
        print(f"warning: '{process_name}' not found, daily limit not updated")
        return False
    return True