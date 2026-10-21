from fastapi import FastAPI, Request, Form, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
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
WHATSAPP_NUMERO = "5531982900087"

HTML_LOGIN = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>AUTON-LINE | Gestão Exclusiva</title>
    <style>
        * { box-sizing: border-box; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        body { background: #121212; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; color: #fff; }
        .login-box { background: #1e1e1e; padding: 35px; border-radius: 8px; border: 1px solid #333; width: 340px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
        h2 { color: #f1c40f; margin-bottom: 20px; font-size: 22px; letter-spacing: 1px; }
        input { width: 100%; padding: 12px; margin-bottom: 15px; border: 1px solid #444; background: #222; color: white; border-radius: 4px; font-size: 15px; outline: none; }
        button { width: 100%; padding: 12px; background: #27ae60; color: white; border: none; font-weight: bold; border-radius: 4px; cursor: pointer; font-size: 15px; }
        button:hover { background: #219150; }
        .error { color: #e74c3c; font-size: 13px; margin-bottom: 12px; }
    </style>
</head>
<body>
<div class="login-box">
    <h2>AUTON-LINE ADM</h2>
    {% if erro %}<div class="error">Senha incorreta. Tente novamente.</div>{% endif %}
    <form action="/login" method="post">
        <input type="password" name="senha" placeholder="Palavra-passe de acesso" required>
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
    <script src="https://unpkg.com/html5-qrcode"></script>
    <style>
        * { box-sizing: border-box; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        body { margin: 0; padding: 0; background-color: #f4f6f9; color: #333; }
        header { background: #1a252f; color: white; padding: 15px 20px; display: flex; justify-content: space-between; align-items: center; border-bottom: 3px solid #f1c40f; }
        header h1 { margin: 0; font-size: 18px; color: #f1c40f; }
        nav { display: flex; gap: 8px; align-items: center; }
        nav button, .btn-logout { background: #34495e; color: white; border: none; padding: 8px 15px; border-radius: 4px; cursor: pointer; font-size: 14px; text-decoration: none; }
        nav button.active { background: #27ae60; }
        .btn-logout { background: #c0392b; font-size: 13px; font-weight: bold; }
        .btn-logout:hover { background: #a93226; }
        .container { max-width: 1100px; margin: 20px auto; padding: 0 15px; }
        .top-info { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; background: white; padding: 12px 20px; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
        .cards-summary { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 20px; }
        .card { background: white; padding: 15px; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); text-align: center; }
        .card h3 { margin: 0 0 8px 0; font-size: 13px; color: #7f8c8d; text-transform: uppercase; }
        .card p { margin: 0; font-size: 20px; font-weight: bold; color: #2c3e50; }
        .section { display: none; background: white; padding: 20px; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
        .section.active { display: block; }
        form { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; }
        .full-width { grid-column: 1 / -1; }
        label { font-size: 12px; font-weight: bold; color: #555; margin-bottom: 4px; display: block; }
        input, select, button { width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 4px; font-size: 14px; outline: none; }
        button.btn-primary { background: #27ae60; color: white; border: none; font-weight: bold; cursor: pointer; }
        button.btn-danger { background: #e74c3c; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; width: auto; }
        button.btn-sell { background: #2980b9; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; width: auto; }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        th, td { padding: 10px 12px; text-align: left; border-bottom: 1px solid #ddd; font-size: 14px; }
        th { background: #
