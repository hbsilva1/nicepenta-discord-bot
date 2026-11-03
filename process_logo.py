import os
from PIL import Image, ImageEnhance

src_path = r"C:\Users\Herbert Borges\.gemini\antigravity\brain\832dea22-c57d-4fb3-84c4-1940b8bd2666\pokemon_reload_logo_1793223489181.jpg"
out_dir = r"D:\POKEMASTERX\site_modern_theme"

im = Image.open(src_path).convert("RGBA")
print("Original size:", im.size)

# 1. Salvar Hero Image em alta resolução
hero_path = os.path.join(out_dir, "pokemon_reload_hero.png")
im.save(hero_path, format="PNG", optimize=True)
print(f"Salvo hero: {hero_path}")

# 2. Criar versão do logo com recorte / transparência para a barra de navegação e cabeçalho
# O logo gerado possui fundo escuro de estúdio. Vamos criar uma versão otimizada para logo
logo_path = os.path.join(out_dir, "pokemon_reload_logo.png")
# Redimensionar para tamanho ideal de logo sem perder nitidez
im_logo = im.copy()
im_logo.save(logo_path, format="PNG", optimize=True)
print(f"Salvo logo: {logo_path}")

# Atualizar também com os nomes legados caso algum arquivo ainda aponte para pokemontros_logo.png
im.save(os.path.join(out_dir, "pokemontros_logo.png"), format="PNG")
im.save(os.path.join(out_dir, "pokemontros_hero.png"), format="PNG")
print("Assets sincronizados com sucesso!")
