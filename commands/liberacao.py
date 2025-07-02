import discord
from discord.ext import commands
from discord.ui import Modal, TextInput, View, Button
from config import COMMANDS_CONFIG, CARGOS, CANAIS
import pymysql

class LiberarAcessoModal(Modal, title="Nome do Personagem"):
    nome = TextInput(label="Nome do personagem", placeholder="Ex: João")
    sobrenome = TextInput(label="Sobrenome do personagem", placeholder="Ex: Silva")
    player_id = TextInput(label="ID", placeholder="Ex: 75")

    def __init__(self, member: discord.Member):
        super().__init__()
        self.member = member

    async def on_submit(self, interaction: discord.Interaction):
        nome = self.nome.value.strip().capitalize()
        sobrenome = self.sobrenome.value.strip().capitalize()
        player_id = self.player_id.value.strip()

        if not nome.isalpha() or not sobrenome.isalpha():
            await interaction.response.send_message("❌ Nome e sobrenome devem conter apenas letras.", ephemeral=True)
            return

        if not player_id.isdigit():
            await interaction.response.send_message("❌ O ID deve conter apenas números.", ephemeral=True)
            return

        char_id = None
        try:
            conn = pymysql.connect(
                host="localhost",
                user="discordbot",
                password="senha123",
                database="bewitched"
            )
            with conn.cursor() as cursor:
                cursor.execute("SELECT License, Whitelist FROM accounts WHERE id = %s", (player_id,))
                result = cursor.fetchone()
                if not result:
                    await interaction.response.send_message("❌ ID não encontrado na tabela de contas.", ephemeral=True)
                    conn.close()
                    return

                license, whitelist = result
                if whitelist == 1:
                    await interaction.response.send_message("⚠️ Esse ID já foi liberado!", ephemeral=True)
                    conn.close()
                    return

                cursor.execute("UPDATE accounts SET Whitelist = 1 WHERE id = %s", (player_id,))
                conn.commit()

                cursor.execute("SELECT id FROM characters WHERE License = %s", (license,))
                char_result = cursor.fetchone()
                if char_result:
                    char_id = char_result[0]

            conn.close()
        except Exception as e:
            print(f"[ERRO BANCO] {e}")
            await interaction.response.send_message("❌ Erro ao acessar o banco de dados.", ephemeral=True)
            return

        nome_completo = f"{nome} {sobrenome}"
        if char_id:
            nome_completo = f"{nome_completo} - {char_id}"
        if len(nome_completo) > 32:
            nome_completo = nome_completo[:29] + "..."

        try:
            await self.member.edit(nick=nome_completo)
        except Exception as e:
            print(f"[ERRO] Falha ao alterar nome: {e}")

        try:
            visitante = discord.Object(id=CARGOS["VISITANTE"])
            morador = discord.Object(id=CARGOS["MORADOR"])
            await self.member.remove_roles(visitante)
            await self.member.add_roles(morador)
        except Exception as e:
            print(f"[ERRO] Falha ao alterar cargos: {e}")

        await interaction.response.send_message("✅ Liberação registrada com sucesso!", ephemeral=True)

class LiberarButtonView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Liberar Acesso", style=discord.ButtonStyle.success, custom_id="botao_liberar_acesso")
    async def liberar_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(LiberarAcessoModal(interaction.user))

class LiberacaoCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("[COG] Liberacao instanciado")

    @commands.command(name="liberação")
    async def liberacao(self, ctx):
        if not await self.check_access(ctx.author):
            await ctx.send("❌ Você não tem permissão para usar este comando.")
            return

        canal_conexao = f"<#{CANAIS['CONECAO']}>" if "CONECAO" in CANAIS else "#conexao"

        embed = discord.Embed(
            title="📥 Liberando seu Acesso – New Zone RP",
            description=f"""1️⃣ Efetue a primeira conexão no servidor através do canal {canal_conexao}.
2️⃣ Seu **NÚMERO** aparecerá na mensagem no seu FIVEM.
3️⃣ Aperte no botão abaixo **Liberar Acesso** para poder fazer a liberação dele.
4️⃣ Aguarde o sistema efetuar a verificação do que foi enviado.""",
            color=discord.Color.green()
        )

        view = LiberarButtonView()
        await ctx.send(embed=embed, view=view)

    async def check_access(self, user) -> bool:
        roles_permitidas = COMMANDS_CONFIG.get("liberação", {}).get("allowed_roles", [])
        return any(role.id in roles_permitidas for role in user.roles)

async def setup(bot):
    await bot.add_cog(LiberacaoCommand(bot))
    bot.add_view(LiberarButtonView())
    print("[EXTENSAO] setup() de liberacao.py EXECUTADO")
