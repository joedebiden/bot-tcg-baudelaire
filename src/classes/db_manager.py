import sqlite3

class DatabaseManager:
    """seule et unique connexion à la db (singleton ^^)"""
    _instance = None

    def __new__(cls, db_path="db/elo_database.db"):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.conn = sqlite3.connect(db_path, check_same_thread=False)
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
