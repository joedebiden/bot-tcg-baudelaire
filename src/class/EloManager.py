import sqlite3
from Joueur import Joueur


class EloManager:
    def __init__(self, db_path="../db/elo_database.db"):
        self.conn=sqlite3.connect(db_path)
        self.cursor=self.conn.cursor
        self._create_table()


    def _create_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS joueurs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT UNIQUE NOT NULL,
            elo INTEGER NOT NULL DEFAULT 1200
        )
        """)
        self.conn.commit()

    def ajouter_joueur(self, nom, elo=1000):
        try:
            self.cursor.execute("insert into joueurs (nom, elo) values (?, ?)", (nom, elo))
            self.conn.commit()

        except sqlite3.InternalError:
            print(f"le joueur {nom} existe déjà.")

    def obtenir_joueur(self, nom):
        self.cursor.execute("select * from joueurs where nom = ?", (nom,))
        row = self.cursor.fetchone()
        if row:
            return Joueur(*row)
        return None

    def mettre_a_jour_elo(self, joueur: Joueur):
        self.cursor.execute("update joueurs SET elo = ? where id = ?", (joueur.elo, joueur.id))
        self.conn.commit()