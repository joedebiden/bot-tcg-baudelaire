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
        condiction : aucun des deux joueurs ne peut etre déjà dans un match ou ayant une demande
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
        """
        requete qui prend l'id du match en paramètre, recherche le joueur2 et le status du match
        donc évidemment si c'est en attente alors le match est accepté sinon les conditions font que le match ne peut pas être accepté
        """
        try:
            requete = self.db.fetchone("select * FROM matches WHERE id = ?", (match_id,))
            print(f"[DEBUG] : {requete}")
            if requete:
                print(f"le joueur ayant reçu la demande : {requete[2]}")
                if requete[3] == 'en attente':
                    print(f"changement d'état du match pour : {requete[0]}")
                    self.db.execute("update matches set etat = 'en cours' where id = ?", (match_id,))
                    return True
                elif requete[3] == 'en cours':
                    print("un match est déjà en cours")
                    return False
                elif requete[3] == 'terminé':
                    print("le match est déjà terminé")
                    return False
                else:
                    print("une erreur inconnu")
            else:
                print("le joueur n'est enregistré dans aucun combat")
                return False

        except sqlite3.InternalError as e:
            print(f"Une erreur est survenue: {e}")
            return False





    def create_match_test(self):
        try:
            self.db.execute("insert into matches (joueur1, joueur2, etat) values ('bode', 'bodelaire', 'en attente')")
            print("Match test added")
        except sqlite3.InternalError as e:
            print(f"Une erreur est survenue: {e}")

    def delete_match_test(self):
        try:
            self.db.execute("delete from matches where (joueur1 = 'bodelaire' or joueur2 = 'bodelaire')")
            print("matches tests deleted")
        except sqlite3.InternalError as e:
            print(f"Une erreur est survenue: {e}")