#database.py
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import os

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'users.db')

def get_connection():
    return sqlite3.connect(DATABASE_PATH)

def create_tables():
    conn = get_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    nickname TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL,
                    email TEXT NOT NULL,
                    about TEXT,
                    profile_pic TEXT
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS scores (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 user_id INTEGER,
                 game_name TEXT,
                 highest_score INTEGER,
                 FOREIGN KEY(user_id) REFERENCES users(id))''')
    conn.commit()
    conn.close()

def add_user(nickname, username, password, email):
    try:
        conn = get_connection()
        c = conn.cursor()
        hashed_password = generate_password_hash(password)
        c.execute("INSERT INTO users (nickname, username, password, email) VALUES (?, ?, ?, ?)", (nickname, username, hashed_password, email))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def get_user(username):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    user = c.fetchone()
    conn.close()
    if user:
        return {
            'id': user[0],
            'username': user[1],
            'nickname': user[2],
            'password': user[3],
            'email': user[4],
            'about': user[5],
            'profile_pic': user[6]
        }
    return None

def get_user_id(username):
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT id FROM users WHERE username = ?', (username,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

def update_highest_score(username, game_name, score):
    user_id = get_user_id(username)
    if user_id is None:
        return

    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT highest_score FROM scores WHERE user_id = ? AND game_name = ?', (user_id, game_name))
    result = c.fetchone()

    if result:
        if score > result[0]:
            c.execute('UPDATE scores SET highest_score = ? WHERE user_id = ? AND game_name = ?', (score, user_id, game_name))
    else:
        c.execute('INSERT INTO scores (user_id, game_name, highest_score) VALUES (?, ?, ?)', (user_id, game_name, score))

    conn.commit()
    conn.close()

def game_highest_score(username, game_name):
    user_id = get_user_id(username)
    if user_id is None:
        return 0

    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT highest_score FROM scores WHERE user_id = ? AND game_name = ?', (user_id, game_name))
    result = c.fetchone()
    conn.close()
    
    if result:
        return result[0]
    else:
        return 0

def get_highest_scores(username):
    user_id = get_user_id(username)
    if user_id is None:
        return {}
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT game_name, highest_score FROM scores WHERE user_id = ?', (user_id,))
    results = c.fetchall()
    conn.close()
    return {game_name: score for game_name, score in results}

def update_profile(username, about):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET about=? WHERE username=?", (about, username))
    conn.commit()
    conn.close()

def update_nickname(username, nickname):
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("UPDATE users SET nickname=? WHERE username=?", (nickname, username))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def update_profile_pic(username, profile_pic_path):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET profile_pic=? WHERE username=?", (profile_pic_path, username))
    conn.commit()
    conn.close()

def update_password(username, new_password):
    conn = get_connection()
    c = conn.cursor()
    hashed_password = generate_password_hash(new_password)
    c.execute("UPDATE users SET password=? WHERE username=?", (hashed_password, username))
    conn.commit()
    conn.close()

def verify_password(password, hashed_password):
    return check_password_hash(hashed_password, password)

create_tables()


