import os
import sys
import socket
import time
import asyncio
from datetime import datetime
import discord
from dotenv import load_dotenv

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
SERVER_IP = "138.121.165.67"
PORT_SITE = 8088
PORT_GAME_LOGIN = 7171
PORT_GAME_WORLD = 7172

SITE_URL = f"http://{SERVER_IP}:{PORT_SITE}"
REGISTER_URL = f"{SITE_URL}/register.php"
CHARACTER_URL = f"{SITE_URL}/createcharacter.php"
HIGHSCORES_URL = f"{SITE_URL}/highscores.php"
RECOVERY_URL = f"{SITE_URL}/recovery.php"
DL_WINDOWS_URL = f"{SITE_URL}/downloads/pokemaster-windows.zip"
DL_APK_URL = f"{SITE_URL}/downloads/pokemaster.apk"

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

def test_connection(host, port, timeout=2.5):
    start = time.time()
    try:
        s = socket.create_connection((host, port), timeout=timeout)
        s.close()
        latency = int((time.time() - start) * 1000)
        return True, latency
    except Exception:
        return False, 0

async def purge_and_send(channel: discord.TextChannel, embeds: list, pin_first: bool = False):
    print(f"[ATUALIZANDO] #{channel.name}...")
    try:
        await channel.purge(limit=30)
    except Exception as e:
        print(f"Aviso ao limpar #{channel.name}: {e}")
        
    first_msg = None
    for emb in embeds:
        msg = await channel.send(embed=emb)
        if first_msg is None:
            first_msg = msg
        await asyncio.sleep(0.35)
        
    if pin_first and first_msg:
        try:
            await first_msg.pin()
        except Exception:
            pass

@client.event
async def on_ready():
    print(f"[OK] Conectado como {client.user} ({client.user.id})")
    guild = client.guilds[0]
    print(f"Servidor: {guild.name}")
    
    admin_roles = [r for r in guild.roles if r.permissions.administrator and r != guild.default_role]
    
    # Overwrite estrito de modo seguro/admin-only
    safe_overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, embed_links=True, manage_channels=True)
    }
    if guild.owner:
        safe_overwrites[guild.owner] = discord.PermissionOverwrite(view_channel=True, send_messages=True)
    for role in admin_roles:
        safe_overwrites[role] = discord.PermissionOverwrite(view_channel=True, send_messages=True)

    # 1. Garantir novos canais
    cat_infos = discord.utils.get(guild.categories, name="✦ BEM-VINDO & INFOS")
    cat_wiki = discord.utils.get(guild.categories, name="✦ WIKI & GUIAS")
    
    # Canal: #📖・sobre-o-servidor
    ch_sobre = discord.utils.get(guild.text_channels, name="📖・sobre-o-servidor")
    if not ch_sobre and cat_infos:
        ch_sobre = await guild.create_text_channel(
            name="📖・sobre-o-servidor",
            category=cat_infos,
            topic="Descrição detalhada, filosofia de RPG Hard, rates e hardware do Pokémon Reload",
            overwrites=safe_overwrites
        )
        print("Criado canal #📖・sobre-o-servidor")
        
    # Canal: #🛡️・clãs-e-especializações
    ch_clas = discord.utils.get(guild.text_channels, name="🛡️・clãs-e-especializações")
    if not ch_clas and cat_wiki:
        ch_clas = await guild.create_text_channel(
            name="🛡️・clãs-e-especializações",
            category=cat_wiki,
            topic="Guia dos 9 clãs, pokébolas de clã, bônus elementais e ranks",
            overwrites=safe_overwrites
        )
        print("Criado canal #🛡️・clãs-e-especializações")

    # Canal: #✨・pokémons-shinies-e-raros
    ch_shinies = discord.utils.get(guild.text_channels, name="✨・pokémons-shinies-e-raros")
    if not ch_shinies and cat_wiki:
        ch_shinies = await guild.create_text_channel(
            name="✨・pokémons-shinies-e-raros",
            category=cat_wiki,
            topic="Guia de spawns de Shinies, variantes Cybers e pokémons lendários",
            overwrites=safe_overwrites
        )
        print("Criado canal #✨・pokémons-shinies-e-raros")

    # Canal: #🔔・comandos-dos-jogadores
    ch_cmds = discord.utils.get(guild.text_channels, name="🔔・comandos-dos-jogadores")
    if not ch_cmds and cat_wiki:
        ch_cmds = await guild.create_text_channel(
            name="🔔・comandos-dos-jogadores",
            category=cat_wiki,
            topic="Guia completo de comandos, atalhos do cliente e qualidade de vida",
            overwrites=safe_overwrites
        )
        print("Criado canal #🔔・comandos-dos-jogadores")

    channels = {ch.name: ch for ch in guild.text_channels}

    # =========================================================================
    # CONTEÚDO 1: #📖・sobre-o-servidor (MANIFESTO DETALHADO E RATES)
    # =========================================================================
    if ch_sobre:
        emb_sobre1 = discord.Embed(
            title="📖 O QUE É O POKÉMON RELOAD? • VISÃO GERAL",
            description=(
                "O **Pokémon Reload** é um MMORPG brasileiro completo baseado no universo Pokémon clássico "
                "com a profundidade e mecânicas táticas do Tibia (PokeTibia). Nosso projeto nasceu para resgatar "
                "a essência do verdadeiro **Hard RPG**, onde cada conquista, cada captura e cada nível alcançado "
                "têm peso real e valor no mercado do jogo!"
            ),
            color=discord.Color.from_rgb(41, 128, 185),
            timestamp=datetime.now()
        )
        emb_sobre1.add_field(
            name="🎯 Filosofia do Servidor: Hard RPG Sem 'Pay-to-Win'",
            value=(
                "• **Economia 100% Sustentável:** Itens raros têm valor real entre os jogadores. Não vendemos itens apelativos que quebram a jogabilidade.\n"
                "• **Meritocracia e Estratégia:** Conhecer fraquezas elementais, posicionamento, uso de held items e combinações de clãs é o que define as vitórias em PvP e Dungeons.\n"
                "• **Comunidade Ativa:** Sistema de comércio seguro (`🤝・comércio-trade`), leilões no site e eventos cooperativos globais."
            ),
            inline=False
        )
        emb_sobre1.add_field(
            name="🖥️ Infraestrutura Host & Dedicado",
            value=(
                f"• **Servidor Host:** Dedicado Linux Ubuntu de última geração (`{SERVER_IP}`)\n"
                f"• **Portas de Conexão:** Login Server (`{PORT_GAME_LOGIN}`) | Game World (`{PORT_GAME_WORLD}`) | Portal Web (`{PORT_SITE}`)\n"
                "• **Link de Internet:** Conexão de fibra ótica de 1 Gbps com baixa latência para todo o Brasil.\n"
                "• **Proteção Anti-DDoS:** Camadas de mitigação de ataques para garantir estabilidade 24 horas por dia, 7 dias por semana sem rollbacks!"
            ),
            inline=False
        )
        
        emb_sobre2 = discord.Embed(
            title="📊 RATES DO SERVIDOR & BALANCEAMENTO",
            description="Todas as taxas do jogo foram minuciosamente balanceadas para proporcionar uma experiência fluida, sem grind exaustivo mas sem facilidades excessivas:",
            color=discord.Color.from_rgb(52, 152, 219)
        )
        emb_sobre2.add_field(
            name="⚔️ Experiência (EXP Rate)",
            value="Estágios dinâmicos inteligentes: progressão agradável nos níveis iniciais para você explorar o mapa, tornando-se mais desafiador nos níveis avançados para valorizar os mestres treinadores.",
            inline=False
        )
        emb_sobre2.add_field(
            name="🎯 Catch Rate & Sistema Anti-Frustração (Catch Streak / Pity)",
            value=(
                "Nosso diferencial exclusivo! Ao tentar capturar um Pokémon repetidamente sem sucesso, o sistema acumula um bônus invisível de **Catch Streak**, "
                "aumentando progressivamente suas chances de sucesso a cada bola lançada até a captura garantida!"
            ),
            inline=False
        )
        emb_sobre2.add_field(
            name="💎 Loot Rate & Respawns",
            value=(
                "• **Loot Rate:** Drops calibrados para manter a economia aquecida. Stones, pedras preciosas e held items são recompensadores.\n"
                "• **Taxa de Respawn:** Spawns rápidos em todas as cidades e cavernas para evitar que você fique esperando pokémons renascerem."
            ),
            inline=False
        )
        emb_sobre2.set_footer(text="Pokémon Reload • Servidor Dedicado 24/7")
        await purge_and_send(ch_sobre, [emb_sobre1, emb_sobre2], pin_first=True)

    # =========================================================================
    # CONTEÚDO 2: #🛡️・clãs-e-especializações (OS 9 CLÃS DETALHADOS)
    # =========================================================================
    if ch_clas:
        emb_cla1 = discord.Embed(
            title="🛡️ SISTEMA DE CLÃS & ESPECIALIZAÇÕES • POKÉMON RELOAD",
            description=(
                "Ao atingir o nível necessário, você pode escolher se especializar em um dos **9 Clãs Tradicionais**.\n"
                "Pertencer a um clã concede bônus passivos monstruosos de dano e defesa para pokémons daquele elemento, "
                "além de permitir a compra e uso de **Pokébolas de Clã Exclusivas** e acesso à Sede do Clã!"
            ),
            color=discord.Color.from_rgb(230, 126, 34)
        )
        emb_cla1.add_field(
            name="🌊 Seavell (Água e Gelo)",
            value="• **Elementos:** Water / Ice\n• **Bônus:** Dano ampliado com hidrobombas e nevascas, regeneração passiva em água.\n• **Pokébola Exclusiva:** *Seavell Ball* (Taxa absurda de captura em aquáticos)\n• **Mascote Clássico:** *Shiny Politoed*",
            inline=True
        )
        emb_cla1.add_field(
            name="🔥 Volcanic (Fogo)",
            value="• **Elementos:** Fire\n• **Bônus:** Poder de queimadura ampliado, bônus crítico em clima de Sol.\n• **Pokébola Exclusiva:** *Magu Ball*\n• **Mascote Clássico:** *Shiny Ninetales*",
            inline=True
        )
        emb_cla1.add_field(
            name="🌿 Naturia (Planta e Inseto)",
            value="• **Elementos:** Grass / Bug\n• **Bônus:** Cura potencializada por Leech Seed e Giga Drain, resistências naturais.\n• **Pokébola Exclusiva:** *Janguru Ball*\n• **Mascote Clássico:** *Shiny Venusaur*",
            inline=True
        )
        emb_cla1.add_field(
            name="⚡ Raibolt (Elétrico)",
            value="• **Elementos:** Electric\n• **Bônus:** Velocidade de movimento ampliada, chance massiva de paralisia.\n• **Pokébola Exclusiva:** *Tinker Ball*\n• **Mascote Clássico:** *Shiny Raichu*",
            inline=True
        )
        emb_cla1.add_field(
            name="🌑 Malefic (Veneno e Fantasma)",
            value="• **Elementos:** Ghost / Poison\n• **Bônus:** Maldições letais e venenos cumulativos que desgastam qualquer adversário.\n• **Pokébola Exclusiva:** *Moon Ball*\n• **Mascote Clássico:** *Shiny Gengar*",
            inline=True
        )
        emb_cla1.add_field(
            name="🔮 Psycraft (Psíquico)",
            value="• **Elementos:** Psychic\n• **Bônus:** Maior amplificação de dano especial do jogo e efeitos de confusão mental contínuos.\n• **Pokébola Exclusiva:** *Sora Ball*\n• **Mascote Clássico:** *Shiny Alakazam*",
            inline=True
        )
        emb_cla1.add_field(
            name="🪨 Orebound (Pedra e Terra)",
            value="• **Elementos:** Rock / Ground\n• **Bônus:** Máxima armadura física, imunidade a terremotos e grande vida.\n• **Pokébola Exclusiva:** *Tenta Ball*\n• **Mascote Clássico:** *Shiny Golem*",
            inline=True
        )
        emb_cla1.add_field(
            name="🌪️ Wingeon (Voador e Dragão)",
            value="• **Elementos:** Flying / Dragon\n• **Bônus:** Alta esquiva de ataques em área e velocidade de voo aumentada.\n• **Pokébola Exclusiva:** *Wing Ball*\n• **Mascote Clássico:** *Shiny Pidgeot*",
            inline=True
        )
        emb_cla1.add_field(
            name="🥋 Gardestrike (Lutador e Normal)",
            value="• **Elementos:** Fighting / Normal\n• **Bônus:** Dano corpo a corpo avassalador e capacidade de quebrar defesas inimigas.\n• **Pokébola Exclusiva:** *Fighter Ball*\n• **Mascote Clássico:** *Shiny Hitmonlee*",
            inline=True
        )
        emb_cla1.add_field(
            name="📈 Como Subir de Rank no Clã?",
            value="Complete as missões do seu Mestre de Clã para avançar do Rank 1 ao Rank 5, desbloqueando acesso a pokémons cada vez mais fortes e vestimentas exclusivas!",
            inline=False
        )
        await purge_and_send(ch_clas, [emb_cla1])

    # =========================================================================
    # CONTEÚDO 3: #✨・pokémons-shinies-e-raros (SHINIES E VARIANTES CYBER)
    # =========================================================================
    if ch_shinies:
        emb_shiny = discord.Embed(
            title="✨ POKÉMONS SHINIES, CYBERS & LENDÁRIOS • GUIA OFICIAL",
            description=(
                "Os Pokémons **Shinies** são as criaturas mais cobiçadas do Pokémon Reload! "
                "Eles possuem cores alternativas, atributos de vida e ataque consideravelmente superiores "
                "e efeitos visuais de brilho contínuo ao seu redor."
            ),
            color=discord.Color.from_rgb(241, 196, 15)
        )
        emb_shiny.add_field(
            name="🌟 Como Encontrar um Shiny Selvagem?",
            value=(
                "• **Spawns Globais Raros:** Qualquer monstro que renasce no mapa tem uma chance de nascer na sua forma Shiny!\n"
                "• **Alerta Visual e Sonoro:** Quando um Shiny renasce próximo a você, um efeito de faíscas estelares aparece na tela.\n"
                "• **Pokémons Cybers:** Variantes futuristas desenvolvidas em laboratórios secretos da Silph Co., com ataques cibernéticos especiais!"
            ),
            inline=False
        )
        emb_shiny.add_field(
            name="🧬 Pokémons 100% Puros (Hundo - IV 31 Perfeito)",
            value=(
                "O Pokémon Reload possui sistema de genética real (IVs de 0 a 31 em cada um dos 6 atributos):\n"
                "• HP, Attack, Defense, Special Attack, Special Defense e Speed.\n"
                "• Pokémons com IV 31 em todos os atributos são categorizados como **Hundos Perfeitos**, o ápice do potencial competitivo!"
            ),
            inline=False
        )
        emb_shiny.add_field(
            name="🏆 Dicas Cruciais de Captura",
            value=(
                "1. Nunca enfrente um Shiny sem estoque farto de **Ultra Balls** ou **Pokébolas de Clã**.\n"
                "2. Se você possuir uma **Master Ball**, ela garante 100% de captura sem falha!\n"
                "3. Lembre-se: com o **Catch Streak**, mesmo que as primeiras bolas falhem, cada tentativa aumenta suas chances!"
            ),
            inline=False
        )
        await purge_and_send(ch_shinies, [emb_shiny])

    # =========================================================================
    # CONTEÚDO 4: #🔔・comandos-dos-jogadores (GUIA COMPLETO DE COMANDOS)
    # =========================================================================
    if ch_cmds:
        emb_cmds_full = discord.Embed(
            title="🔔 GUIA COMPLETO DE COMANDOS & ATALHOS • POKÉMON RELOAD",
            description="Todos os comandos práticos implementados para proporcionar qualidade de vida absoluta durante sua jornada:",
            color=discord.Color.from_rgb(46, 204, 113)
        )
        emb_cmds_full.add_field(
            name="📦 Coleta Automática (Auto-Loot)",
            value=(
                "`!aloot on` -> Ativa a coleta automática de itens dos monstros derrotados direto para sua bolsa.\n"
                "`!aloot off` -> Desativa o recolhimento automático.\n"
                "`!aloot status` -> Consulta se o auto-loot está ligado ou desligado."
            ),
            inline=False
        )
        emb_cmds_full.add_field(
            name="🎟️ Passe de Batalha (Battle Pass)",
            value="`!passe` ou `/passe` -> Abre imediatamente a interface do Passe de Batalha para conferir missões diárias, níveis e resgatar prêmios.",
            inline=False
        )
        emb_cmds_full.add_field(
            name="🌦️ Telemetria Climática (Weather Engine)",
            value="`!clima` ou `/clima` -> Mostra qual clima está ativo no servidor no momento (Chuva, Sol, Neve, etc.), tempo restante e buffs vigentes.",
            inline=False
        )
        emb_cmds_full.add_field(
            name="🦅 Voo Seguro & Aterrissagem",
            value="`!pousar` ou `/pousar` -> Pousa imediatamente no solo com segurança máxima se você estiver montado (Ride) ou voando (Fly), sem risco de cair em locais travados.",
            inline=False
        )
        emb_cmds_full.add_field(
            name="🚨 Alertas de Invasão",
            value="`/invasion status` -> Informa se há alguma invasão da Equipe Rocket ativa na cidade de Saffron e o status das defesas.",
            inline=False
        )
        emb_cmds_full.add_field(
            name="⌨️ Atalhos Rápidos no Teclado (OTClient)",
            value=(
                "• **Tecla M:** Abre e fecha o **Mapa em Tela Cheia** com nomes de todas as cidades e ilhas.\n"
                "• **Barra de Ação Rápida:** Arraste pokébolas, poções ou revives para os slots da tela para usar com 1 clique ou atalho F1-F12.\n"
                "• **Targeting Inteligente:** Clique no Pokémon selvagem para focar ataque automático sem perder o alvo!"
            ),
            inline=False
        )
        emb_cmds_full.set_footer(text="Pokémon Reload • Guia de Comandos do Jogador")
        await purge_and_send(ch_cmds, [emb_cmds_full], pin_first=True)

    # =========================================================================
    # CONTEÚDO 5: #🌐・site-e-downloads (PORTAL E DOWNLOADS COM DETALHES DE SUPORTE)
    # =========================================================================
    ch_downloads = channels.get("🌐・site-e-downloads")
    if ch_downloads:
        emb_portal = discord.Embed(
            title="🌐 PORTAL OFICIAL & CADASTRO • POKÉMON RELOAD",
            description=(
                "O portal oficial do **Pokémon Reload** está hospedado em servidor dedicado Linux de alta velocidade!\n"
                "Crie sua conta, gerencie personagens e acompanhe o ranking dos melhores treinadores:\n\n"
                f"🔗 **Site Principal:** [{SITE_URL}]({SITE_URL})\n"
                f"📝 **Criar Conta Grátis:** [{REGISTER_URL}]({REGISTER_URL})\n"
                f"👤 **Criar Personagem:** [{CHARACTER_URL}]({CHARACTER_URL})\n"
                f"🏆 **Top Treinadores (Highscores):** [{HIGHSCORES_URL}]({HIGHSCORES_URL})\n"
                f"🔑 **Recuperação de Acesso:** [{RECOVERY_URL}]({RECOVERY_URL})"
            ),
            color=discord.Color.from_rgb(52, 152, 219)
        )

        emb_win = discord.Embed(
            title="💻 DOWNLOAD: CLIENTE PC WINDOWS (AUTO-UPDATER)",
            description=(
                "Versão oficial para PC com otimização gráfica, suporte a DirectX 9.0c / OpenGL e Auto-Updater integrado.\n\n"
                f"📥 **Download Direto (.ZIP):** [Clique aqui para Baixar ({DL_WINDOWS_URL})]({DL_WINDOWS_URL})\n"
                f"📦 **Tamanho aproximado:** `~201 MB`\n\n"
                "**⚙️ Requisitos Recomendados:**\n"
                "• Sistema: Windows 10 / 11 (64 e 32 bits)\n"
                "• Memória RAM: 500 MB ou superior\n"
                "• Gráficos: DirectX 9.0c ou OpenGL 2.0+\n\n"
                "**🚀 Como Instalar:**\n"
                "1. Baixe o arquivo `.zip` acima.\n"
                "2. Extraia os arquivos para qualquer pasta no seu computador.\n"
                "3. Execute o arquivo **`Jogar PokeMaster.bat`** (ou `otclient_dx.exe`).\n"
                "*(Qualquer atualização de mapa, monstros ou sprites é baixada automaticamente pelo launcher!)*"
            ),
            color=discord.Color.from_rgb(46, 204, 113)
        )

        emb_apk = discord.Embed(
            title="📱 DOWNLOAD: CLIENTE ANDROID MOBILE (.APK)",
            description=(
                "Jogue onde você estiver! Cliente móvel nativo com motor híbrido Dual-Engine ARM64 + ARM32.\n\n"
                f"📥 **Download Direto (.APK):** [Clique aqui para Baixar o APK ({DL_APK_URL})]({DL_APK_URL})\n"
                f"📦 **Tamanho aproximado:** `~214 MB`\n\n"
                "**📱 Requisitos Recomendados:**\n"
                "• Sistema: Android 6.0 ou superior\n"
                "• Memória RAM: 1 GB ou superior\n"
                "• Gráficos: OpenGL ES 2.0 / 3.0\n\n"
                "**🚀 Como Instalar:**\n"
                "1. Baixe o APK diretamente no navegador do seu smartphone.\n"
                "2. Abra o arquivo e autorize 'Instalar de Fontes Desconhecidas' se solicitado.\n"
                "3. Abra o jogo, faça login com a conta criada no site e aproveite o Pokémon Reload!"
            ),
            color=discord.Color.from_rgb(155, 89, 182)
        )
        emb_apk.set_footer(text="Pokémon Reload • Arquivos 100% Verificados e Seguros")
        await purge_and_send(ch_downloads, [emb_portal, emb_win, emb_apk])

    # =========================================================================
    # CONTEÚDO 6: #📊・status-do-servidor (MONITOR AO VIVO)
    # =========================================================================
    ch_status = channels.get("📊・status-do-servidor")
    if ch_status:
        ok_site, lat_site = test_connection(SERVER_IP, PORT_SITE)
        ok_login, lat_login = test_connection(SERVER_IP, PORT_GAME_LOGIN)
        ok_world, lat_world = test_connection(SERVER_IP, PORT_GAME_WORLD)
        
        emb_status = discord.Embed(
            title="📊 MONITOR DE DISPONIBILIDADE • POKÉMON RELOAD",
            description="Telemetria e status em tempo real da infraestrutura dedicada do Pokémon Reload.",
            color=discord.Color.green() if (ok_site and ok_login and ok_world) else discord.Color.orange(),
            timestamp=datetime.now()
        )
        emb_status.add_field(
            name="🌐 Website & AAC (Porta 8088)",
            value=f"{'🟢 **ONLINE**' if ok_site else '🔴 **OFFLINE**'} (Resposta: `{lat_site}ms`)\n`{SITE_URL}`",
            inline=False
        )
        emb_status.add_field(
            name="🔑 Login Server (Porta 7171)",
            value=f"{'🟢 **ONLINE**' if ok_login else '🔴 **OFFLINE**'} (Resposta: `{lat_login}ms`)",
            inline=True
        )
        emb_status.add_field(
            name="⚔️ Game World (Porta 7172)",
            value=f"{'🟢 **ONLINE**' if ok_world else '🔴 **OFFLINE**'} (Resposta: `{lat_world}ms`)",
            inline=True
        )
        emb_status.add_field(
            name="🖥️ Infraestrutura Host",
            value=f"• Host Dedicado: Ubuntu Linux (`{SERVER_IP}`)\n• Proteção contra quedas e tráfego malicioso.",
            inline=False
        )
        emb_status.set_footer(text="Atualizado continuamente pelo Bot HBCRIATE")
        await purge_and_send(ch_status, [emb_status], pin_first=True)

    print("\n[SUCESSO COMPLETO] Todos os novos canais e guias foram implementados no Pokémon Reload!")
    await client.close()

if __name__ == "__main__":
    client.run(TOKEN)
