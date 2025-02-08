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


    # bug fixed 
    def match_id(self, joueur1):
        """retourne l'id du match le plus récente en fonction du joueur (implique un match max par joueur)"""
        try:
            match_id = self.db.fetchone("select id from matches where joueur1 = ? order by id desc limit 1", (joueur1,))
            if match_id:
                print(match_id[0])
                return match_id[0]
            return None
        except sqlite3.InternalError as e:
            print(f"Une erreur est survenue: {e}")
            return None


    def accepter_match(self, match_id, joueur2):
        """
        requete qui prend l'id du match en paramètre, recherche le joueur2 et le status du match
        donc évidemment si c'est en attente alors le match est accepté sinon les conditions font que le match ne peut pas être accepté
        le joueur qui accepte le match doit obligatoirement être le joueur2
        """
        try:
            requete = self.db.fetchone("select * FROM matches WHERE id = ?", (match_id,))
            print(f"[DEBUG] : {requete}")
            if requete:
                print(f"le joueur ayant reçu la demande : {requete[2]}")
                if requete[2] == joueur2:
     
                    if requete[3] == 'en attente':
                        print(f"changement d'état du match pour : {requete[0]}")
                        self.db.execute("update matches set etat = 'en cours' where id = ?", (match_id,))
                        return True, "Match accepté"
                    
                    elif requete[3] == 'en cours':
                        return False, "un match est déjà en cours"
                    
                    elif requete[3] == 'terminé':
                        return False, "le match est déjà terminé"
                    else:
                        print("une erreur inconnu")
                else:
                    return False, "le joueur n'appartient pas à la demande"
            else:
                return False, "le joueur n'est enregistré dans aucun combat"

        except sqlite3.InternalError as e:
            return False, str(e)


    def refuser_match(self, match_id, joueur2):
        """
        requete qui prend l'id du match en paramètre, recherche le joueur2 et le status du match
        le joueur qui refuse le match doit obligatoirement être le joueur2
        """
        try:
            requete = self.db.fetchone("select * FROM matches WHERE id = ?", (match_id,))
            print(f"[DEBUG] : {requete}")
            if requete:
                if requete[2] == joueur2 or requete[1] == joueur2:
                    if requete[3] == 'en attente':
                        print(f"changement d'état du match pour : {requete[0]}")
                        self.db.execute("update matches set etat = 'refusé' where id = ?", (match_id,))
                        return True, "Match refusé"
                    
                    elif requete[3] == 'en cours':
                        return False, "un match est déjà en cours"
                    
                    elif requete[3] == 'terminé':
                        return False, "le match est déjà terminé"
                    
                    else:
                        return False, "il y a une erreur inconnue"
                else:
                    return False, "le joueur n'appartient pas à la demande"
            else:
                return False, "le joueur n'est enregistré dans aucun combat"

        except sqlite3.InternalError as e:
            return False, str(e)


    """Retourne les informations d'un match à partir de son ID."""
    def obtenir_match(self, match_id):
        requete = "SELECT etat, joueur1, joueur2 FROM matches WHERE id = ?"
        result = self.db.fetchone(requete, (match_id,))
        if result:
            return result 
        return None
    
    """Met à jour l'état d'un match à 'terminé' et enregistre le gagnant."""
    def terminer_match(self, match_id, gagnant):
        try:    
            requete = """update matches set etat = 'terminé', gagnant = ? where id = ? and etat = 'en cours'"""
            self.db.execute(requete, (gagnant, match_id))
        except sqlite3.InternalError as e:
            print(f"Une erreur est survenue: {e}")