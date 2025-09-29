import sqlite3

DB_NAME = 'database.db'


def init_db():
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            chat_id INTEGER,
            is_blocked INTEGER DEFAULT 0
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS channels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel_id TEXT UNIQUE,
            channel_link TEXT
        )
    ''')

    con.commit()
    con.close()


def block_user(user_id: int):
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    cur.execute("UPDATE users SET is_blocked=1 WHERE user_id=?", (user_id,))
    con.commit()
    con.close()


def unblock_user(user_id: int):
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    cur.execute("UPDATE users SET is_blocked=0 WHERE user_id=?", (user_id,))
    con.commit()
    con.close()


def add_user(user_id: int, username: str, full_name: str, chat_id: int):
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()

    cur.execute('''
        INSERT OR IGNORE INTO users (user_id, username, full_name, chat_id)
        VALUES (?, ?, ?, ?)
    ''', (user_id, username, full_name, chat_id))

    con.commit()
    con.close()


def get_user(user_id):
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    cur.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = cur.fetchone()
    con.close()
    return user


def add_channel(channel_id: str, channel_link: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO channels (channel_id, channel_link)
        VALUES (?, ?)
        ON CONFLICT(channel_id) DO UPDATE SET channel_link=excluded.channel_link
    """, (channel_id, channel_link))
    conn.commit()
    conn.close()


def remove_channel(channel_id: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM channels WHERE channel_id=?", (channel_id,))
    conn.commit()
    conn.close()


def get_channels():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT channel_id, channel_link FROM channels")
    rows = cursor.fetchall()
    conn.close()
    return rows

def blocked_users_count() -> int:
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    cur.execute("SELECT COUNT(*) FROM users WHERE is_blocked=1")
    result = cur.fetchone()[0]
    con.close()
    return result



def total_users_count() -> int:
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    cur.execute("SELECT COUNT(*) FROM users")
    result = cur.fetchone()[0]
    con.close()
    return result


def get_all_chat_ids():
    """Bazada saqlangan barcha chat_id larni olish"""
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()

    cur.execute("SELECT chat_id FROM users WHERE is_blocked = 0")  # faqat bloklanmaganlar
    rows = cur.fetchall()

    con.close()

    # faqat chat_id larni ro‘yxat sifatida qaytaradi
    return [row[0] for row in rows]


if __name__ == "__main__":
    init_db()
    print("✅ Database yaratildi va jadvallar tayyor!")
