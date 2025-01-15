import discord
from discord.ext import commands
import sqlite3
from dotenv import load_dotenv
import os

from classes.db_manager import DatabaseManager
from classes.elo_manager import EloManager
from classes.joueur import Joueur
from classes.match import Match

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=".", intents=intents)

elo_manager = EloManager()
match = Match()

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Connecté en tant que bot {bot.user}")

@bot.event
async def on_close():
    db_manager = DatabaseManager()
    db_manager.close()
    print("La base de donnée est fermée correctement")



"""gere l'ajout d'un joueur"""
@bot.command(name="start")
async def ajouter_joueur(ctx):
    joueur = ctx.author.name
    try:
        elo_manager.ajouter_joueur(joueur)
        await ctx.send(f"Bienvenue {joueur} dans l'aventure, tu as 1200 points à toi de monter dans le classement!")
    except ValueError as e:
        await ctx.send(str(e))


"""Affiche info du joueur"""
@bot.command(name="info")
async def info_joueur(ctx, nom: str):
    if not nom.strip():
        await ctx.send("Fournissez un nom de joueur valide et existant dans la compétition")
        return

    joueur = elo_manager.obtenir_joueur(nom)
    if joueur:
        await ctx.send(f"Joueur : {joueur.nom}\nELO : {joueur.elo}")
    else:
        await ctx.send("Fournissez un nom de joueur valide et existant dans la compétition")


"""déclaration de match"""
@bot.command(name="match")
async def declarer_match(ctx, adversaire: str):
    joueur1 = ctx.author.name

    game = match.ajouter_match(joueur1, adversaire) # permet d'insérer le match dans la base (unique match par joueur)
    if game == False:
        await ctx.send("Un des deux joueurs participe déjà dans un match")
        return
    elif game == True:
        match_id = match.match_id(joueur1)
        await ctx.send(f"Le match entre {joueur1} et {adversaire} est en cours d'attente.\n"
                       f"ID du match pour pouvoir accepter/annuler la demande à tout moment : `{match_id}`\n"
                       f"Utilise `.accepte {match_id}` pour accepter le match\n"
                       f"Et `.refuser {match_id}` pour décliner la demande")

    else:
        await ctx.send("Une erreur est survenue lors de la création du match")


"""Accepter un match"""
@bot.command(name="accepter")
async def accepter_match(ctx, match_id: int):
    match_data = match.accepter_match(match_id)
    if not match_data:
        await ctx.send("Match non trouvé")
        return

    etat, joueur1, joueur2 = match_data
    if etat != "en attente":
        await ctx.send("Ce match n'est pas en attente")
        return

    if ctx.author.name not in (joueur1, joueur2):
        await ctx.send("Seuls les joueurs concernés peuvent accepter ce match")
        return

    match.update_match(match_id)
    await ctx.send(f"Match entre {joueur1} et {joueur2} accepté, que le meilleur gagne!")






bot.run(BOT_TOKEN)