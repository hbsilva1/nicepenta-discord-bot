import os
import sys
import asyncio
import discord
from dotenv import load_dotenv

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
TARGET_GUILD_ID = 219177367296278538  # NICEPENTA E-SPORTS

intents = discord.Intents.default()
intents.guilds = True
intents.members = True

client = discord.Client(intents=intents)

ELO_ROLES = [
    ("DESAFIANTE", discord.Color.from_rgb(241, 196, 15)),
    ("GRÃO-MESTRE", discord.Color.from_rgb(231, 76, 60)),
    ("MESTRE", discord.Color.from_rgb(155, 89, 182)),
    ("DIAMANTE", discord.Color.from_rgb(52, 152, 219)),
    ("ESMERALDA", discord.Color.from_rgb(46, 204, 113)),
    ("PLATINA", discord.Color.from_rgb(26, 188, 156)),
    ("OURO", discord.Color.from_rgb(243, 156, 18)),
    ("PRATA", discord.Color.from_rgb(189, 195, 199)),
    ("BRONZE", discord.Color.from_rgb(211, 84, 0)),
    ("FERRO", discord.Color.from_rgb(127, 140, 141)),
    ("UNRANKED", discord.Color.from_rgb(90, 100, 110))
]

LANE_ROLES = [
    ("🛡️ TOP LANER", discord.Color.from_rgb(230, 126, 34)),
    ("🌲 JUNGLER", discord.Color.from_rgb(39, 174, 96)),
    ("🧙 MID LANER", discord.Color.from_rgb(142, 68, 173)),
    ("🏹 BOT LANER (ADC)", discord.Color.from_rgb(231, 76, 60)),
    ("🩹 SUPORTE", discord.Color.from_rgb(52, 152, 219))
]

SPECIAL_ROLES = [
    ("VERIFICADO (LOL)", discord.Color.from_rgb(41, 128, 185)),
    ("NOTIFICAÇÃO DE SCRIMS", discord.Color.from_rgb(241, 196, 15)),
    ("BUSCO DUO", discord.Color.from_rgb(46, 204, 113))
]

@client.event
async def on_ready():
    print(f"[OK] Conectado como {client.user}")
    guild = client.get_guild(TARGET_GUILD_ID)
    if not guild:
        print(f"[ERRO] Servidor {TARGET_GUILD_ID} não encontrado!")
        await client.close()
        return

    print(f"\n=======================================================")
    print(f"REESTRUTURANDO SERVIDOR: {guild.name}")
    print(f"=======================================================")

    # 1. CRIAR OU ATUALIZAR CARGOS
    print("\n--- 1. CONFIGURANDO CARGOS DE ELO, ROTAS E VERIFICAÇÃO ---")
    existing_roles = {r.name.upper(): r for r in guild.roles}

    all_roles_to_create = ELO_ROLES + LANE_ROLES + SPECIAL_ROLES
    for role_name, color in all_roles_to_create:
        if role_name.upper() not in existing_roles:
            try:
                new_role = await guild.create_role(name=role_name, color=color, mentionable=False)
                print(f"  [+] Cargo criado: {new_role.name}")
                await asyncio.sleep(0.2)
            except Exception as e:
                print(f"  Erro ao criar cargo {role_name}: {e}")
        else:
            print(f"  [=] Cargo já existente: {role_name}")

    # 2. REMOVER CANAIS E CATEGORIAS ANTIGAS
    print("\n--- 2. LIMPANDO CANAIS E CATEGORIAS ANTIGAS ---")
    # Preservar apenas a categoria 🛡️ ADMINISTRAÇÃO e seu painel
    for ch in list(guild.channels):
        if ch.category and "ADMINISTRAÇÃO" in ch.category.name:
            continue
        if "painel" in ch.name.lower() or "admin" in ch.name.lower():
            continue
        try:
            await ch.delete(reason="Reestruturacao profissional League of Legends")
            print(f"  [-] Deletado: {ch.name}")
            await asyncio.sleep(0.2)
        except Exception as e:
            print(f"  Aviso ao deletar {ch.name}: {e}")

    # 3. RECRIAR CATEGORIAS E CANAIS COMPETITIVOS
    print("\n--- 3. CRIANDO NOVAS CATEGORIAS E CANAIS COMPETITIVOS ---")
    
    # A. Categoria: ✦ BEM-VINDO & IDENTIDADE
    cat_welcome = await guild.create_category(name="✦ BEM-VINDO & IDENTIDADE")
    ch_regras = await guild.create_text_channel(name="📜・regras-da-casa", category=cat_welcome, topic="Conduta esportiva e diretrizes da comunidade NicePenta")
    ch_vincular = await guild.create_text_channel(name="🔗・vincular-conta-lol", category=cat_welcome, topic="Vincule seu Riot ID (Nome#TAG) para receber seu Elo automaticamente")
    ch_rotas = await guild.create_text_channel(name="🎭・escolha-de-rotas", category=cat_welcome, topic="Escolha suas rotas principais (Top, Jungle, Mid, ADC, Suporte)")

    # B. Categoria: ✦ CENTRAL LEAGUE OF LEGENDS
    cat_lol = await guild.create_category(name="✦ CENTRAL LEAGUE OF LEGENDS")
    ch_geral = await guild.create_text_channel(name="💬・chat-geral-lol", category=cat_lol, topic="Bate-papo principal sobre League of Legends")
    ch_duo = await guild.create_text_channel(name="🔍・busco-duo-e-flex", category=cat_lol, topic="Encontre parceiros de SoloQ, Duo e time de Flex")
    ch_clips = await guild.create_text_channel(name="🎬・clips-e-pentakills", category=cat_lol, topic="Poste suas melhores jogadas, pentakills e roubos de Barão")
    ch_patch = await guild.create_text_channel(name="📊・patch-notes-e-meta", category=cat_lol, topic="Notas das atualizações oficiais da Riot Games, buffs, nerfs e tier lists")

    # C. Categoria: ✦ COMPETITIVO & SCRIMS
    cat_comp = await guild.create_category(name="✦ COMPETITIVO & SCRIMS")
    ch_scrims = await guild.create_text_channel(name="🏆・partidas-e-scrims", category=cat_comp, topic="Registro automático de partidas e métricas quando membros jogam juntos")
    ch_agenda = await guild.create_text_channel(name="📅・agenda-e-torneios", category=cat_comp, topic="Datas de Clash, torneios e treinos do time NicePenta")
    ch_lineup = await guild.create_text_channel(name="⭐・lineup-nicepenta", category=cat_comp, topic="Ficha técnica dos jogadores oficiais do time NicePenta")

    # D. Categoria: ✦ SALAS DE VOZ DINÂMICAS
    cat_voice = await guild.create_category(name="✦ SALAS DE VOZ DINÂMICAS")
    await guild.create_voice_channel(name="➕・Criar Duo (2 Vagas)", category=cat_voice, user_limit=2)
    await guild.create_voice_channel(name="➕・Criar Trio / Flex (5 Vagas)", category=cat_voice, user_limit=5)
    await guild.create_voice_channel(name="🔊・ARAM & Modos Rápidos", category=cat_voice)
    await guild.create_voice_channel(name="🔊・Treino Titular (NicePenta)", category=cat_voice, user_limit=5)

    print("\n[SUCESSO] Toda a estrutura competitiva foi construída no NICEPENTA E-SPORTS!")
    await client.close()

if __name__ == "__main__":
    client.run(TOKEN)
