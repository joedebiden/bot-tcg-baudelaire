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
        """
        créé un match unique pour deux joueurs
        condiction : aucun des deux joueurs ne peut etre déjà dans un match
        """
        try:
            result = self.db.fetchall("select * from matches where (joueur1 = ? or joueur2 = ?) and etat in ('en attente', 'en cours')", (joueur1, joueur2))
            if result:
                print(f"Echec de la création du match entre [{joueur1} & {joueur2}]")
                return False
            else:
                self.db.execute("insert into matches (joueur1, joueur2) values (? , ?)", (joueur1, joueur2))
                print(f"Match entre [{joueur1} & {joueur2}] ajouté avec succes")
                return True

        except sqlite3.InternalError as e:
            print(f"Une erreur est survenue: {e}")


    def match_id(self, joueur1):
        """retourne l'id du match en fonction du joueur (implique un match max par joueur)"""
        try:
            match_id = self.db.fetchone("select id from matches where joueur1 = ?", (joueur1,))
            if match_id:
                print(match_id[0])
                return match_id[0]
            return None
        except sqlite3.InternalError as e:
            print(f"Une erreur est survenue: {e}")
            return None

    def accepter_match(self, match_id):
        try:
            result = self.db.execute("select etat, joueur1, joueur2 FROM matches WHERE id = ?", (match_id,))
            print(f"Match n°{match_id} accepté avec succes")
            return result
        except sqlite3.InternalError as e:
            print(f"Une erreur est survenue: {e}")
            return None

    def update_match(self, match_id):
        try:
            self.db.execute("UPDATE matches SET etat = 'en cours' WHERE id = ?", (match_id,))
            print(f"Match ")
        except sqlite3.InternalError as e:
            print(f"Une erreur est survenue: {e}")