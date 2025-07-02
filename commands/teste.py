from discord.ext import commands
from config import COMMANDS_CONFIG

async def check_access(user) -> bool:
    allowed = COMMANDS_CONFIG.get("teste", {}).get("allowed_roles", [])
    return any(role.id in allowed for role in user.roles)

class Teste(commands.Cog):
    _instance_count = 0

    def __init__(self, bot):
        self.bot = bot
        Teste._instance_count += 1
        print(f"[COG] Teste instanciado ({Teste._instance_count})")

        print("[COG] Comandos registrados no bot:")
        for cmd in bot.commands:
            print(f"  - {cmd.name} ({cmd.callback.__qualname__})")

    @commands.command(name="teste")
    async def teste_cmd(self, ctx):
        if not await check_access(ctx.user if hasattr(ctx, 'user') else ctx.author):
            await ctx.send('❌ Você não tem permissão para usar este comando.')
            return
        print(f"[COMANDO] !teste chamado por {ctx.author} - Bot ID: {self.bot.user.id}")
        await ctx.send("Ativo")

async def setup(bot):
    print("[EXTENSAO] setup() de teste.py EXECUTADO")
    await bot.add_cog(Teste(bot))