import discord
from discord.ext import commands
import sqlite3
from dotenv import load_dotenv
import os
from classes.EloManager import EloManager
from classes.Joueur import Joueur

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=".", intents=intents)

elo_manager = EloManager()

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Connecté en tant que bot {bot.user}")


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
    joueur = elo_manager.obtenir_joueur(nom)
    if joueur:
        await ctx.send(f"Joueur : {joueur.nom}\nELO : {joueur.elo}")
    else:
        await ctx.send("Aucun joueur trouvé")


"""déclaration de match"""
@bot.command(name="match")
async def declarer_match(ctx, gagnant_nom: str, perdant_nom: str):
    gagnant = elo_manager.obtenir_joueur(gagnant_nom)
    perdant = elo_manager.obtenir_joueur(perdant_nom)

    if not gagnant or not perdant:
        await ctx.send("L'un des joueurs spécifiés n'existe pas. Utilisez `?ajouter` pour les ajouter.")
        return



bot.run(BOT_TOKEN)