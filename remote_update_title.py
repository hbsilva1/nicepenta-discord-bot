with open('/mnt/armazenamento/pokemaster/site/config.php', 'r', encoding='latin1') as f:
    text = f.read()

import re
text = re.sub(r"\$config\['site_title'\]\s*=\\s*'[^']+';", "$config['site_title'] = 'Pokémon Reload';", text)
text = text.replace("$config['site_title'] = 'PokeMontrosBR';", "$config['site_title'] = 'Pokémon Reload';")
text = text.replace("$config['site_title'] = 'PokeMaster X';", "$config['site_title'] = 'Pokémon Reload';")

with open('/mnt/armazenamento/pokemaster/site/config.php', 'w', encoding='latin1') as f:
    f.write(text)

print("Remote config.php updated cleanly!")
