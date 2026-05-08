import requests
from datetime import datetime
import re

def buscar_links():
    # Mistura de APIs, Repositórios GitHub e Listas dinâmicas
    fontes = [
        "https://iptv-org.github.io/api/streams.json",
        "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/br.m3u",
        "https://raw.githubusercontent.com/GuikiAnimes/Canal-Aberto-Brasil/main/CanalAbertoBrasil.m3u",
        "https://raw.githubusercontent.com/LITUATUI/IPTV/main/BR.m3u",
        "https://raw.githubusercontent.com/HelmerLousas/m3u-br/main/br.m3u",
        "https://raw.githubusercontent.com/Telesv/Documentarios/main/documentarios.m3u",
        "https://raw.githubusercontent.com/paimp/lista-iptv/master/lista.m3u",
        "https://raw.githubusercontent.com/yanosho/open-iptv/master/streams/br.m3u",
        "https://raw.githubusercontent.com/AssignZ/Iptv-Gratis-Brasil/main/Lista%20Atualizada.m3u",
        "https://iptv-org.github.io/iptv/countries/br.m3u"
    ]
    
    canais_encontrados = []
    print(f"Iniciando varredura massiva em {len(fontes)} bases de dados...")

    for url in fontes:
        try:
            print(f"Extraindo de: {url}")
            # Aumentei o timeout porque algumas listas são pesadas
            response = requests.get(url, timeout=30)
            if not response.ok: continue

            if url.endswith(".json"):
                dados = response.json()
                for c in dados:
                    if c.get("url"):
                        chan_id = str(c.get("channel", "")).lower()
                        country = str(c.get("country", "")).lower()
                        if "-br" in chan_id or country == "br":
                            nome = chan_id.split("-")[0].upper()
                            canais_encontrados.append({"nome": nome, "url": c.get("url")})
            else:
                conteudo = response.text
                # Regex Ninja: Pega o nome do canal em listas M3U muito bagunçadas
                # Procura por qualquer coisa após a vírgula e captura a URL HTTP/HTTPS/RTSP
                pattern = re.compile(r'#EXTINF:.*?,(.*?)\n(?:#.*?\n)*(http[^\s\n\r]+)')
                matches = pattern.findall(conteudo)
                
                for nome, link in matches:
                    nome_limpo = nome.strip().upper()
                    # Remove tags comuns de listas (ex: [pt-br], (720p))
                    nome_limpo = re.sub(r'\[.*?\]|\(.*?\)|\d+P|HD|SD|FHD', '', nome_limpo).strip()
                    if nome_limpo and len(link) > 10:
                        canais_encontrados.append({"nome": nome_limpo, "url": link.strip()})
        except Exception as e:
            print(f"Falha na fonte {url}: {e}")

    # Limpeza e Deduplicação por URL e Nome
    vistos_url = set()
    lista_final = []
    
    for c in canais_encontrados:
        u = c['url'].split("?")[0] # Remove tokens da URL para comparar se é o mesmo sinal
        if u not in vistos_url:
            vistos_url.add(u)
            lista_final.append(c)
    
    return sorted(lista_final, key=lambda x: x['nome'])

def gerar_painel(canais):
    agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    html_template = f"""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <title>PH-TV FINDER ULTIMATE</title>
        <style>
            body {{ background: #050505; color: #00ff41; font-family: 'Segoe UI', sans-serif; margin: 0; padding: 0; }}
            .container {{ padding: 20px; }}
            .header-sticky {{ 
                position: sticky; top: 0; background: rgba(5,5,5,0.95); 
                padding: 20px; z-index: 100; border-bottom: 2px solid #00ff41;
                backdrop-filter: blur(10px);
            }}
            #searchBar {{ 
                width: 100%; padding: 15px; font-size: 18px; border-radius: 30px; 
                border: 2px solid #333; background: #111; color: #00ff41; outline: none;
                box-sizing: border-box; transition: 0.3s;
            }}
            #searchBar:focus {{ border-color: #00ff41; box-shadow: 0 0 15px #00ff4133; }}
            .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; margin-top: 20px; }}
            .card {{ 
                background: #111; border: 1px solid #222; padding: 15px; border-radius: 12px; 
                transition: 0.3s; display: flex; flex-direction: column; justify-content: space-between;
            }}
            .card:hover {{ border-color: #00ff41; transform: translateY(-5px); background: #161616; }}
            .card strong {{ color: #fff; font-size: 16px; margin-bottom: 10px; display: block; }}
            input.url-input {{ 
                width: 100%; background: #000; color: #0f8; border: 1px solid #333; 
                padding: 10px; margin-bottom: 10px; border-radius: 6px; font-size: 11px; font-family: monospace; 
            }}
            button {{ 
                background: #00ff41; color: #000; border: none; padding: 12px; 
                cursor: pointer; font-weight: bold; border-radius: 8px; transition: 0.2s;
            }}
            button:active {{ transform: scale(0.95); }}
            .hidden {{ display: none !important; }}
            h1 {{ text-align: center; margin: 0; font-size: 28px; color: #fff; letter-spacing: 2px; }}
            .stats {{ text-align: center; color: #888; margin: 10px 0; font-size: 14px; }}
        </style>
    </head>
    <body>
        <div class="header-sticky">
            <h1>🔍 PH-TV MUNIÇÃO MASSIVA</h1>
            <div class="stats">Sinais Únicos Detectados: <strong>{len(canais)}</strong> | Atualizado em: {agora}</div>
            <input type="text" id="searchBar" placeholder="Pesquisar entre os {len(canais)} canais..." onkeyup="filter()">
        </div>

        <div class="container">
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
        </div>
        <script>
            function filter() {
                let val = document.getElementById('searchBar').value.toUpperCase();
                let cards = document.getElementsByClassName('card');
                for (let i = 0; i < cards.length; i++) {
                    let name = cards[i].getAttribute('data-name');
                    cards[i].classList.toggle('hidden', !name.includes(val));
                }
            }
            function copy(id) {
                let el = document.getElementById(id);
                el.select();
                document.execCommand("copy");
                let b = el.nextElementSibling;
                let t = b.innerText;
                b.innerText = "COPIADO!";
                b.style.background = "#fff";
                setTimeout(() => { b.innerText = t; b.style.background = "#00ff41"; }, 1000);
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
    print(f"Finalizado: {len(lista)} canais no painel.")
