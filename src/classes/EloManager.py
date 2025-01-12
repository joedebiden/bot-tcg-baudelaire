import sqlite3
from classes.Joueur import Joueur


class EloManager:
    def __init__(self, db_path="db/elo_database.db"):
        self.conn=sqlite3.connect(db_path)
        self.cursor=self.conn.cursor()
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

    def ajouter_joueur(self, nom, elo=1200):
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

    def update_elo(self, joueur: Joueur):
        self.cursor.execute("update joueurs SET elo = ? where id = ?", (joueur.elo, joueur.id))
        self.conn.commit()

    def manage_elo(self, gagnant: Joueur, perdant: Joueur, k=32):
        # ici la logique de l'elo - a changer si besoin
        proba_gagnant = 1 / (1 + 10 ** ((perdant.elo - gagnant.elo) / 400))
        proba_perdant = 1 - proba_gagnant

        gagnant.elo += round(k * (1 - proba_gagnant))
        perdant.elo += round(k * (0 - proba_perdant))
        self.update_elo(gagnant)
        self.update_elo(perdant)