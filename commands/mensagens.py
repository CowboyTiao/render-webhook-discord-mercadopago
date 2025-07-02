import discord
from discord.ext import commands, tasks
from config import CANAIS, CARGOS

# Tempo entre as mensagens automáticas (em minutos)
INTERVALO_MINUTOS = 180

class MensagensCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.enviar_mensagem.start()
        print("[COG] Mensagens instanciado")

    def cog_unload(self):
        self.enviar_mensagem.cancel()

    @tasks.loop(minutes=INTERVALO_MINUTOS)
    async def enviar_mensagem(self):
        await self.bot.wait_until_ready()
        canal = self.bot.get_channel(CANAIS["CHAT_GERAL"])
        if canal:
            try:
                cargo = f"<@&{CARGOS['MORADOR']}>"
                canal_conexao = f"<#{CANAIS['CONEXAO']}>"

                await canal.send(
                    content=(
                        f"{cargo} {canal_conexao}\n"
                        "**Venha para a melhor do FIVEM**"
                    ),
                    file=discord.File("commands/assets/server_on.gif", filename="server_on.gif")
                )
            except Exception as e:
                print(f"[ERRO] Falha ao enviar mensagem automática: {e}")

async def setup(bot):
    await bot.add_cog(MensagensCommand(bot))
    print("[EXTENSAO] setup() de mensagens.py EXECUTADO")
