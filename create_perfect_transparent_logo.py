from PIL import Image, ImageFilter
import math

src_path = r"C:\Users\Herbert Borges\.gemini\antigravity\brain\832dea22-c57d-4fb3-84c4-1940b8bd2666\pokemon_reload_logo_1793223489181.jpg"
im = Image.open(src_path).convert("RGBA")
w, h = im.size

# Carregar pixels
pixels = im.load()

# 1. Processar cada pixel:
# Remover fundo escuro com curva de transição suave (antialiasing)
# e desvanecer suavemente nas bordas (feathering) para eliminar 100% das bordas retangulares.

for y in range(h):
    # Distância vertical para a borda mais próxima
    dist_y = min(y, h - 1 - y)
    norm_y = min(1.0, dist_y / 50.0) # 50px de fade nas bordas superior e inferior
    
    for x in range(w):
        r, g, b, a = pixels[x, y]
        
        # Distância horizontal para a borda mais próxima
        dist_x = min(x, w - 1 - x)
        norm_x = min(1.0, dist_x / 80.0) # 80px de fade nas bordas laterais
        
        edge_factor = norm_x * norm_y
        
        # Brilho / Luminância perceptual
        lum = 0.299 * r + 0.587 * g + 0.114 * b
        
        # Fundo escuro (< 35) fica 100% transparente
        # Entre 35 e 75, transição suave
        # > 75 mantém sólido
        if lum <= 32:
            alpha = 0
        elif lum < 75:
            alpha = int(255 * ((lum - 32) / (75 - 32)))
        else:
            alpha = 255
            
        # Aplica o desvanecimento de borda
        final_alpha = int(alpha * edge_factor)
        
        pixels[x, y] = (r, g, b, final_alpha)

# Salvar nas pastas locais
out_nav = r"D:\POKEMASTERX\site_modern_theme\pokemon_reload_logo.png"
out_hero = r"D:\POKEMASTERX\site_modern_theme\pokemon_reload_hero.png"

im.save(out_nav, format="PNG", optimize=True)
im.save(out_hero, format="PNG", optimize=True)
im.save(r"D:\POKEMASTERX\site_modern_theme\pokemontros_logo.png", format="PNG")
im.save(r"D:\POKEMASTERX\site_modern_theme\pokemontros_hero.png", format="PNG")

print("Logo transparente gerado com sucesso!")
print("Pixels dos cantos após corte:")
print("TL:", im.getpixel((0, 0)))
print("TR:", im.getpixel((w - 1, 0)))
print("BL:", im.getpixel((0, h - 1)))
print("BR:", im.getpixel((w - 1, h - 1)))
