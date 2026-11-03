import os
import sys
import asyncio
import discord
from dotenv import load_dotenv

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.guilds = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"[OK] Conectado como {client.user}")
    guild = client.guilds[0]
    print(f"Nome atual do servidor: {guild.name}")
    
    NEW_NAME = "✔ POKÉMON RELOAD ✔"
    try:
        await guild.edit(name=NEW_NAME, reason="Atualizacao de marca solicitada pelo dono para POKEMON RELOAD")
        print(f"[SUCESSO] Nome do servidor alterado para: {NEW_NAME}")
    except Exception as e:
        print(f"[ERRO] Nao foi possivel alterar o nome do servidor: {e}")
        
    for cat in guild.categories:
        if "COMUNIDADE" in cat.name:
            try:
                await cat.edit(name="✦ COMUNIDADE POKÉMON RELOAD")
                print(f"[CATEGORIA ATUALIZADA] {cat.name}")
            except Exception as e:
                print(f"Erro ao renomear categoria: {e}")
                
    await client.close()

if __name__ == "__main__":
    client.run(TOKEN)
