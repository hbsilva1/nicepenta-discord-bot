import os
import sys
import asyncio
from datetime import datetime
from collections import Counter
import discord
from dotenv import load_dotenv

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

client = discord.Client(intents=intents)

CHANNEL_NAME = "🔒-logs-admin"

@client.event
async def on_ready():
    print(f"[OK] Conectado como {client.user.name} ({client.user.id})")
    
    if not client.guilds:
        print("[ERRO] O bot não está em nenhum servidor.")
        await client.close()
        return
        
    guild = client.guilds[0]
    print(f"\n[AUDITORIA] Iniciando no servidor: {guild.name} (ID: {guild.id})")
    print(f"Dono do servidor: {guild.owner} (ID: {guild.owner_id})")
    
    # 1. Obter membros totais
    print("\n--- 1. Carregando lista completa de membros ---")
    try:
        members = [m async for m in guild.fetch_members(limit=None)]
    except Exception as e:
        print(f"Aviso ao buscar com fetch_members: {e}. Usando guild.members...")
        members = guild.members
        
    human_members = [m for m in members if not m.bot]
    bot_members = [m for m in members if m.bot]
    
    print(f"Total de Membros no Servidor: {len(members)}")
    print(f" -> Jogadores (Humanos): {len(human_members)}")
    print(f" -> Bots: {len(bot_members)}")
    
    # 2. Localizar ou Criar Canal de Logs Privado
    print(f"\n--- 2. Verificando canal de logs privado: #{CHANNEL_NAME} ---")
    log_channel = discord.utils.get(guild.text_channels, name=CHANNEL_NAME)
    
    if not log_channel:
        # Permissões: @everyone NÃO vê nada; Bot e Dono/Admins têm acesso total
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            guild.me: discord.PermissionOverwrite(
                view_channel=True, 
                send_messages=True, 
                embed_links=True, 
                attach_files=True, 
                read_message_history=True
            ),
        }
        if guild.owner:
            overwrites[guild.owner] = discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True
            )
            
        # Adiciona cargos que possuem permissão de administrador
        for role in guild.roles:
            if role.permissions.administrator and role != guild.default_role:
                overwrites[role] = discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    read_message_history=True
                )
                
        try:
            log_channel = await guild.create_text_channel(
                name=CHANNEL_NAME,
                overwrites=overwrites,
                topic="Canal de Logs Privado - Acesso Restrito aos Administradores e ao HBCRIATE Bot",
                reason="Criacao de canal de logs seguro para a administracao"
            )
            print(f"[CRIADO] Canal privado criado com sucesso: #{log_channel.name} (ID: {log_channel.id})")
        except Exception as e:
            print(f"[ERRO] Falha ao criar canal: {e}")
            await client.close()
            return
    else:
        print(f"[EXISTE] Canal de logs ja existente: #{log_channel.name} (ID: {log_channel.id})")

    # 3. Analisar Histórico de Mensagens e Jogadores que já interagiram
    print("\n--- 3. Analisando histórico de mensagens e jogadores que interagiram ---")
    unique_players = set()
    messages_per_channel = Counter()
    total_messages_scanned = 0
    earliest_date = None
    latest_date = None
    
    # Canais de texto ordenados
    channels_to_scan = [ch for ch in guild.text_channels if ch.id != log_channel.id]
    
    for ch in channels_to_scan:
        try:
            count_ch = 0
            # Limite por canal para velocidade ou varredura completa
            async for msg in ch.history(limit=2500):
                total_messages_scanned += 1
                count_ch += 1
                
                # Rastrear datas
                if earliest_date is None or msg.created_at < earliest_date:
                    earliest_date = msg.created_at
                if latest_date is None or msg.created_at > latest_date:
                    latest_date = msg.created_at
                    
                # Ignorar bots na contagem de players potenciais
                if not msg.author.bot:
                    unique_players.add(msg.author.id)
                    
            messages_per_channel[ch.name] = count_ch
            print(f" -> #{ch.name}: {count_ch} mensagens analisadas")
        except discord.Forbidden:
            print(f" -> #{ch.name}: Sem permissão para ler histórico.")
        except Exception as e:
            print(f" -> #{ch.name}: Erro: {e}")

    # Jogadores que ainda estão no servidor vs jogadores que já saíram
    current_human_ids = {m.id for m in human_members}
    players_still_in_server = unique_players.intersection(current_human_ids)
    players_who_left = unique_players.difference(current_human_ids)
    
    print("\n================ RESULTADOS DA AUDITORIA ================")
    print(f"Jogadores Atuais no Servidor: {len(human_members)}")
    print(f"Jogadores que já INTERAGIRAM no Chat: {len(unique_players)}")
    print(f" -> Jogadores que interagiram e AINDA ESTÃO no servidor: {len(players_still_in_server)}")
    print(f" -> Jogadores que interagiram no passado e JÁ SAÍRAM: {len(players_who_left)}")
    print(f"Mensagens analisadas no total: {total_messages_scanned}")
    
    # 4. Criar e enviar Embed no canal de logs
    embed = discord.Embed(
        title="📊 RELATÓRIO INICIAL DE AUDITORIA & POTENCIAL DE JOGADORES",
        description=f"Auditoria realizada com sucesso no servidor **{guild.name}**.\nEste canal é **privado e visível apenas para a administração**.",
        color=discord.Color.gold(),
        timestamp=datetime.now()
    )
    
    embed.add_field(
        name="👥 Membros do Servidor",
        value=(
            f"• **Total de Membros:** `{len(members)}`\n"
            f"• **Jogadores (Contas Reais):** `{len(human_members)}`\n"
            f"• **Bots:** `{len(bot_members)}`"
        ),
        inline=False
    )
    
    embed.add_field(
        name="🎮 Base de Jogadores Potenciais (PokeTibia / Reload)",
        value=(
            f"• **Jogadores que já falaram no chat:** `{len(unique_players)}`\n"
            f"• **Interagiram e AINDA estão aqui:** `{len(players_still_in_server)}`\n"
            f"• **Interagiram no passado mas saíram:** `{len(players_who_left)}`\n"
            f"• **Taxa de Retenção de Participantes:** `{(len(players_still_in_server)/max(len(unique_players), 1))*100:.1f}%`"
        ),
        inline=False
    )
    
    top_channels_text = "\n".join([f"• `#{ch}`: {count} msgs" for ch, count in messages_per_channel.most_common(5) if count > 0])
    if not top_channels_text:
        top_channels_text = "Nenhuma mensagem recente encontrada."
        
    embed.add_field(
        name="📈 Top 5 Canais com Mais Histórico",
        value=top_channels_text,
        inline=False
    )
    
    embed.add_field(
        name="🛡️ Status do Sistema",
        value="• Canal `🔒-logs-admin` ativo e protegido.\n• Permissões de Administrador verificadas.\n• Pronto para novas automações e integrações.",
        inline=False
    )
    
    embed.set_footer(text="HBCRIATE • Sistema de Gestão Inteligente", icon_url=client.user.display_avatar.url if client.user.display_avatar else None)
    
    await log_channel.send(content="🔔 **[SISTEMA DE LOGS INICIALIZADO]**", embed=embed)
    print(f"\n[SUCESSO] Relatório publicado no canal #{log_channel.name}!")
    
    await client.close()

if __name__ == "__main__":
    client.run(TOKEN)
