import requests
from datetime import datetime
import re

def buscar_links():
    # Fontes focadas 100% em Brasil e listas que não caem fácil
    fontes = [
        "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/br.m3u",
        "https://raw.githubusercontent.com/GuikiAnimes/Canal-Aberto-Brasil/main/CanalAbertoBrasil.m3u",
        "https://raw.githubusercontent.com/LITUATUI/IPTV/main/BR.m3u",
        "https://raw.githubusercontent.com/HelmerLousas/m3u-br/main/br.m3u",
        "https://raw.githubusercontent.com/paimp/lista-iptv/master/lista.m3u",
        "https://raw.githubusercontent.com/AssignZ/Iptv-Gratis-Brasil/main/Lista%20Atualizada.m3u",
        "https://raw.githubusercontent.com/yanosho/open-iptv/master/streams/br.m3u",
        "https://raw.githubusercontent.com/Deivid-Souto/IPTV-Brasil/main/canais.m3u",
        "https://raw.githubusercontent.com/estebandiazp/Lista-IPTV-Brasil/master/Brasil.m3u",
        "https://raw.githubusercontent.com/Jose-S-B/IPTV-Brasil/main/LISTA.m3u"
    ]
    
    canais_encontrados = []
    print(f"Apelando para {len(fontes)} fontes brasileiras...")

    for url in fontes:
        try:
            print(f"Minerando: {url}")
            response = requests.get(url, timeout=25, headers={'User-Agent': 'Mozilla/5.0'})
            if not response.ok: continue

            conteudo = response.text
            # Captura o nome após a vírgula e a URL na linha seguinte
            # Aceita quase qualquer caractere no nome (inclusive emojis e símbolos)
            matches = re.findall(r'#EXTINF:.*?,(.*?)\n(http[^\s\n\r]+)', conteudo)
            
            for nome, link in matches:
                n_upper = nome.strip().upper()
                # Filtra canais que não são do Brasil em listas mistas
                # Mas como as fontes agora são focadas em BR, o filtro é mais relaxado
                if n_upper and len(link) > 10:
                    # Limpeza de lixo visual no nome do canal
                    n_limpo = re.sub(r'\[.*?\]|\(.*?\)|\d+P|HD|SD|FHD|4K|\||★|►', '', n_upper).strip()
                    canais_encontrados.append({"nome": n_limpo, "url": link.strip()})
        except Exception as e:
            print(f"Erro em {url}: {e}")

    # DEDUPLICAÇÃO PESADA
    vistos_url = set()
    lista_final = []
    
    for c in canais_encontrados:
        # Normaliza a URL para evitar duplicados por causa de pequenos parâmetros
        url_norm = c['url'].split('?')[0].split('|')[0].lower().strip()
        if url_norm not in vistos_url:
            vistos_url.add(url_norm)
            lista_final.append(c)
    
    return sorted(lista_final, key=lambda x: x['nome'])

def gerar_painel(canais):
    agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    html_template = f"""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <title>PH-TV APELAÇÃO MÁXIMA</title>
        <style>
            body {{ background: #000; color: #00ff41; font-family: 'Segoe UI', sans-serif; margin: 0; }}
            .header {{ 
                position: sticky; top: 0; background: rgba(0,0,0,0.9); 
                padding: 20px; z-index: 100; border-bottom: 3px solid #f00; /* Vermelho pra mostrar que o bicho pegou */
                text-align: center;
            }}
            #searchBar {{ 
                width: 90%; max-width: 800px; padding: 15px; border-radius: 5px; 
                border: 2px solid #f00; background: #111; color: #fff; font-size: 18px;
                outline: none; margin-top: 10px;
            }}
            .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 15px; padding: 20px; }}
            .card {{ background: #111; border: 1px solid #333; padding: 15px; border-radius: 8px; }}
            .card:hover {{ border-color: #f00; box-shadow: 0 0 10px #f00; }}
            .card strong {{ display: block; color: #fff; margin-bottom: 10px; font-size: 16px; }}
            input {{ width: 100%; background: #222; color: #0f8; border: none; padding: 8px; font-size: 11px; margin-bottom: 10px; }}
            button {{ width: 100%; background: #f00; color: #fff; border: none; padding: 10px; cursor: pointer; font-weight: bold; border-radius: 4px; }}
            .hidden {{ display: none !important; }}
            .stats {{ font-size: 14px; color: #aaa; margin-top: 5px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>PH-TV: MODO APELAÇÃO 🚀</h1>
            <div class="stats">SINAIS ENCONTRADOS: <strong>{len(canais)}</strong> | ATUALIZADO: {agora}</div>
            <input type="text" id="searchBar" placeholder="Pesquisar canal..." onkeyup="filter()">
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
                alert("IP copiado com sucesso!");
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
    print(f"Apelação concluída! {len(lista)} canais no painel.")
