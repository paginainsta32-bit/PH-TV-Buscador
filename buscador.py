import requests
from datetime import datetime
import re

def buscar_links():
    # Fontes atualizadas e testadas (incluindo repositórios gigantes)
    fontes = [
        "https://iptv-org.github.io/api/streams.json",
        "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/br.m3u",
        "https://raw.githubusercontent.com/GuikiAnimes/Canal-Aberto-Brasil/main/CanalAbertoBrasil.m3u",
        "https://raw.githubusercontent.com/LITUATUI/IPTV/main/BR.m3u",
        "https://raw.githubusercontent.com/HelmerLousas/m3u-br/main/br.m3u",
        "https://raw.githubusercontent.com/Telesv/Documentarios/main/documentarios.m3u",
        "https://raw.githubusercontent.com/paimp/lista-iptv/master/lista.m3u"
    ]
    
    canais_encontrados = []
    print(f"Buscando munição em {len(fontes)} fontes...")

    for url in fontes:
        try:
            print(f"Escaneando: {url}")
            response = requests.get(url, timeout=25)
            if not response.ok: continue

            if url.endswith(".json"):
                dados = response.json()
                for c in dados:
                    if c.get("url") and ("-br" in str(c.get("channel", "")) or c.get("country") == "BR"):
                        nome = str(c.get("channel")).split("-")[0].upper()
                        canais_encontrados.append({"nome": nome, "url": c.get("url")})
            else:
                conteudo = response.text
                # REGEX TURBINADO: Pega o nome após a vírgula e a URL na linha seguinte ou depois
                # Este padrão ignora tags extras no meio do caminho
                matches = re.findall(r'#EXTINF:.*?,(.*?)\n(?:#.*?\n)*(http[^\s]+)', conteudo)
                
                for nome, link in matches:
                    nome_limpo = nome.strip().upper()
                    # Filtra apenas se não for vazio e for um link m3u8 ou ts
                    if nome_limpo and ("http" in link):
                        canais_encontrados.append({"nome": nome_limpo, "url": link.strip()})
        except Exception as e:
            print(f"Erro em {url}: {e}")

    # DEDUPLICAÇÃO E LIMPEZA
    vistos_url = set()
    lista_final = []
    
    for c in canais_encontrados:
        # Remove canais com nomes genéricos ou links de rádio se houver
        url_lower = c['url'].lower()
        if c['url'] not in vistos_url and (".m3u8" in url_lower or ".ts" in url_lower or "/" in url_lower):
            vistos_url.add(c['url'])
            lista_final.append(c)
    
    # Ordena alfabeticamente
    return sorted(lista_final, key=lambda x: x['nome'])

def gerar_painel(canais):
    agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    html_template = f"""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <title>PH-TV MUNIÇÃO V6</title>
        <style>
            body {{ background: #050505; color: #00ff41; font-family: 'Segoe UI', sans-serif; padding: 20px; }}
            .header-sticky {{ position: sticky; top: 0; background: #050505; padding: 15px 0; z-index: 100; border-bottom: 2px solid #222; }}
            #searchBar {{ 
                width: 100%; padding: 15px; font-size: 18px; border-radius: 8px; 
                border: 2px solid #00ff41; background: #111; color: #00ff41; outline: none;
                box-sizing: border-box; box-shadow: 0 0 15px rgba(0,255,65,0.1);
            }}
            .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 15px; margin-top: 25px; }}
            .card {{ background: #111; border: 1px solid #222; padding: 15px; border-radius: 8px; transition: 0.2s; position: relative; overflow: hidden; }}
            .card:hover {{ border-color: #00ff41; background: #161616; }}
            .card strong {{ display: block; margin-bottom: 10px; font-size: 16px; color: #fff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
            input.url-input {{ width: 100%; background: #000; color: #0f8; border: 1px solid #333; padding: 8px; margin-bottom: 10px; border-radius: 4px; font-size: 10px; font-family: monospace; }}
            button {{ background: #00ff41; color: #000; border: none; padding: 10px; cursor: pointer; font-weight: bold; border-radius: 4px; width: 100%; transition: 0.2s; }}
            button:hover {{ background: #00cc33; transform: scale(1.02); }}
            .hidden {{ display: none !important; }}
            h1 {{ text-align: center; margin: 0 0 10px 0; color: #fff; font-size: 24px; letter-spacing: 2px; }}
            .stats {{ text-align: center; color: #888; font-size: 14px; margin-bottom: 10px; }}
        </style>
    </head>
    <body>
        <div class="header-sticky">
            <h1>🔍 PH-TV MUNIÇÃO BR</h1>
            <div class="stats">Canais Carregados: <strong>{len(canais)}</strong> | Atualizado: {agora}</div>
            <input type="text" id="searchBar" placeholder="Pesquisar entre os {len(canais)} canais..." onkeyup="filterChannels()">
        </div>

        <div class="grid" id="channelGrid">
    """
    
    for i, c in enumerate(canais):
        safe_id = f"id-{i}"
        html_template += f"""
            <div class="card" data-name="{c['nome']}">
                <strong>{c['nome']}</strong>
                <input type="text" value="{c['url']}" id="{safe_id}" class="url-input" readonly>
                <button onclick="copy('{safe_id}')">COPIAR LINK</button>
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
                // Feedback visual simples
                let originalText = event.target.innerText;
                event.target.innerText = "COPIADO!";
                event.target.style.background = "#fff";
                setTimeout(() => {
                    event.target.innerText = originalText;
                    event.target.style.background = "#00ff41";
                }, 1000);
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
    print(f"Sucesso: {len(lista)} canais gerados.")
