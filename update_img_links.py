import os

theme_dir = r"D:\POKEMASTERX\site_modern_theme"

for root, dirs, files in os.walk(theme_dir):
    for f in files:
        if f.endswith((".php", ".html")):
            p = os.path.join(root, f)
            with open(p, "r", encoding="utf-8", errors="ignore") as fp:
                c = fp.read()
            c_new = c.replace("pokemontros_logo.png", "pokemon_reload_logo.png")
            c_new = c_new.replace("pokemontros_hero.png", "pokemon_reload_hero.png")
            if c_new != c:
                with open(p, "w", encoding="utf-8") as fp:
                    fp.write(c_new)
                print(f"[REPLACE LOGO] {f}")

print("Substituições de links de imagem concluídas.")
