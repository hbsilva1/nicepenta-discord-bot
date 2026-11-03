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

# Links REAIS extraídos do site e arquivos
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
    print(f"[ATUALIZANDO CONTEÚDO] #{channel.name}...")
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
    # 1. #🌐・site-e-downloads (LINKS 100% REAIS E DIRETOS)
    # =========================================================================
    ch_downloads = channels.get("🌐・site-e-downloads")
    if ch_downloads:
        emb_portal = discord.Embed(
            title="🌐 PORTAL OFICIAL & CADASTRO • POKEMONSTROSBR",
            description=(
                "O portal do **PokeMonstrosBR** está hospedado em servidor dedicado de alta velocidade. "
                "Crie sua conta, gerencie personagens e acompanhe o ranking dos melhores treinadores!\n\n"
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
                "Versão completa com otimização gráfica, suporte a DirectX 9.0c / OpenGL e atualizador automático.\n\n"
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
                "2. Abra o arquivo e, se solicitado, autorize 'Instalar de Fontes Desconhecidas'.\n"
                "3. Abra o jogo, faça login com a conta criada no site e divirta-se!"
            ),
            color=discord.Color.from_rgb(155, 89, 182)
        )
        emb_apk.set_footer(text="PokeMonstrosBR • Arquivos 100% Verificados e Livres de Vírus")
        await purge_and_send(ch_downloads, [emb_portal, emb_win, emb_apk])

    # =========================================================================
    # 2. #📢・anúncios (SISTEMAS REAIS DO POKEMONSTROSBR)
    # =========================================================================
    ch_anuncios = channels.get("📢・anúncios")
    if ch_anuncios:
        emb_anuncio = discord.Embed(
            title="⚡ GRANDE RELANÇAMENTO: POKEMONSTROSBR • RPG HARD",
            description=(
                "Treinadores de todo o Brasil,\n\n"
                "O servidor renasce completamente repaginado em arquitetura dedicada **Linux Ubuntu**, "
                "reunindo o melhor do RPG clássico com inovações modernas exclusivas que transformam a jogabilidade!"
            ),
            color=discord.Color.from_rgb(230, 126, 34),
            timestamp=datetime.now()
        )
        emb_anuncio.add_field(
            name="🌦️ Sistema Climático Dinâmico (Weather Engine)",
            value=(
                "6 climas reais que afetam o mapa e os combates em tempo real: "
                "**Chuva (Rain)**, **Ensolarado (Sunny)**, **Tempestade (Thunderstorm)**, **Neve (Snow)**, **Tempestade de Areia (Sandstorm)** e **Nevoeiro (Fog)**!\n"
                "Golpes de Fogo causam dano ampliado no sol, Água e Elétrico ganham poder na chuva e tempestade, e pokémons raros aparecem durante climas específicos!"
            ),
            inline=False
        )
        emb_anuncio.add_field(
            name="🚨 Mega Evento: Invasão da Equipe Rocket em Saffron",
            value=(
                "A Equipe Rocket invadiu a grande metrópole de Saffron! Grunts e Executives fortemente armados tomam as ruas em eventos globais com drops raríssimos para quem defender a cidade!"
            ),
            inline=False
        )
        emb_anuncio.add_field(
            name="🎯 Sistema de Catch Streak & Anti-Frustração (Pity System)",
            value=(
                "Cansado de jogar centenas de pokébolas sem capturar? Nosso sistema rastreia suas tentativas consecutivas e **aumenta progressivamente a taxa de captura**, garantindo recompensa para a sua persistência!"
            ),
            inline=False
        )
        emb_anuncio.add_field(
            name="⭐ Pokémons 100% Puros (Hundo Perfeito)",
            value=(
                "Sistema exclusivo de pureza genética: Pokémons perfeitos com IV 31 em todos os 6 atributos (HP, Atk, Def, SpAtk, SpDef e Speed) e bônus de performance!"
            ),
            inline=False
        )
        emb_anuncio.add_field(
            name="🎟️ Passe de Batalha com Missões Individuais",
            value="Ganhe níveis completando missões diárias personalizadas e desbloqueie recompensas da trilha gratuita ou da trilha VIP com moedas de doação.",
            inline=False
        )
        emb_anuncio.add_field(
            name="🎅 Temporada Especial de Natal",
            value="Cidade decorada com neve, NPC Ajudante do Papai Noel na praça central, missões diárias sem trava linear e Tokens de Natal para trocar por itens exclusivos e decorações!",
            inline=False
        )
        emb_anuncio.set_footer(text="PokeMonstrosBR • Dedicado Linux 138.121.165.67")
        await purge_and_send(ch_anuncios, [emb_anuncio])

    # =========================================================================
    # 3. #📊・status-do-servidor (MONITOR REAL)
    # =========================================================================
    ch_status = channels.get("📊・status-do-servidor")
    if ch_status:
        ok_site, lat_site = test_connection(SERVER_IP, PORT_SITE)
        ok_login, lat_login = test_connection(SERVER_IP, PORT_GAME_LOGIN)
        ok_world, lat_world = test_connection(SERVER_IP, PORT_GAME_WORLD)
        
        emb_status = discord.Embed(
            title="📊 MONITOR DE DISPONIBILIDADE EM TEMPO REAL",
            description="Painel de telemetria dos serviços do PokeMonstrosBR.",
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
            value=f"• Host Dedicado: Ubuntu Linux (`{SERVER_IP}`)\n• Proteção contra quedas e firewall ativo.",
            inline=False
        )
        emb_status.set_footer(text="Atualizado pelo Bot HBCRIATE")
        await purge_and_send(ch_status, [emb_status], pin_first=True)

    # =========================================================================
    # 4. #🎟️・passe-de-batalha (DETALHES DO PASSE E MOEDA)
    # =========================================================================
    ch_passe = channels.get("🎟️・passe-de-batalha")
    if ch_passe:
        emb_passe = discord.Embed(
            title="🎟️ SISTEMA DO PASSE DE BATALHA (BATTLE PASS)",
            description=(
                "O Passe de Batalha do **PokeMonstrosBR** recompensa cada hora que você dedica ao seu treinamento!\n\n"
                "Para abrir o painel in-game, basta usar o comando:\n"
                "👉 `!passe` ou `/passe` (ou clicar no botão dedicado na barra superior do OTClient)."
            ),
            color=discord.Color.from_rgb(241, 196, 15)
        )
        emb_passe.add_field(
            name="🎯 Missões Individuais & Não-Lineares",
            value=(
                "• Cada jogador recebe suas próprias missões para concluir no seu ritmo.\n"
                "• Nada de filas ou bloqueios: derrote monstros de elementos específicos, conclua tarefas diárias e acumule pontos.\n"
                "• Ao bater a meta, seus pontos são creditados instantaneamente no seu perfil do Passe."
            ),
            inline=False
        )
        emb_passe.add_field(
            name="🎁 Trilha Gratuita (Free)",
            value="Acessível a 100% dos jogadores desde o primeiro minuto! Distribui poções especiais, pokébolas de clan, held items básicos e boost stones.",
            inline=False
        )
        emb_passe.add_field(
            name="💎 Trilha Deluxe (Moeda de Doação)",
            value=(
                "• Ativada com moedas exclusivas de doação (Donate Coins).\n"
                "• Desbloqueia cosméticos de alto escalão, skins de pokémons, montarias exclusivas, caixas místicas e held items de tiers avançados."
            ),
            inline=False
        )
        emb_passe.set_footer(text="PokeMonstrosBR • Battle Pass Season")
        await purge_and_send(ch_passe, [emb_passe])

    # =========================================================================
    # 5. #🎄・eventos-sazonais (EVENTO DE NATAL E CLIMAS)
    # =========================================================================
    ch_eventos = channels.get("🎄・eventos-sazonais")
    if ch_eventos:
        emb_natal = discord.Embed(
            title="❄️ TEMPORADA DE NATAL: A GRANDE FESTA DE GELO",
            description=(
                "O PokeMonstrosBR preparou um evento natalino completo com cidades nevadas, "
                "músicas temáticas e eventos dinâmicos que acontecem por todo o continente!"
            ),
            color=discord.Color.from_rgb(192, 57, 43)
        )
        emb_natal.add_field(
            name="🎅 NPC Ajudante do Papai Noel",
            value=(
                "• Localizado na praça central natalina de Saffron.\n"
                "• Concede missões diárias com objetivos exclusivos.\n"
                "• Recompensa: **Tokens de Natal** para serem trocados na Loja Festiva."
            ),
            inline=False
        )
        emb_natal.add_field(
            name="🎁 Loja de Recompensas de Natal",
            value="Troque seus Tokens por Gorros de Papai Noel exclusivos, bonecos de neve decorativos para suas casas, itens raros e doces natalinos com buffs de velocidade!",
            inline=False
        )
        emb_natal.add_field(
            name="⛄ Efeito de Clima Nevado (Snow Weather)",
            value="Durante o evento, nevascas repentinas ativam spawns especiais de pokémons do elemento Gelo e bônus para ataques gélidos!",
            inline=False
        )
        emb_natal.set_footer(text="PokeMonstrosBR • Eventos Sazonais")
        await purge_and_send(ch_eventos, [emb_natal])

    # =========================================================================
    # 6. #📘・guia-de-helds (HELDS X E Y DETALHADOS)
    # =========================================================================
    ch_helds = channels.get("📘・guia-de-helds")
    if ch_helds:
        emb_held = discord.Embed(
            title="🔮 GUIA COMPLETO: HELDS ITEMS (TIERS 1 A 7)",
            description=(
                "Os **Held Items** são itens de aprimoramento que você equipa no seu Pokémon para customizar "
                "seus atributos e conceder habilidades exclusivas no combate e exploração."
            ),
            color=discord.Color.from_rgb(142, 68, 173)
        )
        emb_held.add_field(
            name="⚔️ Helds Tipo X (Combate & Eficiência)",
            value=(
                "• **X-Attack:** Multiplica o ataque físico em porcentagem crescente do Tier 1 ao 7.\n"
                "• **X-Defense:** Diminui o dano físico recebido.\n"
                "• **X-SpAtk / X-SpDef:** Bônus para movimentos mágicos/especiais.\n"
                "• **X-Experience:** Amplia o ganho de experiência nas caçadas.\n"
                "• **X-Critical:** Taxa crítica de acerto com dano dobrado."
            ),
            inline=False
        )
        emb_held.add_field(
            name="🛡️ Helds Tipo Y (Habilidades & Sobrevivência)",
            value=(
                "• **Y-Regeneration:** Regenera a vida em combate e fora dele continuamente.\n"
                "• **Y-Cure:** Remove automaticamente efeitos de veneno, paralisia e sono.\n"
                "• **Y-Cut:** Concede corte de arbustos e folhagens sem necessidade de HM.\n"
                "• **Y-Ghost:** Permite ultrapassar passagens secretas etéreas."
            ),
            inline=False
        )
        emb_held.add_field(
            name="⚙️ Como Evoluir o Tier dos seus Helds?",
            value="Converse com o NPC Especialista em Helds para fundir helds menores da mesma classe e avançar até o Tier 7 máximo!",
            inline=False
        )
        emb_held.set_footer(text="PokeMonstrosBR • Guia de Helds")
        await purge_and_send(ch_helds, [emb_held])

    # =========================================================================
    # 7. #🎁・boxes-e-boost (BOXES 1-4, MEW BOX E STONES NOBRES)
    # =========================================================================
    ch_boxes = channels.get("🎁・boxes-e-boost")
    if ch_boxes:
        emb_box = discord.Embed(
            title="🎁 TABELA DE POKÉ-BOXES & SISTEMA DE BOOST",
            description="Confira os pokémons obtíveis em cada caixa e a proporção de stones para o boost.",
            color=discord.Color.from_rgb(39, 174, 96)
        )
        emb_box.add_field(
            name="📦 Categorias de Boxes",
            value=(
                "• **Box 1:** Slowpoke, Magnemite, Doduo, Seel, Grimer, Gastly, Drowzee, Voltorb, Cubone, Koffing, Shellder, Pidgeotto, Goldeen.\n"
                "• **Box 2:** Ivysaur, Charmeleon, Wartortle, Haunter, Graveler, Kadabra, Machoke, Weepinbell, Gloom.\n"
                "• **Box 3:** Fearow, Dugtrio, Arbok, Clefairy, Nidorino, Nidorina, Golbat, Dodrio, Eevee, Seadra, Jigglypuff, Parasect.\n"
                "• **Box 4:** Dragonair, Lapras, Golem, Chansey, Mr. Mime, Pinsir, Porygon, Onix, Lickitung, Clefable, Wigglytuff, Exeggutor.\n"
                "• **Mew Box:** Chance exclusiva de surpresas raras, shinies comemorativos e itens sagrados."
            ),
            inline=False
        )
        emb_box.add_field(
            name="⚡ Boost Machine (+1 até +50)",
            value=(
                "• Cada nível de boost melhora permanentemente a vida, força e resistências do Pokémon.\n"
                "• **Stones Normais:** Quantidade padrão proporcional ao boost atual.\n"
                "• **Stones Nobres (Ancient, Metal, Crystal):** **Valem o dobro**, gastando metade das pedras para subir de nível!"
            ),
            inline=False
        )
        await purge_and_send(ch_boxes, [emb_box])

    # =========================================================================
    # 8. #🗺️・mapas-kanto-hoenn (ROTAS E NAVEGAÇÃO)
    # =========================================================================
    ch_mapas = channels.get("🗺️・mapas-kanto-hoenn")
    if ch_mapas:
        emb_map = discord.Embed(
            title="🗺️ CARTOGRAFIA: CONTINENTES DE KANTO & HOENN",
            description=(
                "Nosso cliente conta com o recurso de **Mapa em Tela Cheia** e **Nomes de Cidades no Minimapa** "
                "para que você nunca se perca em suas expedições!"
            ),
            color=discord.Color.from_rgb(41, 128, 185)
        )
        emb_map.add_field(
            name="🏙️ Destaques de Kanto",
            value=(
                "• **Saffron City:** O coração do comércio, templo central e palco das invasões da Equipe Rocket.\n"
                "• **Cerulean City & Viridian:** Rotas aquáticas e florestas ideais para treinadores iniciantes e intermediários.\n"
                "• **Cinnabar Island:** Zona vulcânica extrema com cavernas profundas de pokémons de fogo e rocha."
            ),
            inline=False
        )
        emb_map.add_field(
            name="🌴 Destaques de Hoenn",
            value="Região tropical com praias, ilhas de corais e cavernas profundas com pokémons da 3ª Geração.",
            inline=False
        )
        emb_map.add_field(
            name="🧭 Atalho de Voo e Desembarque Seguro",
            value="Use o comando `!pousar` ou `/pousar` (ou o botão Land na tela) para pousar com segurança total se estiver voando (Fly) ou montado (Ride).",
            inline=False
        )
        await purge_and_send(ch_mapas, [emb_map])

    # =========================================================================
    # 9. #❓・dúvidas-e-ajuda (COMANDOS ESSENCIAIS DOS JOGADORES)
    # =========================================================================
    ch_faq = channels.get("❓・dúvidas-e-ajuda")
    if ch_faq:
        emb_cmds = discord.Embed(
            title="🎮 COMANDOS ÚTEIS PARA TODOS OS JOGADORES",
            description="Comandos práticos disponíveis para facilitar a sua jornada no PokeMonstrosBR:",
            color=discord.Color.from_rgb(26, 188, 156)
        )
        emb_cmds.add_field(
            name="📦 `!aloot on` / `!aloot off` / `!aloot status`",
            value="Ativa ou desativa a coleta automática (Auto-Loot) de itens, pedras e moedas direto para a sua bolsa ao derrotar pokémons selvagens.",
            inline=False
        )
        emb_cmds.add_field(
            name="🎟️ `!passe` ou `/passe`",
            value="Abre o painel do Passe de Batalha com suas missões individuais e recompensas da temporada.",
            inline=False
        )
        emb_cmds.add_field(
            name="🌦️ `!clima` ou `/clima`",
            value="Informa qual o clima ativo no momento no servidor (Chuva, Sol, Neve, etc.), tempo restante e buffs em vigor.",
            inline=False
        )
        emb_cmds.add_field(
            name="🦅 `!pousar` ou `/pousar`",
            value="Pousa com segurança imediata no solo se você estiver usando Fly ou Ride.",
            inline=False
        )
        emb_cmds.add_field(
            name="🚨 `/invasion status`",
            value="Verifica se há alguma invasão da Equipe Rocket acontecendo na cidade de Saffron.",
            inline=False
        )
        await purge_and_send(ch_faq, [emb_cmds])

    # =========================================================================
    # 10. #📜・regras-e-diretrizes
    # =========================================================================
    ch_regras = channels.get("📜・regras-e-diretrizes")
    if ch_regras:
        emb_regras = discord.Embed(
            title="📜 DIRETRIZES & REGRAS OFICIAIS • POKEMONSTROSBR",
            description=(
                "Para preservar a competitividade e o espírito de RPG Hard do **PokeMonstrosBR**, "
                "todos os membros e jogadores devem seguir as diretrizes abaixo:"
            ),
            color=discord.Color.from_rgb(231, 76, 60),
            timestamp=datetime.now()
        )
        emb_regras.add_field(
            name="1️⃣ Respeito e Fair Play",
            value="Ofensas de cunho discriminatório, assédio, preconceito ou difamação resultarão em silenciamento imediato ou banimento permanente.",
            inline=False
        )
        emb_regras.add_field(
            name="2️⃣ Trapaças, Macros e Bots Ilegais",
            value="O uso de programas externos não autorizados ou exploração deliberada de falhas/bugs sem reportar acarreta banimento da conta e reset de bens.",
            inline=False
        )
        emb_regras.add_field(
            name="3️⃣ Segurança de Credenciais",
            value="A Staff **JAMAIS** pedirá a sua senha de acesso. Use senhas fortes e exclusivas.",
            inline=False
        )
        emb_regras.add_field(
            name="4️⃣ Transações Externas (RMT)",
            value="Negociações envolvendo dinheiro real fora dos canais e sistemas de doação oficiais do servidor são proibidas.",
            inline=False
        )
        await purge_and_send(ch_regras, [emb_regras])

    # =========================================================================
    # 11. #🐛・reportar-bugs
    # =========================================================================
    ch_bugs = channels.get("🐛・reportar-bugs")
    if ch_bugs:
        emb_bug = discord.Embed(
            title="🐛 CENTRAL DE REPORTE DE BUGS",
            description=(
                "Encontrou um erro em algum mapa, quest, monstro ou no cliente?\n\n"
                "Copie o modelo abaixo, preencha os dados e poste neste canal para que nossa equipe de desenvolvimento corrija rapidamente:"
            ),
            color=discord.Color.from_rgb(127, 140, 141)
        )
        emb_bug.add_field(
            name="📋 Modelo de Reporte",
            value=(
                "```\n"
                "• Nome do Personagem (Nick): \n"
                "• Plataforma: [ ] PC Windows (.EXE)   [ ] Android (.APK)\n"
                "• Local / Coordenadas / Cidade: \n"
                "• Descrição da Falha: \n"
                "• Como Reproduzir o Bug: \n"
                "• Print / Vídeo (Anexo):\n"
                "```"
            ),
            inline=False
        )
        await purge_and_send(ch_bugs, [emb_bug])

    # =========================================================================
    # 12. #💡・sugestões & #💬・chat-geral
    # =========================================================================
    ch_sug = channels.get("💡・sugestões")
    if ch_sug:
        emb_sug = discord.Embed(
            title="💡 CANAL DE SUGESTÕES DA COMUNIDADE",
            description=(
                "Deseja sugerir novas missões, balanceamento de pokémons, novos climas ou melhorias no cliente?\n\n"
                "Poste sua sugestão detalhada neste canal! A comunidade apoia com 👍 ou 👎."
            ),
            color=discord.Color.from_rgb(243, 156, 18)
        )
        await purge_and_send(ch_sug, [emb_sug])

    ch_geral = channels.get("💬・chat-geral")
    if ch_geral:
        emb_geral = discord.Embed(
            title="💬 BATE-PAPO GERAL • POKEMONSTROSBR",
            description="Canal de bate-papo oficial dos treinadores de Kanto e Hoenn! Sejam bem-vindos!",
            color=discord.Color.from_rgb(52, 73, 94)
        )
        await purge_and_send(ch_geral, [emb_geral])

    print("\n[SUCESSO COMPLETO] Todos os canais foram sincronizados com dados reais do PokeMonstrosBR!")
    await client.close()

if __name__ == "__main__":
    client.run(TOKEN)
