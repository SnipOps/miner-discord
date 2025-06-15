import discord
from discord.ext import commands
import random
import asyncio

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# Inventaire des joueurs
inventaire = {}

# Liste des minerais possibles
minerais_possibles = [
    "Pierre", "Fer", "Charbon", "Cuivre", "Or",
    "Émeraude", "Rubis", "Diamant", "Obsidienne"
]

# ID du salon
CHANNEL_ID = 1383808500735414283

# Dictionnaire pour stocker les derniers messages d'interaction par utilisateur
user_last_messages = {}

class MinerView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def cleanup_previous(self, interaction: discord.Interaction):
        # Supprime le message précédent de l'utilisateur s'il existe
        user_id = interaction.user.id
        if user_id in user_last_messages and user_last_messages[user_id]:
            try:
                message = user_last_messages[user_id]
                await message.delete()
            except:
                pass

    @discord.ui.button(label="⛏️ Miner", style=discord.ButtonStyle.green)
    async def miner_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await self.cleanup_previous(interaction)
        
        user_id = interaction.user.id
        minerai = random.choice(minerais_possibles)
        quantite = random.randint(1, 5)

        if user_id not in inventaire:
            inventaire[user_id] = {}
        inventaire[user_id][minerai] = inventaire[user_id].get(minerai, 0) + quantite

        # Envoie le résultat et les nouveaux boutons
        view = MinerView()
        message = await interaction.followup.send(
            f"⛏️ {interaction.user.mention}, tu as trouvé {quantite}x {minerai} !\n\nQue veux-tu faire maintenant ?",
            view=view,
            ephemeral=True
        )
        user_last_messages[user_id] = message

    @discord.ui.button(label="🎒 Sac", style=discord.ButtonStyle.blurple)
    async def sac_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await self.cleanup_previous(interaction)
        
        user_id = interaction.user.id
        sac = inventaire.get(user_id, {})

        if not sac:
            content = f"🎒 {interaction.user.mention}, ton sac est vide."
        else:
            contenu = "\n".join([f"- {k} : {v}" for k, v in sac.items()])
            content = f"🎒 {interaction.user.mention}, voici ton sac :\n{contenu}"

        # Envoie le résultat et les nouveaux boutons
        view = MinerView()
        message = await interaction.followup.send(
            f"{content}\n\nQue veux-tu faire maintenant ?",
            view=view,
            ephemeral=True
        )
        user_last_messages[user_id] = message

    @discord.ui.button(label="🔄 Reset", style=discord.ButtonStyle.red)
    async def reset_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await self.cleanup_previous(interaction)
        
        await envoyer_boutons()
        message = await interaction.followup.send(
            "🔄 Les boutons ont été réinitialisés !",
            ephemeral=True
        )
        user_last_messages[interaction.user.id] = message

@bot.event
async def on_ready():
    print(f"✅ Bot connecté en tant que {bot.user}")
    await envoyer_boutons()

async def envoyer_boutons():
    await bot.wait_until_ready()
    channel = bot.get_channel(CHANNEL_ID)

    if not channel:
        print("❌ Channel introuvable")
        return

    # Supprime les anciens messages du bot dans le channel
    async for message in channel.history(limit=20):
        if message.author == bot.user:
            await message.delete()

    # Envoie un nouveau message avec les boutons
    view = MinerView()
    await channel.send("👋 Cliquez sur un bouton pour miner ou voir votre sac :", view=view)

# Commande textuelle !miner
@bot.command()
async def miner(ctx):
    user_id = ctx.author.id
    minerai = random.choice(minerais_possibles)
    quantite = random.randint(1, 5)

    if user_id not in inventaire:
        inventaire[user_id] = {}
    inventaire[user_id][minerai] = inventaire[user_id].get(minerai, 0) + quantite

    await ctx.send(f"⛏️ {ctx.author.mention}, tu as trouvé {quantite}x {minerai} !")

# Commande textuelle !sac
@bot.command()
async def sac(ctx):
    user_id = ctx.author.id
    sac = inventaire.get(user_id, {})

    if not sac:
        await ctx.send(f"🎒 {ctx.author.mention}, ton sac est vide.")
    else:
        contenu = "\n".join([f"- {k} : {v}" for k, v in sac.items()])
        await ctx.send(f"🎒 {ctx.author.mention}, voici ton sac :\n{contenu}")

# Permet de taper "!" ou "reset" pour relancer les boutons
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.content.strip().lower() in ("!", "reset"):
        await envoyer_boutons()
        await message.delete()

    await bot.process_commands(message)

# Démarrer le bot
bot.run("MTM4MzgxMTQ5NzIzNDUzMDUxNQ.GM_bUy.wpu3MXCE69zeYH7qQ2WXV6aRhQLnpA_B3YbvMg")