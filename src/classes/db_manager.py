import sqlite3
import os

class DatabaseManager:
    """seule et unique connexion à la db (singleton ^^)"""
    _instance = None

    def __new__(cls, db_path="db/elo_database.db"):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 
            full_path = os.path.join(base_dir, db_path)

            if not os.path.exists(full_path):
                print(f"Database not found, creating on {full_path}...")
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                cls._create_database(full_path)

            cls._instance.conn = sqlite3.connect(full_path, check_same_thread=False)
            cls._instance.cursor = cls._instance.conn.cursor()
        return cls._instance

    def execute(self, query, params=()):
        self.cursor.execute(query, params)
        self.conn.commit()

    def fetchall(self, query, params=()):
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def fetchone(self, query, params=()):
        self.cursor.execute(query, params)
        return self.cursor.fetchone()

    def close(self):
        self.conn.close()

    @staticmethod
    def _create_database(db_path):
        conn = sqlite3.connect(db_path)
        conn.commit()
        conn.close()
        print("Database created.")