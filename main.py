from fastapi import FastAPI, Request, Form, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from supabase import create_client, Client
import os
import json
import base64

app = FastAPI()

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://ijirrzrallxuqqagwviq.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "sb_publishable_oq13Ilt9dcMFxXSu862Rw_9Q4wa12-")

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception:
    supabase = None

SENHA_ADMIN = "142933"

@app.get("/logo.jpeg")
async def get_logo():
    if os.path.exists("logo.jpeg"):
        return FileResponse("logo.jpeg")
    return HTMLResponse(content="Logo não encontrada", status_code=404)

HTML_LOGIN = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>AUTON-LINE | Acesso Restrito</title>
    <style>
        * { box-sizing: border-box; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        body { background: #121212; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; color: #fff; }
        .login-box { background: #1e1e1e; padding: 35px; border-radius: 8px; border: 1px solid #333; width: 340px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.8); }
        .logo-img { height: 40px; object-fit: contain; margin-bottom: 20px; }
        h2 { color: #f1c40f; margin-bottom: 20px; font-size: 20px; letter-spacing: 1px; }
        input { width: 100%; padding: 12px; margin-bottom: 15px; border: 1px solid #444; background: #2a2a2a; color: white; border-radius: 4px; font-size: 15px; outline: none; }
        input:focus { border-color: #f1c40f; }
        button { width: 100%; padding: 12px; background: #27ae60; color: white; border: none; font-weight: bold; border-radius: 4px; cursor: pointer; font-size: 15px; }
        button:hover { background: #219653; }
        .error { color: #e74c3c; font-size: 13px; margin-bottom: 12px; font-weight: bold; }
    </style>
</head>
<body>
<div class="login-box">
    <img src="/logo.jpeg" class="logo-img" alt="Logo Auton-Line">
    <h2>AUTON-LINE ADM</h2>
    {% if erro %}<div class="error">Senha incorreta. Tente novamente.</div>{% endif %}
    <form action="/login" method="post">
        <input type="password" name="senha" placeholder="Palavra-passe de acesso" required autofocus>
        <button type="submit">Entrar no Sistema</button>
    </form>
</div>
</body>
</html>
"""

HTML_ADMIN = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>AUTON-LINE - Gestão de Pátio e Vendas</title>
    <style>
        * { box-sizing: border-box; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        body { margin: 0; padding: 0; background-color: #121212; color: #e0e0e0; }
        header { background: #000000; color: white; padding: 12px 25px; display: flex; justify-content: space-between; align-items: center; border-bottom: 3px solid #f1c40f; box-shadow: 0 2px 10px rgba(0,0,0,0.8); }
        .logo-container { display: flex; align-items: center; gap: 15px; }
        .logo-img { height: 42px; object-fit: contain; border-radius: 4px; border: 1px solid #333; }
        header h1 { margin: 0; font-size: 16px; color: #f1c40f; font-weight: bold; letter-spacing: 0.5px; }
        nav { display: flex; gap: 10px; align-items: center; }
        nav button, .btn-logout { background: #1e1e1e; color: #bbb; border: 1px solid #444; padding: 8px 16px; border-radius: 4px; cursor: pointer; font-size: 14px; font-weight: 600; text-decoration: none; display: inline-block; transition: all 0.2s; }
        nav button:hover, .btn-logout:hover { background: #333; color: #fff; }
        nav button.active { background: #f1c40f; color: #000; border-color: #f1c40f; }
        .btn-logout { background: #c0392b; color: #fff; border-color: #c0392b; }
        .btn-logout:hover { background: #a93226; }
        .container { max-width: 1100px; margin: 25px auto; padding: 0 15px; }
        .top-info { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; background: #1e1e1e; padding: 15px 20px; border-radius: 6px; border: 1px solid #333; box-shadow: 0 2px 5px rgba(0,0,0,0.3); }
        .cards-summary { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 25px; }
        .card { background: #1e1e1e; padding: 18px; border-radius: 6px; border: 1px solid #333; box-shadow: 0 2px 5px rgba(0,0,0,0.3); text-align: center; }
        .card h3 { margin: 0 0 8px 0; font-size: 12px; color: #aaa; text-transform: uppercase; letter-spacing: 0.5px; }
        .card p { margin: 0; font-size: 22px; font-weight: bold; color: #f1c40f; }
        .section { display: none; background: #1e1e1e; padding: 25px; border-radius: 6px; border: 1px solid #333; box-shadow: 0 2px 5px rgba(0,0,0,0.3); }
        .section.active { display: block; }
        h2 { color: #f1c40f; margin-top: 0; font-size: 18px; border-bottom: 1px solid #333; padding-bottom: 10px; }
        form { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }
        .full-width { grid-column: 1 / -1; }
        label { font-size: 12px; font-weight: bold; color: #ccc; margin-bottom: 5px; display: block; }
        input, select, button { width: 100%; padding: 10px; border: 1px solid #444; background: #2a2a2a; color: #fff; border-radius: 4px; font-size: 14px; outline: none; }
        input:focus { border-color: #f1c40f; }
        button.btn-primary { background: #27ae60; color: white; border: none; font-weight: bold; cursor: pointer; transition: background 0.2s; }
        button.btn-primary:hover { background: #219653; }
        button.btn-danger { background: #c0392b; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; width: auto; font-weight: 600; }
        button.btn-danger:hover { background: #a93226; }
        button.btn-sell { background: #2980b9; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; width: auto; font-weight: 600; }
        button.btn-sell:hover { background: #2471a3; }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #333; font-size: 14px; }
        th { background: #161616; font-size: 12px; color: #f1c40f; text-transform: uppercase; }
        tr:hover { background: #252525; }
        .img-thumb { width: 45px; height: 45px; object-fit: cover; border-radius: 4px; border: 1px solid #444; }
    </style>
</head>
<body>

<header>
    <div class="logo-container">
        <img src="/logo.jpeg" class="logo-img" alt="Logo Auton-Line">
        <h1>AUTON-LINE — Gestão de Pátio e Vendas</h1>
    </div>
    <nav>
        <button id="btn-tab-estoque" class="active" onclick="switchTab('estoque')">Estoque Pátio</button>
        <button id="btn-tab-vendas" onclick="switchTab('vendas')">Vendas Realizadas</button>
        <a href="/logout" class="btn-logout">Sair 🔒</a>
    </nav>
</header>

<div class="container">
    <div class="top-info">
        <div>WhatsApp Comercial: <strong>(31) 98290-0087</strong></div>
        <div style="color: #27ae60; font-weight: bold;">● Painel Autenticado</div>
    </div>

    <div class="cards-summary">
        <div class="card"><h3>Total em Estoque</h3><p>__TOTAL_PECAS__</p></div>
        <div class="card"><h3>Valor Estoque (Venda)</h3><p>R$ __VALOR_ESTOQUE__</p></div>
        <div class="card"><h3>Vendas Realizadas</h3><p>R$ __TOTAL_VENDAS__</p></div>
    </div>

    <!-- ABA ESTOQUE -->
    <div id="tab-estoque" class="section active">
        <h2>Cadastrar Peça no Pátio</h2>
        
        <form action="/admin/cadastrar" method="post" enctype="multipart/form-data">
