from classes.EloManager import EloManager
import matplotlib.pyplot as plt

if __name__ == "__main__":
    elo_manager = EloManager()

    # elo_manager.ajouter_joueur("Alice")
    # elo_manager.ajouter_joueur("Bob")

    alice = elo_manager.obtenir_joueur("Alice")
    bob = elo_manager.obtenir_joueur("Bob")

    # simulation d'un match
    if alice and bob:
        alice_elos = [alice.elo]
        bob_elos = [bob.elo]

        for match in range(100):
            gagnant = alice if match % 2 == 0 else bob  # Alterne les gagnants pour varier
            perdant = bob if gagnant == alice else alice


            elo_manager.manage_elo(gagnant=gagnant, perdant=perdant)

            alice_elos.append(alice.elo)
            bob_elos.append(bob.elo)

        plt.figure(figsize=(10, 6))
        plt.plot(range(101), alice_elos, label="Alice", color="blue", marker="o", linestyle="-")
        plt.plot(range(101), bob_elos, label="Bob", color="red", marker="o", linestyle="-")
        plt.title("Évolution des Elos après 100 matchs", fontsize=14)
        plt.xlabel("Matchs", fontsize=12)
        plt.ylabel("Elo", fontsize=12)
        plt.legend()
        plt.grid()
        plt.tight_layout()
        plt.show()
