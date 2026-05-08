import requests
from datetime import datetime

def buscar_links():
    # Usando a base de dados bruta para ter mais chances de achar
    url_api = "https://iptv-org.github.io/api/streams.json"
    try:
        print("Iniciando varredura de sinais...")
        response = requests.get(url_api, timeout=20)
        dados = response.json()
        
        canais_br = []
        for c in dados:
            channel_id = str(c.get("channel", "")).lower()
            # Busca ampliada: IDs que contenham .br ou nomes que indiquem Brasil
            if ".br" in channel_id or channel_id.endswith("-br"):
                if c.get("url"):
                    canais_br.append(c)
        
        return canais_br
    except Exception as e:
        print(f"Erro na conexão: {e}")
        return []

def gerar_painel(canais):
    agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    html_inicio = f"""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <title>PH - TV Finder v2.0</title>
        <style>
            body {{ background: #0f0f0f; color: #00ff88; font-family: 'Courier New', monospace; padding: 20px; }}
            .card {{ background: #1a1a1a; border: 1px solid #333; padding: 15px; margin-bottom: 10px; border-radius: 8px; }}
            input {{ width: 70%; background: #000; color: #fff; border: 1px solid #00ff88; padding: 5px; margin: 10px 0; }}
            button {{ background: #00ff88; color: #000; border: none; padding: 8px 15px; cursor: pointer; font-weight: bold; }}
            h1 {{ border-bottom: 2px solid #00ff88; display: inline-block; }}
        </style>
    </head>
    <body>
        <h1>🔍 PH-TV SEARCH ENGINE</h1>
        <p>Última varredura: {agora}</p>
        <div id="lista">
    """
    
    conteudo = ""
    for c in canais:
        nome = c['channel'].split('.')[0].replace("-", " ").upper()
        url = c['url']
        conteudo += f"""
        <div class="card">
            <strong>CANAL: {nome}</strong><br>
            <input type="text" value="{url}" id="url-{nome}" readonly>
            <button onclick="copyToClipboard('url-{nome}')">COPIAR IP</button>
        </div>
        """
    
    html_fim = """
        </div>
        <script>
            function copyToClipboard(id) {
                var copyText = document.getElementById(id);
                copyText.select();
                document.execCommand("copy");
                alert("URL copiada!");
            }
        </script>
    </body>
    </html>
    """
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_inicio + conteudo + html_fim)

if __name__ == "__main__":
    lista = buscar_links()
    if lista:
        gerar_painel(lista)
        print(f"Finalizado: {len(lista)} canais encontrados.")
    else:
        # Se não achar nada, vamos gerar um aviso mas manter a estrutura
        with open("index.html", "w", encoding="utf-8") as f:
            f.write("<html><body style='background:#000;color:#fff;'><h1>Nenhum sinal captado. Tente o 'Run Workflow' novamente.</h1></body></html>")
