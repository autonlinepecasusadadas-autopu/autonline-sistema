from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from supabase import create_client, Client
import os

app = FastAPI()

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://ijirrzrallxuqqagwviq.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "sb_publishable_oq13Ilt9dcMFxXSu862Rw_9Q4wa12-")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

WHATSAPP_NUMERO = "5531982900087"

HTML_CATALOGO = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AUTON-LINE | Peças Usadas</title>
    <style>
        * { box-sizing: border-box; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        body { margin: 0; padding: 0; background-color: #121212; color: #f1f1f1; }
        header { background: #000; border-bottom: 3px solid #f1c40f; padding: 25px 15px; text-align: center; }
        .brand-title { color: #f1c40f; font-size: 30px; font-weight: 800; letter-spacing: 1.5px; margin: 0; }
        .brand-sub { color: #ffffff; font-size: 14px; margin-top: 6px; font-style: italic; }
        .container { max-width: 1200px; margin: 25px auto; padding: 0 15px; }
        .search-box { margin-bottom: 30px; text-align: center; }
        .search-box input { width: 100%; max-width: 550px; padding: 14px 20px; border-radius: 25px; border: 1px solid #444; background: #1e1e1e; color: white; font-size: 16px; outline: none; }
        .grid-pecas { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 20px; }
        .card-peca { background: #1a1a1a; border-radius: 8px; overflow: hidden; border: 1px solid #333; display: flex; flex-direction: column; justify-content: space-between; }
        .card-img { width: 100%; height: 200px; object-fit: cover; background: #2a2a2a; }
        .card-body { padding: 15px; }
        .card-title { font-size: 17px; font-weight: bold; color: #fff; margin-bottom: 8px; }
        .card-info { font-size: 13px; color: #aaa; margin: 4px 0; }
        .card-price { font-size: 20px; font-weight: bold; color: #27ae60; margin: 12px 0; }
        .btn-whatsapp { display: block; text-align: center; background: #25d366; color: white; text-decoration: none; padding: 12px; border-radius: 5px; font-weight: bold; font-size: 14px; }
        .btn-whatsapp:hover { background: #1ebd59; }
    </style>
</head>
<body>

<header>
    <div class="brand-title">AUTON-LINE</div>
    <div class="brand-sub">PEÇAS USADAS — A peça que falta em seu carro na palma da sua mão</div>
</header>

<div class="container">
    <div class="search-box">
        <input type="text" id="searchInput" onkeyup="filtrarCatalogo()" placeholder="🔍 Pesquise por veículo, modelo ou peça...">
    </div>

    <div class="grid-pecas">
        {% for p in pecas %}
        <div class="card-peca item-peca" data-text="{{ p.descricao | lower }} {{ p.fabricante | lower }} {{ p.modelo | lower }} {{ p.ano }}">
            {% if p.foto %}
            <img src="{{ p.foto }}" class="card-img">
            {% else %}
            <div class="card-img" style="display:flex; align-items:center; justify-content:center; color:#555;">Sem foto do item</div>
            {% endif %}
            <div class="card-body">
                <div class="card-title">{{ p.descricao }}</div>
                <div class="card-info">🚗 {{ p.fabricante }} {{ p.modelo }} ({{ p.ano }})</div>
                {% if p.cor %}<div class="card-info">🎨 Cor: {{ p.cor }}</div>{% endif %}
                <div class="card-price">R$ {{ "%.2f"|format(p.preco_venda or 0) }}</div>
                <a href="https://wa.me/{{ whatsapp }}?text=Olá!%20Tenho%20interesse%20na%20peça:%20*{{ p.descricao }}*%20do%20veículo%20*{{ p.fabricante }}%20{{ p.modelo }}%20({{ p.ano }})*" target="_blank" class="btn-whatsapp">📲 Consultar via WhatsApp</a>
            </div>
        </div>
        {% else %}
        <div style="grid-column: 1/-1; text-align:center; color:#777; padding:40px;">Nenhuma peça disponível no catálogo no momento.</div>
        {% endfor %}
    </div>
</div>

<script>
    function filtrarCatalogo() {
        const termo = document.getElementById('searchInput').value.toLowerCase();
        const cards = document.querySelectorAll('.item-peca');
        cards.forEach(card => {
            const texto = card.getAttribute('data-text');
            card.style.display = texto.includes(termo) ? 'flex' : 'none';
        });
    }
</script>

</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def catalogo():
    try:
        response = supabase.table("pecas").select("*").eq("status", "disponivel").execute()
        data = response.data if response.data else []
    except Exception:
        data = []

    from jinja2 import Template
    template = Template(HTML_CATALOGO)
    rendered = template.render(pecas=data, whatsapp=WHATSAPP_NUMERO)
    return HTMLResponse(content=rendered)
