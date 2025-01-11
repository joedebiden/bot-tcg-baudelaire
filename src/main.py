from classes.EloManager import EloManager

if __name__ == "__main__":
    elo_manager = EloManager()

    # Ajouter des joueurs
    elo_manager.ajouter_joueur("Alice")
    elo_manager.ajouter_joueur("Bob")

    # Récupérer les joueurs
    alice = elo_manager.obtenir_joueur("Alice")
    bob = elo_manager.obtenir_joueur("Bob")

    # Déclarer un match
    if alice and bob:
        print(f"Avant le match : Alice({alice.elo}) vs Bob({bob.elo})")
        elo_manager.manage_elo(gagnant=alice, perdant=bob)
        print(f"Après le match : Alice({alice.elo}) vs Bob({bob.elo})")
