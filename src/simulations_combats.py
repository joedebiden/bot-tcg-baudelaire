import random
from itertools import combinations
from classes.elo_manager import EloManager
import matplotlib.pyplot as plt

def simuler_matchs(elo_manager, joueurs, n_matchs=1500):
    """
    Simule des matchs entre tous les joueurs de manière aléatoire.
    """
    # Historique des Elos
    historique_elos = {joueur.nom: [joueur.elo] for joueur in joueurs}

    for _ in range(n_matchs):
        # Sélectionne deux joueurs au hasard
        joueur1, joueur2 = random.sample(joueurs, 2)

        # Génère un gagnant aléatoirement avec un taux de victoire/défaite
        gagnant = joueur1 if random.random() > 0.5 else joueur2
        perdant = joueur2 if gagnant == joueur1 else joueur1

        # Met à jour les scores Elo
        elo_manager.manage_elo(gagnant=gagnant, perdant=perdant)

        # Met à jour l'historique
        historique_elos[joueur1.nom].append(joueur1.elo)
        historique_elos[joueur2.nom].append(joueur2.elo)

    return historique_elos

if __name__ == "__main__":
    elo_manager = EloManager()

    # Ajout des joueurs
    noms_joueurs = ["Alice", "Bob", "Dave", "Eve","Mallory", "Oscar", "Peggy", "Trent", "Walter", "Victor", "Zoe", "Yves", "Xavier"]
    # for nom in noms_joueurs:
        # elo_manager.ajouter_joueur(nom)

    joueurs = [elo_manager.obtenir_joueur(nom) for nom in noms_joueurs]

    historique_elos = simuler_matchs(elo_manager, joueurs, n_matchs=1500)

    # Visualisation des résultats
    plt.figure(figsize=(12, 8))
    for nom, elos in historique_elos.items():
        plt.plot(range(len(elos)), elos, label=nom, marker="o")

    plt.title("Évolution des Elos après 500 matchs aléatoires", fontsize=16)
    plt.xlabel("Matchs", fontsize=14)
    plt.ylabel("Elo", fontsize=14)
    plt.legend(fontsize=12)
    plt.grid(True)
    plt.tight_layout()
    plt.show()
