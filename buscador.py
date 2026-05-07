# ... (mantenha o resto do código igual)

if __name__ == "__main__":
    lista_canais = buscar_links()
    if not lista_canais:
        # Se a API falhar, cria um arquivo básico para não dar erro no Git
        with open("index.html", "w", encoding="utf-8") as f:
            f.write("<html><body><h1>Nenhum canal encontrado no momento.</h1></body></html>")
        print("Aviso: Nenhun canal encontrado, gerando HTML vazio.")
    else:
        gerar_painel(lista_canais)
        print(f"Sucesso! {len(lista_canais)} canais processados.")
import requests
from datetime import datetime

def buscar_links():
    # Fonte oficial da IPTV-org (API de streams)
    url_api = "https://iptv-org.github.io/api/streams.json"
    
    try:
        print("Buscando sinais ativos na rede...")
        response = requests.get(url_api, timeout=15)
        dados = response.json()
        
        # Filtra canais do Brasil que tenham URL válida
        canais_br = [c for c in dados if c.get("channel") and c["channel"].endswith("-br") and c.get("url")]
        return canais_br
    except Exception as e:
        print(f"Erro ao conectar na API: {e}")
        return []

def gerar_painel(canais):
    agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    # Início do HTML
    html_template = f"""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>PH - Localizador de Canais</title>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #121212; color: #e0e0e0; padding: 20px; }}
            .container {{ max-width: 1000px; margin: auto; }}
            h1 {{ color: #00ff88; text-shadow: 2px 2px #000; }}
            .info {{ background: #1e1e1e; padding: 10px; border-radius: 5px; margin-bottom: 20px; border-left: 5px solid #00ff88; }}
            table {{ width: 100%; border-collapse: collapse; background: #1e1e1e; border-radius: 10px; overflow: hidden; }}
            th, td {{ padding: 15px; border-bottom: 1px solid #333; text-align: left; }}
            th {{ background: #007bff; color: white; }}
            tr:hover {{ background: #252525; }}
            input {{ width: 90%; background: #000; color: #00ff88; border: 1px solid #444; padding: 8px; border-radius: 4px; font-family: monospace; }}
            .btn-copy {{ background: #28a745; color: white; border: none; padding: 10px 15px; border-radius: 4px; cursor: pointer; font-weight: bold; }}
            .btn-copy:hover {{ background: #218838; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔍 PH - Localizador de IPs de TV</h1>
            <div class="info">
                <strong>Status:</strong> Online | <strong>Última atualização:</strong> {agora} (Horário do Servidor)
            </div>
            <table>
                <thead>
                    <tr>
                        <th>CANAIS ENCONTRADOS</th>
                        <th>URL / IP DO STREAM (.m3u8)</th>
                        <th>AÇÃO</th>
                    </tr>
                </thead>
                <tbody>
    """

    # Adiciona as linhas dos canais
    for c in canais:
        nome = c['channel'].replace("-br", "").upper()
        url = c['url']
        html_template += f"""
                    <tr>
                        <td><strong>{nome}</strong></td>
                        <td><input type="text" value="{url}" id="in-{nome}" readonly></td>
                        <td><button class="btn-copy" onclick="copy('{nome}')">COPIAR</button></td>
                    </tr>
        """

    # Fecha o HTML
    html_template += """
                </tbody>
            </table>
        </div>
        <script>
            function copy(id) {
                var input = document.getElementById('in-' + id);
                input.select();
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
    lista_canais = buscar_links()
    if lista_canais:
        gerar_painel(lista_canais)
        print(f"Sucesso! {len(lista_canais)} canais processados.")
