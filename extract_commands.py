import sys
import re

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open(r'D:\POKEMASTERX\COMANDOS_ADM_GM.html', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

# Split by sections
sections = re.findall(r'<h2 class="section-title">(.*?)</h2>(.*?)(?=<h2 class="section-title">|<script>|\Z)', text, re.DOTALL)
print(f"Total de Seções: {len(sections)}")

for sec_title, sec_content in sections:
    sec_title_clean = re.sub(r'<[^>]+>', '', sec_title).strip()
    print(f"\n=== {sec_title_clean} ===")
    
    cards = re.findall(r'<div class="card">(.*?)</div>\s*</div>', sec_content, re.DOTALL)
    for card in cards:
        cmd = re.search(r'<span class="cmd-name">(.*?)</span>', card)
        badge = re.search(r'<span class="badge[^"]*">(.*?)</span>', card)
        desc = re.search(r'<div class="cmd-desc">(.*?)</div>', card, re.DOTALL)
        
        cmd_txt = re.sub(r'<[^>]+>', '', cmd.group(1)).strip() if cmd else ''
        badge_txt = badge.group(1).strip() if badge else ''
        desc_txt = re.sub(r'<[^>]+>', '', desc.group(1)).strip() if desc else ''
        
        print(f"  • [{badge_txt}] {cmd_txt} -> {desc_txt[:100]}")
