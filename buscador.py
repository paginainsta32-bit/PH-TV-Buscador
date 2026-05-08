import requests
from datetime import datetime
import re

def buscar_links():
    # As melhores fontes brasileiras e globais unificadas
    fontes = [
        "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/br.m3u",
        "https://raw.githubusercontent.com/GuikiAnimes/Canal-Aberto-Brasil/main/CanalAbertoBrasil.m3u",
        "https://raw.githubusercontent.com/LITUATUI/IPTV/main/BR.m3u",
        "https://raw.githubusercontent.com/HelmerLousas/m3u-br/main/br.m3u",
        "https://raw.githubusercontent.com/Deivid-Souto/IPTV-Brasil/main/canais.m3u",
        "https://raw.githubusercontent.com/AssignZ/Iptv-Gratis-Brasil/main/Lista%20Atualizada.m3u",
        "https://raw.githubusercontent.com/maikofreitas/TV_ABERTA/main/tv_aberta.m3u",
        "https://raw.githubusercontent.com/paimp/lista-iptv/master/lista.m3u",
        "https://raw.githubusercontent.com/yanosho/open-iptv/master/streams/br.m3u",
        "https://iptv-org.github.io/iptv/countries/br.m3u"
    ]
    
    canais = []
    print("Iniciando busca massiva...")

    for url in fontes:
        try:
            # Fingimos ser um navegador para a fonte não nos bloquear
            res = requests.get(url, timeout=25, headers={'User-Agent': 'Mozilla/5.0'})
            if res.ok:
                # Regex potente: pega nome e URL ignorando lixos no meio
                matches = re.findall(r'#EXTINF:.*?,(.*?)\n(?:#.*?\n)*(http[^\s\n\r]+)', res.text)
                for nome, link in matches:
                    n_limpo = re.sub(r'\[.*?\]|\(.*?\)|\d+P|HD|SD|FHD|\|', '', nome).strip().upper()
                    if n_limpo and len(link) > 10:
                        canais.append({"nome": n_limpo, "url": link.strip()})
        except:
            continue

    # Remove duplicados por URL para o painel não ficar gigante com lixo
    vistos = set()
    lista_final = []
    for c in canais:
        u_base = c['url'].split('?')[0].lower().strip()
        if u_base not in vistos:
            vistos.add(u_base)
            lista_final.append(c)
    
    return sorted(lista_final, key=lambda x: x['nome'])

def gerar_painel(canais):
    agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    html_template = f"""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <title>PH-TV MULTIVERSO</title>
        <style>
            body {{ background: #000; color: #0f0; font-family: 'Courier New', monospace; margin: 0; padding: 0; }}
            .header {{ position: sticky; top: 0; background: #111; padding: 20px; border-bottom: 2px solid #0f0; text-align: center; z-index: 100; }}
            #search {{ width: 80%; padding: 12px; background: #000; border: 1px solid #0f0; color: #0f0; border-radius: 20px; outline: none; margin-top: 10px; }}
            .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 15px; padding: 20px; }}
            .card {{ background: #0a0a0a; border: 1px solid #222; padding: 15px; border-radius: 8px; transition: 0.3s; }}
            .card:hover {{ border-color: #0f0; box-shadow: 0 0 10px #0f0; }}
            strong {{ display: block; color: #fff; margin-bottom: 10px; font-size: 14px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
            input {{ width: 100%; background: #111; color: #0f0; border: none; padding: 8px; font-size: 10px; margin-bottom: 10px; }}
            .btns {{ display: flex; gap: 5px; }}
            button {{ flex: 1; background: #0f0; color: #000; border: none; padding: 8px; cursor: pointer; font-weight: bold; font-size: 10px; }}
            .play {{ background: #007bff; color: #fff; text-decoration: none; text-align: center; line-height: 25px; }}
            .hidden {{ display: none !important; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>PH-TV: MULTIVERSO BR 🚀</h1>
            <div style="font-size: 12px; color: #888;">CANAIS: <strong>{len(canais)}</strong> | ATUALIZADO: {agora}</div>
            <input type="text" id="search" placeholder="PESQUISAR CANAL..." onkeyup="filter()">
        </div>
        <div class="grid" id="grid">
    """
    for i, c in enumerate(canais):
        sid = f"u{i}"
        html_template += f"""
            <div class="card" data-name="{c['nome']}">
                <strong>{c['nome']}</strong>
                <input type="text" value="{c['url']}" id="{sid}" readonly>
                <div class="btns">
                    <button onclick="copy('{sid}')">COPIAR</button>
                    <a class="btns play" href="https://hls-js.netlify.app/demo/?src={c['url']}" target="_blank">TESTAR</a>
                </div>
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
                    cards[i].classList.toggle('hidden', !name.includes(s));
                }
            }
            function copy(id) {
                let el = document.getElementById(id);
                el.select();
                document.execCommand("copy");
                alert("URL Copiada!");
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
    print(f"Finalizado: {len(lista)} canais.")
