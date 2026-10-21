from fastapi import FastAPI, Request, Form, UploadFile, Cookie, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from supabase import create_client, Client
import os
import json
import base64

app = FastAPI()

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://ijirrzrallxuqqagwviq.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "sb_publishable_oq13Ilt9dcMFxXSu862Rw_9Q4wa12-")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Configurações de acesso e contato
SENHA_ADMIN = "admin123"
WHATSAPP_NUMERO = "5531982900087"

HTML_CATALOGO_PUBLICO = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AUTON-LINE Peças Usadas | Catálogo</title>
    <style>
        * { box-sizing: border-box; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        body { margin: 0; padding: 0; background-color: #121212; color: #f1f1f1; }
        header { background: #000000; border-bottom: 3px solid #f1c40f; padding: 20px; text-align: center; position: relative; }
        .header-title { color: #f1c40f; font-size: 26px; font-weight: bold; margin: 0; letter-spacing: 1px; }
        .header-sub { color: #ffffff; font-size: 13px; margin-top: 5px; font-style: italic; }
        .admin-link { position: absolute; right: 20px; top: 20px; background: #222; color: #f1c40f; padding: 6px 12px; border-radius: 4px; text-decoration: none; font-size: 12px; font-weight: bold; border: 1px solid #f1c40f; }
        .admin-link:hover { background: #f1c40f; color: #000; }
        .container { max-width: 1200px; margin: 25px auto; padding: 0 15px; }
        .search-box { margin-bottom: 30px; text-align: center; }
        .search-box input { width: 100%; max-width: 550px; padding: 12px 20px; border-radius: 25px; border: 1px solid #444; background: #1e1e1e; color: white; font-size: 15px; outline: none; }
        .grid-pecas { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 20px; }
        .card-peca { background: #1a1a1a; border-radius: 8px; overflow: hidden; border: 1px solid #333; display: flex; flex-direction: column; justify-content: space-between; }
        .card-img { width: 100%; height: 180px; object-fit: cover; background: #2a2a2a; }
        .card-body { padding: 15px; }
        .card-title { font-size: 16px; font-weight: bold; color: #fff; margin-bottom: 6px; }
        .card-info { font-size: 13px; color: #aaa; margin: 3px 0; }
        .card-price { font-size: 18px; font-weight: bold; color: #27ae60; margin: 10px 0; }
        .btn-whatsapp { display: block; text-align: center; background: #25d366; color: white; text-decoration: none; padding: 10px; border-radius: 4px; font-weight: bold; margin-top: 8px; font-size: 14px; }
        .btn-whatsapp:hover { background: #1ebd59; }
    </style>
</head>
<body>

<header>
    <a href="/admin" class="admin-link">⚙️ Painel Gestão</a>
    <div class="header-title">AUTON-LINE</div>
    <div class="header-sub">PEÇAS USADAS — A peça que falta em seu carro na palma da sua mão</div>
</header>

<div class="container">
    <div class="search-box">
        <input type="text" id="searchInput" onkeyup="filtrarCatalogo()" placeholder="🔍 Pesquise por veículo, modelo ou peça (Ex: Uno, Alternador)...">
    </div>

    <div class="grid-pecas" id="gridPecas">
        {% for p in pecas %}
        <div class="card-peca item-peca" data-text="{{ p.descricao | lower }} {{ p.fabricante | lower }} {{ p.modelo | lower }} {{ p.ano }}">
            {% if p.foto %}
            <img src="{{ p.foto }}" class="card-img">
            {% else %}
            <div class="card-img" style="display:flex; align-items:center; justify-content:center; color:#555; font-size:12px;">Sem foto</div>
            {% endif %}
            <div class="card-body">
                <div class="card-title">{{ p.descricao }}</div>
                <div class="card-info">🚗 {{ p.fabricante }} {{ p.modelo }} ({{ p.ano }})</div>
                {% if p.cor %}<div class="card-info">🎨 Cor: {{ p.cor }}</div>{% endif %}
                <div class="card-price">R$ {{ "%.2f"|format(p.preco_venda or 0) }}</div>
                <a href="https://wa.me/{{ whatsapp }}?text=Olá!%20Gostaria%20de%20informações%20sobre%20a%20peça:%20*{{ p.descricao }}*%20do%20veículo%20*{{ p.fabricante }}%20{{ p.modelo }}%20({{ p.ano }})*" target="_blank" class="btn-whatsapp">📲 Consultar via WhatsApp</a>
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

HTML_LOGIN = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>AUTON-LINE | Login Administrativo</title>
    <style>
        body { font-family: Arial, sans-serif; background: #121212; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; color: #fff; }
        .login-box { background: #1e1e1e; padding: 30px; border-radius: 8px; border: 1px solid #333; width: 320px; text-align: center; }
        h2 { color: #f1c40f; margin-bottom: 20px; font-size: 20px; }
        input { width: 100%; padding: 12px; margin-bottom: 15px; border: 1px solid #444; background: #222; color: white; border-radius: 4px; box-sizing: border-box; }
        button { width: 100%; padding: 12px; background: #27ae60; color: white; border: none; font-weight: bold; border-radius: 4px; cursor: pointer; }
        button:hover { background: #219150; }
        .error { color: #e74c3c; font-size: 13px; margin-bottom: 12px; }
        .back-link { display: block; margin-top: 15px; color: #aaa; text-decoration: none; font-size: 12px; }
    </style>
</head>
<body>
<div class="login-box">
    <h2>Acesso ao Painel</h2>
    {% if erro %}<div class="error">Senha incorreta. Tente novamente.</div>{% endif %}
    <form action="/admin-login" method="post">
        <input type="password" name="senha" placeholder="Digite a senha" required>
        <button type="submit">Entrar</button>
    </form>
    <a href="/" class="back-link">← Voltar ao Catálogo Público</a>
</div>
</body>
</html>
"""

HTML_ADMIN = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>AUTON-LINE | Gestão de Estoque</title>
    <script src="https://unpkg.com/html5-qrcode"></script>
    <style>
        * { box-sizing: border-box; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        body { margin: 0; padding: 0; background-color: #f4f6f9; color: #333; }
        header { background: #1a252f; color: white; padding: 15px 20px; display: flex; justify-content: space-between; align-items: center; }
        header h1 { margin: 0; font-size: 18px; color: #f1c40f; }
        nav button { background: #34495e; color: white; border: none; padding: 8px 15px; margin-left: 5px; border-radius: 4px; cursor: pointer; }
        nav button.active { background: #27ae60; }
        .container { max-width: 1100px; margin: 20px auto; padding: 0 15px; }
        .top-info { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; background: white; padding: 12px 20px; border-radius
