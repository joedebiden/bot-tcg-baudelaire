import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Select, View
from discord.ui import Select, View, Modal, TextInput
from datetime import datetime


intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

nom_fichier = "C:\\Users\\rapha\\Documents\\perso\\a_cotes\\discord pokemon carte\\Classement_bot\\classement.txt"

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Connecté en tant que {bot.user}")

#-----------------------------------------------------------------------------------------------------------------------------------------

@bot.command()
async def liste(ctx):

    date = datetime.today().strftime('%Y-%m-%d / %Hh %Mmin %Ssec')

    await ctx.send(f"Le {date}\n")
    
    try:
        with open(nom_fichier, 'r') as fichier:
            lignes = fichier.readlines()
            print(f"contenu fichier : {lignes}")

        with open(nom_fichier, 'w') as fichier:
            for ligne in lignes:
                nom, valeur = ligne.split(':')
                nom = nom.strip()
                valeur = valeur.strip()

                print(ligne)
                await ctx.send(f"• {nom} : {valeur} Points")
                fichier.write(f"{nom} : {valeur}\n")

    except FileNotFoundError:
        await ctx.send("Le fichier n'existe pas.")
        return "Le fichier n'existe pas."

#-----------------------------------------------------------------------------------------------------------------------------------------

@bot.command()

async def set_score(ctx):

    try:
        with open(nom_fichier, 'r') as fichier:
            lignes = fichier.readlines()

        # Liste pour stocker les options
        options = []
        for ligne in lignes:
            nom, valeur = ligne.split(':')
            nom = nom.strip()
            valeur = valeur.strip()

            # Ajouter chaque nom dans les options du Select
            options.append(discord.SelectOption(label=nom, description=f"{valeur} Points", emoji="➕"))



#   AJOUTER DEF JOUEUR


            #discord.SelectOption(label="new", description="Ajouter un nouveau joueur", emoji="🆕")
    except FileNotFoundError:
        await ctx.send("Le fichier n'existe pas.")
        return


    player_select = Select(
        placeholder="Choisir un joueur :",
        options=options  # Les options créées à partir du fichier
    )

    async def player_callback(interaction):
        nom_player = player_select.values[0]
        await set_score(interaction, nom_player)

    player_select.callback = player_callback  # Associer la fonction callback

    # Créer la vue et ajouter le menu déroulant
    view = View()
    view.add_item(player_select)

    await ctx.send("Choisir le joueur auquel mettre le score :", view=view)

async def set_score(interaction, nom_player):

    class CarteModal(Modal):
        def __init__(self):
            super().__init__(title="Changer un score")

            # Champs de saisie pour les cartes
            self.score = TextInput(label="Score à mettre au joueur", placeholder="Ex: 500")

            self.add_item(self.score)

        async def on_submit(self, interaction: discord.Interaction):
            nouveau_score = int(self.score.value)
            points_ajoutes = await ajout_point(nom_player, nouveau_score)
            # Répondre directement à l'interaction du modal
            await interaction.response.send_message(f"{nom_player} a maintenant {points_ajoutes} Points !")

    modal = CarteModal()
    await interaction.response.send_modal(modal)

async def ajout_point(nom_player, nouveau_score):

    try:
        with open(nom_fichier, 'r') as fichier:
            lignes = fichier.readlines()

        # Trouver le gagnant et récupérer ses points actuels
        nouveau_contenu = []
        points_finaux = 0  # Initialiser les points finaux
        for ligne in lignes:
            nom, valeur = ligne.split(':')
            nom = nom.strip()
            valeur = int(valeur.strip())

            if nom == nom_player:
                
                # Mettre à jour le score
                ligne = f"{nom} : {nouveau_score}\n"

            nouveau_contenu.append(ligne)

        # Écrire les nouveaux points dans le fichier
        with open(nom_fichier, 'w') as fichier:
            fichier.writelines(nouveau_contenu)

        return nouveau_score

    except FileNotFoundError:
        await interaction.followup.send("Le fichier n'existe pas.")

#-----------------------------------------------------------------------------------------------------------------------------------------

@bot.command()
async def egalite(ctx):

    egalite_select = Select(
        placeholder="Égalité ?",
        options=[
            discord.SelectOption(label="oui", emoji="✅"),
            discord.SelectOption(label="non", emoji="❌")
        ]
    )

    # Callback pour le premier Select (égalité)
    async def egalite_callback(interaction):

        if egalite_select.values[0] == "oui":

            await gerer_egalite(interaction)

        elif egalite_select.values[0] == "non":

            await interaction.response.send_message("Écriver : !gagnant ou !perdant pour compter les points.")

    egalite_select.callback = egalite_callback

    view = View()
    view.add_item(egalite_select)

    await ctx.send("Égalité ?", view=view)


async def gerer_egalite(interaction):
    # Lire les scores actuels depuis le fichier
    try:
        with open(nom_fichier, 'r') as fichier:
            lignes = fichier.readlines()
        
        # Extraire les noms des joueurs et créer un menu déroulant pour choisir les deux joueurs
        options = [discord.SelectOption(label=ligne.split(':')[0].strip(), description=f"{ligne.split(':')[1].strip()} Points") for ligne in lignes]
        
        # Créer un Select pour choisir le premier joueur
        joueur1_select = Select(placeholder="Choisissez le premier joueur :", options=options)
        
        # Créer un Select pour choisir le deuxième joueur
        joueur2_select = Select(placeholder="Choisissez le deuxième joueur :", options=options)

        view = View()
        view.add_item(joueur1_select)
        view.add_item(joueur2_select)

        await interaction.response.send_message("Choisissez les joueurs à égalité :", view=view)

        # Callback pour gérer les joueurs sélectionnés
        async def tie_callback(interaction):
            if not joueur1_select.values or not joueur2_select.values:  # Vérifiez si les joueurs sont sélectionnés

                if joueur1_select.values == joueur2_select.values:

                    await interaction.response.send_message("Veuillez choisir deux joueurs différents", ephemeral=True)
                    return  # Sortir si aucune valeur n'est sélectionnée

                else:

                    await interaction.response.send_message("Veuillez choisir les deux joueurs.", ephemeral=True)
                    return  # Sortir si aucune valeur n'est sélectionnée

            joueur1 = joueur1_select.values[0]
            joueur2 = joueur2_select.values[0]

            await demander_cartes_perdant(interaction, joueur1, joueur2)

        joueur1_select.callback = tie_callback
        joueur2_select.callback = tie_callback

    except FileNotFoundError:
        await interaction.followup.send("Le fichier n'existe pas.")


async def demander_cartes_perdant(interaction, joueur1, joueur2):
    class CarteModal(Modal):
        def __init__(self):
            super().__init__(title="Information des cartes")

            # Champs de saisie pour les cartes
            self.cartes_perdues_joueur1 = TextInput(label=f"Nombre de cartes perdues : {joueur1}", placeholder="Ex: 5")
            self.cartes_perdues_joueur2 = TextInput(label=f"Nombre de cartes perdues : {joueur2}", placeholder="Ex: 2")

            self.add_item(self.cartes_perdues_joueur1)
            self.add_item(self.cartes_perdues_joueur2)

        async def on_submit(self, interaction: discord.Interaction):
            nb_cartes_perdues_joueur1 = int(self.cartes_perdues_joueur1.value)
            nb_cartes_perdues_joueur2 = int(self.cartes_perdues_joueur2.value)

            # Calculer les nouveaux points
            resultat = await calculer_points_egalite(joueur1, joueur2, nb_cartes_perdues_joueur1, nb_cartes_perdues_joueur2)
            await interaction.response.send_message(resultat)

    modal = CarteModal()
    await interaction.response.send_modal(modal)


async def calculer_points_egalite(joueur1, joueur2, nb_cartes_perdues_joueur1, nb_cartes_perdues_joueur2):
    try:
        with open(nom_fichier, 'r') as fichier:
            lignes = fichier.readlines()

        nouveau_contenu = []
        
        # Initialiser les points pour les deux joueurs
        points_joueur1 = 0
        points_joueur2 = 0

        for ligne in lignes:
            nom, valeur = ligne.split(':')
            nom = nom.strip()
            valeur = int(valeur.strip())

            if nom == joueur1:
                points_joueur1 = valeur + (10 * nb_cartes_perdues_joueur1)  # Mettez à jour cela avec le nombre réel de cartes perdues pour le joueur 1
                ligne = f"{nom} : {points_joueur1}\n"
            elif nom == joueur2:
                points_joueur2 = valeur + (10 * nb_cartes_perdues_joueur2)  # Mettez à jour cela avec le nombre réel de cartes perdues pour le joueur 2
                ligne = f"{nom} : {points_joueur2}\n"

            nouveau_contenu.append(ligne)

        # Écrire les scores mis à jour dans le fichier
        with open(nom_fichier, 'w') as fichier:
            fichier.writelines(nouveau_contenu)

        resultat = (f"{joueur1} à maintenant {points_joueur1} points ! et {joueur2} {points_joueur2} points !")
        return resultat

    except FileNotFoundError:
        await interaction.followup.send("Le fichier n'existe pas.")

#-----------------------------------------------------------------------------------------------------------------------------------------

@bot.command()
async def win(ctx):
    try:
        with open(nom_fichier, 'r') as fichier:
            lignes = fichier.readlines()

        # Liste pour stocker les options
        options = []

        for ligne in lignes:
            nom, valeur = ligne.split(':')
            nom = nom.strip()
            valeur = valeur.strip()

            # Ajouter chaque nom dans les options du Select
            options.append(
                discord.SelectOption(label=nom, description=f"{valeur} Points", emoji="👑"))

        gagnant_select = Select(
            placeholder="Choisir le gagnant :",
            options=options  # Les options créées à partir du fichier
        )

        async def gagnant_callback(interaction):

            if interaction.data.get("values"):

                nom_gagnant = interaction.data["values"][0]
                await demander_cartes_gagnant(interaction, nom_gagnant)

            else:

                await interaction.response.send_message("Aucune option sélectionnée. Veuillez essayer à nouveau.", ephemeral=True)

        gagnant_select.callback = gagnant_callback  # Associer la fonction callback
        view = View()
        view.add_item(gagnant_select)

        await ctx.send("Choisir le gagnant :", view=view)
            
    except Exception as e:
        await ctx.send(f"Une erreur s'est produite : {str(e)}")

    # Demander les cartes jouées et restantes
    async def demander_cartes_gagnant(interaction, nom_gagnant):
        class CarteModal(Modal):
            def __init__(self):
                super().__init__(title="Information des cartes du gagnant")

                # Champs de saisie pour les cartes
                self.carte_jouee = TextInput(label="Nombre de cartes récompense jouées", placeholder="Ex: 5")
                self.cartes_restantes_gagnant = TextInput(label="Nombre de cartes restantes du gagnant", placeholder="Ex: 2")
                self.cartes_restantes_perdant = TextInput(label="Nombre de cartes restantes du perdant", placeholder="Ex: 4")
                self.cartes_perdues = TextInput(label="Nombre de cartes du perdant", placeholder="Ex: 2")

                self.add_item(self.carte_jouee)
                self.add_item(self.cartes_restantes_gagnant)
                self.add_item(self.cartes_restantes_perdant)
                self.add_item(self.cartes_perdues)

            async def on_submit(self, interaction: discord.Interaction):
                nb_cartes_jouees = int(self.carte_jouee.value)
                nb_cartes_restantes_gagnant = int(self.cartes_restantes_gagnant.value)
                nb_cartes_restantes_perdant = int(self.cartes_restantes_perdant.value)
                nb_cartes_perdues = int(self.cartes_perdues.value)

                # Calculer les nouveaux points
                points_finaux = await calculer_points_gagnant(nom_gagnant, nb_cartes_jouees, nb_cartes_restantes_gagnant, nb_cartes_restantes_perdant, nb_cartes_perdues)

                # Répondre directement à l'interaction du modal
                await interaction.response.send_message(f"{nom_gagnant} a maintenant {points_finaux} Points!")

        modal = CarteModal()
        await interaction.response.send_modal(modal)

    # Fonction pour calculer les points
    async def calculer_points_gagnant(nom_gagnant, nb_cartes_jouees, nb_cartes_restantes_gagnant, nb_cartes_restantes_perdant, nb_cartes_perdues):
        try:
            with open(nom_fichier, 'r') as fichier:
                lignes = fichier.readlines()

            # Trouver le gagnant et récupérer ses points actuels
            nouveau_contenu = []
            points_finaux = 0  # Initialiser les points finaux
            for ligne in lignes:
                nom, valeur = ligne.split(':')
                nom = nom.strip()
                valeur = int(valeur.strip())

                if nom == nom_gagnant:
                    # Appliquer la formule correcte
                    points_avant = valeur
                    points_finaux = points_avant + (nb_cartes_jouees * 10 * (nb_cartes_restantes_perdant - nb_cartes_restantes_gagnant)) + (4 * (6 - nb_cartes_perdues))

                    # Mettre à jour la ligne du gagnant
                    ligne = f"{nom} : {points_finaux}\n"

                nouveau_contenu.append(ligne)

            # Écrire les nouveaux points dans le fichier
            with open(nom_fichier, 'w') as fichier:
                fichier.writelines(nouveau_contenu)

            return points_finaux  # Retourner les points finaux calculés

        except FileNotFoundError:
            await interaction.followup.send("Le fichier n'existe pas.")

#-----------------------------------------------------------------------------------------------------------------------------------------

@bot.command()
async def lose(ctx):
    try:
        with open(nom_fichier, 'r') as fichier:
            lignes = fichier.readlines()

        options = []
        for ligne in lignes:
            nom, valeur = ligne.split(':')
            nom = nom.strip()
            valeur = valeur.strip()
            options.append(discord.SelectOption(label=nom, description=f"{valeur} Points", emoji="🤡"))

        perdant_select = Select(
            placeholder="Choisir un perdant :",
            options=options
        )

        async def perdant_callback(interaction):
            # Use interaction to get selected values
            if interaction.data.get("values"):
                nom_perdant = interaction.data["values"][0]  # Get selected value from interaction data
                await demander_cartes_perdant(interaction, nom_perdant)
            else:
                await interaction.response.send_message("Aucune option sélectionnée. Veuillez essayer à nouveau.", ephemeral=True)

        perdant_select.callback = perdant_callback
        view = View()
        view.add_item(perdant_select)

        await ctx.send("Choisir le perdant :", view=view)
    except Exception as e:
        await ctx.send(f"Une erreur s'est produite : {str(e)}")



    # Créer le menu déroulant avec les noms des perdants
    perdant_select = Select(
        placeholder="Choisir un perdant :",
        options=options  # Les options créées à partir du fichier
    )

    # Callback pour la sélection d'un perdant
    async def perdant_callback(interaction):
        nom_perdant = perdant_select.values[0]
        await demander_cartes_perdant(interaction, nom_perdant)

        perdant_select.callback = perdant_callback  # Associer la fonction callback

        # Créer la vue et ajouter le menu déroulant
        view = View()
        view.add_item(perdant_select)

        # Ajouter `await` ici pour attendre l'envoi du message
        await ctx.send("Choisir le perdant :", view=view)

    # Demander les cartes jouées et restantes
    async def demander_cartes_perdant(interaction, nom_perdant):
        class CarteModal(Modal):
            def __init__(self):
                super().__init__(title="Information des cartes du perdant")

                # Champs de saisie pour les cartes
                self.carte_jouee = TextInput(label="Nombre de cartes récompense jouées", placeholder="Ex: 5")
                self.cartes_perdues = TextInput(label="Nombre de cartes du perdant", placeholder="Ex: 2")

                self.add_item(self.carte_jouee)
                self.add_item(self.cartes_perdues)

            async def on_submit(self, interaction: discord.Interaction):
                nb_cartes_jouees = int(self.carte_jouee.value)
                nb_cartes_perdues = int(self.cartes_perdues.value)

                # Calculer les nouveaux points
                points_finaux = await calculer_points_perdant(nom_perdant, nb_cartes_jouees, nb_cartes_perdues)

                # Répondre directement à l'interaction du modal
                await interaction.response.send_message(f"{nom_perdant} a maintenant {points_finaux} Points!")

        modal = CarteModal()
        await interaction.response.send_modal(modal)

    # Fonction pour calculer les points
    async def calculer_points_perdant(nom_perdant, nb_cartes_jouees, nb_cartes_perdues):
        try:
            with open(nom_fichier, 'r') as fichier:
                lignes = fichier.readlines()

            # Trouver le perdant et récupérer ses points actuels
            nouveau_contenu = []
            points_finaux = 0  # Initialiser les points finaux
            for ligne in lignes:
                nom, valeur = ligne.split(':')
                nom = nom.strip()
                valeur = int(valeur.strip())

                if nom == nom_perdant:
                    # Appliquer la formule correcte
                    points_avant = valeur
                    points_finaux = points_avant + nb_cartes_jouees * 2 * ( 6 - nb_cartes_perdues) + 10 

                    # Mettre à jour la ligne du perdant
                    ligne = f"{nom} : {points_finaux}\n"

                nouveau_contenu.append(ligne)

            # Écrire les nouveaux points dans le fichier
            with open(nom_fichier, 'w') as fichier:
                fichier.writelines(nouveau_contenu)

            return points_finaux  # Retourner les points finaux calculés

        except FileNotFoundError:
            await interaction.followup.send("Le fichier n'existe pas.")


