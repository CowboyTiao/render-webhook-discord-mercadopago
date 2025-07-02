import discord
from discord.ext import commands
from discord.ui import View, Select
from config import CARGOS
import random
import string
from PIL import Image, ImageDraw, ImageFont
import io

class CaptchaSelect(discord.ui.Select):
    def __init__(self, correct_code, member):
        self.correct_code = correct_code
        self.member = member
        options = [
            discord.SelectOption(label=correct_code)
        ] + [
            discord.SelectOption(label=''.join(random.choices(string.ascii_uppercase + string.digits, k=6)))
            for _ in range(4)
        ]
        random.shuffle(options)
        super().__init__(placeholder="Selecione o código correto", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        print(f"[INTERACTION] Select callback ativado por {interaction.user}")
        if interaction.user != self.member:
            await interaction.response.send_message("Esse CAPTCHA não é pra você.", ephemeral=True)
            return

        selected = self.values[0]
        if selected == self.correct_code:
            await self.member.add_roles(discord.Object(id=CARGOS["LIBERACAO"]))
            await self.member.remove_roles(discord.Object(id=CARGOS['VISITANTE']))
            await interaction.response.send_message("✅ Verificação concluída com sucesso!", ephemeral=True)
            print(f"[CAPTCHA] {self.member} passou no CAPTCHA e recebeu o cargo LIBERACAO.")
        else:
            await interaction.response.send_message("❌ Código incorreto. Tente novamente.", ephemeral=True)
            print(f"[CAPTCHA] {self.member} errou o CAPTCHA. Código correto era {self.correct_code}.")

class CaptchaView(View):
    def __init__(self, code, member):
        super().__init__(timeout=60)
        self.add_item(CaptchaSelect(code, member))

class CaptchaCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("[COG] Captcha instanciado")

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        try:
            if interaction.type == discord.InteractionType.component:
                print(f"[INTERACTION] Botão clicado: {interaction.data.get('custom_id')} por {interaction.user}")

                if interaction.data.get("custom_id") == "verificar_inicio":
                    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
                    try:
                        image = self.generate_realistic_captcha(code)
                        with io.BytesIO() as image_binary:
                            image.save(image_binary, 'PNG')
                            image_binary.seek(0)
                            file = discord.File(fp=image_binary, filename="captcha.png")
                            embed = discord.Embed(
                                title="🧩 Verificação CAPTCHA",
                                description="Selecione o código correspondente à imagem abaixo:",
                                color=discord.Color.green()
                            )
                            embed.set_image(url="attachment://captcha.png")
                            await interaction.response.send_message(
                                embed=embed,
                                file=file,
                                view=CaptchaView(code, interaction.user),
                                ephemeral=True
                            )
                            print(f"[CAPTCHA] Imagem enviada para {interaction.user}")
                    except Exception as e:
                        print(f"[ERRO] Erro ao gerar ou enviar CAPTCHA: {e}")
                        await interaction.response.send_message(
                            "❌ Erro ao gerar o CAPTCHA. Tente novamente mais tarde.",
                            ephemeral=True
                        )

                elif interaction.data.get("custom_id") == "verificar_info":
                    embed = discord.Embed(
                        title="🔐 Por que verificar a conta?",
                        description=(
                            "A verificação de conta é para prevenir que contas indesejadas entrem em nosso servidor como contas que praticam MASS DM, golpes e afins. "
                            "Assim deixando uma comunidade mais segura e sem SPAM desnecessários em sua DM.\n\n"
                            "Contas com nomes suspeitos, vindo de supostas atitudes suspeitas são removidas do servidor automaticamente, "
                            "além de contas recentes serem verificadas históricos de discords suspeitos para avaliar se é passível de kick ou ban."
                        ),
                        color=discord.Color.orange()
                    )
                    await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            print(f"[ERRO] Interação falhou: {e}")

    def generate_realistic_captcha(self, code):
        width, height = 300, 100
        background_color = (230, 230, 230)
        text_color = (40, 40, 40)
        line_color = (150, 150, 150)

        image = Image.new("RGB", (width, height), background_color)
        draw = ImageDraw.Draw(image)

        try:
            font = ImageFont.truetype("DejaVuSans-Bold.ttf", 44)
        except:
            font = ImageFont.load_default()

        for _ in range(6):
            start = (random.randint(0, width), random.randint(0, height))
            end = (random.randint(0, width), random.randint(0, height))
            draw.line([start, end], fill=line_color, width=2)

        spacing = 8
        total_width = sum([font.getbbox(c)[2] for c in code]) + spacing * (len(code) - 1)
        x = (width - total_width) // 2
        y = (height - font.getbbox(code[0])[3]) // 2

        for char in code:
            draw.text((x, y), char, font=font, fill=text_color)
            x += font.getbbox(char)[2] + spacing

        return image

async def setup(bot):
    await bot.add_cog(CaptchaCommand(bot))
    print("[EXTENSAO] setup() de verificar_captcha.py EXECUTADO")
