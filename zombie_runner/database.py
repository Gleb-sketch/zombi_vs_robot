import sqlite3

class Database:
    def __init__(self, db_name="zombie_runner.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                score INTEGER NOT NULL,
                date DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()

    def insert_score(self, score):
        self.cursor.execute("INSERT INTO scores (score) VALUES (?)", (score,))
        self.conn.commit()

    def get_best_score(self):
        self.cursor.execute("SELECT MAX(score) FROM scores")
        result = self.cursor.fetchone()[0]
        return result if result else 0

    def close(self):
        self.conn.close()
