import os
import sys
import discord
from dotenv import load_dotenv

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.members = True
intents.guilds = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"[CONECTADO] Bot: {client.user} (ID: {client.user.id})")
    print(f"Total de Servidores: {len(client.guilds)}")
    
    for guild in client.guilds:
        print(f"\n=======================================================")
        print(f"Servidor: {guild.name} (ID: {guild.id})")
        print(f"Dono do Servidor: {guild.owner} (ID: {guild.owner_id})")
        print(f"=======================================================")
        
        # Bot member in this guild
        bot_member = guild.me
        print(f"Cargo mais alto do Bot: '{bot_member.top_role.name}' (Posição: {bot_member.top_role.position})")
        print(f"Bot é Administrador? {'SIM' if bot_member.guild_permissions.administrator else 'NÃO'}")
        
        # Procurar cargo FUNDADORES ou similar
        roles_sorted = sorted(guild.roles, key=lambda r: r.position, reverse=True)
        print("\nHierarquia de Cargos (Do mais alto para o mais baixo):")
        for r in roles_sorted:
            is_bot_role = (r == bot_member.top_role)
            tag = " <-- [CARGO DO BOT]" if is_bot_role else ""
            print(f"  [{r.position:2d}] {r.name}{tag}")
            
        print("\n--- ANÁLISE DE GESTÃO DO CARGO 'FUNDADORES' ---")
        fundadores_role = None
        for r in guild.roles:
            if "fundador" in r.name.lower():
                fundadores_role = r
                break
                
        if fundadores_role:
            print(f"Cargo encontrado: '{fundadores_role.name}' (Posição: {fundadores_role.position})")
            if bot_member.top_role.position > fundadores_role.position:
                print(">> RESULTADO: O BOT ESTÁ ACIMA de 'FUNDADORES'!")
                print("   -> Ele CONSEGUE gerenciar membros com esse cargo (exceto se o membro for o DONO absoluto do servidor).")
            elif bot_member.top_role.position == fundadores_role.position:
                print(">> RESULTADO: O BOT ESTÁ NA MESMA POSIÇÃO de 'FUNDADORES'.")
                print("   -> Ele NÃO CONSEGUE gerenciar membros com esse cargo. Precisa subir o cargo do bot.")
            else:
                print(">> RESULTADO: O BOT ESTÁ ABAIXO de 'FUNDADORES'!")
                print("   -> O Discord BLOQUEIA qualquer ação do bot contra quem tem o cargo 'FUNDADORES'.")
                print("   -> SOLUÇÃO: Arrastar o cargo 'HBCRIATE' para cima de 'FUNDADORES' nas configurações do servidor.")
        else:
            print("Nenhum cargo com nome 'FUNDADOR' encontrado neste servidor.")

    await client.close()

if __name__ == "__main__":
    client.run(TOKEN)
