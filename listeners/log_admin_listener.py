import discord
from discord.ext import commands
from flask import Flask, request
import threading
import asyncio
from datetime import datetime
from config import CANAIS
app = Flask(__name__)
bot_reference = None

@app.route('/log', methods=['POST'])
def receber_log():
    data = request.json
    passport = data.get("passport")
    comando = data.get("comando")

    print(f"[LOG_HTTP] Log recebido: Passaporte: {passport} | Comando: {comando}")
    if bot_reference:
        asyncio.run_coroutine_threadsafe(enviar_log(passport, comando), bot_reference.loop)
    return 'OK', 200

async def enviar_log(passport, comando):
    canal = bot_reference.get_channel(CANAIS['log_comandos'])
    if canal:
        embed = discord.Embed(title="🛠️ Log Administrativo", color=0x7289DA)
        embed.add_field(name="Passaporte", value=passport, inline=True)
        embed.add_field(name="Comando", value=comando, inline=False)
        embed.set_footer(text=f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        await canal.send(embed=embed)

def iniciar_http():
    app.run(port=5000, debug=False, use_reloader=False)

class LogHTTP(commands.Cog):
    def __init__(self, bot):
        global bot_reference
        self.bot = bot
        bot_reference = bot
        print("[COG] LogHTTP instanciado")

    @commands.Cog.listener()
    async def on_ready(self):
        print("[EXTENSAO] HTTP listener online e aguardando logs de admin via POST")
        threading.Thread(target=iniciar_http).start()

async def setup(bot):
    await bot.add_cog(LogHTTP(bot))
    print("[BOT] Comando HTTP de log registrado no bot")