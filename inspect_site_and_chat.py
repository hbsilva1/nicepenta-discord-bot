import urllib.request
import re
import json

print("=== 1. ANALISANDO O WEBSITE (138.121.165.67:8088) ===")
url = "http://138.121.165.67:8088"
try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=5) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
        print(f"Status 200 OK! Tamanho: {len(html)} bytes")
        titles = re.findall(r'<title>(.*?)</title>', html, re.I)
        print("Titulo da pagina:", titles)
        
        # Links
        links = re.findall(r'href=[\'"]([^\'"]+)[\'"]', html, re.I)
        downloads = [l for l in links if any(k in l.lower() for k in ['download', 'apk', 'exe', 'client', 'mediafire', 'drive'])]
        print("Links de Download encontrados:", downloads)
        
        # Sub-páginas
        subpages = [l for l in set(links) if 'subtopic=' in l or l.endswith('.php')]
        print("Subpáginas encontradas:", subpages[:15])
        
        # Buscar páginas específicas de downloads ou server info
        for sub in ['?subtopic=downloads', '?subtopic=serverinfo', '?subtopic=createaccount', '?subtopic=characters']:
            try:
                sub_url = f"{url}/{sub}"
                with urllib.request.urlopen(urllib.request.Request(sub_url, headers={'User-Agent': 'Mozilla/5.0'}), timeout=4) as sresp:
                    sub_html = sresp.read().decode('utf-8', errors='ignore')
                    sub_links = re.findall(r'href=[\'"]([^\'"]+)[\'"]', sub_html, re.I)
                    sub_dl = [l for l in sub_links if any(k in l.lower() for k in ['download', 'apk', 'exe', 'client', 'mediafire', 'drive', '.zip', '.rar'])]
                    if sub_dl:
                        print(f"Downloads na subpagina {sub}:", sub_dl)
            except Exception as se:
                pass
except Exception as e:
    print("Erro ao acessar site:", e)

print("\n=== 2. ANALISANDO O TRANSCRIPT DA CONVERSA b95147c3 ===")
transcript_path = r"C:\Users\Herbert Borges\.gemini\antigravity\brain\b95147c3-f6cb-42f6-b178-cd5d3b899074\.system_generated\logs\transcript.jsonl"

keywords = [
    'download', 'apk', 'exe', 'cliente', 'site', 'ip', 'porta', 'passe', 'natal', 
    'pokemontrosbr', 'held', 'box', 'clan', 'moeda', 'crystal', 'donate', 
    'comandos', 'xp', 'stage', 'catch', 'autoloot'
]

matches = []
with open(transcript_path, 'r', encoding='utf-8') as f:
    for line_idx, line in enumerate(f):
        data = json.loads(line)
        content = data.get('content', '')
        if any(k in content.lower() for k in keywords):
            matches.append((data.get('type'), data.get('source'), content))

print(f"Total de mensagens relevantes encontradas no chat: {len(matches)}")
for m_type, m_source, m_content in matches[-20:]:
    print(f"\n[{m_type} | {m_source}]")
    print(m_content[:300].replace('\n', ' '))
