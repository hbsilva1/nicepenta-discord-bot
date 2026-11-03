# -*- coding: utf-8 -*-
import subprocess
import os
import sys

SSH_KEY = r"C:\Users\Herbert Borges\.ssh\hb_server_codex_ed25519"
SERVER = "root@192.168.1.50"
REMOTE_SITE = "/mnt/armazenamento/pokemaster/site"

def run_ssh(cmd):
    p = subprocess.run(["ssh", "-i", SSH_KEY, "-o", "StrictHostKeyChecking=no", SERVER, cmd], capture_output=True, text=True)
    if p.returncode != 0:
        print(f"[ERROR] SSH failed: {p.stderr}")
        return False
    return p.stdout

def run_scp(src, dst):
    p = subprocess.run(["scp", "-i", SSH_KEY, "-o", "StrictHostKeyChecking=no", src, f"{SERVER}:{dst}"], capture_output=True, text=True)
    if p.returncode != 0:
        print(f"[ERROR] SCP failed: {p.stderr}")
        return False
    print(f"  [SCP OK] {src} -> {dst}")
    return True

print("===================================================================")
print("POKÉMON RELOAD - DEPLOY NO SITE (http://138.121.165.67:8088)")
print("===================================================================")

# 1. ATUALIZAR CONFIG.PHP NO SERVIDOR LINUX
print("\n== PASSO 1: Atualizando config.php com 'Pokémon Reload' ==")
update_cfg_script = """
python3 -c "
with open('/mnt/armazenamento/pokemaster/site/config.php', 'r') as f:
    c = f.read()
import re
c = re.sub(r\"\\$config\\['site_title'\\]\\s*=\\s*'[^']+';\", \"\\$config['site_title'] = 'Pokémon Reload';\", c)
with open('/mnt/armazenamento/pokemaster/site/config.php', 'w') as f:
    f.write(c)
print('Site title atualizado com sucesso no config.php!')
"
"""
out = run_ssh(update_cfg_script)
print("  Output:", out.strip() if out else "OK")

# 2. UPLOAD DOS ARQUIVOS E IMAGENS
print("\n== PASSO 2: Enviando Logos e Arquivos do Tema ==")
theme_dir = r"D:\POKEMASTERX\site_modern_theme"

files_to_copy = [
    (os.path.join(theme_dir, "pokemon_reload_logo.png"), f"{REMOTE_SITE}/layout/img/pokemon_reload_logo.png"),
    (os.path.join(theme_dir, "pokemon_reload_hero.png"), f"{REMOTE_SITE}/layout/img/pokemon_reload_hero.png"),
    (os.path.join(theme_dir, "pokemontros_logo.png"), f"{REMOTE_SITE}/layout/img/pokemontros_logo.png"),
    (os.path.join(theme_dir, "pokemontros_hero.png"), f"{REMOTE_SITE}/layout/img/pokemontros_hero.png"),
    (os.path.join(theme_dir, "admin.php"), f"{REMOTE_SITE}/admin.php"),
    (os.path.join(theme_dir, "menu.php"), f"{REMOTE_SITE}/layout/menu.php"),
    (os.path.join(theme_dir, "menu.php"), f"{REMOTE_SITE}/layout/overall/menu.php"),
    (os.path.join(theme_dir, "header.php"), f"{REMOTE_SITE}/layout/overall/header.php"),
    (os.path.join(theme_dir, "footer.php"), f"{REMOTE_SITE}/layout/overall/footer.php"),
    (os.path.join(theme_dir, "aside.php"), f"{REMOTE_SITE}/layout/aside.php"),
    (os.path.join(theme_dir, "aside.php"), f"{REMOTE_SITE}/layout/overall/aside.php"),
    (os.path.join(theme_dir, "index.php"), f"{REMOTE_SITE}/index.php"),
    (os.path.join(theme_dir, "index.php"), f"{REMOTE_SITE}/layout/sub/index.php"),
    (os.path.join(theme_dir, "downloads.php"), f"{REMOTE_SITE}/downloads.php"),
    (os.path.join(theme_dir, "style.css"), f"{REMOTE_SITE}/layout/css/style.css"),
    (os.path.join(theme_dir, "resp.css"), f"{REMOTE_SITE}/layout/css/resp.css"),
]

for src, dst in files_to_copy:
    if os.path.exists(src):
        run_scp(src, dst)
    else:
        print(f"  [MISSING] {src}")

# 3. LIMPAR CACHE E REINICIAR SERVIÇOS WEB
print("\n== PASSO 3: Limpando Cache e Recarregando Servidor Web ==")
cleanup_cmd = """
chown -R www-data:www-data /mnt/armazenamento/pokemaster/site/
chmod -R 755 /mnt/armazenamento/pokemaster/site/
rm -f /mnt/armazenamento/pokemaster/site/engine/cache/*
systemctl reload nginx php8.1-fpm
echo 'Serviços recarregados e cache limpo com sucesso!'
"""
out = run_ssh(cleanup_cmd)
print(out)

print("===================================================================")
print("SITE ATUALIZADO COM SUCESSO PARA POKÉMON RELOAD!")
print("===================================================================")
