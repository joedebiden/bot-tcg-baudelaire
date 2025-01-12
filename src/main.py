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
@bot.command(name="ajouter")
async def ajouter_joueur(ctx, nom: str):
    try:
        elo_manager.ajouter_joueur(nom)
        await ctx.send(f"Bienvenue {nom} dans l'aventure, tu as 1200 points à toi de monter dans le classement!")
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
    joueur2 = adversaire

    if not elo_manager.obtenir_joueur(joueur1) or not elo_manager.obtenir_joueur(adversaire):
        await ctx.send("Un des joueurs mentionné n'est pas enregistré, faites `.ajouter` pour l'enregistrer dans la compet!")
        return

    match.ajouter_match(joueur1, joueur2)
    match_id = match.cursor.lastrowid

    ctx.send(f"Le match entre {joueur1} et {joueur2} est en cours d'attente. ID du match pour pouvoir accepter/annuler la demande à tout moment : {match_id}.\n"
             f"Utilise `.accepte {match_id}` pour accepter le match.")




bot.run(BOT_TOKEN)