import os
import re

theme_dir = r"D:\POKEMASTERX\site_modern_theme"

def replace_in_file(file_path):
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    orig = content
    # Substituições principais
    content = content.replace("POKEMONTROS <span>BR</span>", "POKÉMON <span>RELOAD</span>")
    content = content.replace("POKEMONTROS BR", "POKÉMON RELOAD")
    content = content.replace("POKEMONTROSBR", "POKÉMON RELOAD")
    content = content.replace("PokeMontrosBR", "Pokémon Reload")
    content = content.replace("PokeMontros BR", "Pokémon Reload")
    content = content.replace("PokeMonstrosBR", "Pokémon Reload")
    content = content.replace("PokeMonstros BR", "Pokémon Reload")
    content = content.replace("PokeMaster X", "Pokémon Reload")
    content = content.replace("POKEMASTER X", "POKÉMON RELOAD")

    if content != orig:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"[ATUALIZADO] {os.path.basename(file_path)}")

for root, dirs, files in os.walk(theme_dir):
    for f in files:
        if f.endswith((".php", ".html", ".css", ".js")):
            replace_in_file(os.path.join(root, f))

print("Arquivos locais do tema modernizado atualizados com sucesso!")
