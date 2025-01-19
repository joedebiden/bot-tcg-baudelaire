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
    
    joueur1_obj = elo_manager.obtenir_joueur(joueur1)
    if joueur1_obj is None:
        embed_error = discord.Embed(
            title=":x: Erreur : Joueur introuvable",
            description="Vous n'êtes pas enregistré dans la compétition.\n"
                        "Commencez par vous inscrire avec la commande `.start`",
            color=discord.Color.red())
        await ctx.send(embed=embed_error)
        return
    
    adversaire_obj = elo_manager.obtenir_joueur(adversaire)
    if adversaire_obj is None:
        embed_error = discord.Embed(
            title=":x: Erreur : Adversaire introuvable",
            description=f"Le joueur **{adversaire}** n'est pas enregistré dans la compétition.\n"
                        "Veuillez vérifier le nom de l'adversaire et réessayer.",
            color=discord.Color.red())
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



"""Enregistre le gagnant d'un match et met à jour l'état à 'terminé' + manage l'elo"""
@bot.command(name="win")
async def enregistrer_gagnant(ctx, match_id: int, gagnant_nom: str):
    joueur_actuel = ctx.author.name

    try:
        match_data = match.obtenir_match(match_id)

        if not match_data:
            await ctx.send(embed=discord.Embed(
                title="Erreur",
                description=f"Le match avec l'ID `{match_id}` n'existe pas.",
                color=discord.Color.red()))
            return

        etat, joueur1, joueur2 = match_data
        if etat != "en cours":
            await ctx.send(embed=discord.Embed(
                title="Match non valide",
                description=f"Le match avec l'ID `{match_id}` n'est pas en cours.",
                color=discord.Color.orange()))
            return

        if joueur_actuel not in [joueur1, joueur2]:
            await ctx.send(embed=discord.Embed(
                title="Permission refusée",
                description="Vous ne participez pas à ce match.",
                color=discord.Color.red()))
            return

        if gagnant_nom not in [joueur1, joueur2]:
            await ctx.send(embed=discord.Embed(
                title="Erreur",
                description=f"Le joueur `{gagnant_nom}` ne participe pas à ce match.",
                color=discord.Color.red()))
            return
        
        perdant_nom = joueur1 if gagnant_nom == joueur2 else joueur2

        match.terminer_match(match_id, gagnant_nom)

        gagnant_obj = elo_manager.obtenir_joueur(gagnant_nom)
        perdant_obj = elo_manager.obtenir_joueur(perdant_nom)

        if gagnant_obj is None or perdant_obj is None:
            await ctx.send(embed=discord.Embed(
                title="Erreur",
                description="Impossible de trouver les informations des joueurs pour mettre à jour l'ELO.",
                color=discord.Color.red()))
            return

        elo_change_gagnant, elo_change_perdant = elo_manager.manage_elo(gagnant=gagnant_obj, perdant=perdant_obj, k=32)

        await ctx.send(embed=discord.Embed(
            title="Match Terminé 🎉",
            description=f"Le joueur **{gagnant_nom}** a remporté le match contre **{perdant_nom}** !\n"
                        f"Le match avec l'ID `{match_id}` est maintenant marqué comme **terminé**.\n"
                        f"**{gagnant_nom}** a gagné {elo_change_gagnant:.2f} ELO.\n"
                        f"**{perdant_nom}** a perdu {elo_change_perdant:.2f} ELO.",
            color=discord.Color.green()))

    except Exception as e:
        await ctx.send(embed=discord.Embed(
            title="Erreur inattendue",
            description=str(e),
            color=discord.Color.red()))


bot.run(BOT_TOKEN)