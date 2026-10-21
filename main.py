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
        th { background: #f8f9fa; font-size: 12px; color: #555; }
        .img-thumb { width: 40px; height: 40px; object-fit: cover; border-radius: 4px; }
        #reader { width: 100%; max-width: 320px; margin: 10px auto; display: none; }
    </style>
</head>
<body>

<header>
    <h1>AUTON-LINE — Gestão de Pátio e Vendas</h1>
    <nav>
        <button id="btn-tab-estoque" class="active" onclick="switchTab('estoque')">Estoque Pátio</button>
        <button id="btn-tab-vendas" onclick="switchTab('vendas')">Vendas Realizadas</button>
        <a href="/logout" class="btn-logout">Sair 🔒</a>
    </nav>
</header>

<div class="container">
    <div class="top-info">
        <div>WhatsApp Comercial Configurado: <strong>(31) 98290-0087</strong></div>
        <div style="color: #27ae60; font-weight: bold;">Painel Administrativo Restrito</div>
    </div>

    <div class="cards-summary">
        <div class="card"><h3>Total em Estoque</h3><p>{{ total_pecas }}</p></div>
        <div class="card"><h3>Valor Estoque (Venda)</h3><p>R$ {{ "%.2f"|format(valor_estoque) }}</p></div>
        <div class="card"><h3>Vendas Realizadas</h3><p>R$ {{ "%.2f"|format(total_vendas) }}</p></div>
    </div>

    <!-- ABA ESTOQUE -->
    <div id="tab-estoque" class="section active">
        <h2>Cadastrar / Reutilizar Peça</h2>
        
        <div style="margin-bottom: 15px;">
            <label>Copiar dados de peça existente</label>
            <select onchange="preencherCamposExistentes(this.value)">
                <option value="">-- Selecione para duplicar informações --</option>
                {% for p in pecas_unicas %}
                <option value='{{ p | tojson | safe }}'>{{ p.descricao }} - {{ p.fabricante }} {{ p.modelo }} ({{ p.ano }})</option>
                {% endfor %}
            </select>
        </div>

        <form action="/admin/cadastrar" method="post" enctype="multipart/form-data">
            <div>
                <label>QR Code / Código Tag</label>
                <input type="text" id="codigo" name="codigo" placeholder="Ex: QR-001" required>
                <button type="button" onclick="toggleCamera()" style="margin-top:5px; background:#e67e22; color:white; border:none; padding:5px;">📷 Leitor QR</button>
            </div>
            <div>
                <label>Nº Baixa DETRAN</label>
                <input type="text" id="detran" name="detran" placeholder="Ex: BX-1234">
            </div>
            <div>
                <label>Fabricante</label>
                <input type="text" id="fabricante" name="fabricante" placeholder="Ex: FIAT" required>
            </div>
            <div>
                <label>Modelo</label>
                <input type="text" id="modelo" name="modelo" placeholder="Ex: Uno" required>
            </div>
            <div>
                <label>Ano</label>
                <input type="number" id="ano" name="ano" placeholder="Ex: 2020" required>
            </div>
            <div>
                <label>Cor</label>
                <input type="text" id="cor" name="cor" placeholder="Ex: Branco">
            </div>
            <div>
                <label>Descrição da Peça</label>
                <input type="text" id="descricao" name="descricao" placeholder="Ex: Alternador 75A" required>
            </div>
            <div>
                <label>Custo Inicial (R$)</label>
                <input type="number" step="0.01" id="custo_inicial" name="custo_inicial" placeholder="Ex: 100.00" oninput="calcularLucro(this.value)" required>
            </div>
            <div>
                <label>Preço Venda (+250%)</label>
                <input type="number" step="0.01" id="preco_venda" name="preco_venda" readonly style="background:#eef2f5;">
            </div>
            <div class="full-width">
                <label>Anexar Foto da Peça</label>
                <input type="file" name="foto_file" accept="image/*">
            </div>
            <div class="full-width">
                <div id="reader"></div>
            </div>
            <div class="full-width">
                <button type="submit" class="btn-primary">+ Registrar Peça no Pátio</button>
            </div>
        </form>

        <h2 style="margin-top: 30px;">Itens em Pátio</h2>
        <table>
            <thead>
                <tr>
                    <th>Foto</th>
                    <th>Código</th>
                    <th>Descrição</th>
                    <th>Veículo</th>
                    <th>Valor Venda</th>
                    <th>Ações</th>
                </tr>
            </thead>
            <tbody>
                {% for p in pecas_estoque %}
                <tr>
                    <td>{% if p.foto %}<img src="{{ p.foto }}" class="img-thumb">{% else %}<span style="font-size:10px; color:#aaa;">Sem foto</span>{% endif %}</td>
                    <td><strong>{{ p.codigo }}</strong></td>
                    <td>{{ p.descricao }}</td>
                    <td>{{ p.fabricante }} {{ p.modelo }} ({{ p.ano }})</td>
                    <td>R$ {{ "%.2f"|format(p.preco_venda or 0) }}</td>
                    <td>
                        <form action="/admin/vender/{{ p.id }}" method="post" style="display:inline;">
                            <button type="submit" class="btn-sell">Dar Baixa (Venda)</button>
                        </form>
                        <form action="/admin/excluir/{{ p.id }}" method="post" style="display:inline;" onsubmit="return confirm('Remover peça?');">
                            <button type="submit" class="btn-danger">Excluir</button>
                        </form>
                    </td>
                </tr>
                {% else %}
                <tr><td colspan="6" style="text-align:center;">Nenhum item em estoque.</td></tr>
                {% endfor %}
            </tbody>
        </table>
    </div>

    <!-- ABA VENDAS -->
    <div id="tab-vendas" class="section">
        <h2>Histórico de Baixas</h2>
        <table>
            <thead>
                <tr>
                    <th>Foto</th>
                    <th>Código</th>
                    <th>Descrição</th>
                    <th>Veículo</th>
                    <th>Valor de Venda</th>
                </tr>
            </thead>
            <tbody>
                {% for p in pecas_vendidas %}
                <tr>
                    <td>{% if p.foto %}<img src="{{ p.foto }}" class="img-thumb">{% else %}<span style="font-size:10px; color:#aaa;">Sem foto</span>{% endif %}</td>
                    <td><strong>{{ p.codigo }}</strong></td>
                    <td>{{ p.descricao }}</td>
                    <td>{{ p.fabricante }} {{ p.modelo }} ({{ p.ano }})</td>
                    <td>R$ {{ "%.2f"|format(p.preco_venda or 0) }}</td>
                </tr>
                {% else %}
                <tr><td colspan="5" style="text-align:center;">Nenhuma venda registrada.</td></tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>

<script>
    function switchTab(tabName) {
        document.querySelectorAll('.section').forEach(el => el.classList.remove('active'));
        document.querySelectorAll('nav button').forEach(el => el.classList.remove('active'));
        document.getElementById('tab-' + tabName).classList.add('active');
        document.getElementById('btn-tab-' + tabName).classList.add('active');
    }

    function calcularLucro(custo) {
        const val = parseFloat(custo);
        if (!isNaN(val) && val > 0) {
            document.getElementById('preco_venda').value = (val * 3.5).toFixed(2);
        } else {
            document.getElementById('preco_venda').value = '';
        }
    }

    function preencherCamposExistentes(jsonStr) {
        if (!jsonStr) return;
        const p = JSON.parse(jsonStr);
        document.getElementById('fabricante').value = p.fabricante || '';
        document.getElementById('modelo').value = p.modelo || '';
        document.getElementById('ano').value = p.ano || '';
        document.getElementById('cor').value = p.cor || '';
        document.getElementById('descricao').value = p.descricao || '';
        document.getElementById('detran').value = p.detran || '';
        if (p.custo_inicial) {
            document.getElementById('custo_inicial').value = p.custo_inicial;
            calcularLucro(p.custo_inicial);
        }
    }

    let html5QrCode;
    let cameraActive = false;
    function toggleCamera() {
        const reader = document.getElementById('reader');
        if (!cameraActive) {
            reader.style.display = 'block';
            html5QrCode = new Html5Qrcode("reader");
            html5QrCode.start(
                { facingMode: "environment" },
                { fps: 10, qrbox: 200 },
                (text) => {
                    document.getElementById('codigo').value = text;
                    toggleCamera();
                },
                () => {}
            );
            cameraActive = true;
        } else {
            if (html5QrCode) {
                html5QrCode.stop().then(() => {
                    reader.style.display = 'none';
                    cameraActive = false;
                });
            }
        }
    }
</script>

</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def admin_get(admin_auth: str = Cookie(None)):
    if admin_auth != "ativo":
        from jinja2 import Template
        return HTMLResponse(content=Template(HTML_LOGIN).render(erro=False))
    
    data = []
    if supabase:
        try:
            response = supabase.table("pecas").select("*").execute()
            data = response.data if response and response.data else []
        except Exception:
            data = []

    pecas_estoque = [p for p in data if p.get("status") != "vendido"]
    pecas_vendidas = [p for p in data if p.get("status") == "vendido"]

    total_pecas = len(pecas_estoque)
    valor_estoque = sum(float(p.get("preco_
