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
                       f"Utilise `.accepter {match_id}` pour accepter le match\n"
                       f"Et `.refuser {match_id}` pour décliner la demande")

    else:
        await ctx.send("Une erreur est survenue lors de la création du match")


@bot.command(name="accepter")
async def accepter_match(ctx, match_id: int):
    result = match.accepter_match(match_id)

    if result == True: 
        await ctx.send("Match accepté")
    elif result == False:
        await ctx.send("Le match est soit en cours ou terminé")


@bot.command(name="leaderboard")
async def leaderboard(ctx):
    leaderboard = elo_manager.classement()
    if leaderboard:
        await ctx.send(leaderboard)
    else:
        await ctx.send("Aucun joueur n'est enregistré dans la compétition")


@bot.command(name="add")
async def add(ctx):
    match.create_match_test()
    await ctx.send("simulation de match créée")

@bot.command(name="del")
async def delete(ctx):
    match.delete_match_test()
    await ctx.send("simulations des matchs supprimées")

bot.run(BOT_TOKEN)