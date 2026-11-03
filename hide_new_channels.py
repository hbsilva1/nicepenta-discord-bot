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
intents.message_content = True
client = discord.Client(intents=intents)

TARGET_CATEGORIES = [
    "✦ BEM-VINDO & INFOS",
    "✦ COMUNIDADE POKEMON",
    "✦ WIKI & GUIAS",
    "✦ SUPORTE & FEEDBACK",
    "🛡️ ADMINISTRAÇÃO"
]

@client.event
async def on_ready():
    print(f"[OK] Conectado como {client.user} ({client.user.id})")
    guild = client.guilds[0]
    print(f"Alvo: {guild.name}")
    
    admin_roles = [r for r in guild.roles if r.permissions.administrator and r != guild.default_role]
    print(f"Cargos com Administrador: {[r.name for r in admin_roles]}")
    
    for category in guild.categories:
        if category.name in TARGET_CATEGORIES:
            print(f"\n[TRANCANDO CATEGORIA] {category.name}")
            
            # Montar permissões: @everyone NÃO vê nada; Bot e Admins veem tudo
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                guild.me: discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    manage_channels=True,
                    embed_links=True
                )
            }
            if guild.owner:
                overwrites[guild.owner] = discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True
                )
            for role in admin_roles:
                overwrites[role] = discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True
                )
                
            # Atualiza categoria
            await category.edit(overwrites=overwrites)
            
            # Sincroniza e força em cada canal filho
            for ch in category.text_channels:
                ch_overwrites = ch.overwrites
                ch_overwrites[guild.default_role] = discord.PermissionOverwrite(view_channel=False)
                ch_overwrites[guild.me] = discord.PermissionOverwrite(view_channel=True, send_messages=True, embed_links=True)
                if guild.owner:
                    ch_overwrites[guild.owner] = discord.PermissionOverwrite(view_channel=True, send_messages=True)
                for role in admin_roles:
                    ch_overwrites[role] = discord.PermissionOverwrite(view_channel=True, send_messages=True)
                    
                await ch.edit(overwrites=ch_overwrites)
                print(f"  🔒 #{ch.name} -> Invisível para membros comuns (@everyone view_channel=False)")
                await asyncio.sleep(0.2)
                
    print("\n[SUCESSO] Todas as categorias e canais foram ocultados para membros normais!")
    await client.close()

if __name__ == "__main__":
    client.run(TOKEN)
