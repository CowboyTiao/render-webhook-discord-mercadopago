import re
import discord
from discord.ext import commands
from config import GUILD_ID, CANAIS, COMMANDS_CONFIG
from datetime import datetime

class Apagar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("[COG] Apagar instanciado")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild or message.guild.id != GUILD_ID:
            return

        match = re.match(r"^!apagar(\d+)$", message.content.strip())
        if not match:
            return  # Não interfere nos outros comandos

        config = COMMANDS_CONFIG.get("apagar", {})
        if not config.get("enabled", False):
            return

        user_role_ids = [role.id for role in message.author.roles]
        allowed = config.get("allowed_roles", [])

        if not any(role_id in user_role_ids for role_id in allowed):
            await message.channel.send("Você não tem permissão para usar este comando.", delete_after=1)
            return

        amount = int(match.group(1))
        deleted = await message.channel.purge(limit=amount + 1)
        await message.channel.send(f"{len(deleted) - 1} mensagens apagadas.", delete_after=1)

        # Log de comando
        canal_log = message.guild.get_channel(CANAIS["LOG_COMANDOS"])
        if canal_log:
            embed = discord.Embed(
                title="Comando executado",
                description=f"**Usuário:** {message.author.mention} (`{message.author.id}`)\n"
                            f"**Comando:** `{message.content}`\n"
                            f"**Canal:** {message.channel.mention}",
                color=discord.Color.blue(),
                timestamp=datetime.utcnow()
            )
            await canal_log.send(embed=embed)

async def setup(bot):
    print("[EXTENSAO] setup() de apagar.py EXECUTADO")
    await bot.add_cog(Apagar(bot))
