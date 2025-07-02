import discord
from discord.ext import commands
from config import GUILD_ID, COMMANDS_CONFIG, DISCORD_TOKEN
from flask import Flask
from threading import Thread

from commands.verificar import VerificarView  # 👈 Adicionado para registrar a View persistente

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents.all())
        self.loaded_cogs = set()

    async def setup_hook(self):
        print("[BOT] Executando setup_hook()")

        # ✅ Registra a View persistente do botão "Verificar"
        self.add_view(VerificarView())

        if COMMANDS_CONFIG.get("teste", {}).get("enabled"):
            if "commands.teste" not in self.extensions:
                print("[BOT] Carregando extensão commands.teste")
                await self.load_extension("commands.teste")
            else:
                print("[BOT] EXTENSION 'commands.teste' já carregada")
        else:
            print("[BOT] Comando 'teste' desativado em config.")

        if "listeners.on_member_events" not in self.extensions:
            await self.load_extension("listeners.on_member_events")

        if "listeners.on_command_log" not in self.extensions:
            await self.load_extension("listeners.on_command_log")

        if COMMANDS_CONFIG.get("apagar", {}).get("enabled"):
            if "commands.apagar" not in self.extensions:
                print("[BOT] Carregando extensão commands.apagar")
                await self.load_extension("commands.apagar")
            else:
                print("[BOT] EXTENSION 'commands.apagar' já carregada")
            
        if COMMANDS_CONFIG.get("verificar", {}).get("enabled"):
            if "commands.verificar" not in self.extensions:
                print("[BOT] Carregando extensão commands.verificar")
                await self.load_extension("commands.verificar")
            else:
                print("[BOT] EXTENSION 'commands.verificar' já carregada")
        else:
            print("[BOT] Comando 'verificar' desativado em config.")
            
        if "commands.verificar_captcha" not in self.extensions:
            print("[BOT] Carregando extensão commands.verificar_captcha")
            await self.load_extension("commands.verificar_captcha")
        else:
            print("[BOT] EXTENSION 'commands.verificar_captcha' já carregada")

        if COMMANDS_CONFIG.get("liberacao", {}).get("enabled"):
            if "commands.liberacao" not in self.extensions:
                print("[BOT] Carregando extensão commands.liberacao")
                await self.load_extension("commands.liberacao")
            else:
                print("[BOT] EXTENSION 'commands.liberacao' já carregada")
        else:
            print("[BOT] Comando 'liberação' desativado em config.")

        if COMMANDS_CONFIG.get("log_itens_listener", {}).get("enabled"):
            await self.load_extension("commands.log_itens_listener")

        if COMMANDS_CONFIG.get("mensagens", {}).get("enabled"):
            await self.load_extension("commands.mensagens")

        if COMMANDS_CONFIG.get("log_admin_listener", {}).get("enabled"):
            await bot.load_extension("listeners.log_admin_listener")

        if COMMANDS_CONFIG.get("carregar", {}).get("enabled"):
            print("[BOT] Carregando extensão commands.carregar")
            await self.load_extension("commands.carregar")
            await self.load_extension("commands.carregarteste")









bot = MyBot()

@bot.event
async def on_ready():
    print(f"[BOT] Conectado como {bot.user} (ID: {bot.user.id})")

if __name__ == "__main__":
    if not DISCORD_TOKEN or DISCORD_TOKEN == "INSIRA_SEU_TOKEN_AQUI":
        print("[ERRO] Coloque seu token real em config.py")
    else:
        print("[BOT] Iniciando...")

        # Inicia o servidor Flask em paralelo (usando webhook.py diretamente)
        from webhook import app  # Usa o app já configurado

        def iniciar_flask():
            app.run(host="0.0.0.0", port=5001, debug=False)

        flask_thread = Thread(target=iniciar_flask)
        flask_thread.start()


        # Inicia o bot normalmente
        bot.run(DISCORD_TOKEN)

