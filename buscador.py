import requests
from datetime import datetime
import re

def buscar_links():
    # Fontes variadas para garantir o máximo de canais
    fontes = [
        "https://iptv-org.github.io/api/streams.json",
        "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/br.m3u",
        "https://raw.githubusercontent.com/GuikiAnimes/Canal-Aberto-Brasil/main/CanalAbertoBrasil.m3u",
        "https://raw.githubusercontent.com/LITUATUI/IPTV/main/BR.m3u"
    ]
    
    canais_encontrados = []
    print(f"Iniciando busca em {len(fontes)} fontes...")

    for url in fontes:
        try:
            print(f"Escaneando: {url}")
            response = requests.get(url, timeout=20)
            if not response.ok: continue

            if url.endswith(".json"):
                dados = response.json()
                for c in dados:
                    # Filtra por ID do canal ou país
                    if c.get("url") and ("-br" in str(c.get("channel", "")) or c.get("country") == "BR"):
                        nome = str(c.get("channel")).split("-")[0].upper()
                        canais_encontrados.append({"nome": nome, "url": c.get("url")})
            
            else:
                # Parsing de listas M3U (o padrão mais comum de canais abertos)
                conteudo = response.text
                # Regex para pegar o nome do canal e a URL logo abaixo
                matches = re.findall(r'#EXTINF:.*?,(.*?)\n(http.*)', conteudo)
                for nome, link in matches:
                    nome_limpo = nome.strip().upper()
                    canais_encontrados.append({"nome": nome_limpo, "url": link.strip()})

        except Exception as e:
            print(f"Erro ao acessar {url}: {e}")

    # Remove duplicados (pela URL) e ordena por nome
    vistos = set()
    lista_final = []
    for c in canais_encontrados:
        if c['url'] not in vistos:
            vistos.add(c['url'])
            lista_final.append(c)
    
    return sorted(lista_final, key=lambda x: x['nome'])

def gerar_painel(canais):
    agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    html_template = f"""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <title>PH-TV MUNIÇÃO V3</title>
        <style>
            body {{ background: #0a0a0a; color: #00ff41; font-family: 'Segoe UI', Tahoma, sans-serif; padding: 20px; }}
            .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 15px; }}
            .card {{ background: #161616; border: 1px solid #333; padding: 15px; border-radius: 8px; transition: 0.3s; }}
            .card:hover {{ border-color: #00ff41; box-shadow: 0 0 10px #00ff4133; }}
            input {{ width: 100%; background: #000; color: #0f8; border: 1px solid #444; padding: 8px; margin: 10px 0; border-radius: 4px; font-size: 12px; }}
            button {{ background: #00ff41; color: #000; border: none; padding: 8px 15px; cursor: pointer; font-weight: bold; border-radius: 4px; width: 100%; }}
            h1 {{ color: #fff; text-align: center; margin-bottom: 5px; }}
            .stats {{ text-align: center; color: #888; margin-bottom: 30px; }}
        </style>
    </head>
    <body>
        <h1>🔍 PAINEL DE MUNIÇÃO PH-TV</h1>
        <div class="stats">Canais Online: {len(canais)} | Atualizado: {agora}</div>
        <div class="grid">
    """
    
    for c in canais:
        html_template += f"""
            <div class="card">
                <strong>{c['nome']}</strong>
                <input type="text" value="{c['url']}" id="url-{hash(c['url'])}" readonly>
                <button onclick="copy('url-{hash(c['url'])}')">COPIAR URL</button>
            </div>
        """
        
    html_template += """
        </div>
        <script>
            function copy(id) {
                var btn = document.getElementById(id);
                btn.select();
                document.execCommand("copy");
                alert("URL copiada!");
            }
        </script>
    </body>
    </html>
    """
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_template)

if __name__ == "__main__":
    lista = buscar_links()
    gerar_painel(lista)
    print(f"Finalizado: {len(lista)} canais gerados.")
