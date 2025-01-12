import sqlite3
from classes.db_manager import DatabaseManager
from classes.elo_manager import EloManager

class Match:
    def __init__(self):
        self.db = DatabaseManager()
        self._create_table()

    def _create_table(self):
        self.db.execute("""
        CREATE TABLE IF NOT EXISTS matches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        joueur1 TEXT NOT NULL,
        joueur2 TEXT NOT NULL,
        etat TEXT NOT NULL DEFAULT 'en attente',
        gagnant TEXT
        )
        """)

    def ajouter_match(self, joueur1, joueur2):
        try:
            cursor = self.db.execute("insert into matches (joueur1, joueur2) values (? , ?)", (joueur1, joueur2))
            print(f"Match entre [{joueur1} & {joueur2}] ajouté avec succes")
            return cursor.lastrowid
        except sqlite3.InternalError as e:
            print(f"Une erreur est survenue: {e}")
            return None

    def accepter_match(self, match_id):
        try:
            self.db.execute("select etat, joueur1, joueur2 FROM matches WHERE id = ?", (match_id,))
            print(f"Match n°{match_id} accepté avec succes")
        except sqlite3.InternalError as e:
            print(f"Une erreur est survenue: {e}")

    def update_match(self, match_id):
        try:
            self.db.execute("UPDATE matches SET etat = 'en cours' WHERE id = ?", (match_id,))
            print(f"Match ")
        except sqlite3.InternalError as e:
            print(f"Une erreur est survenue: {e}")