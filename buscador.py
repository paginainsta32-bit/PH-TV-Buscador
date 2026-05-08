import requests
from datetime import datetime

def buscar_links():
    # Lista de APIs e Repositórios confiáveis
    fontes = [
        "https://iptv-org.github.io/api/streams.json",
        "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/br.m3u"
    ]
    
    canais_encontrados = []
    print("Iniciando varredura em múltiplas fontes...")

    for url in fontes:
        try:
            response = requests.get(url, timeout=15)
            if url.endswith(".json"):
                dados = response.json()
                # Filtro ampliado: busca 'br' no canal ou no país
                for c in dados:
                    if c.get("url") and ("-br" in str(c.get("channel", "")) or c.get("country") == "BR"):
                        canais_encontrados.append({"nome": str(c.get("channel")).upper(), "url": c.get("url")})
            
            elif url.endswith(".m3u"):
                # Se for lista M3U, fazemos um parsing manual simples
                linhas = response.text.split("\n")
                for i in range(len(linhas)):
                    if "#EXTINF" in linhas[i] and "," in linhas[i]:
                        nome = linhas[i].split(",")[-1].strip()
                        proxima_linha = linhas[i+1].strip()
                        if proxima_linha.startswith("http"):
                            canais_encontrados.append({"nome": nome, "url": proxima_linha})
        except Exception as e:
            print(f"Erro na fonte {url}: {e}")

    # Remove duplicados
    lista_limpa = {c['url']: c for c in canais_encontrados}.values()
    return list(lista_limpa)

def gerar_painel(canais):
    agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    html_template = f"""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <title>PH-TV MUNIÇÃO V2</title>
        <style>
            body {{ background: #0f0f0f; color: #00ff41; font-family: 'Courier New', monospace; padding: 20px; }}
            .card {{ background: #1a1a1a; border: 1px solid #00ff41; margin: 10px 0; padding: 15px; border-radius: 5px; }}
            input {{ width: 70%; background: #000; color: #00ff41; border: 1px solid #00ff41; padding: 5px; }}
            button {{ background: #00ff41; color: #000; border: none; padding: 5px 15px; cursor: pointer; font-weight: bold; }}
            h1 {{ border-bottom: 2px solid #00ff41; padding-bottom: 10px; }}
        </style>
    </head>
    <body>
        <h1>💻 PH-PROGRAMADOR | SCANNER DE IPS TV</h1>
        <p>Sinais encontrados: {len(canais)} | Atualizado: {agora}</p>
        <div id="lista">
    """
    
    for c in canais:
        nome_limpo = c['nome'].replace("-", " ")
        html_template += f"""
            <div class="card">
                <strong>{nome_limpo}</strong><br><br>
                <input type="text" value="{c['url']}" id="url-{nome_limpo}">
                <button onclick="copy('{nome_limpo}')">COPIAR IP</button>
            </div>
        """
        
    html_template += """
        </div>
        <script>
            function copy(id) {
                var btn = document.getElementById('url-' + id);
                btn.select();
                document.execCommand("copy");
                alert("IP Copiado para o PHflix!");
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
    print(f"Processo finalizado. {len(lista)} canais no painel.")
