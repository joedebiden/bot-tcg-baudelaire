import sqlite3
from classes.db_manager import DatabaseManager
from classes.joueur import Joueur

class EloManager:
    def __init__(self):
        self.db = DatabaseManager()
        self._create_table()


    def _create_table(self):
        self.db.execute("""
        CREATE TABLE IF NOT EXISTS joueurs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT UNIQUE NOT NULL,
            elo INTEGER NOT NULL DEFAULT 1200
        )
        """)

    def ajouter_joueur(self, nom, elo=1200):
        try:
            self.db.execute("insert into joueurs (nom, elo) values (?, ?)", (nom, elo))
        except sqlite3.InternalError:
            print(f"le joueur {nom} existe déjà.")

    def obtenir_joueur(self, nom):
        if not nom:
            raise ValueError("Le nom ne peut pas etre vide")

        requete = "select * from joueurs where nom = ?"
        row = self.db.fetchone(requete, (nom,))
        if row:
            return Joueur(id=row[0], nom=row[1], elo=row[2])
        else:
            return None


    def update_elo(self, joueur: Joueur):
        self.db.execute("update joueurs SET elo = ? where id = ?", (joueur.elo, joueur.id))


    def manage_elo(self, gagnant: Joueur, perdant: Joueur, k=32):
        # ici la logique de l'elo - a changer si besoin
        proba_gagnant = 1 / (1 + 10 ** ((perdant.elo - gagnant.elo) / 400))
        proba_perdant = 1 - proba_gagnant

        elo_change_gagnant = k * (1 - proba_gagnant)
        elo_change_perdant = k * (0 - proba_perdant)

        gagnant.elo += round(elo_change_gagnant)
        perdant.elo += round(elo_change_perdant)

        self.update_elo(gagnant)
        self.update_elo(perdant)

        return elo_change_perdant, elo_change_gagnant


    def classement(self):
        return self.db.fetchall("select * from joueurs order by elo desc")