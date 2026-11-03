import os
import sys
import json
import asyncio
import urllib.request
from datetime import datetime
import discord
from discord import ui
from dotenv import load_dotenv

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
RIOT_KEY = os.getenv("RIOT_API_KEY")
GUILD_ID = 219177367296278538

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = True

client = discord.Client(intents=intents)

async def purge_and_send(channel, embeds, view=None):
    try:
        await channel.purge(limit=25)
    except Exception:
        pass
    first = None
    for i, emb in enumerate(embeds):
        v = view if (i == len(embeds) - 1) else None
        msg = await channel.send(embed=emb, view=v)
        if first is None:
            first = msg
        await asyncio.sleep(0.3)
    return first

# Dummy views para inicialização dos botões estáticos no chat
class LinkButtonView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @ui.button(label="🔗 Vincular Riot ID (LoL)", style=discord.ButtonStyle.primary, emoji="⚡", custom_id="btn_link_riot_id")
    async def link_riot(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_message("Painel de vinculação ativo no bot principal!", ephemeral=True)

class LaneSelectionView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @ui.button(label="Top", style=discord.ButtonStyle.secondary, emoji="🛡️", custom_id="btn_role_top")
    async def btn_top(self, interaction: discord.Interaction, button: ui.Button):
        pass
    @ui.button(label="Jungle", style=discord.ButtonStyle.secondary, emoji="🌲", custom_id="btn_role_jg")
    async def btn_jg(self, interaction: discord.Interaction, button: ui.Button):
        pass
    @ui.button(label="Mid", style=discord.ButtonStyle.secondary, emoji="🧙", custom_id="btn_role_mid")
    async def btn_mid(self, interaction: discord.Interaction, button: ui.Button):
        pass
    @ui.button(label="ADC", style=discord.ButtonStyle.secondary, emoji="🏹", custom_id="btn_role_adc")
    async def btn_adc(self, interaction: discord.Interaction, button: ui.Button):
        pass
    @ui.button(label="Suporte", style=discord.ButtonStyle.secondary, emoji="🩹", custom_id="btn_role_sup")
    async def btn_sup(self, interaction: discord.Interaction, button: ui.Button):
        pass
    @ui.button(label="Avisos de Scrims", style=discord.ButtonStyle.success, emoji="🔔", custom_id="btn_notif_scrims")
    async def btn_scrim(self, interaction: discord.Interaction, button: ui.Button):
        pass
    @ui.button(label="Busco Duo", style=discord.ButtonStyle.primary, emoji="🤝", custom_id="btn_notif_duo")
    async def btn_duo(self, interaction: discord.Interaction, button: ui.Button):
        pass

@client.event
async def on_ready():
    print(f"[OK] Conectado como {client.user}")
    guild = client.get_guild(GUILD_ID)
    if not guild:
        print("[ERRO] Guild não encontrada!")
        await client.close()
        return

    channels = {ch.name: ch for ch in guild.text_channels}

    # 1. #📜・regras-da-casa
    ch_regras = channels.get("📜・regras-da-casa")
    if ch_regras:
        emb_regras = discord.Embed(
            title="📜 DIRETRIZES & CÓDIGO DE CONDUTA • NICEPENTA E-SPORTS",
            description=(
                "Seja bem-vindo ao servidor oficial da organização **NICEPENTA E-SPORTS**!\n"
                "Aqui reunimos jogadores casuais e competitivos de **League of Legends** focados em evolução mecânica, "
                "scrims de alto rendimento e formação de duos/times para o Clash e torneios amadores."
            ),
            color=discord.Color.from_rgb(231, 76, 60),
            timestamp=datetime.now()
        )
        emb_regras.add_field(
            name="1️⃣ Respeito & Anti-Toxicidade",
            value="Rage excessivo, ofensas discriminatórias, assédio ou xingamentos em canais de texto ou calls resultarão em advertência e timeout imediato. Espírito esportivo em primeiro lugar.",
            inline=False
        )
        emb_regras.add_field(
            name="2️⃣ Classificação Obrigatória (Riot ID)",
            value="Para liberar os canais de busca de duo e salas de voz, vincule sua conta oficial de LoL no canal `🔗・vincular-conta-lol`. O bot atribuirá seu cargo de Elo automaticamente.",
            inline=False
        )
        emb_regras.add_field(
            name="3️⃣ Compromisso em Scrims e Treinos",
            value="Respeite os horários marcados de treinos contra equipes parceiras. Desistências de última hora sem aviso prévio acarretam perda de vaga na lineup.",
            inline=False
        )
        emb_regras.set_footer(text="NicePenta E-Sports • Fair Play & Foco no Desafiante")
        await purge_and_send(ch_regras, [emb_regras])

    # 2. #🔗・vincular-conta-lol
    ch_vincular = channels.get("🔗・vincular-conta-lol")
    if ch_vincular:
        emb_vincular = discord.Embed(
            title="⚡ VINCULAÇÃO DE CONTA RIOT GAMES (LEAGUE OF LEGENDS)",
            description=(
                "Conecte sua conta do LoL para ser classificado automaticamente pelo nosso bot oficial!\n\n"
                "**Como funciona:**\n"
                "1. Clique no botão azul **'🔗 Vincular Riot ID (LoL)'** abaixo.\n"
                "2. Digite seu **Riot ID oficial** no formato `Nome#TAG` (Ex: `Faker#BR1`, `Morphel#123`).\n"
                "3. O bot consulta a API da Riot Games em tempo real, valida seu nível, ícone e liga ranqueada (Solo/Duo ou Flex).\n"
                "4. Seu cargo de Elo (`Ferro` até `Desafiante`) e o cargo `VERIFICADO` serão aplicados instantaneamente!"
            ),
            color=discord.Color.from_rgb(52, 152, 219)
        )
        emb_vincular.add_field(
            name="🛡️ Segurança",
            value="Nós **NUNCA** pedimos sua senha. A validação é feita exclusivamente por dados públicos via API oficial da Riot Games.",
            inline=False
        )
        emb_vincular.set_footer(text="Powered by Riot Games API BR1 • NicePenta Bot")
        view_link = LinkButtonView()
        await purge_and_send(ch_vincular, [emb_vincular], view=view_link)

    # 3. #🎭・escolha-de-rotas
    ch_rotas = channels.get("🎭・escolha-de-rotas")
    if ch_rotas:
        emb_rotas = discord.Embed(
            title="🎭 SELEÇÃO DE ROTAS (LANES) & NOTIFICAÇÕES",
            description=(
                "Selecione as posições que você joga em Summoner's Rift para facilitar a montagem de grupos e duos!\n\n"
                "Basta clicar nos botões abaixo para **adicionar ou remover** os cargos correspondentes:"
            ),
            color=discord.Color.from_rgb(155, 89, 182)
        )
        emb_rotas.add_field(
            name="🛡️ Rotas do Mapa",
            value="`Top` • `Jungle` • `Mid` • `ADC` • `Suporte`",
            inline=True
        )
        emb_rotas.add_field(
            name="🔔 Notificações Especiais",
            value="• **Avisos de Scrims:** Seja alertado quando faltar vaga em treinos do time.\n• **Busco Duo:** Receba alertas de membros procurando duo no seu elo.",
            inline=False
        )
        view_lanes = LaneSelectionView()
        await purge_and_send(ch_rotas, [emb_rotas], view=view_lanes)

    # 4. #📊・patch-notes-e-meta
    ch_patch = channels.get("📊・patch-notes-e-meta")
    if ch_patch:
        emb_patch = discord.Embed(
            title="📊 CENTRAL DE PATCH NOTES & META ATUAL • LEAGUE OF LEGENDS",
            description=(
                "Painel atualizado dinamicamente via **Riot Games CDN (Data Dragon)** com as últimas informações do balanceamento oficial."
            ),
            color=discord.Color.from_rgb(46, 204, 113),
            timestamp=datetime.now()
        )
        emb_patch.add_field(
            name="⚡ Patch em Vigor",
            value="**League of Legends 16.21.1** (Servidor BR1 🟢 Online)",
            inline=False
        )
        emb_patch.add_field(
            name="🔥 Campeões Tier S+ no Meta Atual (SoloQ)",
            value=(
                "• **Top:** Aatrox, Fiora, Camille, Jax\n"
                "• **Jungle:** Viego, Lee Sin, Jarvan IV, Kayn\n"
                "• **Mid:** Ahri, Sylas, Yone, Orianna\n"
                "• **ADC:** Kai'Sa, Jinx, Jhin, Ezreal\n"
                "• **Suporte:** Thresh, Nautilus, Lulu, Nami"
            ),
            inline=False
        )
        emb_patch.add_field(
            name="📌 Links Úteis do Meta",
            value=(
                "• [Notas Oficiais do Patch no Portal da Riot](https://www.leagueoflegends.com/pt-br/news/game-updates/)\n"
                "• [Tier List & Estatísticas Globais (OP.GG)](https://www.op.gg/statistics/champions)\n"
                "• [Builds e Runas Recomendadas (U.GG)](https://u.gg/lol/tier-list)"
            ),
            inline=False
        )
        emb_patch.set_footer(text="Atualizado continuamente pelo HBCRIATE Bot")
        await purge_and_send(ch_patch, [emb_patch])

    # 5. #⭐・lineup-nicepenta
    ch_lineup = channels.get("⭐・lineup-nicepenta")
    if ch_lineup:
        emb_lineup = discord.Embed(
            title="⭐ ROSTER OFICIAL • TIME COMPETITIVO NICEPENTA",
            description=(
                "Conheça a escalação oficial da organização para as disputas de campeonatos amadores, ligas comunitárias e Clash:"
            ),
            color=discord.Color.from_rgb(241, 196, 15)
        )
        emb_lineup.add_field(name="🛡️ Top Laner", value="*Em Seletiva / Treinos*", inline=True)
        emb_lineup.add_field(name="🌲 Jungler", value="*Em Seletiva / Treinos*", inline=True)
        emb_lineup.add_field(name="🧙 Mid Laner", value="*Em Seletiva / Treinos*", inline=True)
        emb_lineup.add_field(name="🏹 Bot Laner (ADC)", value="*Em Seletiva / Treinos*", inline=True)
        emb_lineup.add_field(name="🩹 Suporte", value="*Em Seletiva / Treinos*", inline=True)
        emb_lineup.add_field(name="🧠 Comissão Técnica", value="Coach & Analista: `Staff NicePenta`", inline=False)
        emb_lineup.set_footer(text="NicePenta E-Sports • Rumo ao Circuito Desafiante")
        await purge_and_send(ch_lineup, [emb_lineup])

    # 6. #🏆・partidas-e-scrims
    ch_scrims = channels.get("🏆・partidas-e-scrims")
    if ch_scrims:
        emb_scrims = discord.Embed(
            title="🏆 FEED AUTOMÁTICO DE PARTIDAS & SCRIMS",
            description=(
                "Este canal monitora e registra **automaticamente** as partidas em grupo dos membros da comunidade!\n\n"
                "### 📡 Como funciona o Radar do Bot:\n"
                "1. Quando 2 ou mais membros verificados entram juntos em uma **Sala de Voz** (Duo ou Flex) e entram em partida no LoL, o bot detecta o jogo ao vivo via `Spectator-V5`.\n"
                "2. Ao final da partida, o bot consulta a API `Match-V5` da Riot Games e publica aqui o resumo completo:\n"
                "   • Resultado (Vitória 🏆 / Derrota 💀)\n"
                "   • KDA individual, dano causado e farm (CS/min)\n"
                "   • Destaque do **MVP da Partida** e tempo de jogo!\n\n"
                "🎮 *Basta vincular seu Riot ID e jogar nas nossas salas de voz!*"
            ),
            color=discord.Color.from_rgb(41, 128, 185)
        )
        await purge_and_send(ch_scrims, [emb_scrims])

    print("\n[SUCESSO COMPLETO] Todos os canais de League of Legends foram preenchidos!")
    await client.close()

if __name__ == "__main__":
    client.run(TOKEN)
