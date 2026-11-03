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

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

def test_connection(host, port, timeout=2.0):
    start = time.time()
    try:
        s = socket.create_connection((host, port), timeout=timeout)
        s.close()
        latency = int((time.time() - start) * 1000)
        return True, latency
    except Exception:
        return False, 0

async def purge_and_send(channel: discord.TextChannel, embeds: list, pin_first: bool = False):
    print(f"[PREENCHENDO] #{channel.name}...")
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
    print(f"Alvo: Servidor {guild.name}")
    
    channels = {ch.name: ch for ch in guild.text_channels}
    
    # -------------------------------------------------------------
    # 1. #📜・regras-e-diretrizes
    # -------------------------------------------------------------
    ch_regras = channels.get("📜・regras-e-diretrizes")
    if ch_regras:
        emb_regras = discord.Embed(
            title="📜 DIRETRIZES & REGRAS OFICIAIS • POKEMONSTROSBR",
            description=(
                "Bem-vindo à comunidade oficial do **PokeMonstrosBR**!\n"
                "Para manter um ambiente saudável, divertido e seguro para todos os treinadores, "
                "leia com atenção as diretrizes abaixo. O desconhecimento das regras não isenta punições."
            ),
            color=discord.Color.from_rgb(231, 76, 60),
            timestamp=datetime.now()
        )
        emb_regras.add_field(
            name="1️⃣ Respeito & Convivência",
            value="Trate todos os membros com educação. São proibidos qualquer forma de preconceito, racismo, assédio, toxicidade extrema ou perseguição.",
            inline=False
        )
        emb_regras.add_field(
            name="2️⃣ Uso Correto dos Canais",
            value="Mantenha as conversas em seus canais respectivos:\n• Vendas e trocas apenas no `🤝・comércio-trade`.\n• Relato de falhas técnicas apenas no `🐛・reportar-bugs`.\n• Dúvidas no `❓・dúvidas-e-ajuda`.",
            inline=False
        )
        emb_regras.add_field(
            name="3️⃣ Trapaças & Abuso de Bugs (Zero Tolerância)",
            value="É estritamente proibido o uso de macros ilegais, bots não autorizados ou programas de terceiros que modifiquem a jogabilidade. Encontrar um bug e explorá-lo sem reportar resultará em banimento definitivo.",
            inline=False
        )
        emb_regras.add_field(
            name="4️⃣ Segurança da Conta",
            value="Nunca compartilhe seus dados de login. A **Staff NUNCA solicitará sua senha** ou códigos de verificação em hipótese alguma.",
            inline=False
        )
        emb_regras.add_field(
            name="5️⃣ Comércio Externo (RMT)",
            value="É proibida a negociação de itens, contas ou pokémons por dinheiro real fora dos canais e sistemas oficiais autorizados pela administração.",
            inline=False
        )
        emb_regras.set_footer(text="PokeMonstrosBR Staff • Atualizado 2026")
        await purge_and_send(ch_regras, [emb_regras])

    # -------------------------------------------------------------
    # 2. #📢・anúncios
    # -------------------------------------------------------------
    ch_anuncios = channels.get("📢・anúncios")
    if ch_anuncios:
        emb_anuncio = discord.Embed(
            title="🔥 RELANÇAMENTO OFICIAL: BEM-VINDO AO POKEMONSTROSBR!",
            description=(
                "Treinadores de Kanto e Hoenn,\n\n"
                "É com imenso orgulho que anunciamos a nova era do nosso servidor: **PokeMonstrosBR (RPG Hard)**!\n\n"
                "Passamos semanas reconstruindo o servidor do zero em infraestrutura Linux dedicada de alta performance, "
                "trazendo uma experiência rica, balanceada e competitiva para jogadores clássicos e novos desbravadores!"
            ),
            color=discord.Color.from_rgb(230, 126, 34),
            timestamp=datetime.now()
        )
        emb_anuncio.add_field(
            name="✨ O que há de novo?",
            value=(
                "• **Novo Cliente Moderno (Dark Glass):** Interface limpa para PC e Celular (Android APK).\n"
                "• **Sistema de Helds Items:** Tiers 1 a 7 totalmente balanceados para customização tática.\n"
                "• **Passe de Batalha (Battle Pass):** Missões diárias, níveis progressivos e recompensas exclusivas.\n"
                "• **Eventos Sazonais Dinâmicos:** Sistema de Natal com missões diárias individuais e tokens especiais.\n"
                "• **Auto-Loot Unificado & Mapa Expandido:** Navegação com mapa em tela cheia e minimapa detalhado."
            ),
            inline=False
        )
        emb_anuncio.add_field(
            name="🚀 Status dos Testes",
            value="Estamos nos preparativos finais de validação. Confira o canal `🌐・site-e-downloads` para criar sua conta antecipada e baixar o cliente!",
            inline=False
        )
        emb_anuncio.set_footer(text="PokeMonstrosBR • A Grande Jornada Começa!")
        await purge_and_send(ch_anuncios, [emb_anuncio])

    # -------------------------------------------------------------
    # 3. #🌐・site-e-downloads
    # -------------------------------------------------------------
    ch_downloads = channels.get("🌐・site-e-downloads")
    if ch_downloads:
        emb_site = discord.Embed(
            title="🌐 WEBSITE OFICIAL & CRIAÇÃO DE CONTAS",
            description=(
                "Acesse nosso portal oficial para criar sua conta, gerenciar personagens, visualizar rankings e novidades:\n\n"
                "👉 **Acesse o Site Oficial:** [http://138.121.165.67:8088](http://138.121.165.67:8088)\n\n"
                "📌 **Passo a passo:**\n"
                "1. Clique no link acima.\n"
                "2. Vá em **Criar Conta / Register**.\n"
                "3. Defina seu login, senha e crie seu primeiro personagem treinador."
            ),
            color=discord.Color.from_rgb(52, 152, 219)
        )
        
        emb_clients = discord.Embed(
            title="📥 DOWNLOADS DOS CLIENTES (PC WINDOWS & ANDROID)",
            description="Escolha a plataforma de sua preferência para jogar:",
            color=discord.Color.from_rgb(46, 204, 113)
        )
        emb_clients.add_field(
            name="💻 Cliente PC Windows (.EXE)",
            value=(
                "• **Recursos:** Gráficos em alta resolução, atalhos de teclado, auto-loot integrado e auto-updater.\n"
                "• **Download:** Disponível diretamente na aba de downloads do nosso [Site Oficial](http://138.121.165.67:8088).\n"
                "• *Dica:* Não é necessário baixar o jogo todo a cada atualização; o launcher atualiza automaticamente!"
            ),
            inline=False
        )
        emb_clients.add_field(
            name="📱 Cliente Mobile Android (.APK)",
            value=(
                "• **Recursos:** Controles por toque otimizados, interface adaptativa e minimapa com nomes de locais.\n"
                "• **Instalação:** Baixe o arquivo APK pelo site, habilite a permissão de *Instalar de Fontes Desconhecidas* no Android e conclua a instalação."
            ),
            inline=False
        )
        emb_clients.set_footer(text="PokeMonstrosBR • Servidor Dedicado 138.121.165.67")
        await purge_and_send(ch_downloads, [emb_site, emb_clients])

    # -------------------------------------------------------------
    # 4. #📊・status-do-servidor
    # -------------------------------------------------------------
    ch_status = channels.get("📊・status-do-servidor")
    if ch_status:
        ok_site, lat_site = test_connection(SERVER_IP, PORT_SITE)
        ok_login, lat_login = test_connection(SERVER_IP, PORT_GAME_LOGIN)
        ok_world, lat_world = test_connection(SERVER_IP, PORT_GAME_WORLD)
        
        emb_status = discord.Embed(
            title="📊 STATUS EM TEMPO REAL DOS SERVIDORES",
            description="Painel de monitoramento contínuo da infraestrutura do PokeMonstrosBR.",
            color=discord.Color.green() if (ok_site and ok_login and ok_world) else discord.Color.orange(),
            timestamp=datetime.now()
        )
        emb_status.add_field(
            name="🌐 Website / Painel AAC (Porta 8088)",
            value=f"{'🟢 **ONLINE**' if ok_site else '🔴 **OFFLINE**'} (Latência: `{lat_site}ms`)\n`http://{SERVER_IP}:{PORT_SITE}`",
            inline=False
        )
        emb_status.add_field(
            name="🔑 Servidor de Login (Porta 7171)",
            value=f"{'🟢 **ONLINE**' if ok_login else '🔴 **OFFLINE**'} (Latência: `{lat_login}ms`)",
            inline=True
        )
        emb_status.add_field(
            name="⚔️ Servidor do Jogo / Mundo (Porta 7172)",
            value=f"{'🟢 **ONLINE**' if ok_world else '🔴 **OFFLINE**'} (Latência: `{lat_world}ms`)",
            inline=True
        )
        emb_status.add_field(
            name="🛡️ Host & Sistema",
            value="Dedicado Linux Ubuntu • Proteção Anti-DDoS Ativa",
            inline=False
        )
        emb_status.set_footer(text="Atualizado automaticamente pelo HBCRIATE Bot")
        await purge_and_send(ch_status, [emb_status], pin_first=True)

    # -------------------------------------------------------------
    # 5. #📘・guia-de-helds
    # -------------------------------------------------------------
    ch_helds = channels.get("📘・guia-de-helds")
    if ch_helds:
        emb_held1 = discord.Embed(
            title="🔮 GUIA COMPLETO: SISTEMA DE HELD ITEMS",
            description=(
                "Os **Held Items** são pedras e amuletos sagrados equipados diretamente no seu Pokémon, "
                "concedendo bônus estratégicos que mudam drasticamente o combate e a exploração!\n\n"
                "Eles são classificados por **Tiers (do Tier 1 ao Tier 7)** e divididos em duas grandes famílias: **Helds X** e **Helds Y**."
            ),
            color=discord.Color.from_rgb(155, 89, 182)
        )
        emb_held1.add_field(
            name="⚔️ Helds Tipo X (Atributos de Batalha)",
            value=(
                "• **X-Attack:** Aumenta consideravelmente o ataque físico e dano dos movimentos físicos.\n"
                "• **X-Defense:** Reduz o dano sofrido contra golpes físicos.\n"
                "• **X-SpAtk / X-SpDef:** Fortalece ou protege contra ataques mágicos/especiais.\n"
                "• **X-Experience:** Amplia em porcentagem o ganho de EXP durante o grind e caçadas.\n"
                "• **X-Critical:** Chance ampliada de acertos críticos devastadores."
            ),
            inline=False
        )
        emb_held1.add_field(
            name="🛡️ Helds Tipo Y (Utilidades e Resistências)",
            value=(
                "• **Y-Regeneration:** Regenera a vida do Pokémon gradualmente, inclusive no meio do combate.\n"
                "• **Y-Cure:** Protege contra paralisia, veneno ou sleep em intervalos regulares.\n"
                "• **Y-Cut:** Concede a habilidade de corte para avançar pela vegetação sem precisar do HM.\n"
                "• **Y-Ghost:** Permite atravessar certas passagens etéreas."
            ),
            inline=False
        )
        emb_held1.add_field(
            name="⚙️ Como Melhorar Seus Helds?",
            value="Visite o NPC Mestre dos Helds para fundir helds menores e subir de Tier (ex: 2 Helds Tier 2 + Essências = 1 Held Tier 3).",
            inline=False
        )
        emb_held1.set_footer(text="PokeMonstrosBR Wiki • Helds System")
        await purge_and_send(ch_helds, [emb_held1])

    # -------------------------------------------------------------
    # 6. #🎟️・passe-de-batalha
    # -------------------------------------------------------------
    ch_passe = channels.get("🎟️・passe-de-batalha")
    if ch_passe:
        emb_passe = discord.Embed(
            title="🎟️ GUIA DO PASSE DE BATALHA (BATTLE PASS)",
            description=(
                "O Passe de Batalha do **PokeMonstrosBR** recompensa sua dedicação no jogo!\n\n"
                "A cada temporada, uma nova trilha de recompensas exclusivas fica disponível. "
                "Conforme você realiza tarefas e acumula pontos, novos níveis são desbloqueados."
            ),
            color=discord.Color.from_rgb(241, 196, 15)
        )
        emb_passe.add_field(
            name="🎯 Missões Diárias & Individuais",
            value=(
                "• As missões são **individuais** para cada treinador.\n"
                "• Exemplos: Derrotar 30 Pokémons de determinado elemento, capturar um Pokémon específico, concluir uma dungeon ou dungeon diária.\n"
                "• Ao completar a missão, você resgata seus pontos direto no painel do jogo."
            ),
            inline=False
        )
        emb_passe.add_field(
            name="🎁 Trilha Gratuita vs Passe Premium",
            value=(
                "• **Trilha Comum (Grátis):** Aberta a todos os jogadores! Dá Poções, Pokebolas especiais, Helds básicos e Stones.\n"
                "• **Trilha Premium (Donate):** Adquirida com moedas exclusivas de doação. Desbloqueia skins exclusivas, montarias, helds raros e caixas especiais."
            ),
            inline=False
        )
        emb_passe.add_field(
            name="📱 Onde Acessar in-game?",
            value="Abra a janela do Passe pelo botão dedicado na barra superior do OTClient.",
            inline=False
        )
        emb_passe.set_footer(text="PokeMonstrosBR • Temporada Ativa")
        await purge_and_send(ch_passe, [emb_passe])

    # -------------------------------------------------------------
    # 7. #🗺️・mapas-kanto-hoenn
    # -------------------------------------------------------------
    ch_mapas = channels.get("🗺️・mapas-kanto-hoenn")
    if ch_mapas:
        emb_mapas = discord.Embed(
            title="🗺️ GUIA GEOGRÁFICO: CONTINENTES DE KANTO & HOENN",
            description=(
                "Explore um mundo gigantesco repleto de rotas secretas, cavernas perigosas e cidades icônicas!\n\n"
                "O cliente do jogo conta com **Mapa em Tela Cheia** e nomes das cidades e ilhas integrados ao minimapa."
            ),
            color=discord.Color.from_rgb(41, 128, 185)
        )
        emb_mapas.add_field(
            name="🏙️ Cidades Principais de Kanto",
            value=(
                "• **Pallet Town:** Ponto de partida dos jovens treinadores.\n"
                "• **Viridian & Pewter City:** Acesso à Floresta de Viridian e primeiro ginásio Rocha.\n"
                "• **Cerulean City:** Ginásio de Água e rotas para a Caverna dos Iniciais.\n"
                "• **Saffron City:** A grande metrópole central com conexões para todas as rotas e Dojo.\n"
                "• **Cinnabar Island:** Ilha vulcânica ideal para treino de pokémons aquáticos e fogo."
            ),
            inline=False
        )
        emb_mapas.add_field(
            name="🌴 Continente de Hoenn",
            value="Região tropical com ambientes extremos: praias de Slateport, vulcões ativos de Lavaridge e cavernas profundas de Sootopolis com spawns de pokémons da 3ª Geração.",
            inline=False
        )
        emb_mapas.add_field(
            name="🧭 Atalhos do Cliente",
            value="Pressione a tecla de atalho configurada no OTClient para expandir o mapa em tela cheia com marcadores de NPCs e Quests.",
            inline=False
        )
        emb_mapas.set_footer(text="PokeMonstrosBR • Cartografia Oficial")
        await purge_and_send(ch_mapas, [emb_mapas])

    # -------------------------------------------------------------
    # 8. #🎁・boxes-e-boost
    # -------------------------------------------------------------
    ch_boxes = channels.get("🎁・boxes-e-boost")
    if ch_boxes:
        emb_boxes = discord.Embed(
            title="🎁 SISTEMA DE POKÉ-BOXES & BOOST STONES",
            description="Entenda como funcionam as caixas de recompensa e o aprimoramento de pokémons.",
            color=discord.Color.from_rgb(46, 204, 113)
        )
        emb_boxes.add_field(
            name="📦 Lista de Boxes",
            value=(
                "• **Box 1:** Pokémons iniciais e rotas de entrada (Slowpoke, Magnemite, Gastly, Cubone, etc.).\n"
                "• **Box 2:** Formas intermediárias (Ivysaur, Charmeleon, Wartortle, Haunter, etc.).\n"
                "• **Box 3:** Pokémons avançados e formas finais (Fearow, Arbok, Eevee, Seadra, Graveler, etc.).\n"
                "• **Box 4:** Pokémons raros de alto escalão (Lapras, Dragonair, Golem, Pinsir, Chansey, Onix, Exeggutor).\n"
                "• **Mew Box:** Contém surpresas místicas e shinies raros de eventos."
            ),
            inline=False
        )
        emb_boxes.add_field(
            name="⚡ Sistema de Boost (+1 até +50)",
            value=(
                "• O boost aumenta permanentemente os atributos base do seu companheiro.\n"
                "• **Stones Normais:** Quantidade proporcional por nível de boost.\n"
                "• **Stones Nobres (Ancient, Metal, Crystal):** Valem o dobro na máquina de boost, economizando recursos!"
            ),
            inline=False
        )
        emb_boxes.set_footer(text="PokeMonstrosBR Wiki")
        await purge_and_send(ch_boxes, [emb_boxes])

    # -------------------------------------------------------------
    # 9. #🎄・eventos-sazonais
    # -------------------------------------------------------------
    ch_eventos = channels.get("🎄・eventos-sazonais")
    if ch_eventos:
        emb_natal = discord.Embed(
            title="❄️ EVENTO DE NATAL: CIDADE CONGELADA & O PAPAI NOEL",
            description=(
                "O inverno chegou ao PokeMonstrosBR com um evento global completo e dinâmico!\n\n"
                "As cidades foram cobertas pela neve e o próprio Papai Noel trouxe desafios diários para os treinadores!"
            ),
            color=discord.Color.from_rgb(192, 57, 43)
        )
        emb_natal.add_field(
            name="🎅 NPC Papai Noel & Missões Diárias",
            value=(
                "• Localizado no centro da praça principal natalina.\n"
                "• Cada dia traz uma missão exclusiva e individual (sem necessidade de sequências lineares travadas).\n"
                "• Complete as tarefas para receber **Tokens Natalinos**."
            ),
            inline=False
        )
        emb_natal.add_field(
            name="🎁 Loja de Trocas de Natal",
            value="Troque seus Tokens por Outfits exclusivas com gorros de Papai Noel, bonecos de neve para decorações de casas e itens raros de edição limitada!",
            inline=False
        )
        emb_natal.set_footer(text="PokeMonstrosBR • Temporada Natalina")
        await purge_and_send(ch_eventos, [emb_natal])

    # -------------------------------------------------------------
    # 10. #❓・dúvidas-e-ajuda
    # -------------------------------------------------------------
    ch_faq = channels.get("❓・dúvidas-e-ajuda")
    if ch_faq:
        emb_faq = discord.Embed(
            title="❓ CENTRAL DE DÚVIDAS & PERGUNTAS FREQUENTES (FAQ)",
            description="Tire suas dúvidas rápidas aqui ou converse com a comunidade!",
            color=discord.Color.from_rgb(26, 188, 156)
        )
        emb_faq.add_field(
            name="1. Como começo a jogar?",
            value="Acesse o canal `🌐・site-e-downloads`, crie sua conta no site e baixe o cliente para Windows ou Android.",
            inline=False
        )
        emb_faq.add_field(
            name="2. Esqueci minha conta ou senha, o que fazer?",
            value="Utilize a ferramenta de recuperação direto pelo painel de gerenciamento do site oficial.",
            inline=False
        )
        emb_faq.add_field(
            name="3. Posso jogar no celular Android?",
            value="Sim! Nosso cliente OTClient Mobile tem interface touch adaptada e suporte total.",
            inline=False
        )
        emb_faq.add_field(
            name="4. Como chamo a equipe de suporte?",
            value="Envie sua mensagem neste canal detalhando sua dúvida, ou use `🐛・reportar-bugs` caso tenha enfrentado um problema técnico.",
            inline=False
        )
        emb_faq.set_footer(text="PokeMonstrosBR Suporte")
        await purge_and_send(ch_faq, [emb_faq])

    # -------------------------------------------------------------
    # 11. #🐛・reportar-bugs
    # -------------------------------------------------------------
    ch_bugs = channels.get("🐛・reportar-bugs")
    if ch_bugs:
        emb_bugs = discord.Embed(
            title="🐛 CENTRAL DE REPORTE DE BUGS & ERROS",
            description=(
                "Encontrou um erro no mapa, no cliente ou na jogabilidade? Nos ajude a manter o servidor impecável!\n\n"
                "Para agilizar a correção pela nossa equipe de desenvolvimento, **copie e preencha o modelo abaixo** ao postar:"
            ),
            color=discord.Color.from_rgb(149, 165, 166)
        )
        emb_bugs.add_field(
            name="📋 Modelo de Reporte (Copie e Cole)",
            value=(
                "```\n"
                "• Nome do Personagem (Nick): \n"
                "• Plataforma: [ ] PC Windows  [ ] Android APK\n"
                "• Localização / Cidade: \n"
                "• Descrição do Bug: \n"
                "• Passo a passo para reproduzir o erro: \n"
                "• Print ou Vídeo em anexo:\n"
                "```"
            ),
            inline=False
        )
        emb_bugs.add_field(
            name="⚠️ Importante",
            value="Reportar bugs críticos e que possam comprometer a economia pode render recompensas in-game aos colaboradores!",
            inline=False
        )
        emb_bugs.set_footer(text="PokeMonstrosBR QA & Dev Team")
        await purge_and_send(ch_bugs, [emb_bugs])

    # -------------------------------------------------------------
    # 12. #💡・sugestões
    # -------------------------------------------------------------
    ch_sugestoes = channels.get("💡・sugestões")
    if ch_sugestoes:
        emb_sug = discord.Embed(
            title="💡 CENTRAL DE SUGESTÕES DA COMUNIDADE",
            description=(
                "O PokeMonstrosBR é construído ouvindo os jogadores!\n\n"
                "Deixe sua sugestão de balanceamento, novo evento, melhoria no cliente ou novas mecânicas neste canal.\n"
                "Reaja com 👍 para apoiar ideias de outros treinadores ou 👎 caso discorde."
            ),
            color=discord.Color.from_rgb(243, 156, 18)
        )
        emb_sug.set_footer(text="PokeMonstrosBR Comunidade")
        await purge_and_send(ch_sugestoes, [emb_sug])

    # -------------------------------------------------------------
    # 13. #💬・chat-geral
    # -------------------------------------------------------------
    ch_geral = channels.get("💬・chat-geral")
    if ch_geral:
        emb_geral = discord.Embed(
            title="💬 BATE-PAPO GERAL • POKEMONSTROSBR",
            description=(
                "Espaço aberto para conversas, amizades, formação de equipes de caça e resenhas!\n\n"
                "Mantenha o respeito com os colegas e siga as diretrizes do canal `📜・regras-e-diretrizes`."
            ),
            color=discord.Color.from_rgb(52, 73, 94)
        )
        await purge_and_send(ch_geral, [emb_geral])

    print("\n[SUCESSO COMPLETO] Todos os canais foram preenchidos com sucesso!")
    await client.close()

if __name__ == "__main__":
    client.run(TOKEN)
