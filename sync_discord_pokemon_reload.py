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
    print(f"[SINCRONIZANDO CANAL] #{channel.name}...")
    try:
        await channel.purge(limit=25)
    except Exception as e:
        print(f"Aviso ao limpar #{channel.name}: {e}")
        
    first_msg = None
    for emb in embeds:
        msg = await channel.send(embed=emb)
        if first_msg is None:
            first_msg = msg
        await asyncio.sleep(0.4)
        
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
    
    channels = {ch.name: ch for ch in guild.text_channels}

    # =========================================================================
    # 1. #🌐・site-e-downloads (POKÉMON RELOAD)
    # =========================================================================
    ch_downloads = channels.get("🌐・site-e-downloads")
    if ch_downloads:
        emb_portal = discord.Embed(
            title="🌐 PORTAL OFICIAL & CADASTRO • POKÉMON RELOAD",
            description=(
                "O portal oficial do **Pokémon Reload** está online em servidor dedicado Linux de alta velocidade!\n"
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
    # 2. #📢・anúncios (POKÉMON RELOAD)
    # =========================================================================
    ch_anuncios = channels.get("📢・anúncios")
    if ch_anuncios:
        emb_anuncio = discord.Embed(
            title="⚡ GRANDE RELANÇAMENTO: POKÉMON RELOAD • RPG HARD",
            description=(
                "Treinadores de todo o Brasil,\n\n"
                "É oficial: o nosso servidor ressurge com sua identidade definitiva: **POKÉMON RELOAD**!\n\n"
                "Operando em infraestrutura dedicada Linux de alta performance, unindo a clássica experiência de RPG "
                "com sistemas de última geração preparados para você e sua guilda dominarem o continente!"
            ),
            color=discord.Color.from_rgb(230, 126, 34),
            timestamp=datetime.now()
        )
        emb_anuncio.add_field(
            name="🌦️ Sistema Climático Dinâmico (Weather Engine)",
            value=(
                "6 climas reais que afetam o mapa e os combates em tempo real: "
                "**Chuva (Rain)**, **Ensolarado (Sunny)**, **Tempestade (Thunderstorm)**, **Neve (Snow)**, **Tempestade de Areia (Sandstorm)** e **Nevoeiro (Fog)**!\n"
                "Golpes de Fogo causam dano ampliado no sol, Água e Elétrico ganham poder na chuva e tempestade, e spawns temáticos acontecem dinamicamente!"
            ),
            inline=False
        )
        emb_anuncio.add_field(
            name="🚨 Mega Evento: Invasão da Equipe Rocket em Saffron",
            value="A Equipe Rocket invadiu Saffron City! Participe dos eventos de defesa da cidade para conquistar itens e drops valiosos!",
            inline=False
        )
        emb_anuncio.add_field(
            name="🎯 Sistema de Catch Streak & Anti-Frustração (Pity System)",
            value="Cada tentativa consecutiva de captura sem sucesso aumenta progressivamente a sua chance, garantindo recompensa pela sua persistência!",
            inline=False
        )
        emb_anuncio.add_field(
            name="⭐ Pokémons 100% Puros (Hundo Perfeito)",
            value="Sistema de pureza genética: Pokémons perfeitos com IV 31 em todos os 6 atributos com bônus de performance e poder máximo!",
            inline=False
        )
        emb_anuncio.add_field(
            name="🎟️ Passe de Batalha com Missões Individuais",
            value="Ganhe níveis concluindo tarefas diárias sem travamento linear e desbloqueie recompensas da trilha gratuita e da trilha Deluxe com moedas de doação.",
            inline=False
        )
        emb_anuncio.add_field(
            name="🎅 Temporada Especial de Natal",
            value="Cidades com neve, NPC Ajudante do Papai Noel na praça central, missões diárias com Tokens de Natal e loja temática exclusiva!",
            inline=False
        )
        emb_anuncio.set_footer(text="Pokémon Reload • Dedicado Linux 138.121.165.67")
        await purge_and_send(ch_anuncios, [emb_anuncio])

    # =========================================================================
    # 3. #📊・status-do-servidor
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

    # =========================================================================
    # 4. #🎟️・passe-de-batalha
    # =========================================================================
    ch_passe = channels.get("🎟️・passe-de-batalha")
    if ch_passe:
        emb_passe = discord.Embed(
            title="🎟️ PASSE DE BATALHA • POKÉMON RELOAD",
            description=(
                "O Passe de Batalha do **Pokémon Reload** valoriza o seu tempo de jogo!\n\n"
                "Para consultar seu passe in-game:\n"
                "👉 `!passe` ou `/passe` (ou clique no botão no topo do cliente)."
            ),
            color=discord.Color.from_rgb(241, 196, 15)
        )
        emb_passe.add_field(
            name="🎯 Missões Individuais",
            value="Tarefas diárias para derrotar pokémons de elementos específicos, explorar dungeons e acumular pontos no seu próprio ritmo.",
            inline=False
        )
        emb_passe.add_field(
            name="🎁 Trilha Gratuita",
            value="Disponível para todos os treinadores! Conquiste poções, pokébolas de clã, helds básicos e boost stones.",
            inline=False
        )
        emb_passe.add_field(
            name="💎 Trilha Deluxe (Donate)",
            value="Ativada com moedas exclusivas de doação, desbloqueando skins, montarias, helds raros e caixas místicas.",
            inline=False
        )
        await purge_and_send(ch_passe, [emb_passe])

    # =========================================================================
    # 5. #🎄・eventos-sazonais
    # =========================================================================
    ch_eventos = channels.get("🎄・eventos-sazonais")
    if ch_eventos:
        emb_natal = discord.Embed(
            title="❄️ TEMPORADA DE NATAL • POKÉMON RELOAD",
            description="Evento natalino global com praça de Saffron nevada e desafios especiais para todos os treinadores!",
            color=discord.Color.from_rgb(192, 57, 43)
        )
        emb_natal.add_field(
            name="🎅 NPC Ajudante do Papai Noel",
            value="Localizado na praça central natalina de Saffron com missões diárias individuais concedendo **Tokens de Natal**.",
            inline=False
        )
        emb_natal.add_field(
            name="🎁 Loja Festiva",
            value="Troque seus Tokens por gorros temáticos, decorações para casas e guloseimas natalinas com buffs de corrida!",
            inline=False
        )
        await purge_and_send(ch_eventos, [emb_natal])

    # =========================================================================
    # 6. #📘・guia-de-helds
    # =========================================================================
    ch_helds = channels.get("📘・guia-de-helds")
    if ch_helds:
        emb_held = discord.Embed(
            title="🔮 GUIA COMPLETO: HELDS ITEMS • POKÉMON RELOAD",
            description="Aprimoramentos especiais para equipar no seu Pokémon do Tier 1 ao Tier 7:",
            color=discord.Color.from_rgb(142, 68, 173)
        )
        emb_held.add_field(
            name="⚔️ Helds Tipo X (Combate)",
            value="• **X-Attack:** Dano físico ampliado.\n• **X-Defense:** Redução de dano recebido.\n• **X-SpAtk / X-SpDef:** Bônus especiais.\n• **X-Experience:** Mais EXP em caçadas.\n• **X-Critical:** Chance crítica devastadora.",
            inline=False
        )
        emb_held.add_field(
            name="🛡️ Helds Tipo Y (Utilidades)",
            value="• **Y-Regeneration:** Regeneração contínua de vida.\n• **Y-Cure:** Cura passiva de veneno/paralisia/sono.\n• **Y-Cut:** Habilidade de corte sem precisar de HM.\n• **Y-Ghost:** Passagem por rotas secretas.",
            inline=False
        )
        await purge_and_send(ch_helds, [emb_held])

    # =========================================================================
    # 7. #🎁・boxes-e-boost
    # =========================================================================
    ch_boxes = channels.get("🎁・boxes-e-boost")
    if ch_boxes:
        emb_box = discord.Embed(
            title="🎁 POKÉ-BOXES & SISTEMA DE BOOST • POKÉMON RELOAD",
            description="Tabela de boxes e proporção de stones para o aprimoramento:",
            color=discord.Color.from_rgb(39, 174, 96)
        )
        emb_box.add_field(
            name="📦 Boxes 1 a 4 + Mew Box",
            value="• **Box 1:** Iniciais e rotas de entrada.\n• **Box 2:** Formas intermediárias.\n• **Box 3:** Pokémons avançados e formas finais.\n• **Box 4:** Pokémons raros de alto escalão (Lapras, Dragonair, Golem, Pinsir, etc.).\n• **Mew Box:** Surpresas lendárias e shinies comemorativos.",
            inline=False
        )
        emb_box.add_field(
            name="⚡ Boost Machine (+1 até +50)",
            value="Melhora permanentemente atributos base do Pokémon. Stones Nobres (*Ancient, Metal, Crystal*) **valem o dobro**!",
            inline=False
        )
        await purge_and_send(ch_boxes, [emb_box])

    # =========================================================================
    # 8. #🗺️・mapas-kanto-hoenn
    # =========================================================================
    ch_mapas = channels.get("🗺️・mapas-kanto-hoenn")
    if ch_mapas:
        emb_map = discord.Embed(
            title="🗺️ CARTOGRAFIA: KANTO & HOENN • POKÉMON RELOAD",
            description="Mapas expansivos com navegação em tela cheia e nomes das cidades integrados no minimapa.",
            color=discord.Color.from_rgb(41, 128, 185)
        )
        emb_map.add_field(
            name="🧭 Desembarque Seguro",
            value="Use o comando `!pousar` ou `/pousar` para aterrissar com segurança imediata de qualquer montaria ou voo.",
            inline=False
        )
        await purge_and_send(ch_mapas, [emb_map])

    # =========================================================================
    # 9. #❓・dúvidas-e-ajuda
    # =========================================================================
    ch_faq = channels.get("❓・dúvidas-e-ajuda")
    if ch_faq:
        emb_cmds = discord.Embed(
            title="🎮 COMANDOS ÚTEIS • POKÉMON RELOAD",
            description="Comandos essenciais disponíveis para todos os jogadores:",
            color=discord.Color.from_rgb(26, 188, 156)
        )
        emb_cmds.add_field(
            name="📦 `!aloot on` / `!aloot off` / `!aloot status`",
            value="Coleta automática de itens, stones e moedas para sua bolsa.",
            inline=False
        )
        emb_cmds.add_field(
            name="🎟️ `!passe` ou `/passe`",
            value="Abre o painel do Passe de Batalha com suas missões individuais.",
            inline=False
        )
        emb_cmds.add_field(
            name="🌦️ `!clima` ou `/clima`",
            value="Consulta o clima ativo e os bônus elementais em vigor.",
            inline=False
        )
        emb_cmds.add_field(
            name="🦅 `!pousar` ou `/pousar`",
            value="Pousa com segurança do Fly/Ride.",
            inline=False
        )
        emb_cmds.add_field(
            name="🚨 `/invasion status`",
            value="Verifica o andamento da invasão Rocket em Saffron.",
            inline=False
        )
        await purge_and_send(ch_faq, [emb_cmds])

    # =========================================================================
    # 10. #📜・regras-e-diretrizes, #🐛・reportar-bugs, #💡・sugestões, #💬・chat-geral
    # =========================================================================
    ch_regras = channels.get("📜・regras-e-diretrizes")
    if ch_regras:
        emb_regras = discord.Embed(
            title="📜 DIRETRIZES & REGRAS OFICIAIS • POKÉMON RELOAD",
            description="Diretrizes fundamentais para garantir a diversão, fair play e respeito mútuo em nossa comunidade.",
            color=discord.Color.from_rgb(231, 76, 60),
            timestamp=datetime.now()
        )
        emb_regras.add_field(name="1️⃣ Respeito Mútuo", value="Sem toxicidade, preconceito ou assédio.", inline=False)
        emb_regras.add_field(name="2️⃣ Zero Trapaças", value="Proibido uso de macros ilegais ou abuso de bugs.", inline=False)
        emb_regras.add_field(name="3️⃣ Segurança de Conta", value="A Staff nunca solicitará sua senha.", inline=False)
        await purge_and_send(ch_regras, [emb_regras])

    ch_bugs = channels.get("🐛・reportar-bugs")
    if ch_bugs:
        emb_bug = discord.Embed(
            title="🐛 CENTRAL DE REPORTE DE BUGS • POKÉMON RELOAD",
            description="Encontrou um problema técnico? Copie e preencha o formulário abaixo:",
            color=discord.Color.from_rgb(127, 140, 141)
        )
        emb_bug.add_field(
            name="📋 Modelo de Reporte",
            value="```\n• Nick: \n• Plataforma: [ ] PC Windows  [ ] Android APK\n• Local / Coordenadas: \n• Descrição: \n• Print / Vídeo:\n```",
            inline=False
        )
        await purge_and_send(ch_bugs, [emb_bug])

    ch_sug = channels.get("💡・sugestões")
    if ch_sug:
        emb_sug = discord.Embed(
            title="💡 CANAL DE SUGESTÕES • POKÉMON RELOAD",
            description="Envie sua ideia de balanceamento, evento ou melhoria! A comunidade vota com 👍 ou 👎.",
            color=discord.Color.from_rgb(243, 156, 18)
        )
        await purge_and_send(ch_sug, [emb_sug])

    ch_geral = channels.get("💬・chat-geral")
    if ch_geral:
        emb_geral = discord.Embed(
            title="💬 BATE-PAPO GERAL • POKÉMON RELOAD",
            description="Bate-papo oficial dos treinadores do Pokémon Reload! Sejam todos muito bem-vindos!",
            color=discord.Color.from_rgb(52, 73, 94)
        )
        await purge_and_send(ch_geral, [emb_geral])

    print("\n[SUCESSO TOTAL] Todos os canais foram sincronizados para POKÉMON RELOAD!")
    await client.close()

if __name__ == "__main__":
    client.run(TOKEN)
