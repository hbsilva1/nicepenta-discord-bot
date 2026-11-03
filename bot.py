import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import time
import json
import re
import random
import socket
import asyncio
import urllib.request
import urllib.parse
from datetime import datetime
import discord
from discord.ext import commands, tasks
from discord import ui, app_commands
from aiohttp import web
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
APP_ID = os.getenv("APPLICATION_ID", "1565065775100727346")
RIOT_KEY = os.getenv("RIOT_API_KEY")

SERVER_IP = "138.121.165.67"
PORT_SITE = 8088
PORT_GAME_LOGIN = 7171
PORT_GAME_WORLD = 7172

GUILD_NICEPENTA = 219177367296278538
GUILD_POKEMON = 619500240189390858

DB_FILE = os.path.join(os.path.dirname(__file__), "players_db.json")
SYNERGY_FILE = os.path.join(os.path.dirname(__file__), "synergy_db.json")
CHAMPS_CACHE_FILE = os.path.join(os.path.dirname(__file__), "champions_cache.json")

# Helpers de Banco de Dados
def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_db(data):
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Erro ao salvar DB: {e}")

def load_synergy():
    if os.path.exists(SYNERGY_FILE):
        try:
            with open(SYNERGY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_synergy(data):
    try:
        with open(SYNERGY_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Erro ao salvar synergy: {e}")

def record_synergy(discord_ids, win: bool):
    if len(discord_ids) < 2:
        return None
    db = load_synergy()
    key = "_".join(sorted(str(i) for i in discord_ids))
    if key not in db:
        db[key] = {"wins": 0, "losses": 0}
    if win:
        db[key]["wins"] += 1
    else:
        db[key]["losses"] += 1
    save_synergy(db)
    
    total = db[key]["wins"] + db[key]["losses"]
    wr = round((db[key]["wins"] / total) * 100, 1) if total > 0 else 0
    return db[key]["wins"], db[key]["losses"], wr, total

def get_champion_info(champ_id_or_key):
    if os.path.exists(CHAMPS_CACHE_FILE):
        try:
            with open(CHAMPS_CACHE_FILE, "r", encoding="utf-8") as f:
                cache = json.load(f)
                champs = cache.get("champions", {})
                str_key = str(champ_id_or_key)
                if str_key in champs:
                    return champs[str_key]
                # Busca por nome/id textual
                for k, v in champs.items():
                    if v.get("id", "").lower() == str_key.lower() or v.get("name", "").lower() == str_key.lower():
                        return v
        except Exception:
            pass
    return {
        "id": str(champ_id_or_key),
        "name": str(champ_id_or_key),
        "title": "Campeão",
        "tags": ["Fighter"],
        "icon": f"https://ddragon.leagueoflegends.com/cdn/16.21.1/img/champion/{champ_id_or_key}.png"
    }

# Helper de requisição à Riot API com User-Agent obrigatório
def riot_api_request(url):
    if not RIOT_KEY:
        return None, 401
    req = urllib.request.Request(url, headers={
        "X-Riot-Token": RIOT_KEY,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) NicePentaBot/3.0"
    })
    try:
        with urllib.request.urlopen(req, timeout=9) as resp:
            body = resp.read().decode('utf-8')
            return json.loads(body), resp.status
    except urllib.error.HTTPError as e:
        return None, e.code
    except Exception as e:
        return None, 0

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

temp_voice_channels = set()
active_live_alerts = set() # Evitar repetição de alertas de partida ao vivo

ELO_MAPPING = {
    "CHALLENGER": "DESAFIANTE",
    "GRANDMASTER": "GRÃO-MESTRE",
    "MASTER": "MESTRE",
    "DIAMOND": "DIAMANTE",
    "EMERALD": "ESMERALDA",
    "PLATINUM": "PLATINA",
    "GOLD": "OURO",
    "SILVER": "PRATA",
    "BRONZE": "BRONZE",
    "IRON": "FERRO"
}

ELO_ORDER = {
    "CHALLENGER": 10,
    "GRANDMASTER": 9,
    "MASTER": 8,
    "DIAMOND": 7,
    "EMERALD": 6,
    "PLATINUM": 5,
    "GOLD": 4,
    "SILVER": 3,
    "BRONZE": 2,
    "IRON": 1,
    "UNRANKED": 0
}

QUEUE_NAMES = {
    420: "Ranqueada Solo/Duo",
    440: "Ranqueada Flex 5v5",
    450: "ARAM (Howling Abyss)",
    400: "Normal Alternada (Draft)",
    430: "Normal Escolha às Cegas",
    490: "Partida Rápida (Quickplay)",
    700: "Clash Competitivo",
    1700: "Arena (2v2v2v2)",
    1900: "URF (Ultra Rápido e Furioso)",
    1300: "Nexus Blitz",
    1400: "Ultimate Spellbook"
}

def format_elo_nick(current_name: str, tier: str, rank: str) -> str:
    tags = {
        'CHALLENGER': '👑 [CHALLENGER]',
        'GRANDMASTER': '🔴 [GM]',
        'MASTER': '🟣 [MESTRE]',
        'DIAMOND': f'💎 [D{rank}]' if rank else '💎 [DIAMANTE]',
        'EMERALD': f'🟢 [E{rank}]' if rank else '🟢 [ESMERALDA]',
        'PLATINUM': f'💠 [P{rank}]' if rank else '💠 [PLATINA]',
        'GOLD': f'🟡 [G{rank}]' if rank else '🟡 [OURO]',
        'SILVER': f'⚪ [S{rank}]' if rank else '⚪ [PRATA]',
        'BRONZE': f'🟤 [B{rank}]' if rank else '🟤 [BRONZE]',
        'IRON': f'⚫ [F{rank}]' if rank else '⚫ [FERRO]',
        'UNRANKED': '⚪ [UNRANKED]'
    }
    tag = tags.get(tier.upper(), '⚪ [UNRANKED]')
    clean_name = re.sub(r'^[^\w\s]*\[[^\]]+\]\s*', '', current_name).strip()
    new_nick = f"{tag} {clean_name}"
    if len(new_nick) > 32:
        max_base = 32 - len(tag) - 1
        new_nick = f"{tag} {clean_name[:max_base]}"
    return new_nick


# =========================================================================
# 1. MODAL E VIEWS DE VINCULAÇÃO E ROTAS (100% PÚBLICOS NO DISCORD)
# =========================================================================

class RiotLinkModal(ui.Modal, title="Vincular Conta Oficial da Riot Games"):
    riot_id_input = ui.TextInput(
        label="Digite seu Riot ID completo (Nome#TAG)",
        placeholder="Exemplo: MorphelJpa#morph ou Faker#KR1",
        required=True,
        min_length=3,
        max_length=40
    )

    async def on_submit(self, interaction: discord.Interaction):
        # RESPOSTA PÚBLICA: Todos no servidor devem ver a vinculação!
        await interaction.response.defer(ephemeral=False)
        raw_id = self.riot_id_input.value.strip()

        if "#" not in raw_id:
            await interaction.followup.send(
                f"❌ **Formato inválido:** `{raw_id}`. É obrigatório incluir o nome e a TAG com `#` (Ex: `Nome#BR1`)."
            )
            return

        game_name, tag_line = raw_id.split("#", 1)
        safe_name = urllib.parse.quote(game_name.strip())
        safe_tag = urllib.parse.quote(tag_line.strip())

        url_acc = f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{safe_name}/{safe_tag}"
        acc_data, status_acc = riot_api_request(url_acc)

        if status_acc == 404 or not acc_data:
            await interaction.followup.send(
                f"❌ **Conta não encontrada na Riot Games:** `{raw_id}`.\nVerifique se digitou o nome e a TAG exatamente como aparecem no LoL."
            )
            return
        elif status_acc != 200:
            await interaction.followup.send(
                f"⚠️ Erro ao consultar a Riot API (Status HTTP {status_acc}). Tente novamente em instantes."
            )
            return

        puuid = acc_data.get("puuid")
        official_name = acc_data.get("gameName")
        official_tag = acc_data.get("tagLine")

        url_summ = f"https://br1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}"
        summ_data, _ = riot_api_request(url_summ)
        level = summ_data.get("summonerLevel", 1) if summ_data else 1
        icon_id = summ_data.get("profileIconId", 29) if summ_data else 29

        url_league = f"https://br1.api.riotgames.com/lol/league/v4/entries/by-puuid/{puuid}"
        league_data, _ = riot_api_request(url_league)

        tier = "UNRANKED"
        rank = ""
        lp = 0
        wins = 0
        losses = 0
        queue_name = "Sem Classificação"

        if league_data and isinstance(league_data, list):
            solo_entry = next((e for e in league_data if e.get("queueType") == "RANKED_SOLO_5x5"), None)
            flex_entry = next((e for e in league_data if e.get("queueType") == "RANKED_FLEX_SR"), None)
            entry = solo_entry or flex_entry or (league_data[0] if league_data else None)

            if entry:
                tier = entry.get("tier", "UNRANKED").upper()
                rank = entry.get("rank", "")
                lp = entry.get("leaguePoints", 0)
                wins = entry.get("wins", 0)
                losses = entry.get("losses", 0)
                queue_name = "Ranqueada Solo/Duo" if entry.get("queueType") == "RANKED_SOLO_5x5" else "Ranqueada Flex"

        guild = interaction.guild
        member = interaction.user
        role_to_add_name = ELO_MAPPING.get(tier, "UNRANKED")

        # Remover cargos antigos de elo
        roles_to_remove = [r for r in member.roles if r.name in ELO_MAPPING.values() or r.name == "UNRANKED"]
        if roles_to_remove:
            try:
                await member.remove_roles(*roles_to_remove, reason="Atualização de Elo LoL")
            except Exception:
                pass

        target_role = discord.utils.get(guild.roles, name=role_to_add_name)
        verified_role = discord.utils.get(guild.roles, name="VERIFICADO (LOL)")

        roles_to_grant = []
        if target_role and target_role not in member.roles:
            roles_to_grant.append(target_role)
        if verified_role and verified_role not in member.roles:
            roles_to_grant.append(verified_role)

        if roles_to_grant:
            try:
                await member.add_roles(*roles_to_grant, reason=f"Vinculação Riot ID: {official_name}#{official_tag}")
            except Exception as e:
                print(f"Erro ao adicionar cargos: {e}")

        # Atualizar apelido com símbolo de elo
        nick_updated = False
        new_nick = format_elo_nick(member.display_name, tier, rank)
        try:
            await member.edit(nick=new_nick, reason="Atualização automática de Símbolo de Elo no Nickname")
            nick_updated = True
        except discord.Forbidden:
            pass
        except Exception:
            pass

        # Salvar no Banco de Dados
        db = load_db()
        old_match_id = db.get(str(member.id), {}).get("last_match_id", "")
        db[str(member.id)] = {
            "riot_id": f"{official_name}#{official_tag}",
            "puuid": puuid,
            "tier": tier,
            "rank": rank,
            "lp": lp,
            "level": level,
            "icon_id": icon_id,
            "last_updated": datetime.now().isoformat(),
            "last_match_id": old_match_id
        }
        save_db(db)

        total_games = wins + losses
        winrate = round((wins / total_games) * 100, 1) if total_games > 0 else 0
        icon_url = f"https://ddragon.leagueoflegends.com/cdn/16.21.1/img/profileicon/{icon_id}.png"

        # EMBED PÚBLICO DE CONFIRMAÇÃO
        embed = discord.Embed(
            title="🌟 CONTA VINCULADA & ELO IDENTIFICADO!",
            description=f"O membro {member.mention} autenticou sua conta oficial da Riot Games no **NICEPENTA E-SPORTS**!",
            color=discord.Color.from_rgb(46, 204, 113),
            timestamp=datetime.now()
        )
        embed.set_thumbnail(url=icon_url)
        embed.add_field(name="👤 Invocador", value=f"`{official_name}#{official_tag}`", inline=True)
        embed.add_field(name="⭐ Nível", value=f"`Nv. {level}`", inline=True)
        embed.add_field(name="🎖️ Elo Concedido", value=f"**{role_to_add_name} {rank}** (`{lp} PDL`)", inline=True)
        embed.add_field(
            name="📊 Desempenho Ranqueado",
            value=f"• **Fila:** {queue_name}\n• **Vitórias:** `{wins}` | **Derrotas:** `{losses}`\n• **Winrate:** `{winrate}%`",
            inline=False
        )
        if nick_updated:
            embed.add_field(name="🏷️ Apelido Atualizado", value=f"`{new_nick}`", inline=False)
        embed.set_footer(text="Conta Verificada • NicePenta E-Sports Bot")

        # Envia a resposta pública diretamente no canal onde ele clicou!
        await interaction.followup.send(content=f"🎉 **BEM-VINDO AO NICEPENTA E-SPORTS:** {member.mention}", embed=embed)

        # Se clicou fora do chat geral, avisa no chat geral também!
        ch_geral = discord.utils.get(guild.text_channels, name="💬・chat-geral-lol")
        if ch_geral and interaction.channel.id != ch_geral.id:
            try:
                await ch_geral.send(content=f"🎉 **NOVO INVOCADOR REGISTRADO:** {member.mention}", embed=embed)
            except Exception:
                pass


class PersistentRiotLinkView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="⚡ Vincular Riot ID (LoL)", style=discord.ButtonStyle.primary, emoji="🔗", custom_id="btn_link_riot_id")
    async def link_riot(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(RiotLinkModal())

    @ui.button(label="🔄 Atualizar Elo & Dados", style=discord.ButtonStyle.secondary, emoji="📊", custom_id="btn_update_riot_data")
    async def update_riot_data(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.defer(ephemeral=False)
        db = load_db()
        p_info = db.get(str(interaction.user.id))
        if not p_info:
            await interaction.followup.send(f"⚠️ {interaction.user.mention}, você ainda não possui uma conta vinculada! Clique em **⚡ Vincular Riot ID (LoL)** primeiro.")
            return

        puuid = p_info.get("puuid")
        url_league = f"https://br1.api.riotgames.com/lol/league/v4/entries/by-puuid/{puuid}"
        league_data, _ = riot_api_request(url_league)

        tier = "UNRANKED"
        rank = ""
        lp = 0
        wins = 0
        losses = 0
        if league_data and isinstance(league_data, list):
            entry = next((e for e in league_data if e.get("queueType") == "RANKED_SOLO_5x5"), league_data[0] if league_data else None)
            if entry:
                tier = entry.get("tier", "UNRANKED").upper()
                rank = entry.get("rank", "")
                lp = entry.get("leaguePoints", 0)
                wins = entry.get("wins", 0)
                losses = entry.get("losses", 0)

        db[str(interaction.user.id)]["tier"] = tier
        db[str(interaction.user.id)]["rank"] = rank
        db[str(interaction.user.id)]["lp"] = lp
        save_db(db)

        role_to_add = ELO_MAPPING.get(tier, "UNRANKED")
        target_role = discord.utils.get(interaction.guild.roles, name=role_to_add)
        roles_to_remove = [r for r in interaction.user.roles if r.name in ELO_MAPPING.values() or r.name == "UNRANKED"]
        if roles_to_remove:
            try:
                await interaction.user.remove_roles(*roles_to_remove)
            except Exception:
                pass
        if target_role:
            try:
                await interaction.user.add_roles(target_role)
            except Exception:
                pass

        new_nick = format_elo_nick(interaction.user.display_name, tier, rank)
        try:
            await interaction.user.edit(nick=new_nick)
        except Exception:
            pass

        await interaction.followup.send(
            f"✅ **DADOS ATUALIZADOS!** {interaction.user.mention} agora está classificado como **{role_to_add} {rank}** (`{lp} PDL`)!"
        )


class PersistentLaneSelectionView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def toggle_role(self, interaction: discord.Interaction, role_name: str, emoji: str):
        # AÇÃO 100% PÚBLICA: Todos no canal veem a escolha de rotas!
        guild = interaction.guild
        member = interaction.user
        role = discord.utils.get(guild.roles, name=role_name)
        if not role:
            await interaction.response.send_message(f"⚠️ Cargo `{role_name}` não encontrado.", ephemeral=True)
            return

        if role in member.roles:
            await member.remove_roles(role, reason="Remoção de rota")
            await interaction.response.send_message(
                f"🔴 {member.mention} **removeu** o cargo de rota: **{role_name}**.",
                ephemeral=False
            )
        else:
            await member.add_roles(role, reason="Definição de rota")
            await interaction.response.send_message(
                f"✅ {emoji} {member.mention} **definiu sua rota como {role_name}**! Pronto para duplas e scrims!",
                ephemeral=False
            )

    @ui.button(label="Top Laner", style=discord.ButtonStyle.secondary, emoji="🛡️", custom_id="btn_role_top")
    async def btn_top(self, interaction: discord.Interaction, button: ui.Button):
        await self.toggle_role(interaction, "🛡️ TOP LANER", "🛡️")

    @ui.button(label="Jungler", style=discord.ButtonStyle.secondary, emoji="🌲", custom_id="btn_role_jg")
    async def btn_jg(self, interaction: discord.Interaction, button: ui.Button):
        await self.toggle_role(interaction, "🌲 JUNGLER", "🌲")

    @ui.button(label="Mid Laner", style=discord.ButtonStyle.secondary, emoji="🧙", custom_id="btn_role_mid")
    async def btn_mid(self, interaction: discord.Interaction, button: ui.Button):
        await self.toggle_role(interaction, "🧙 MID LANER", "🧙")

    @ui.button(label="Bot Laner (ADC)", style=discord.ButtonStyle.secondary, emoji="🏹", custom_id="btn_role_adc")
    async def btn_adc(self, interaction: discord.Interaction, button: ui.Button):
        await self.toggle_role(interaction, "🏹 BOT LANER (ADC)", "🏹")

    @ui.button(label="Suporte", style=discord.ButtonStyle.secondary, emoji="🩹", custom_id="btn_role_sup")
    async def btn_sup(self, interaction: discord.Interaction, button: ui.Button):
        await self.toggle_role(interaction, "🩹 SUPORTE", "🩹")

    @ui.button(label="Avisos de Scrims", style=discord.ButtonStyle.success, emoji="🔔", custom_id="btn_notif_scrims")
    async def btn_scrim(self, interaction: discord.Interaction, button: ui.Button):
        await self.toggle_role(interaction, "NOTIFICAÇÃO DE SCRIMS", "🔔")

    @ui.button(label="Busco Duo", style=discord.ButtonStyle.primary, emoji="🤝", custom_id="btn_notif_duo")
    async def btn_duo(self, interaction: discord.Interaction, button: ui.Button):
        await self.toggle_role(interaction, "BUSCO DUO", "🤝")


# =========================================================================
# 2. PAINEL DE CONTROLE ADMINISTRATIVO
# =========================================================================

def test_connection(host, port, timeout=2.5):
    start = time.time()
    try:
        s = socket.create_connection((host, port), timeout=timeout)
        s.close()
        return True, int((time.time() - start) * 1000)
    except Exception:
        return False, 0

class AdminDashboardView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="Checar Servidor & Site", style=discord.ButtonStyle.success, emoji="🟢", custom_id="btn_check_status")
    async def check_status(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.defer(ephemeral=True)
        ok_site, lat_site = test_connection(SERVER_IP, PORT_SITE)
        ok_login, lat_login = test_connection(SERVER_IP, PORT_GAME_LOGIN)
        ok_world, lat_world = test_connection(SERVER_IP, PORT_GAME_WORLD)
        
        embed = discord.Embed(
            title="📡 DIAGNÓSTICO EM TEMPO REAL",
            color=discord.Color.green() if (ok_site and ok_login and ok_world) else discord.Color.orange(),
            timestamp=datetime.now()
        )
        embed.add_field(name="🌐 Website / AAC (8088)", value=f"{'🟢 ONLINE' if ok_site else '🔴 OFFLINE'} (`{lat_site}ms`)", inline=False)
        embed.add_field(name="🎮 Login Server (7171)", value=f"{'🟢 ONLINE' if ok_login else '🔴 OFFLINE'} (`{lat_login}ms`)", inline=True)
        embed.add_field(name="⚔️ Game World (7172)", value=f"{'🟢 ONLINE' if ok_world else '🔴 OFFLINE'} (`{lat_world}ms`)", inline=True)
        await interaction.followup.send(embed=embed, ephemeral=True)

    @ui.button(label="Multi-Servidor (Convidar)", style=discord.ButtonStyle.primary, emoji="🌐", custom_id="btn_multi_server")
    async def multi_server(self, interaction: discord.Interaction, button: ui.Button):
        invite_url = f"https://discord.com/oauth2/authorize?client_id={APP_ID}&permissions=8&scope=bot%20applications.commands"
        await interaction.response.send_message(f"👉 **[Link para Convidar o Bot para Outro Servidor]({invite_url})**", ephemeral=True)


async def setup_admin_panel(guild: discord.Guild):
    cat_admin = discord.utils.get(guild.categories, name="🛡️ ADMINISTRAÇÃO")
    if not cat_admin:
        overwrites_cat = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True)
        }
        if guild.owner:
            overwrites_cat[guild.owner] = discord.PermissionOverwrite(view_channel=True, send_messages=True)
        cat_admin = await guild.create_category(name="🛡️ ADMINISTRAÇÃO", overwrites=overwrites_cat)

    panel_ch = discord.utils.get(guild.text_channels, name="🔒-painel-controle")
    if not panel_ch:
        panel_ch = await guild.create_text_channel(
            name="🔒-painel-controle",
            category=cat_admin,
            topic="Painel Central de Controle Interativo"
        )

    try:
        await panel_ch.purge(limit=10)
    except Exception:
        pass

    dashboard_embed = discord.Embed(
        title=f"🎛️ PAINEL DE CONTROLE • {guild.name}",
        description="Centro de comando administrativo do servidor.",
        color=discord.Color.from_rgb(46, 204, 113),
        timestamp=datetime.now()
    )
    view = AdminDashboardView()
    await panel_ch.send(embed=dashboard_embed, view=view)


# =========================================================================
# 3. SALAS DE VOZ DINÂMICAS & BOAS-VINDAS
# =========================================================================

@bot.event
async def on_voice_state_update(member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
    if member.bot:
        return

    if after.channel is not None:
        ch_name = after.channel.name
        guild = after.channel.guild

        if "Criar Duo" in ch_name:
            cat = after.channel.category
            temp_ch = await guild.create_voice_channel(
                name=f"🎮 Duo de {member.display_name}",
                category=cat,
                user_limit=2,
                reason="Sala dinâmica Solo/Duo gerada automaticamente"
            )
            temp_voice_channels.add(temp_ch.id)
            try:
                await member.move_to(temp_ch)
            except Exception:
                pass

        elif "Criar Trio / Flex" in ch_name:
            cat = after.channel.category
            temp_ch = await guild.create_voice_channel(
                name=f"⚔️ Flex de {member.display_name}",
                category=cat,
                user_limit=5,
                reason="Sala dinâmica Flex 5v5 gerada automaticamente"
            )
            temp_voice_channels.add(temp_ch.id)
            try:
                await member.move_to(temp_ch)
            except Exception:
                pass

    if before.channel is not None and before.channel.id in temp_voice_channels:
        if len(before.channel.members) == 0:
            temp_voice_channels.remove(before.channel.id)
            try:
                await before.channel.delete(reason="Sala temporária vazia")
            except Exception:
                pass


@bot.event
async def on_member_join(member: discord.Member):
    if member.guild.id == GUILD_NICEPENTA:
        ch_vincular = discord.utils.get(member.guild.text_channels, name="🔗・vincular-conta-lol")
        ch_geral = discord.utils.get(member.guild.text_channels, name="💬・chat-geral-lol")
        if ch_geral:
            embed = discord.Embed(
                title="👋 NOVO INVOCADOR NA ÁREA!",
                description=(
                    f"Seja muito bem-vindo ao **NICEPENTA E-SPORTS**, {member.mention}!\n\n"
                    f"👉 **Primeiro Passo Obrigatório:** Acesse o canal {ch_vincular.mention if ch_vincular else '#vincular'} "
                    "e clique no botão para vincular seu **Riot ID** e receber seu cargo e símbolo de Elo automático!"
                ),
                color=discord.Color.blue()
            )
            await ch_geral.send(content=f"🔔 {member.mention}", embed=embed)


# =========================================================================
# 4. RADAR UNIVERSAL: PARTIDAS AO VIVO (ESPECTADOR) & MÉTRICAS CO-OP / DUO
# =========================================================================

@tasks.loop(seconds=30)
async def hybrid_match_radar():
    guild = bot.get_guild(GUILD_NICEPENTA)
    if not guild or not RIOT_KEY:
        return

    db = load_db()
    if not db:
        return

    ch_feed = discord.utils.get(guild.text_channels, name="🏆・partidas-e-scrims")
    ch_geral = discord.utils.get(guild.text_channels, name="💬・chat-geral-lol")
    if not ch_feed:
        return

    db_modified = False

    # 1. VERIFICAÇÃO DE PARTIDAS AO VIVO (ESPECTADOR EM TEMPO REAL)
    for discord_id, p_info in list(db.items()):
        puuid = p_info.get("puuid")
        if not puuid:
            continue

        url_spec = f"https://br1.api.riotgames.com/lol/spectator/v5/active-games/by-summoner/{puuid}"
        spec_data, status_s = riot_api_request(url_spec)

        if status_s == 200 and spec_data:
            game_id = str(spec_data.get("gameId"))
            if game_id not in active_live_alerts:
                active_live_alerts.add(game_id)
                key = spec_data.get("observers", {}).get("encryptionKey", "")
                q_id = spec_data.get("gameQueueConfigId", 0)
                m_name = QUEUE_NAMES.get(q_id, spec_data.get("gameMode", "Partida de LoL"))

                # Descobrir quais outros membros do servidor estão nessa mesma partida ao vivo!
                participants = spec_data.get("participants", [])
                puuid_to_discord = {data["puuid"]: d_id for d_id, data in db.items() if "puuid" in data}
                coop_members = [p for p in participants if p.get("puuid") in puuid_to_discord]

                spectate_cmd = f'"C:\\Riot Games\\League of Legends\\Game\\League of Legends.exe" "spectator spectator.br.lol.riotgames.com:80 {key} {game_id} BR1"'
                opgg_url = f"https://www.op.gg/summoners/br/{urllib.parse.quote(p_info.get('riot_id').replace('#', '-'))}/ingame"

                live_embed = discord.Embed(
                    title=f"🔴 PARTIDA AO VIVO DETECTADA • {m_name.upper()}",
                    description=(
                        f"⚡ Membros do NicePenta entraram nos Campos da Justiça!\n"
                        f"• **Modo:** `{m_name}` | **Game ID:** `{game_id}`\n\n"
                        f"👁️ **Como Assistir Direto pelo Client 3D do LoL:**\n"
                        f"Abra o Executar (`Win + R`) ou Prompt de Comando e cole:\n"
                        f"```cmd\n{spectate_cmd}\n```"
                    ),
                    color=discord.Color.red(),
                    timestamp=datetime.now()
                )
                live_embed.add_field(name="🌐 Assistir pelo Navegador", value=f"👉 **[Radar Ao Vivo no OP.GG]({opgg_url})**", inline=False)
                
                names_in_live = []
                for cp in coop_members:
                    c_info = get_champion_info(cp.get("championId"))
                    names_in_live.append(f"• <@{puuid_to_discord[cp['puuid']]}> como **{c_info.get('name')}**")
                live_embed.add_field(name="🎮 Jogadores do Servidor em Campo", value="\n".join(names_in_live) if names_in_live else f"• <@{discord_id}>", inline=False)
                live_embed.set_footer(text="NicePenta Live Spectator • 0 Latência")

                mentions = " ".join([f"<@{puuid_to_discord[cp['puuid']]}>" for cp in coop_members])
                await ch_feed.send(content=f"🔴 {mentions} **estão AO VIVO em jogo!**", embed=live_embed)

        await asyncio.sleep(0.5)

    # 2. VERIFICAÇÃO DE PARTIDAS FINALIZADAS (MATCH-V5 COM MÉTRICAS CO-OP)
    for discord_id, p_info in list(db.items()):
        puuid = p_info.get("puuid")
        if not puuid:
            continue

        url_recent = f"https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?count=1"
        match_ids, status_ids = riot_api_request(url_recent)

        if status_ids != 200 or not match_ids or not isinstance(match_ids, list):
            continue

        latest_match_id = match_ids[0]
        last_recorded = p_info.get("last_match_id", "")

        if latest_match_id != last_recorded:
            print(f"[RADAR] Partida finalizada detectada: {latest_match_id} (Invocador: {p_info.get('riot_id')})", flush=True)

            url_match = f"https://americas.api.riotgames.com/lol/match/v5/matches/{latest_match_id}"
            m_data, status_m = riot_api_request(url_match)

            if status_m != 200 or not m_data:
                db[discord_id]["last_match_id"] = latest_match_id
                db_modified = True
                continue

            info = m_data.get("info", {})
            queue_id = info.get("queueId", 0)
            mode_name = QUEUE_NAMES.get(queue_id, info.get("gameMode", "Partida de LoL"))
            duration_sec = info.get("gameDuration", 0)
            duration_min = round(duration_sec / 60, 1)
            participants = info.get("participants", [])

            # Mapear todos os membros verificados do servidor que estavam nessa partida
            puuid_to_discord = {data["puuid"]: d_id for d_id, data in db.items() if "puuid" in data}
            nicepenta_participants = [p for p in participants if p.get("puuid") in puuid_to_discord]

            # Marcar partida como processada para todos os participantes do servidor
            for np_p in nicepenta_participants:
                d_id = puuid_to_discord.get(np_p.get("puuid"))
                if d_id and d_id in db:
                    db[d_id]["last_match_id"] = latest_match_id
                    db_modified = True

            # CASO 1: DOIS OU MAIS MEMBROS JOGANDO JUNTOS (CO-OP / DUO / SQUAD)
            if len(nicepenta_participants) >= 2:
                teams_in_game = {p.get("teamId") for p in nicepenta_participants}

                if len(teams_in_game) == 1:
                    # MESMO TIME: DUO OU SQUAD COOPERATIVO
                    team_id = nicepenta_participants[0].get("teamId")
                    win = nicepenta_participants[0].get("win", False)
                    team_players = [p for p in participants if p.get("teamId") == team_id]

                    total_team_dmg = sum(p.get("totalDamageDealtToChampions", 0) for p in team_players)
                    total_team_kills = sum(p.get("kills", 0) for p in team_players)
                    total_team_gold = sum(p.get("goldEarned", 0) for p in team_players)

                    comb_dmg = sum(p.get("totalDamageDealtToChampions", 0) for p in nicepenta_participants)
                    comb_kills = sum(p.get("kills", 0) for p in nicepenta_participants)
                    comb_deaths = sum(p.get("deaths", 0) for p in nicepenta_participants)
                    comb_assists = sum(p.get("assists", 0) for p in nicepenta_participants)
                    comb_gold = sum(p.get("goldEarned", 0) for p in nicepenta_participants)
                    comb_vision = sum(p.get("visionScore", 0) for p in nicepenta_participants)

                    dmg_pct = round((comb_dmg / max(total_team_dmg, 1)) * 100, 1)
                    gold_pct = round((comb_gold / max(total_team_gold, 1)) * 100, 1)
                    comb_kda = round((comb_kills + comb_assists) / max(comb_deaths, 1), 2)
                    
                    # Kill Participation aproximado da parceria
                    kp_pct = round(((comb_kills + comb_assists) / max(total_team_kills, 1)) * 100, 1)
                    if kp_pct > 100:
                        kp_pct = 100.0

                    # Identificar o MVP da parceria com base em dano e KDA
                    mvp_player = max(nicepenta_participants, key=lambda x: (x.get("totalDamageDealtToChampions", 0) + (x.get("kills", 0) * 1500)))

                    # Registrar retrospecto da parceria em synergy_db.json
                    involved_discord_ids = [puuid_to_discord[p["puuid"]] for p in nicepenta_participants]
                    s_wins, s_losses, s_wr, s_total = record_synergy(involved_discord_ids, win)

                    group_type = "DUO" if len(nicepenta_participants) == 2 else ("TRIO" if len(nicepenta_participants) == 3 else "SQUAD")
                    res_title = f"🏆 VITÓRIA ESMAGADORA • {group_type} NICEPENTA ({mode_name.upper()})" if win else f"💀 DERROTA COMBATIDA • {group_type} NICEPENTA ({mode_name.upper()})"
                    res_color = discord.Color.gold() if win else discord.Color.red()

                    embed = discord.Embed(
                        title=res_title,
                        description=(
                            f"🤝 **Parceria em Ação:** {len(nicepenta_participants)} membros do servidor jogaram juntos!\n"
                            f"• **Duração:** `{duration_min} min` | **Modo:** `{mode_name}`\n"
                            f"• **Retrospecto da Parceria:** `{s_wins} Vitórias - {s_losses} Derrotas` (**{s_wr}% Winrate Juntos** em {s_total} jogos)\n"
                            f"• ⭐ **MVP do Grupo:** `{mvp_player.get('riotIdGameName')}` com **{mvp_player.get('championName')}**!"
                        ),
                        color=res_color,
                        timestamp=datetime.now()
                    )

                    # MÉTRICAS COLETIVAS DE SINERGIA
                    embed.add_field(
                        name="📊 Sinergia & Impacto Coletivo no Jogo",
                        value=(
                            f"• 💥 **Dano Combinado:** `{comb_dmg:,}` (**{dmg_pct}%** do dano de toda a equipe)\n"
                            f"• ⚔️ **KDA Coletivo:** `{comb_kills}/{comb_deaths}/{comb_assists}` (**{comb_kda} KDA**)\n"
                            f"• 🎯 **Participação em Abates:** **{kp_pct}%** dos abates do time\n"
                            f"• 💰 **Economia Compartilhada:** `{comb_gold:,}` G (**{gold_pct}%** do ouro do time)\n"
                            f"• 👁️ **Visão Total do Grupo:** `{comb_vision}` pts"
                        ),
                        inline=False
                    )

                    # Desempenho individual detalhado de cada membro
                    for p in nicepenta_participants:
                        c_info = get_champion_info(p.get("championId"))
                        c_name = c_info.get("name", p.get("championName"))
                        k = p.get("kills", 0)
                        d = p.get("deaths", 0)
                        a = p.get("assists", 0)
                        cs = p.get("totalMinionsKilled", 0) + p.get("neutralMinionsKilled", 0)
                        cs_min = round(cs / max(duration_min, 1), 1)
                        indiv_dmg = p.get("totalDamageDealtToChampions", 0)
                        indiv_dmg_pct = round((indiv_dmg / max(total_team_dmg, 1)) * 100, 1)

                        multikill_badge = ""
                        if p.get("pentaKills", 0) > 0:
                            multikill_badge = " 🔥 **PENTAKILL!**"
                        elif p.get("quadraKills", 0) > 0:
                            multikill_badge = " ⚡ **QUADRAKILL!**"
                        elif p.get("tripleKills", 0) > 0:
                            multikill_badge = " ⚔️ **TRIPLEKILL!**"

                        embed.add_field(
                            name=f"🎮 {p.get('riotIdGameName')} ({c_name}){multikill_badge}",
                            value=f"• **KDA:** `{k}/{d}/{a}`\n• **Dano:** `{indiv_dmg:,}` ({indiv_dmg_pct}%)\n• **Farm:** `{cs} CS` ({cs_min}/min)",
                            inline=True
                        )

                    embed.set_footer(text=f"Partida ID: {latest_match_id} • Sinergia NicePenta")
                    mentions = " ".join([f"<@{d_id}>" for d_id in involved_discord_ids])
                    await ch_feed.send(content=f"🤝 {mentions}", embed=embed)

                    if ch_geral:
                        try:
                            await ch_geral.send(f"📢 {mentions} acabaram de concluir uma partida de **{mode_name}**! Confira os dados completos em {ch_feed.mention}!")
                        except Exception:
                            pass

                else:
                    # TIMES OPOSTOS: GUERRA CIVIL / DUELO DIRETO
                    win_p = [p for p in nicepenta_participants if p.get("win")]
                    lose_p = [p for p in nicepenta_participants if not p.get("win")]

                    embed = discord.Embed(
                        title=f"⚔️ CONFRONTO INTERNO • GUERRA CIVIL ({mode_name.upper()})",
                        description=f"Membros do servidor caíram em **times opostos** e duelaram diretamente!\n• **Duração:** `{duration_min} min`",
                        color=discord.Color.purple(),
                        timestamp=datetime.now()
                    )
                    winners_txt = "\n".join([f"• 👑 **{p.get('riotIdGameName')}** ({p.get('championName')} - `{p.get('kills')}/{p.get('deaths')}/{p.get('assists')}`)" for p in win_p])
                    losers_txt = "\n".join([f"• 💀 **{p.get('riotIdGameName')}** ({p.get('championName')} - `{p.get('kills')}/{p.get('deaths')}/{p.get('assists')}`)" for p in lose_p])

                    embed.add_field(name="🏆 Vencedores do Confronto", value=winners_txt or "Nenhum", inline=False)
                    embed.add_field(name="💀 Derrotados no Duelo", value=losers_txt or "Nenhum", inline=False)
                    embed.set_footer(text=f"Partida ID: {latest_match_id} • Duelo Direto NicePenta")
                    all_mentions = " ".join([f"<@{puuid_to_discord[p['puuid']]}>" for p in nicepenta_participants])
                    await ch_feed.send(content=f"⚔️ {all_mentions}", embed=embed)

            # CASO 2: UM MEMBRO JOGANDO SOLO
            elif len(nicepenta_participants) == 1:
                p = nicepenta_participants[0]
                win = p.get("win", False)
                champ = p.get("championName", "Campeão")
                c_info = get_champion_info(p.get("championId"))
                c_name = c_info.get("name", champ)
                kills = p.get("kills", 0)
                deaths = p.get("deaths", 0)
                assists = p.get("assists", 0)
                kda_calc = round((kills + assists) / max(deaths, 1), 2)
                dmg = p.get("totalDamageDealtToChampions", 0)
                cs = p.get("totalMinionsKilled", 0) + p.get("neutralMinionsKilled", 0)
                cs_min = round(cs / max(duration_min, 1), 1)
                gold = p.get("goldEarned", 0)

                champ_icon_url = c_info.get("icon", f"https://ddragon.leagueoflegends.com/cdn/16.21.1/img/champion/{champ}.png")
                res_title = f"🏆 VITÓRIA • {mode_name.upper()}" if win else f"💀 DERROTA • {mode_name.upper()}"
                res_color = discord.Color.green() if win else discord.Color.red()

                embed = discord.Embed(
                    title=res_title,
                    description=f"Partida solo finalizada por <@{discord_id}>!\n• **Modo:** `{mode_name}` | **Duração:** `{duration_min} min`",
                    color=res_color,
                    timestamp=datetime.now()
                )
                embed.set_thumbnail(url=champ_icon_url)
                embed.add_field(
                    name=f"🎮 {p.get('riotIdGameName', p_info.get('riot_id'))} ({c_name})",
                    value=(
                        f"• **KDA:** `{kills}/{deaths}/{assists}` (**{kda_calc} KDA**)\n"
                        f"• **Dano:** `{dmg:,}` | **Farm:** `{cs} CS` (`{cs_min}/min`)\n"
                        f"• **Ouro Conquistado:** `{gold:,}` G"
                    ),
                    inline=False
                )
                embed.set_footer(text=f"Partida ID: {latest_match_id} • Radar NicePenta")
                await ch_feed.send(content=f"🔔 <@{discord_id}>", embed=embed)

            await asyncio.sleep(1)

    if db_modified:
        save_db(db)


# =========================================================================
# 5. ARSENAL COMPLETO DE COMANDOS PARA OS JOGADORES (SLASH COMMANDS)
# =========================================================================

def resolve_target_player(target_str, author_id, db):
    if not target_str:
        if str(author_id) in db:
            return db[str(author_id)]
        return None
    mention_match = re.search(r'<@!?(\d+)>', target_str)
    if mention_match:
        uid = mention_match.group(1)
        return db.get(str(uid))
    for d_id, data in db.items():
        if data.get("riot_id", "").lower() == target_str.lower():
            return data
    if "#" in target_str:
        game_name, tag_line = target_str.split("#", 1)
        safe_name = urllib.parse.quote(game_name.strip())
        safe_tag = urllib.parse.quote(tag_line.strip())
        url_acc = f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{safe_name}/{safe_tag}"
        acc_data, status_acc = riot_api_request(url_acc)
        if status_acc == 200 and acc_data:
            puuid = acc_data["puuid"]
            url_summ = f"https://br1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}"
            summ, _ = riot_api_request(url_summ)
            url_league = f"https://br1.api.riotgames.com/lol/league/v4/entries/by-puuid/{puuid}"
            league, _ = riot_api_request(url_league)
            tier = "UNRANKED"
            rank = ""
            lp = 0
            wins = 0
            losses = 0
            if league and isinstance(league, list):
                entry = next((e for e in league if e.get("queueType") == "RANKED_SOLO_5x5"), league[0] if league else None)
                if entry:
                    tier = entry.get("tier", "UNRANKED")
                    rank = entry.get("rank", "")
                    lp = entry.get("leaguePoints", 0)
                    wins = entry.get("wins", 0)
                    losses = entry.get("losses", 0)
            return {
                "riot_id": f"{acc_data['gameName']}#{acc_data['tagLine']}",
                "puuid": puuid,
                "level": summ.get("summonerLevel", 1) if summ else 1,
                "icon_id": summ.get("profileIconId", 29) if summ else 29,
                "tier": tier,
                "rank": rank,
                "lp": lp,
                "wins": wins,
                "losses": losses
            }
    return None


@bot.tree.command(name="perfil", description="Ver perfil completo no LoL (Elo Ranqueado, Nível e Top 3 Maestrias)")
@app_commands.describe(invocador="Membro ou Riot ID (Nome#TAG). Deixe vazio para ver o seu próprio.")
async def cmd_perfil(interaction: discord.Interaction, invocador: str = None):
    await interaction.response.defer()
    db = load_db()
    player = resolve_target_player(invocador, interaction.user.id, db)

    if not player:
        await interaction.followup.send("❌ Invocador não encontrado. Use o formato `Nome#TAG` ou vincule sua conta em `#🔗・vincular-conta-lol`!")
        return

    puuid = player.get("puuid")
    url_m = f"https://br1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}/top?count=3"
    top_m, _ = riot_api_request(url_m)

    m_text = ""
    if top_m and isinstance(top_m, list):
        for m in top_m:
            c_info = get_champion_info(m.get("championId"))
            c_name = c_info.get("name", f"Campeão {m.get('championId')}")
            pts = m.get("championPoints", 0)
            lvl = m.get("championLevel", 1)
            m_text += f"• **{c_name}**: `{pts:,} pts` (Maestria {lvl})\n"
    if not m_text:
        m_text = "Sem registros de maestria."

    icon_id = player.get("icon_id", 29)
    icon_url = f"https://ddragon.leagueoflegends.com/cdn/16.21.1/img/profileicon/{icon_id}.png"
    tier = player.get("tier", "UNRANKED")
    rank = player.get("rank", "")
    lp = player.get("lp", 0)
    elo_role_name = ELO_MAPPING.get(tier.upper(), "UNRANKED")

    embed = discord.Embed(
        title=f"👤 PERFIL DE INVOCADOR • {player.get('riot_id')}",
        color=discord.Color.from_rgb(52, 152, 219),
        timestamp=datetime.now()
    )
    embed.set_thumbnail(url=icon_url)
    embed.add_field(name="⭐ Nível", value=f"`Nv. {player.get('level', 1)}`", inline=True)
    embed.add_field(name="🎖️ Elo Ranqueado", value=f"**{elo_role_name} {rank}** (`{lp} PDL`)", inline=True)
    embed.add_field(name="🏆 Top 3 Campeões Mais Jogados", value=m_text, inline=False)
    embed.add_field(name="🌐 Histórico no OP.GG", value=f"[Ver estatísticas no OP.GG](https://www.op.gg/summoners/br/{urllib.parse.quote(player.get('riot_id').replace('#', '-'))})", inline=False)
    embed.set_footer(text="NicePenta E-Sports • Dados Oficiais da Riot Games")

    await interaction.followup.send(embed=embed)


@bot.tree.command(name="maestria", description="Ver o Top 5 campeões de maior maestria de um jogador")
@app_commands.describe(invocador="Membro ou Riot ID (Nome#TAG). Deixe vazio para ver o seu próprio.")
async def cmd_maestria(interaction: discord.Interaction, invocador: str = None):
    await interaction.response.defer()
    db = load_db()
    player = resolve_target_player(invocador, interaction.user.id, db)

    if not player:
        await interaction.followup.send("❌ Invocador não encontrado. Digite `Nome#TAG` ou vincule sua conta!")
        return

    puuid = player.get("puuid")
    url_top = f"https://br1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}/top?count=5"
    top_m, status_m = riot_api_request(url_top)

    url_score = f"https://br1.api.riotgames.com/lol/champion-mastery/v4/scores/by-puuid/{puuid}"
    score_data, _ = riot_api_request(url_score)
    total_score = score_data if isinstance(score_data, int) else "N/A"

    embed = discord.Embed(
        title=f"🏆 TOP 5 MAESTRIAS • {player.get('riot_id')}",
        description=f"Pontuação Total de Maestria na Conta: **{total_score}**",
        color=discord.Color.gold(),
        timestamp=datetime.now()
    )

    if top_m and isinstance(top_m, list):
        for i, m in enumerate(top_m):
            c_info = get_champion_info(m.get("championId"))
            c_name = c_info.get("name", f"Campeão {m.get('championId')}")
            pts = m.get("championPoints", 0)
            lvl = m.get("championLevel", 1)
            medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
            embed.add_field(
                name=f"{medals[i]} {c_name} (Nível {lvl})",
                value=f"• **Pontos:** `{pts:,} pts`\n• **Título:** *{c_info.get('title', '')}*",
                inline=False
            )
            if i == 0:
                embed.set_thumbnail(url=c_info.get("icon"))
    else:
        embed.description = "Nenhum registro de maestria encontrado para esta conta."

    embed.set_footer(text="Champion-Mastery-V4 • Riot Games")
    await interaction.followup.send(embed=embed)


@bot.tree.command(name="historico", description="Ver o histórico das últimas 5 partidas do invocador")
@app_commands.describe(invocador="Membro ou Riot ID (Nome#TAG). Deixe vazio para ver o seu próprio.")
async def cmd_historico(interaction: discord.Interaction, invocador: str = None):
    await interaction.response.defer()
    db = load_db()
    player = resolve_target_player(invocador, interaction.user.id, db)

    if not player:
        await interaction.followup.send("❌ Invocador não encontrado. Digite `Nome#TAG` ou vincule sua conta!")
        return

    puuid = player.get("puuid")
    url_ids = f"https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?count=5"
    m_ids, status_ids = riot_api_request(url_ids)

    if status_ids != 200 or not m_ids:
        await interaction.followup.send("❌ Nenhuma partida recente encontrada no histórico.")
        return

    embed = discord.Embed(
        title=f"📜 HISTÓRICO DAS ÚLTIMAS 5 PARTIDAS • {player.get('riot_id')}",
        color=discord.Color.blue(),
        timestamp=datetime.now()
    )

    wins_count = 0
    total_matches = len(m_ids)

    for m_id in m_ids:
        url_match = f"https://americas.api.riotgames.com/lol/match/v5/matches/{m_id}"
        m_data, status_m = riot_api_request(url_match)
        if status_m != 200 or not m_data:
            continue

        info = m_data.get("info", {})
        q_id = info.get("queueId", 0)
        mode = QUEUE_NAMES.get(q_id, info.get("gameMode", "LoL"))
        dur_min = round(info.get("gameDuration", 0) / 60, 1)

        p = next((x for x in info.get("participants", []) if x.get("puuid") == puuid), None)
        if not p:
            continue

        win = p.get("win", False)
        if win:
            wins_count += 1
        res_badge = "🟢 **VITÓRIA**" if win else "🔴 **DERROTA**"
        c_info = get_champion_info(p.get("championId"))
        c_name = c_info.get("name", p.get("championName"))
        k = p.get("kills", 0)
        d = p.get("deaths", 0)
        a = p.get("assists", 0)
        dmg = p.get("totalDamageDealtToChampions", 0)

        embed.add_field(
            name=f"{res_badge} — {c_name} ({mode})",
            value=f"• **KDA:** `{k}/{d}/{a}` | **Dano:** `{dmg:,}` | **Duração:** `{dur_min} min`",
            inline=False
        )

    recent_wr = round((wins_count / max(total_matches, 1)) * 100, 1)
    embed.description = f"Desempenho recente: **{wins_count} Vitórias / {total_matches - wins_count} Derrotas** ({recent_wr}% Winrate)"
    embed.set_footer(text="Match-V5 • Riot Games")

    await interaction.followup.send(embed=embed)


@bot.tree.command(name="aovivo", description="Ver partida ao vivo e comando direto para assistir pelo cliente 3D do LoL")
@app_commands.describe(invocador="Membro ou Riot ID (Nome#TAG). Deixe vazio para ver a sua própria.")
async def cmd_aovivo(interaction: discord.Interaction, invocador: str = None):
    await interaction.response.defer()
    db = load_db()
    player = resolve_target_player(invocador, interaction.user.id, db)

    if not player:
        await interaction.followup.send("❌ Invocador não encontrado. Digite `Nome#TAG` ou vincule sua conta!")
        return

    puuid = player.get("puuid")
    url_spec = f"https://br1.api.riotgames.com/lol/spectator/v5/active-games/by-summoner/{puuid}"
    spec_data, status_s = riot_api_request(url_spec)

    if status_s == 404 or not spec_data:
        await interaction.followup.send(f"💤 O invocador **{player.get('riot_id')}** não está em nenhuma partida ativa no momento.")
        return

    game_id = spec_data.get("gameId")
    key = spec_data.get("observers", {}).get("encryptionKey")
    game_mode = spec_data.get("gameMode", "CLASSIC")
    queue_id = spec_data.get("gameQueueConfigId", 0)
    mode_name = QUEUE_NAMES.get(queue_id, game_mode)
    game_len = spec_data.get("gameLength", 0)
    mins = game_len // 60
    secs = game_len % 60

    spectate_cmd = f'"C:\\Riot Games\\League of Legends\\Game\\League of Legends.exe" "spectator spectator.br.lol.riotgames.com:80 {key} {game_id} BR1"'
    opgg_url = f"https://www.op.gg/summoners/br/{urllib.parse.quote(player.get('riot_id').replace('#', '-'))}/ingame"

    embed = discord.Embed(
        title=f"🔴 PARTIDA AO VIVO • {player.get('riot_id')}",
        description=f"Partida em andamento no **{mode_name}**!\n• **Tempo Decorrido:** `{mins}m {secs}s`",
        color=discord.Color.red(),
        timestamp=datetime.now()
    )

    p_self = next((p for p in spec_data.get("participants", []) if p.get("puuid") == puuid), None)
    if p_self:
        c_info = get_champion_info(p_self.get("championId"))
        embed.set_thumbnail(url=c_info.get("icon"))
        embed.add_field(name="🎮 Campeão Escolhido", value=f"**{c_info.get('name')}**", inline=True)

    embed.add_field(
        name="👁️ Como Assistir Ao Vivo no seu LoL (Espectador Direto 3D)",
        value=f"Pressione `Win + R` no seu Windows, cole o comando abaixo e aperte Enter:\n```cmd\n{spectate_cmd}\n```",
        inline=False
    )
    embed.add_field(name="🌐 Acompanhar pelo Navegador", value=f"👉 **[Abrir Radar no OP.GG Ao Vivo]({opgg_url})**", inline=False)
    embed.set_footer(text=f"Riot Spectator V5 • Game ID: {game_id}")

    await interaction.followup.send(embed=embed)


@bot.tree.command(name="ranking", description="Ver a tabela de classificação (Leaderboard) de Elos do servidor")
async def cmd_ranking(interaction: discord.Interaction):
    await interaction.response.defer()
    db = load_db()
    if not db:
        await interaction.followup.send("Nenhum membro classificado ainda!")
        return

    sorted_players = sorted(
        db.items(),
        key=lambda item: (
            ELO_ORDER.get(item[1].get("tier", "UNRANKED").upper(), 0),
            item[1].get("lp", 0),
            item[1].get("level", 0)
        ),
        reverse=True
    )

    embed = discord.Embed(
        title="🏆 TABELA DE CLASSIFICAÇÃO DE ELOS • NICEPENTA E-SPORTS",
        description="Ranking dos melhores treinadores e invocadores da nossa comunidade:",
        color=discord.Color.gold(),
        timestamp=datetime.now()
    )

    lines = []
    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    for i, (d_id, p_info) in enumerate(sorted_players[:15]):
        badge = medals[i] if i < len(medals) else f"`#{i+1}`"
        tier = p_info.get("tier", "UNRANKED")
        rank = p_info.get("rank", "")
        lp = p_info.get("lp", 0)
        elo_name = ELO_MAPPING.get(tier.upper(), "UNRANKED")
        lines.append(f"{badge} <@{d_id}> (`{p_info.get('riot_id')}`) — **{elo_name} {rank}** (`{lp} PDL`) • Nv. {p_info.get('level')}")

    embed.description = "\n".join(lines) if lines else "Nenhum membro registrado."
    embed.set_footer(text="Atualizado via Riot Games API • NicePenta E-Sports")

    await interaction.followup.send(embed=embed)


@bot.tree.command(name="sinergia", description="Ver o retrospecto de vitórias e sinergia entre dois jogadores")
@app_commands.describe(jogador1="Primeiro jogador", jogador2="Segundo jogador")
async def cmd_sinergia(interaction: discord.Interaction, jogador1: discord.Member, jogador2: discord.Member):
    await interaction.response.defer()
    s_db = load_synergy()
    key = "_".join(sorted([str(jogador1.id), str(jogador2.id)]))
    stats = s_db.get(key, {"wins": 0, "losses": 0})
    wins = stats["wins"]
    losses = stats["losses"]
    total = wins + losses
    wr = round((wins / total) * 100, 1) if total > 0 else 0

    embed = discord.Embed(
        title="🤝 HISTÓRICO DE SINERGIA DA DUPLA",
        description=f"Retrospecto de partidas jogadas em conjunto por {jogador1.mention} e {jogador2.mention}:",
        color=discord.Color.from_rgb(46, 204, 113),
        timestamp=datetime.now()
    )
    embed.add_field(name="⚔️ Total de Partidas Juntos", value=f"`{total}` partidas registradas", inline=True)
    embed.add_field(name="🏆 Vitórias da Dupla", value=f"`{wins}` vitórias", inline=True)
    embed.add_field(name="💀 Derrotas da Dupla", value=f"`{losses}` derrotas", inline=True)
    embed.add_field(name="📈 Taxa de Vitória Conjunta (Winrate)", value=f"**{wr}% de aproveitamento**", inline=False)
    embed.set_footer(text="Sinergia NicePenta E-Sports")

    await interaction.followup.send(embed=embed)


@bot.tree.command(name="rotas", description="Ver a lista de membros por rota (Top, Jungle, Mid, ADC, Suporte)")
async def cmd_rotas(interaction: discord.Interaction):
    await interaction.response.defer()
    guild = interaction.guild

    lanes = {
        "🛡️ TOP LANERS": "🛡️ TOP LANER",
        "🌲 JUNGLERS": "🌲 JUNGLER",
        "🧙 MID LANERS": "🧙 MID LANER",
        "🏹 ADCS": "🏹 BOT LANER (ADC)",
        "🩹 SUPORTES": "🩹 SUPORTE"
    }

    embed = discord.Embed(
        title="🎭 ROSTER DE JOGADORES POR ROTA • NICEPENTA",
        description="Confira os membros disponíveis para cada posição no servidor:",
        color=discord.Color.from_rgb(155, 89, 182),
        timestamp=datetime.now()
    )

    for title, role_name in lanes.items():
        role = discord.utils.get(guild.roles, name=role_name)
        if role and role.members:
            m_list = ", ".join([m.mention for m in role.members[:10]])
            embed.add_field(name=f"{title} ({len(role.members)})", value=m_list, inline=False)
        else:
            embed.add_field(name=f"{title} (0)", value="*Nenhum jogador registrado nesta rota*", inline=False)

    embed.set_footer(text="Defina sua rota no canal #🎭・escolha-de-rotas")
    await interaction.followup.send(embed=embed)


@bot.tree.command(name="statuslol", description="Verificar o status dos servidores brasileiros da Riot Games (BR1)")
async def cmd_statuslol(interaction: discord.Interaction):
    await interaction.response.defer()
    url = "https://br1.api.riotgames.com/lol/status/v4/platform-data"
    data, status_code = riot_api_request(url)

    if status_code != 200 or not data:
        await interaction.followup.send("⚠️ Não foi possível consultar o status da Riot no momento.")
        return

    maints = len(data.get("maintenances", []))
    incidents = len(data.get("incidents", []))
    is_healthy = (maints == 0 and incidents == 0)

    embed = discord.Embed(
        title="📡 STATUS DO SERVIDOR RIOT GAMES (BR1)",
        color=discord.Color.green() if is_healthy else discord.Color.orange(),
        timestamp=datetime.now()
    )
    embed.add_field(name="Servidor Oficial", value=f"**{data.get('name')}** (`{data.get('id')}`)", inline=True)
    embed.add_field(name="Estado Operacional", value="🟢 **Normal e Estável**" if is_healthy else "⚠️ **Instabilidade Detectada**", inline=True)
    embed.add_field(name="Manutenções em Andamento", value=f"`{maints}` ativas", inline=True)
    embed.add_field(name="Incidentes / Falhas Registradas", value=f"`{incidents}` reportados", inline=True)
    embed.set_footer(text="Riot Status API • Servidor Brasil")

    await interaction.followup.send(embed=embed)


@bot.tree.command(name="campeao", description="Consultar informações detalhadas, título e splash art de qualquer campeão")
@app_commands.describe(nome="Nome do campeão (Ex: Lux, Yasuo, Jinx, Aatrox)")
async def cmd_campeao(interaction: discord.Interaction, nome: str):
    await interaction.response.defer()
    c_info = get_champion_info(nome)
    
    if not c_info or c_info.get("name") == nome and "tags" not in c_info:
        await interaction.followup.send(f"❌ Campeão `{nome}` não encontrado.")
        return

    c_id = c_info.get("id")
    splash_url = f"https://ddragon.leagueoflegends.com/cdn/img/champion/splash/{c_id}_0.jpg"
    icon_url = c_info.get("icon")

    embed = discord.Embed(
        title=f"⚔️ {c_info.get('name')} — {c_info.get('title')}",
        description=f"**Classes / Funções:** {', '.join(c_info.get('tags', []))}",
        color=discord.Color.gold(),
        timestamp=datetime.now()
    )
    embed.set_thumbnail(url=icon_url)
    embed.set_image(url=splash_url)
    embed.add_field(name="🌐 Ver Builds e Dicas", value=f"[Ver estatísticas no OP.GG](https://www.op.gg/champions/{c_id.lower()})", inline=False)
    embed.set_footer(text="Data Dragon • Patch Oficial 16.21.1")

    await interaction.followup.send(embed=embed)


@bot.tree.command(name="scrim", description="Gerador de Times Balanceados para Scrims e Partidas Personalizadas 5v5")
async def cmd_scrim(interaction: discord.Interaction):
    await interaction.response.defer()
    # Se o usuário estiver em um canal de voz, pega os membros da sala
    members_to_split = []
    if interaction.user.voice and interaction.user.voice.channel:
        members_to_split = [m for m in interaction.user.voice.channel.members if not m.bot]

    if len(members_to_split) < 2:
        # Se não houver membros na sala de voz, busca membros online verificados no servidor
        guild = interaction.guild
        verified_role = discord.utils.get(guild.roles, name="VERIFICADO (LOL)")
        if verified_role:
            members_to_split = [m for m in verified_role.members if not m.bot][:10]

    if len(members_to_split) < 2:
        await interaction.followup.send("⚠️ É necessário pelo menos 2 jogadores no canal de voz para sortear os times de Scrim!")
        return

    random.shuffle(members_to_split)
    mid = len(members_to_split) // 2
    team_blue = members_to_split[:mid]
    team_red = members_to_split[mid:]

    embed = discord.Embed(
        title="⚔️ SORTEIO DE TIMES PARA SCRIM • NICEPENTA",
        description="Os jogadores foram divididos aleatoriamente para a partida personalizada:",
        color=discord.Color.purple(),
        timestamp=datetime.now()
    )
    blue_str = "\n".join([f"• 🔵 {m.mention} (`{m.display_name}`)" for m in team_blue])
    red_str = "\n".join([f"• 🔴 {m.mention} (`{m.display_name}`)" for m in team_red])

    embed.add_field(name=f"🔵 Time Azul ({len(team_blue)})", value=blue_str or "Vazio", inline=True)
    embed.add_field(name=f"🔴 Time Vermelho ({len(team_red)})", value=red_str or "Vazio", inline=True)
    embed.set_footer(text="Que vença o melhor time • NicePenta E-Sports")

    await interaction.followup.send(embed=embed)


# =========================================================================
# 6. SERVIDOR WEB EMBUTIDO (ANTI-SLEEP PARA RENDER CLOUD 24/7)
# =========================================================================

async def start_web_server():
    app = web.Application()

    async def handle_root(request):
        return web.json_response({
            "status": "online",
            "bot": str(bot.user) if bot.user else "HBCRIATE",
            "guilds": len(bot.guilds),
            "timestamp": datetime.now().isoformat()
        })

    async def handle_health(request):
        return web.Response(text="OK - 24/7 ONLINE", status=200)

    app.router.add_get("/", handle_root)
    app.router.add_get("/health", handle_health)

    port = int(os.getenv("PORT", 10000))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"[WEB SERVER] Anti-Sleep Server ativo na porta {port} (Pronto para o Render)!", flush=True)

@tasks.loop(minutes=8)
async def keep_alive_task():
    ext_url = os.getenv("RENDER_EXTERNAL_URL")
    if ext_url:
        try:
            req = urllib.request.Request(f"{ext_url}/health", headers={"User-Agent": "NicePentaAntiSleep/2.0"})
            with urllib.request.urlopen(req, timeout=8) as resp:
                pass
            print(f"[ANTI-SLEEP] Ping enviado com sucesso para {ext_url}/health (Resetando timer de inatividade)", flush=True)
        except Exception as e:
            print(f"[ANTI-SLEEP] Ping falhou: {e}", flush=True)

# =========================================================================
# 7. INICIALIZAÇÃO GERAL DO BOT & SINCRONIZAÇÃO DE COMANDOS
# =========================================================================

@bot.event
async def on_ready():
    print(f"[SUCESSO] Bot online como {bot.user} (ID: {bot.user.id})", flush=True)

    # Iniciar servidor web anti-sleep
    if not hasattr(bot, "_web_server_started"):
        bot._web_server_started = True
        asyncio.create_task(start_web_server())
        if not keep_alive_task.is_running():
            keep_alive_task.start()

    bot.add_view(AdminDashboardView())
    bot.add_view(PersistentRiotLinkView())
    bot.add_view(PersistentLaneSelectionView())

    for guild in bot.guilds:
        print(f"[CONFIGURANDO] Painel em: {guild.name} (ID: {guild.id})", flush=True)
        await setup_admin_panel(guild)

    # Sincronizar Slash Commands
    try:
        synced = await bot.tree.sync()
        print(f"[SLASH COMMANDS] {len(synced)} comandos sincronizados com a árvore do Discord!", flush=True)
    except Exception as e:
        print(f"Erro ao sincronizar slash commands: {e}", flush=True)

    if not hybrid_match_radar.is_running():
        hybrid_match_radar.start()
        print("[RADAR HÍBRIDO ATIVO] Monitorando histórico, duos, partidas ao vivo e espectador 3D!", flush=True)

    await bot.change_presence(activity=discord.Game(name="🏆 NicePenta LoL | /aovivo /perfil"))
    print(">>> BOT 100% OPERACIONAL COM ARSENAL COMPLETO DE COMANDOS E PÚBLICO! <<<", flush=True)


if __name__ == "__main__":
    if not TOKEN:
        print("[ERRO] DISCORD_TOKEN não configurado no .env", flush=True)
    else:
        bot.run(TOKEN)
