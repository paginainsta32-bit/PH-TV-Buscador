import requests
from datetime import datetime
import re

def buscar_links():
    fontes = [
        "https://iptv-org.github.io/api/streams.json",
        "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/br.m3u",
        "https://raw.githubusercontent.com/GuikiAnimes/Canal-Aberto-Brasil/main/CanalAbertoBrasil.m3u",
        "https://raw.githubusercontent.com/LITUATUI/IPTV/main/BR.m3u"
    ]
    
    canais_encontrados = []
    print(f"Buscando munição em {len(fontes)} fontes...")

    for url in fontes:
        try:
            response = requests.get(url, timeout=20)
            if not response.ok: continue

            if url.endswith(".json"):
                dados = response.json()
                for c in dados:
                    if c.get("url") and ("-br" in str(c.get("channel", "")) or c.get("country") == "BR"):
                        nome = str(c.get("channel")).split("-")[0].upper()
                        canais_encontrados.append({"nome": nome, "url": c.get("url")})
            else:
                conteudo = response.text
                matches = re.findall(r'#EXTINF:.*?,(.*?)\n(http.*)', conteudo)
                for nome, link in matches:
                    canais_encontrados.append({"nome": nome.strip().upper(), "url": link.strip()})
        except Exception as e:
            print(f"Erro em {url}: {e}")

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
        <title>PH-TV MUNIÇÃO V4</title>
        <style>
            body {{ background: #0a0a0a; color: #00ff41; font-family: 'Segoe UI', sans-serif; padding: 20px; }}
            .header-sticky {{ position: sticky; top: 0; background: #0a0a0a; padding: 10px 0; z-index: 100; border-bottom: 1px solid #333; }}
            #searchBar {{ 
                width: 100%; padding: 15px; font-size: 18px; border-radius: 8px; 
                border: 2px solid #00ff41; background: #111; color: #00ff41; outline: none;
                margin-bottom: 20px; box-sizing: border-box;
            }}
            .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 15px; margin-top: 20px; }}
            .card {{ background: #161616; border: 1px solid #333; padding: 15px; border-radius: 8px; transition: 0.3s; }}
            .card:hover {{ border-color: #00ff41; }}
            input.url-input {{ width: 100%; background: #000; color: #0f8; border: 1px solid #444; padding: 8px; margin: 10px 0; border-radius: 4px; font-size: 11px; }}
            button {{ background: #00ff41; color: #000; border: none; padding: 8px 15px; cursor: pointer; font-weight: bold; border-radius: 4px; width: 100%; }}
            .hidden {{ display: none !important; }}
            h1 {{ text-align: center; margin: 0; color: #fff; }}
            .stats {{ text-align: center; color: #888; font-size: 14px; margin-bottom: 10px; }}
        </style>
    </head>
    <body>
        <div class="header-sticky">
            <h1>🔍 PH-TV FINDER</h1>
            <div class="stats">Canais: {len(canais)} | Atualizado: {agora}</div>
            <input type="text" id="searchBar" placeholder="Pesquisar canal (ex: Globo, SBT, Record...)" onkeyup="filterChannels()">
        </div>

        <div class="grid" id="channelGrid">
    """
    
    for c in canais:
        # Gerar um ID único para cada input usando hash da URL
        safe_id = f"id-{hash(c['url'])}"
        html_template += f"""
            <div class="card" data-name="{c['nome']}">
                <strong>{c['nome']}</strong>
                <input type="text" value="{c['url']}" id="{safe_id}" class="url-input" readonly>
                <button onclick="copy('{safe_id}')">COPIAR URL</button>
            </div>
        """
        
    html_template += """
        </div>
        <script>
            function filterChannels() {
                let input = document.getElementById('searchBar').value.toUpperCase();
                let grid = document.getElementById('channelGrid');
                let cards = grid.getElementsByClassName('card');

                for (let i = 0; i < cards.length; i++) {
                    let name = cards[i].getAttribute('data-name');
                    if (name.includes(input)) {
                        cards[i].classList.remove('hidden');
                    } else {
                        cards[i].classList.add('hidden');
                    }
                }
            }

            function copy(id) {
                var btn = document.getElementById(id);
                btn.select();
                document.execCommand("copy");
                alert("URL copiada para o PHflix!");
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
    print(f"Sucesso: {len(lista)} canais gerados com barra de pesquisa.")
