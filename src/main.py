import discord
from discord.ext import commands
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


"""création du joueur dans l'aventure (ne permet de s'ajouter que soi meme)"""
@bot.command(name="start")
async def ajouter_joueur(ctx):
    joueur = ctx.author.name
    try:
        elo_manager.ajouter_joueur(joueur)
        embed = discord.Embed(
            title=":sparkles: Bienvenue dans l'aventure ! :sparkles:",
            description=f"**{joueur}**, tu as été ajouté à la compétition avec un score de départ de **1200 points Elo**.\n"
                        "Prépare-toi à monter dans le classement et montre que tu es le meilleur !",
            color=discord.Color.blue())
        embed.set_thumbnail(url="")  # URL pour une icone de welcome (pas oublier !!!)
        embed.set_footer(text="Bonne chance dans cette aventure compétitive !")
        await ctx.send(embed=embed)

# Gestion des erreurs (exemple : joueur déjà existant)
    except ValueError as e:
        embed_error = discord.Embed(
            title=":x: Erreur lors de l'inscription",
            description=str(e),
            color=discord.Color.red())
        await ctx.send(embed=embed_error)


"""Affiche info du joueur"""
@bot.command(name="info")
async def info_joueur(ctx, nom: str = None):
    if not nom:
        embed_error = discord.Embed(
            title=":x: Erreur : Nom manquant",
            description="Veuillez fournir un nom de joueur valide.\n"
                        "Utilisation : `.info <nom_du_joueur>`",
            color=discord.Color.red())
        await ctx.send(embed=embed_error)
        return

    try:
        joueur = elo_manager.obtenir_joueur(nom)
        if joueur:
            embed = discord.Embed(
                title=f":trophy: Informations sur le joueur {joueur.nom}",
                color=discord.Color.gold())
            embed.add_field(name="Nom du joueur", value=joueur.nom, inline=True)
            embed.add_field(name="Score Elo", value=f"**{joueur.elo}** points", inline=True)
            embed.set_footer(text="Lâche pas le grind !")
            await ctx.send(embed=embed)
        else:
            embed_error = discord.Embed(
                title=":x: Joueur introuvable",
                description=f"Le joueur **{nom}** n'est pas enregistré dans la compétition",
                color=discord.Color.red())
            await ctx.send(embed=embed_error)

    except ValueError as e:
        embed_error = discord.Embed(
            title=":x: Erreur interne",
            description=str(e),
            color=discord.Color.red())
        await ctx.send(embed=embed_error)


"""déclaration de match"""
@bot.command(name="match")
async def declarer_match(ctx, adversaire: str = None):
    joueur1 = ctx.author.name

    if not adversaire:
        embed_error = discord.Embed(
            title=":x: Erreur : Adversaire manquant",
            description="Veuillez fournir un nom d'adversaire valide.\n"
                        "Utilisation : `.match <nom_adversaire>`",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed_error)
        return

    if adversaire == joueur1:
        embed_error = discord.Embed(
            title=":x: Erreur : Adversaire invalide",
            description="Vous ne pouvez pas jouer contre vous-même !",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed_error)
        return

    game = match.ajouter_match(joueur1, adversaire)
    if game == False:
        embed_error = discord.Embed(
            title=":x: Match non disponible",
            description="Un des deux joueurs participe déjà à un match.\n"
                        "Terminez votre match en cours avant d'en commencer un nouveau.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed_error)
        return

    elif game == True:
        match_id = match.match_id(joueur1)

        embed = discord.Embed(
            title=":crossed_swords: Match créé avec succès !",
            description=f"Le match entre **{joueur1}** et **{adversaire}** est en attente.",
            color=discord.Color.blue())
        embed.add_field(name="ID du match", value=f"`{match_id}`", inline=False)
        embed.add_field(name="Instructions", value=(
            f"- **Accepter le match** : `.accepter {match_id}`\n"
            f"- **Refuser le match** : `.refuser {match_id}`"), inline=False)
        embed.set_footer(text="Préparez-vous à vous affronter, que le meilleur gagne !")
        await ctx.send(embed=embed)
        return

    else:
        embed_error = discord.Embed(
            title=":x: Erreur",
            description="Une erreur inconnue est survenue lors de la création du match.",
            color=discord.Color.red())
        await ctx.send(embed=embed_error)
        return


@bot.command(name="accepter")
async def accepter_match(ctx, match_id: int = None):
    joueur2 = ctx.author.name
    if match_id is None:
        embed_error = discord.Embed(
            title=":x: Erreur : ID du match manquant",
            description="Veuillez fournir l'ID d'un match valide.\n"
                        "Utilisation : `.accepter <id_du_match>`",
            color=discord.Color.red())
        await ctx.send(embed=embed_error)
        return
    
    result, message = match.accepter_match(match_id, joueur2)
    if result == True:
        embed_success = discord.Embed(
            title=":white_check_mark: Match accepté",
            description=f"Le match **#{match_id}** a été accepté avec succès !\n"
                        f"Que le meilleur gagne ! 🏆",
            color=discord.Color.green())
        await ctx.send(embed=embed_success)

    elif result == False:
        embed_warning = discord.Embed(
            title=":warning: Match non disponible",
            description=f"Vous ne pouvez pas accepter le match n°{match_id} car {message}",
            color=discord.Color.orange())
        await ctx.send(embed=embed_warning)
    else:
        embed_error = discord.Embed(
            title=":x: Erreur",
            description="Une erreur inconnue est survenue lors de l'acceptation du match.\n"
                        "Veuillez réessayer ou contacter un administrateur.\n"
                        f"Erreur : {message}",
            color=discord.Color.red())
        await ctx.send(embed=embed_error)



@bot.command(name="refuser")
async def refuser_match(ctx, match_id: int = None):
    joueur2 = ctx.author.name
    if match_id is None:
        embed_error = discord.Embed(
            title=":x: Erreur : ID du match manquant",
            description="Veuillez fournir l'ID d'un match valide.\n"
                        "Utilisation : `.refuser <id_du_match>`",
            color=discord.Color.red())
        await ctx.send(embed=embed_error)
        return

    result, message = match.refuser_match(match_id, joueur2)
    if result == True:
        embed_success = discord.Embed(
            title=":white_check_mark: Match refusé",
            description=f"Le match **#{match_id}** a été refusé avec succès.\n"
                        "Vous pouvez toujours déclarer un nouveau match !",
            color=discord.Color.green())
        await ctx.send(embed=embed_success)

    elif result == False:
        embed_warning = discord.Embed(
            title=":warning: Match non disponible",
            description=f"Vous ne pouvez pas refuser le match n°{match_id} car {message}",
            color=discord.Color.orange())
        await ctx.send(embed=embed_warning)

    else:
        embed_error = discord.Embed(
            title=":x: Erreur",
            description="Une erreur inconnue est survenue lors du refus du match.\n"
                        "Veuillez réessayer ou contacter un administrateur.",
            color=discord.Color.red())
        await ctx.send(embed=embed_error)



@bot.command(name="leaderboard")
async def leaderboard(ctx):
    leaderboard = elo_manager.classement()
    if leaderboard:
        embed = discord.Embed(
            title=":trophy: Classement des Joueurs :trophy:",
            description="Voici les meilleurs joueurs de la compétition.",
            color=discord.Color.gold())

        for rank, name, score in leaderboard:
            embed.add_field(
                name=f"#{rank} - {name}",
                value=f"Score Elo : **{score}**",
                inline=False)

        embed.set_footer(text="Ceci est le leaderboard officiel")
        embed.set_thumbnail(url="") # url de l'image sur le serveur à mettre /!\ oublie pas !!
        await ctx.send(embed=embed)
    else:
        await ctx.send(":x: Aucun joueur n'est enregistré dans la compétition")

"""
@bot.command(name="win")
async def winner(ctx):
    """


@bot.command(name="add")
async def add(ctx):
    match.create_match_test()
    await ctx.send("simulation de match créée")

@bot.command(name="del")
async def delete(ctx):
    match.delete_match_test()
    await ctx.send("simulations des matchs supprimées")

bot.run(BOT_TOKEN)