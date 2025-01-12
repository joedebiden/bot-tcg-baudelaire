import discord
from discord.ext import commands
import sqlite3
from classes.EloManager import EloManager
from classes.Joueur import Joueur


intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
elo_manager = EloManager()

"""Commande ajout joueur"""
@bot.command(name="ajouter")
async def ajouter_joueur(ctx, nom: str):
    try:
        elo_manager.ajouter_joueur(nom)
        await ctx.send(f"Bienvenue {nom} dans l'aventure, tu as 1200 points à toi de monter dans le classement!")
    except ValueError as e:
        await ctx.send(str(e))

