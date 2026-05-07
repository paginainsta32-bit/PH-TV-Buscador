import requests

def buscar_links():
    # Fonte confiável que agrega streams mundiais
    url_api = "https://iptv-org.github.io/api/streams.json"
    
    try:
        print("Conectando à base de dados de sinais...")
        response = requests.get(url_api, timeout=15)
        dados = response.json()
        
        # Filtramos apenas canais do Brasil (.br)
        canais_br = [c for c in dados if c.get("channel") and c["channel"].endswith("-br")]
        return canais_br
    except Exception as e:
        print(f"Erro na busca: {e}")
        return []

def criar_html(canais):
    tabela_linhas = ""
    for c in canais:
        nome_canal = c['channel'].replace("-br", "").upper()
        url_stream = c['url']
        
        tabela_linhas += f"""
        <tr>
            <td><strong>{nome_canal}</strong></td>
            <td><input type="text" value="{url_stream}" id="input-{nome_canal}" readonly></td>
            <td><button onclick="copyLink('input-{nome_canal}')">Copiar</button></td>
        </tr>
        """

    html_template = f"""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <title>PH - TV Finder</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #1a1a1a; color: #eee; padding: 40px; }}
            table {{ width: 100%; border-collapse: collapse; background: #2d2d2d; border-radius: 8px; overflow: hidden; }}
            th, td {{ padding: 15px; border-bottom: 1px solid #444; text-align: left; }}
            th {{ background: #007bff; color: white; }}
            input {{ width: 80%; background: #111; color: #28a745; border: 1px solid #444; padding: 5px; border-radius: 4px; }}
            button {{ background: #28a745; color: white; border: none; padding: 8px 15px; border-radius: 4px; cursor: pointer; }}
            button:hover {{ background: #218838; }}
        </style>
    </head>
    <body>
        <h1>🔍 Localizador de Canais - PH Programador</h1>
        <p>Última atualização: {pd_hoje()}</p>
        <table>
            <thead>
                <tr><th>Canal</th><th>URL do Stream (IP)</th><th>Ação</th></tr>
            </thead>
            <tbody>
                {tabela_linhas}
            </tbody>
        </table>
        <script>
            function copyLink(id) {{
                var copyText = document.getElementById(id);
                copyText.select();
                document.execCommand("copy");
                alert("Copiado: " + copyText.value);
            }}
        </script>
    </body>
    </html>
    """
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_template)

def pd_hoje():
    from datetime import datetime
    return datetime.now().strftime("%d/%m/%Y %H:%M")

if __name__ == "__main__":
    lista = buscar_links()
    if lista:
        criar_html(lista)
        print("Painel index.html gerado com sucesso!")