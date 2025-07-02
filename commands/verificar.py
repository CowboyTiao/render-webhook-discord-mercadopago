import discord
from discord.ext import commands
from discord.ui import View, Button
from config import COMMANDS_CONFIG

class VerificarView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Button(label="Verificar", style=discord.ButtonStyle.primary, custom_id="verificar_inicio"))
        self.add_item(Button(label="Porque verificar a conta...", style=discord.ButtonStyle.secondary, custom_id="verificar_info"))

async def check_access(user) -> bool:
    allowed = COMMANDS_CONFIG.get("verificar", {}).get("allowed_roles", [])
    return any(role.id in allowed for role in user.roles)

class VerificarCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("[COG] Verificar instanciado")

    @commands.command(name="verificar")
    async def verificar(self, ctx):
        if not await check_access(ctx.author):
            await ctx.send('❌ Você não tem permissão para usar este comando.')
            return
        embed = discord.Embed(
            title="✔️ Verificação - New Zone RP",
            description="Confirme que você é um humano respondendo a um CAPTCHA de segurança.\n\n🕒 Você tem 10 minutos após sua entrada para confirmar.",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed, view=VerificarView())
        print("[BOT] Comando registrado no bot: - verificar (VerificarCommand.verificar)")

async def setup(bot):
    await bot.add_cog(VerificarCommand(bot))
    print("[EXTENSAO] setup() de verificar.py EXECUTADO")