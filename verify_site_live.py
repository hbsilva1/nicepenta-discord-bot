import urllib.request
import re

url = "http://138.121.165.67:8088"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=5) as resp:
    html = resp.read().decode('utf-8', errors='ignore')
    titles = re.findall(r'<title>(.*?)</title>', html, re.I)
    print("PAGE TITLE:", titles)
    brands = re.findall(r'class="brand-text">(.*?)</span>', html, re.I)
    print("BRAND TEXT:", brands)
    badges = re.findall(r'class="hero-badge-tag">(.*?)</div>', html, re.I | re.DOTALL)
    print("HERO BADGE:", [re.sub(r'<[^>]+>', ' ', b).strip() for b in badges])
    logos = re.findall(r'src="([^"]*logo[^"]*)"', html, re.I)
    print("LOGOS IN PAGE:", logos)
