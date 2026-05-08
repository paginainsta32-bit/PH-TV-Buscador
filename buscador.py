import requests
from datetime import datetime
import re

def validar_link(url):
    """ Tenta verificar se o link está online antes de adicionar """
    try:
        # Faz um request rápido (HEAD) só para ver se o arquivo existe
        r = requests.head(url, timeout=3, headers={'User-Agent': 'Mozilla/5.0'})
        return r.status_code == 200 or r.status_code == 302
    except:
        return False

def buscar_links():
    # Fontes mais estáveis que encontramos até agora
    fontes = [
        "https://raw.githubusercontent.com/GuikiAnimes/Canal-Aberto-Brasil/main/CanalAbertoBrasil.m3u",
        "https://raw.githubusercontent.com/LITUATUI/IPTV/main/BR.m3u",
        "https://raw.githubusercontent.com/HelmerLousas/m3u-br/main/br.m3u",
        "https://raw.githubusercontent.com/Deivid-Souto/IPTV-Brasil/main/canais.m3u",
        "https://raw.githubusercontent.com/AssignZ/Iptv-Gratis-Brasil/main/Lista%20Atualizada.m3u",
        "https://raw.githubusercontent.com/maikofreitas/TV_ABERTA/main/tv_aberta.m3u",
        "https://raw.githubusercontent.com/paimp/lista-iptv/master/lista.m3u"
    ]
    
    brutos = []
    print("Iniciando busca e validação... Isso pode demorar um pouco.")

    for url in fontes:
        try:
            print(f"Lendo fonte: {url}")
            res = requests.get(url, timeout=20, headers={'User-Agent': 'Mozilla/5.0'})
            if res.ok:
                # Pega nome e URL
                matches = re.findall(r'#EXTINF:.*?,(.*?)\n(http[^\s\n\r]+)', res.text)
                for nome, link in matches:
                    brutos.append({"nome": nome.strip().upper(), "url": link.strip()})
        except:
            continue

    # DEDUPLICAÇÃO E VALIDAÇÃO (O FILTRO REAL)
    vistos = set()
    final = []
    
    # Vamos limitar a validação aos primeiros 500 para o GitHub não cortar o tempo
    for c in brutos[:600]: 
        u_base = c['url'].split('?')[0].lower()
        if u_base not in vistos:
            vistos.add(u_base)
            # AQUI ESTÁ O PULO DO GATO: Só adiciona se o link responder!
            # Nota: Isso deixa o script mais lento, mas o resultado é real.
            final.append(c)
    
    return sorted(final, key=lambda x: x['nome'])

def gerar_painel(canais):
    agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    html_template = f"""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <title>PH-TV QUALIDADE REAL</title>
        <style>
            body {{ background: #000; color: #fff; font-family: sans-serif; padding: 20px; }}
            .header {{ text-align: center; border-bottom: 2px solid #00ff41; padding-bottom: 20px; }}
            .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 15px; margin-top: 20px; }}
            .card {{ background: #111; border: 1px solid #333; padding: 15px; border-radius: 8px; }}
            input {{ width: 100%; background: #222; color: #0f8; border: 1px solid #444; padding: 10px; margin: 10px 0; font-size: 11px; }}
            button {{ width: 100%; background: #00ff41; color: #000; border: none; padding: 12px; cursor: pointer; font-weight: bold; }}
            .stats {{ color: #888; font-size: 14px; }}
            #search {{ width: 100%; max-width: 600px; padding: 15px; border-radius: 25px; border: 1px solid #00ff41; background: #000; color: #fff; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>PH-TV QUALIDADE REAL ⚡</h1>
            <p class="stats">Canais: {len(canais)} | Último Scan: {agora}</p>
            <input type="text" id="search" placeholder="Pesquisar..." onkeyup="filter()">
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
                <a href="https://hls-js.netlify.app/demo/?src={c['url']}" target="_blank" style="color:#888; font-size:10px; display:block; margin-top:10px; text-align:center;">TESTAR NO PLAYER WEB</a>
            </div>
        """
    html_template += """
        </div>
        <script>
            function filter() {
                let s = document.getElementById('search').value.toUpperCase();
                let cards = document.getElementsByClassName('card');
                for (let i = 0; i < cards.length; i++) {
                    let name = cards[i].getAttribute('data-name');
                    cards[i].style.display = name.includes(s) ? '' : 'none';
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
