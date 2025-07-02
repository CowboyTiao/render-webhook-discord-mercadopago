import discord
from discord.ext import tasks, commands
import pymysql
import asyncio
from config import CANAIS

class LogItensListener(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_id = 0
        self.monitorar_logs.start()
        print("[COG] LogItensListener instanciado")

    def cog_unload(self):
        self.monitorar_logs.cancel()

    @tasks.loop(seconds=5)
    async def monitorar_logs(self):
        await self.bot.wait_until_ready()

        try:
            conn = pymysql.connect(
                host="localhost",
                user="discordbot",
                password="senha123",
                database="bewitched"
            )
            with conn.cursor() as cursor:
                cursor.execute("SELECT id, user_id, action, data, hora, grupo FROM ks_admin_logs ORDER BY id DESC LIMIT 1")
                resultado = cursor.fetchone()

            conn.close()

            if resultado and resultado[0] > self.last_id:
                self.last_id = resultado[0]

                id_log, user_id, action, data, hora, grupo = resultado

                canal = self.bot.get_channel(CANAIS["LOG_ITENS_STAFF"])
                if canal:
                    embed = discord.Embed(
                        title="📦 Ação de Staff Detectada",
                        description=f"**Ação:** {action}",
                        color=discord.Color.orange()
                    )
                    embed.add_field(name="👤 Staff ID", value=user_id, inline=True)
                    embed.add_field(name="📅 Data", value=data, inline=True)
                    embed.add_field(name="🕒 Hora", value=hora, inline=True)
                    embed.set_footer(text=f"Grupo: {grupo}")
                    await canal.send(embed=embed)

        except Exception as e:
            print(f"[ERRO MONITORAMENTO] {e}")

async def setup(bot):
    await bot.add_cog(LogItensListener(bot))
    print("[EXTENSAO] setup() de log_itens_listener.py EXECUTADO")
