import requests
from datetime import datetime
import re

def buscar_links():
    # Fontes Massivas: APIs globais e Repositórios de agregadores
    fontes = [
        "https://iptv-org.github.io/api/streams.json",
        "https://raw.githubusercontent.com/iptv-org/iptv/master/index.m3u", # Index Global (Pesado)
        "https://raw.githubusercontent.com/GuikiAnimes/Canal-Aberto-Brasil/main/CanalAbertoBrasil.m3u",
        "https://raw.githubusercontent.com/LITUATUI/IPTV/main/BR.m3u",
        "https://raw.githubusercontent.com/HelmerLousas/m3u-br/main/br.m3u",
        "https://raw.githubusercontent.com/paimp/lista-iptv/master/lista.m3u",
        "https://raw.githubusercontent.com/AssignZ/Iptv-Gratis-Brasil/main/Lista%20Atualizada.m3u",
        "https://raw.githubusercontent.com/m3u8playlist/Free-IPTV-Links-Daily/master/brazil.m3u",
        "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/br.m3u",
        "https://raw.githubusercontent.com/Telesv/Documentarios/main/documentarios.m3u"
    ]
    
    canais_encontrados = []
    print(f"Iniciando Mineração PH-ULTRA...")

    for url in fontes:
        try:
            print(f"Minerando: {url}")
            # Timeout maior para listas globais que podem ter 50MB+
            response = requests.get(url, timeout=40)
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
                # REGEX AGRESSIVO: Pega tudo que tem nome e URL logo abaixo
                # Captura inclusive formatos que não seguem o padrão EXTINF perfeito
                matches = re.findall(r',(.*?)\n(http[^\s]+)', conteudo)
                
                for nome, link in matches:
                    n_upper = nome.strip().upper()
                    # Filtro de Brasil/Portugal para pegar canais em nossa língua em listas globais
                    if any(x in n_upper for x in ["BR", "BRASIL", "BRAZIL", "PORTUGUESE", "PT-BR"]):
                        # Limpa lixo do nome
                        n_limpo = re.sub(r'\[.*?\]|\(.*?\)|\d+P|HD|SD|FHD|WEB|4K|\|', '', n_upper).strip()
                        if n_limpo and len(link) > 10:
                            canais_encontrados.append({"nome": n_limpo, "url": link.strip()})
        except Exception as e:
            print(f"Erro em {url}: {e}")

    # Deduplicação Profunda
    vistos_url = set()
    lista_final = []
    
    for c in canais_encontrados:
        # Limpa tokens da URL para comparar se o link de vídeo é o mesmo
        url_base = c['url'].split('?')[0].split('|')[0].strip()
        if url_base not in vistos_url:
            vistos_url.add(url_base)
            lista_final.append(c)
    
    return sorted(lista_final, key=lambda x: x['nome'])

def gerar_painel(canais):
    agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    html_template = f"""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <title>PH-TV FINDER V7 - ULTRA</title>
        <style>
            body {{ background: #000; color: #00ff41; font-family: 'Segoe UI', sans-serif; margin: 0; }}
            .header-sticky {{ 
                position: sticky; top: 0; background: rgba(0,0,0,0.9); 
                padding: 15px; z-index: 100; border-bottom: 2px solid #00ff41;
                backdrop-filter: blur(5px); text-align: center;
            }}
            #searchBar {{ 
                width: 90%; max-width: 800px; padding: 12px; border-radius: 20px; 
                border: 1px solid #00ff41; background: #111; color: #fff; font-size: 16px;
                outline: none; margin-top: 10px;
            }}
            .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 15px; padding: 20px; }}
            .card {{ background: #111; border: 1px solid #333; padding: 12px; border-radius: 8px; font-size: 13px; }}
            .card:hover {{ border-color: #00ff41; }}
            .card strong {{ display: block; color: #fff; margin-bottom: 8px; height: 32px; overflow: hidden; }}
            input {{ width: 100%; background: #222; color: #0f8; border: none; padding: 5px; font-size: 10px; border-radius: 3px; margin-bottom: 8px; }}
            button {{ width: 100%; background: #00ff41; border: none; padding: 8px; cursor: pointer; font-weight: bold; border-radius: 4px; }}
            .hidden {{ display: none !important; }}
            .stats {{ font-size: 12px; color: #888; }}
        </style>
    </head>
    <body>
        <div class="header-sticky">
            <h1>🔍 PH-TV ULTRA FINDER</h1>
            <div class="stats">TOTAL DE SINAIS: <strong>{len(canais)}</strong> | ATUALIZADO: {agora}</div>
            <input type="text" id="searchBar" placeholder="Pesquise entre os {len(canais)} canais..." onkeyup="filter()">
        </div>
        <div class="grid" id="grid">
    """
    
    for i, c in enumerate(canais):
        sid = f"u{i}"
        html_template += f"""
            <div class="card" data-name="{c['nome']}">
                <strong>{c['nome']}</strong>
                <input type="text" value="{c['url']}" id="{sid}" readonly>
                <button onclick="copy('{sid}')">COPIAR</button>
            </div>
        """
        
    html_template += """
        </div>
        <script>
            function filter() {
                let s = document.getElementById('searchBar').value.toUpperCase();
                let cards = document.getElementsByClassName('card');
                for (let i = 0; i < cards.length; i++) {
                    let name = cards[i].getAttribute('data-name');
                    cards[i].classList.toggle('hidden', !name.includes(s));
                }
            }
            function copy(id) {
                let el = document.getElementById(id);
                el.select();
                document.execCommand("copy");
                alert("Copiado!");
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
    print(f"Pronto! {len(lista)} canais minerados.")
