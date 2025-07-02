import discord
from discord.ext import commands
from config import COMMANDS_CONFIG, CARGOS, CANAIS
from utils.payment_handler import criar_pagamento_pix
from datetime import datetime
import base64
from io import BytesIO
from PIL import Image

# Apenas para testes locais (o real crédito é feito pelo webhook)
def adicionar_coins(account_id: int, quantidade: int):
    print(f"[DEBUG] Adicionar {quantidade} coins para o ID do personagem: {account_id}")

class ComprarView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="💰 Compra Recarga", style=discord.ButtonStyle.grey, custom_id="compra_recarga")
    async def compra_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        class ModalRecarga(discord.ui.Modal, title="Recarga de Coins"):
            id_personagem = discord.ui.TextInput(label="ID do personagem", placeholder="Ex: 1032", required=True)
            valor = discord.ui.TextInput(label="Valor (R$)", placeholder="Digite o valor mínimo: 1", required=True)
            nome = discord.ui.TextInput(label="Nome", placeholder="Ex: Joao", required=True)
            sobrenome = discord.ui.TextInput(label="Sobrenome", placeholder="Ex: Silva", required=True)
            cpf = discord.ui.TextInput(label="CPF (somente números)", placeholder="Ex: 000000000", required=True)

            async def on_submit(self, interaction: discord.Interaction):
                try:
                    valor_reais = float(self.valor.value)
                    if valor_reais < 1:
                        await interaction.response.send_message("❌ Valor mínimo: R$1", ephemeral=True)
                        return

                    account_id = int(self.id_personagem.value)

                    pagamento = criar_pagamento_pix(
                        valor_reais,
                        account_id,
                        self.nome.value.strip(),
                        self.sobrenome.value.strip(),
                        self.cpf.value.strip()
                    )

                    if not pagamento or "qrcode_base64" not in pagamento:
                        erro = pagamento.get("message", "Erro desconhecido") if isinstance(pagamento, dict) else str(pagamento)
                        print(f"[ERRO] Falha ao gerar pagamento: {erro}")
                        await interaction.response.send_message(f"❌ Erro ao gerar pagamento: {erro}", ephemeral=True)
                        return

                    # Decodifica imagem QR Code
                    img_data = base64.b64decode(pagamento["qrcode_base64"])
                    img = Image.open(BytesIO(img_data))
                    img_bytes = BytesIO()
                    img.save(img_bytes, format="PNG")
                    img_bytes.seek(0)

                    # Cria embed com QR Code
                    file = discord.File(fp=img_bytes, filename="qrcode.png")
                    embed = discord.Embed(
                        title="🔁 Pagamento Pix Gerado",
                        description=f"**Valor:** R${valor_reais:.2f}",
                        color=0x00ff00
                    )
                    embed.set_image(url="attachment://qrcode.png")
                    embed.add_field(name="📌 Código Pix", value=f"```{pagamento.get('qrcode', 'Indisponível')}```", inline=False)
                    embed.set_footer(text="Você será creditado automaticamente após o pagamento.\nQualquer dúvida, chame o suporte.")

                    await interaction.response.send_message(embed=embed, file=file, ephemeral=True)

                except Exception as e:
                    print(f"[ERRO] Erro ao gerar pagamento: {e}")
                    await interaction.response.send_message("Erro ao processar pagamento!", ephemeral=True)

        await interaction.response.send_modal(ModalRecarga())

class Carregar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("[COG] Carregar instanciado")
        self.bot.add_view(ComprarView())

    @commands.command(name="carregar")
    async def carregar(self, ctx):
        permissoes = COMMANDS_CONFIG.get("carregar", {}).get("allowed_roles", [])
        user_roles = [role.id for role in ctx.author.roles]

        if not any(role_id in permissoes for role_id in user_roles):
            await ctx.send("❌ Você não tem permissão para usar este comando.")
            return

        embed = discord.Embed(
            title="Loja de recarga",
            description="Olá! Seja bem-vindo à loja de recarga 😁",
            color=0x800080
        )
        embed.add_field(
            name=" ",
            value="[+] Caso precise de ajuda na sua compra, chame um membro do suporte.",
            inline=False
        )
        await ctx.send(embed=embed, view=ComprarView())

async def setup(bot):
    await bot.add_cog(Carregar(bot))
    print("[EXTENSAO] setup() de carregar.py EXECUTADO")
