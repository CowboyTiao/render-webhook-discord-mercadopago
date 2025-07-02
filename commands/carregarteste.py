
import discord
from discord.ext import commands
from utils.payment_handler import criar_pagamento_pix
import base64
from io import BytesIO
import qrcode

class CarregarTeste(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("[COG] CarregarTeste instanciado")

    @commands.command(name="carregarteste")
    async def carregarteste(self, ctx):
        try:
            pagamento = criar_pagamento_pix(1, ctx.author.id)
            qr_base64 = pagamento["qr_code_base64"]

            # Corrigir padding
            missing_padding = len(qr_base64) % 4
            if missing_padding:
                qr_base64 += "=" * (4 - missing_padding)

            # Decodificar a imagem
            img_data = base64.b64decode(qr_base64)
            qr_img = BytesIO(img_data)

            file = discord.File(fp=qr_img, filename="qrcode.png")

            embed = discord.Embed(
                title="🔁 Pagamento Pix Gerado (Teste)",
                description="Use o QR Code abaixo para efetuar o pagamento real de R$1,00 e liberar produção.",
                color=0x00ff00
            )
            embed.set_image(url="attachment://qrcode.png")

            await ctx.author.send(file=file, embed=embed)
            await ctx.reply("✅ QR Code enviado por DM!", ephemeral=True if hasattr(ctx, "response") else False)

        except Exception as e:
            print(f"[ERRO] {e}")
            await ctx.send("❌ Ocorreu um erro ao gerar o QR Code.")

async def setup(bot):
    await bot.add_cog(CarregarTeste(bot))
    print("[EXTENSAO] setup() de carregarteste.py EXECUTADO")
