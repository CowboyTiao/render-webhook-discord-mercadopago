from discord.ext import commands
from config import GUILD_ID, CANAIS
import discord
from datetime import datetime

# Variável de proteção contra múltiplas instâncias
_logger_loaded = False

class CommandLogger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("[LOGGER] CommandLogger instanciado")

    @commands.Cog.listener()
    async def on_command(self, ctx):
        print(f"[LOGGER] on_command chamado por {ctx.author} - {ctx.command}")
        if ctx.guild and ctx.guild.id != GUILD_ID:
            return

        canal_log = ctx.guild.get_channel(CANAIS["LOG_COMANDOS"])
        if canal_log:
            embed = discord.Embed(
                title="Comando executado",
                description=(
                    f"**Usuário:** {ctx.author.mention} (`{ctx.author.id}`)\n"
                    f"**Comando:** `{ctx.message.content}`\n"
                    f"**Canal:** {ctx.channel.mention}"
                ),
                color=discord.Color.blue(),
                timestamp=datetime.utcnow()
            )
            await canal_log.send(embed=embed)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound) and ctx.message.content.startswith("!apagar"):
            return

        if ctx.guild and ctx.guild.id != GUILD_ID:
            return

        canal_log = ctx.guild.get_channel(CANAIS["LOG_COMANDOS"])
        if canal_log:
            embed = discord.Embed(
                title="Erro ao executar comando",
                description=(
                    f"**Usuário:** {ctx.author.mention} (`{ctx.author.id}`)\n"
                    f"**Comando:** `{ctx.message.content}`\n"
                    f"**Erro:** `{type(error).__name__}: {error}`"
                ),
                color=discord.Color.red(),
                timestamp=datetime.utcnow()
            )
            await canal_log.send(embed=embed)

async def setup(bot):
    global _logger_loaded
    if _logger_loaded:
        print("[LOGGER] setup() ignorado: CommandLogger já foi carregado!")
        return
    print("[LOGGER] Executando setup() de on_command_log")
    await bot.add_cog(CommandLogger(bot))
    _logger_loaded = True
