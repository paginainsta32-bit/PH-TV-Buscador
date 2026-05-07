import requests
from datetime import datetime

# 1. DEFINIMOS A FUNÇÃO PRIMEIRO
def buscar_links():
    url_api = "https://iptv-org.github.io/api/streams.json"
    try:
        print("Buscando sinais ativos...")
        response = requests.get(url_api, timeout=15)
        dados = response.json()
        # Filtra canais do Brasil
        canais_br = [c for c in dados if c.get("channel") and c["channel"].endswith("-br") and c.get("url")]
        return canais_br
    except Exception as e:
        print(f"Erro: {e}")
        return []

# 2. DEFINIMOS A FUNÇÃO DO PAINEL
def gerar_painel(canais):
    agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    html_inicio = f"""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <title>PH - TV Finder</title>
        <style>
            body {{ background: #121212; color: white; font-family: sans-serif; padding: 20px; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ border: 1px solid #333; padding: 10px; text-align: left; }}
            th {{ background: #007bff; }}
            input {{ width: 80%; background: #000; color: #0f8; border: 1px solid #444; padding: 5px; }}
        </style>
    </head>
    <body>
        <h1>🔍 Localizador PH - Atualizado: {agora}</h1>
        <table>
            <thead><tr><th>Canal</th><th>URL / IP</th><th>Ação</th></tr></thead>
            <tbody>
    """
    
    linhas = ""
    for c in canais:
        nome = c['channel'].replace("-br", "").upper()
        url = c['url']
        linhas += f"""
        <tr>
            <td>{nome}</td>
            <td><input type="text" value="{url}" id="id-{nome}" readonly></td>
            <td><button onclick="document.getElementById('id-{nome}').select();document.execCommand('copy');alert('Copiado!')">Copiar</button></td>
        </tr>
        """
    
    html_fim = "</tbody></table></body></html>"
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_inicio + linhas + html_fim)

# 3. EXECUTAMOS TUDO NA ORDEM CERTA
if __name__ == "__main__":
    lista = buscar_links()
    if lista:
        gerar_painel(lista)
        print(f"Sucesso: {len(lista)} canais encontrados.")
    else:
        # Cria um arquivo simples se a lista vier vazia para não dar erro no Git
        with open("index.html", "w", encoding="utf-8") as f:
            f.write("<h1>Nenhum canal encontrado. Tente novamente mais tarde.</h1>")
        print("Aviso: Lista vazia.")
