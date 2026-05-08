import requests
from datetime import datetime
import re

def buscar_links():
    # Fontes de altíssimo volume (algumas têm milhares de links)
    fontes = [
        "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/br.m3u",
        "https://raw.githubusercontent.com/GuikiAnimes/Canal-Aberto-Brasil/main/CanalAbertoBrasil.m3u",
        "https://raw.githubusercontent.com/LITUATUI/IPTV/main/BR.m3u",
        "https://raw.githubusercontent.com/HelmerLousas/m3u-br/main/br.m3u",
        "https://raw.githubusercontent.com/paimp/lista-iptv/master/lista.m3u",
        "https://raw.githubusercontent.com/AssignZ/Iptv-Gratis-Brasil/main/Lista%20Atualizada.m3u",
        "https://raw.githubusercontent.com/Deivid-Souto/IPTV-Brasil/main/canais.m3u",
        "https://raw.githubusercontent.com/estebandiazp/Lista-IPTV-Brasil/master/Brasil.m3u",
        "https://raw.githubusercontent.com/maikofreitas/TV_ABERTA/main/tv_aberta.m3u",
        "https://raw.githubusercontent.com/Telesv/Documentarios/main/documentarios.m3u",
        "https://iptv-org.github.io/iptv/countries/br.m3u",
        "https://raw.githubusercontent.com/joao-p-marques/iptv-br/master/br.m3u"
    ]
    
    canais_encontrados = []
    print(f"Iniciando varredura em massa...")

    for url in fontes:
        try:
            print(f"Minerando: {url}")
            # User-Agent é vital para não ser bloqueado por servidores mais rígidos
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(url, timeout=35, headers=headers)
            if not response.ok: continue

            conteudo = response.text
            # Regex que aceita quase tudo: captura o que vem depois da vírgula e a URL abaixo
            matches = re.findall(r'#EXTINF:.*?,(.*?)\n(http[^\s\n\r]+)', conteudo)
            
            for nome, link in matches:
                n_upper = nome.strip().upper()
                if n_upper and len(link) > 10:
                    # Limpeza agressiva para facilitar a sua pesquisa no site
                    n_limpo = re.sub(r'\[.*?\]|\(.*?\)|\d+P|HD|SD|FHD|4K|\||★|►|TV|CHANNEL|ONLINE', '', n_upper).strip()
                    if not n_limpo: n_limpo = "CANAL SEM NOME"
                    canais_encontrados.append({"nome": n_limpo, "url": link.strip()})
        except Exception as e:
            print(f"Erro em {url}: {e}")

    # Deduplicação por URL (Ignora parâmetros de token para achar duplicados reais)
    vistos_url = set()
    lista_final = []
    
    for c in canais_encontrados:
        url_base = c['url'].split('?')[0].lower().strip()
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
        <title>PH-TV HYPER FINDER</title>
        <style>
            body {{ background: #050505; color: #00ff41; font-family: 'Segoe UI', sans-serif; margin: 0; }}
            .header {{ 
                position: sticky; top: 0; background: rgba(5,5,5,0.95); 
                padding: 15px; z-index: 100; border-bottom: 2px solid #00ff41;
                text-align: center; box-shadow: 0 5px 20px rgba(0,0,0,0.5);
            }}
            #searchBar {{ 
                width: 85%; max-width: 700px; padding: 12px; border-radius: 25px; 
                border: 1px solid #00ff41; background: #000; color: #fff; font-size: 16px;
                outline: none; margin-top: 10px;
            }}
            .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 15px; padding: 20px; }}
            .card {{ background: #111; border: 1px solid #222; padding: 15px; border-radius: 10px; transition: 0.2s; }}
            .card:hover {{ border-color: #00ff41; transform: scale(1.02); }}
            .card strong {{ display: block; color: #fff; margin-bottom: 10px; font-size: 15px; height: 20px; overflow: hidden; }}
            input {{ width: 100%; background: #222; color: #0f8; border: none; padding: 8px; font-size: 10px; margin-bottom: 10px; border-radius: 5px; }}
            button {{ width: 100%; background: #00ff41; color: #000; border: none; padding: 10px; cursor: pointer; font-weight: bold; border-radius: 5px; }}
            .hidden {{ display: none !important; }}
            .stats {{ font-size: 12px; color: #777; margin-top: 5px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>PH-TV HYPER FINDER ⚡</h1>
            <div class="stats">CANAIS ÚNICOS: <strong>{len(canais)}</strong> | ÚLTIMA CARGA: {agora}</div>
            <input type="text" id="searchBar" placeholder="Pesquisar entre os {len(canais)} canais..." onkeyup="filter()">
        </div>
        <div class="grid" id="grid">
    """
    
    for i, c in enumerate(canais):
        sid = f"u{i}"
        html_template += f"""
            <div class="card" data-name="{c['nome']}">
                <strong>{c['nome']}</strong>
                <input type="text" value="{c['url']}" id="{sid}" readonly>
                <button onclick="copy('{sid}')">COPIAR LINK</button>
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
    print(f"Sucesso! {len(lista)} canais disponíveis.")
