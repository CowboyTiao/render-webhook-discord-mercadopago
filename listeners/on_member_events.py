from discord.ext import commands
from discord import Embed, Member, AuditLogAction
from config import CANAIS, CARGOS, GUILD_ID
from datetime import datetime
import asyncio

TEMPO_LIMITE_VERIFICACAO_MIN = 10

class MemberEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("[COG] MemberEvents instanciado")

    @commands.Cog.listener()
    async def on_member_join(self, member: Member):
        if member.guild.id != GUILD_ID:
            return

        canal_alfandega = member.guild.get_channel(CANAIS["ALFANDEGA"])
        dias_conta = (datetime.now(tz=member.created_at.tzinfo) - member.created_at).days

        if dias_conta < 3:
            try:
                if canal_alfandega:
                    embed = Embed(
                        title="⚠️ Conta Removida por ser Recente",
                        description=f"{member.mention} (`{member.id}`) foi removido automaticamente.",
                        color=0xE67E22
                    )
                    embed.add_field(name="Conta criada", value=member.created_at.strftime('%d/%m/%Y às %H:%M'))
                    await canal_alfandega.send(embed=embed)
            except Exception as e:
                print(f"[ERRO] Falha ao logar conta recente: {e}")
            await member.kick(reason="Conta criada há menos de 3 dias")
            return

        nome_suspeito = any(p in member.name.lower() for p in [
            "porn", "xxx", "sex", "suporte", "promo", "nitro", "discord",
            "giveaway", "steam", "robux", "vbucks", "paypal", "free", "grátis"
        ])
        if nome_suspeito:
            try:
                if canal_alfandega:
                    embed = Embed(
                        title="⚠️ Nome suspeito detectado",
                        description=f"{member.mention} (`{member.id}`) entrou com um nome possivelmente malicioso.",
                        color=0xF1C40F
                    )
                    embed.add_field(name="Username", value=member.name, inline=True)
                    embed.set_thumbnail(url=member.display_avatar.url)
                    await canal_alfandega.send(embed=embed)
            except Exception as e:
                print(f"[ERRO] Falha ao logar nome suspeito: {e}")

        visitante_role = member.guild.get_role(CARGOS["VISITANTE"])
        if visitante_role and visitante_role not in member.roles:
            try:
                await member.add_roles(visitante_role, reason="Entrada automática no servidor")
                print(f"[JOIN] Cargo VISITANTE atribuído a {member.name}")
            except Exception as e:
                print(f"[ERRO] Falha ao aplicar cargo VISITANTE: {e}")

        try:
            if canal_alfandega:
                embed = Embed(
                    title=f"🟢 {member.name} entrou no servidor!",
                    color=0x2ECC71
                )
                embed.set_thumbnail(url=member.display_avatar.url)
                embed.add_field(name="🪪 Username", value=f"`{member}`", inline=True)
                embed.add_field(name="🆔 ID", value=f"`{member.id}`", inline=True)
                embed.add_field(
                    name="⏳ Conta Criada",
                    value=f"{member.created_at.strftime('%d/%m/%Y às %H:%M')} (há {dias_conta} dias)",
                    inline=False
                )
                embed.add_field(
                    name="📅 Entrada no Servidor",
                    value=f"{datetime.now(tz=member.created_at.tzinfo).strftime('%d/%m/%Y às %H:%M')}",
                    inline=False
                )
                embed.set_footer(text=f"{len(member.guild.members)} membros agora no servidor.")
                await canal_alfandega.send(embed=embed)
        except Exception as e:
            print(f"[ERRO] Falha ao enviar embed de entrada: {e}")

        await self.verificar_timeout(member)

    async def verificar_timeout(self, member: Member):
        await asyncio.sleep(TEMPO_LIMITE_VERIFICACAO_MIN * 60)
        role_verificacao = member.guild.get_role(CARGOS["LIBERACAO"])
        if role_verificacao not in member.roles:
            try:
                await member.kick(reason="BOT_AUTO_KICK_VERIFICACAO")
                print(f"[KICK] {member.name} foi expulso por inatividade na verificação.")
            except Exception as e:
                print(f"[ERRO] Falha ao expulsar {member.name}: {e}")

    @commands.Cog.listener()
    async def on_member_remove(self, member: Member):
        canal = member.guild.get_channel(CANAIS["ALFANDEGA"])
        if not canal:
            return

        expulsor = None
        motivo = "Usuário saiu do servidor."

        async for entry in member.guild.audit_logs(limit=5, action=AuditLogAction.kick):
            if entry.target.id == member.id:
                expulsor = entry.user
                if expulsor.id == self.bot.user.id:
                    motivo = "Usuário foi expulso automaticamente por não se verificar."
                else:
                    motivo = "Usuário foi expulso manualmente."
                break

        embed = Embed(
            title=f"🔴 {member.name} saiu do servidor!",
            color=0xE74C3C
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="🪪 Username", value=f"`{member}`", inline=True)
        embed.add_field(name="🆔 ID", value=f"`{member.id}`", inline=True)
        embed.add_field(
            name="⏳ Conta Criada",
            value=member.created_at.strftime('%d/%m/%Y às %H:%M'),
            inline=False
        )
        embed.add_field(
            name="📅 Registro de Saída",
            value=datetime.now().strftime('%d/%m/%Y às %H:%M'),
            inline=False
        )
        embed.add_field(
            name="📌 Motivo",
            value=motivo,
            inline=False
        )

        if expulsor and expulsor.id != self.bot.user.id:
            embed.add_field(name="👮 Expulsor", value=f"{expulsor.mention} (`{expulsor}`)", inline=False)

        embed.set_footer(text=f"{len(member.guild.members)} membros restantes no servidor.")

        try:
            await canal.send(embed=embed)
        except Exception as e:
            print(f"[ERRO] Falha ao logar saída de {member.name}: {e}")

async def setup(bot):
    print("[EXTENSAO] setup() de on_member_events.py EXECUTADO")
    await bot.add_cog(MemberEvents(bot))
