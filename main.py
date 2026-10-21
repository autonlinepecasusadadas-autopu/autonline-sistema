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

# Configurações do sistema
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
        header { background: #000000; border-bottom: 3px solid #f1c40f; padding: 25px 15px; text-align: center; position: relative; }
        .header-title { color: #f1c40f; font-size: 28px; font-weight: bold; margin: 0; letter-spacing: 1px; }
        .header-sub { color: #ffffff; font-size: 13px; margin-top: 6px; font-style: italic; }
        .admin-link { position: absolute; right: 20px; top: 20px; background: #222; color: #f1c40f; padding: 8px 14px; border-radius: 4px; text-decoration: none; font-size: 12px; font-weight: bold; border: 1px solid #f1c40f; }
        .admin-link:hover { background: #f1c40f; color: #000; }
        .container { max-width: 1200px; margin: 25px auto; padding: 0 15px; }
        .search-box { margin-bottom: 30px; text-align: center; }
        .search-box input { width: 100%; max-width: 550px; padding: 14px 20px; border-radius: 25px; border: 1px solid #444; background: #1e1e1e; color: white; font-size: 16px; outline: none; }
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
        input, select, button { width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 4px; font-size: 14px; }
        button.btn-primary { background: #27ae60; color: white; border: none; font-weight: bold; cursor: pointer; }
        button.btn-danger { background: #e74c3c; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; width: auto; }
        button.btn-sell { background: #2980b9; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; width: auto; }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        th, td { padding: 10px 12px; text-align: left; border-bottom: 1px solid #ddd; font-size: 14px; }
        th { background: #f8f9fa; font-size: 12px; color: #555; }
        .img-thumb { width: 40px; height: 40px; object-fit: cover; border-radius: 4px; }
        #reader { width: 100%; max-width: 320px; margin: 10px auto; display: none; }
        .btn-link-publico { background: #e67e22; color: white; text-decoration: none; padding: 8px 14px; border-radius: 4px; font-size: 12px; font-weight: bold; }
    </style>
</head>
<body>

<header>
    <h1>AUTON-LINE — Gestão de Pátio</h1>
    <nav>
        <button id="btn-tab-estoque" class="active" onclick="switchTab('estoque')">Estoque Pátio</button>
        <button id="btn-tab-vendas" onclick="switchTab('vendas')">Vendas Realizadas</button>
    </nav>
</header>

<div class="container">
    <div class="top-info">
        <div>WhatsApp Comercial: <strong>(31) 98290-0087</strong></div>
        <a href="/" class="btn-link-publico" target="_blank">🌐 Visualizar Catálogo Público</a>
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
async def catalogo_publico():
    try:
        response = supabase.table("pecas").select("*").execute()
        data = response.data if response.data else []
    except Exception:
        data = []
    
    pecas_estoque = [p for p in data if p.get("status") != "vendido"]

    from jinja2 import Template
    template = Template(HTML_CATALOGO_PUBLICO)
    rendered = template.render(pecas=pecas_estoque, whatsapp=WHATSAPP_NUMERO)
    return HTMLResponse(content=rendered)

@app.get("/admin", response_class=HTMLResponse)
async def admin_get(admin_auth: str = Cookie(None)):
    if admin_auth != "ativo":
        from jinja2 import Template
        return HTMLResponse(content=Template(HTML_LOGIN).render(erro=False))
    
    try:
        response = supabase.table("pecas").select("*").execute()
        data = response.data if response.data else []
    except Exception:
        data = []

    pecas_estoque = [p for p in data if p.get("status") != "vendido"]
    pecas_vendidas = [p for p in data if p.get("status") == "vendido"]

    total_pecas = len(pecas_estoque)
    valor_estoque = sum(float(p.get("preco_venda", 0) or 0) for p in pecas_estoque)
    total_vendas = sum(float(p.get("preco_venda", 0) or 0) for p in pecas_vendidas)

    vistas = set()
    pecas_unicas = []
    for p in data:
        chave = f"{p.get('fabricante')}-{p.get('modelo')}-{p.get('descricao')}"
        if chave not in vistas:
            vistas.add(chave)
            pecas_unicas.append(p)

    from jinja2 import Template
    template = Template(HTML_ADMIN)
    rendered = template.render(
        total_pecas=total_pecas,
        valor_estoque=valor_estoque,
        total_vendas=total_vendas,
        pecas_estoque=pecas_estoque,
        pecas_vendidas=pecas_vendidas,
        pecas_unicas=pecas_unicas,
        tojson=lambda x: json.dumps(x)
    )
    return HTMLResponse(content=rendered)

@app.post("/admin-login")
async def admin_login(senha: str = Form(...)):
    if senha == SENHA_ADMIN:
        response = RedirectResponse(url="/admin", status_code=303)
        response.set_cookie(key="admin_auth", value="ativo")
        return response
    
    from jinja2 import Template
    return HTMLResponse(content=Template(HTML_LOGIN).render(erro=True))

@app.post("/admin/cadastrar")
async def admin_cadastrar(
