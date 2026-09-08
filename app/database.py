import sqlite3
DATABASE_PATH="test_library.db"
def get_connection():
    conn=sqlite3.connect(DATABASE_PATH,check_same_thread=False)
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    return conn
def init_db():
    conn=get_connection()
    cursor=conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS books(
    isbn TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    image_path TEXT NULL)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL,
    image_profile TEXT NULL,
    is_verified BOOL DEFAULT 0 )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS borrowing(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    isbn TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    borrowed_at TEXT NULL,
    returned_at  TEXT NULL,
    FOREIGN KEY (isbn) REFERENCES books(isbn) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS refresh_tokens(
    user_id INTEGER NOT NULL,
    hash_token TEXT NOT NULL,
    create_at TEXT NOT NULL,
    expire_at TEXT NOT NULL,
    revoked INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS email_verifications(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    token_hash TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    used BOOL DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS password_resets(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    token_hash TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    used BOOL DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE)''')
    
    conn.commit()
    conn.close()

