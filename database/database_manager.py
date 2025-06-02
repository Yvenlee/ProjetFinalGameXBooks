import sqlite3

def initialize_database():
    conn = sqlite3.connect('games.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_name TEXT NOT NULL,
            recommended INTEGER,
            hours_played REAL,
            date_posted TEXT,
            comment TEXT
        )
    ''')
    conn.commit()
    conn.close()

def clear_database():
    conn = sqlite3.connect('games.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM reviews')
    conn.commit()
    conn.close()

def insert_data(data):
    conn = sqlite3.connect('games.db')
    cursor = conn.cursor()
    for game_name, reviews in data.items():
        for review in reviews:
            cursor.execute('''
                INSERT INTO reviews (game_name, recommended, hours_played, date_posted, comment)
                VALUES (?, ?, ?, ?, ?)
            ''', (game_name, review['Recommended'], review['Hours Played'], review['Date Posted'], review['Comment']))
    conn.commit()
    conn.close()

def fetch_data():
    conn = sqlite3.connect('games.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM reviews')
    data = cursor.fetchall()
    conn.close()
    return data
