import subprocess

SSH_KEY = r"C:\Users\Herbert Borges\.ssh\hb_server_codex_ed25519"
SERVER = "root@192.168.1.50"

script = """python3 -c "
with open('/mnt/armazenamento/pokemaster/site/config.php', 'r', encoding='latin1') as f:
    text = f.read()

import re
text = re.sub(r\"\\$config\\['site_title'\\]\\s*=\\s*'.*?';\", \"$config['site_title'] = 'Pokémon Reload';\", text)

with open('/mnt/armazenamento/pokemaster/site/config.php', 'w', encoding='latin1') as f:
    f.write(text)

print('Updated successfully!')
" """

p = subprocess.run(["ssh", "-i", SSH_KEY, "-o", "StrictHostKeyChecking=no", SERVER, script], capture_output=True, text=True)
print("Output:", p.stdout, p.stderr)

p_check = subprocess.run(["ssh", "-i", SSH_KEY, "-o", "StrictHostKeyChecking=no", SERVER, "grep 'site_title' /mnt/armazenamento/pokemaster/site/config.php"], capture_output=True, text=True)
print("Config:", p_check.stdout)
