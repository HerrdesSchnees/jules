import sqlite3
import os

class StateManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS processed_mails (
                    message_id TEXT PRIMARY KEY,
                    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    score REAL,
                    action TEXT
                )
            ''')

    def is_processed(self, message_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('SELECT 1 FROM processed_mails WHERE message_id = ?', (message_id,))
            return cursor.fetchone() is not None

    def mark_processed(self, message_id, score, action):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT OR REPLACE INTO processed_mails (message_id, score, action)
                VALUES (?, ?, ?)
            ''', (message_id, score, action))
