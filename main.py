from fastapi import FastAPI, Request, Form, Cookie, UploadFile, File
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
            <div>
                <label>QR Code / Código Tag</label>
                <input type="text" name="codigo" placeholder="Ex: QR-001" required>
            </div>
            <div>
                <label>Nº Baixa DETRAN</label>
                <input type="text" name="detran" placeholder="Ex: BX-1234">
            </div>
            <div>
                <label>Fabricante</label>
                <input type="text" name="fabricante" placeholder="Ex: FIAT" required>
            </div>
            <div>
                <label>Modelo</label>
                <input type="text" name="modelo" placeholder="Ex: Uno" required>
            </div>
            <div>
                <label>Ano</label>
                <input type="number" name="ano" placeholder="Ex: 2020" required>
            </div>
            <div>
                <label>Cor</label>
                <input type="text" name="cor" placeholder="Ex: Branco">
            </div>
            <div>
                <label>Descrição da Peça</label>
                <input type="text" name="descricao" placeholder="Ex: Alternador 75A" required>
            </div>
            <div>
                <label>Custo Inicial (R$)</label>
                <input type="number" step="0.01" name="custo_inicial" placeholder="Ex: 100.00" oninput="document.getElementById('preco_venda').value = (this.value * 3.5).toFixed(2)" required>
            </div>
            <div>
                <label>Preço Venda (+250%)</label>
                <input type="number" step="0.01" id="preco_venda" name="preco_venda" readonly style="background:#1a1a1a; color:#f1c40f; font-weight:bold;">
            </div>
            <div class="full-width">
                <label>Anexar Foto da Peça</label>
                <input type="file" name="foto_file" accept="image/*">
            </div>
            <div class="full-width">
                <button type="submit" class="btn-primary">+ Registrar Peça no Pátio</button>
            </div>
        </form>

        <h2 style="margin-top: 35px;">Itens em Pátio</h2>
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
                __TABELA_ESTOQUE__
            </tbody>
        </table>
    </div>

    <!-- ABA VENDAS -->
    <div id="tab-vendas" class="section">
        <h2>Registar Nova Venda Diretamente</h2>
        
        <form action="/admin/cadastrar_venda" method="post" enctype="multipart/form-data" style="margin-bottom: 30px; background: #161616; padding: 18px; border-radius: 6px; border: 1px solid #333;">
            <div>
                <label>Código Tag</label>
                <input type="text" name="codigo" placeholder="Ex: V-001" required>
            </div>
            <div>
                <label>Fabricante</label>
                <input type="text" name="fabricante" placeholder="Ex: VW" required>
            </div>
            <div>
                <label>Modelo</label>
                <input type="text" name="modelo" placeholder="Ex: Gol" required>
            </div>
            <div>
                <label>Ano</label>
                <input type="number" name="ano" placeholder="Ex: 2018" required>
            </div>
            <div>
                <label>Descrição da Peça</label>
                <input type="text" name="descricao" placeholder="Ex: Farol Dianteiro" required>
            </div>
            <div>
                <label>Valor de Venda (R$)</label>
                <input type="number" step="0.01" name="preco_venda" placeholder="Ex: 250.00" required>
            </div>
            <div class="full-width">
                <label>Anexar Foto da Peça</label>
                <input type="file" name="foto_file" accept="image/*">
            </div>
            <div class="full-width">
                <button type="submit" class="btn-primary" style="background:#2980b9;">+ Adicionar Venda Concluída</button>
            </div>
        </form>

        <h2>Histórico de Vendas Realizadas</h2>
        <table>
            <thead>
                <tr>
                    <th>Foto</th>
                    <th>Código</th>
                    <th>Descrição</th>
                    <th>Veículo</th>
                    <th>Valor de Venda</th>
                    <th>Ações</th>
                </tr>
            </thead>
            <tbody>
                __TABELA_VENDAS__
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
    valor_estoque = sum(float(p.get("preco_venda", 0) or 0) for p in pecas_estoque)
    total_vendas = sum(float(p.get("preco_venda", 0) or 0) for p in pecas_vendidas)

    linhas_estoque = ""
    if pecas_estoque:
        for p in pecas_estoque:
            foto_tag = f'<img src="{p.get("foto")}" class="img-thumb">' if p.get("foto") else '<span style="color:#777;">Sem foto</span>'
            linhas_estoque += f"""
                <tr>
                    <td>{foto_tag}</td>
                    <td><strong>{p.get('codigo', '')}</strong></td>
                    <td>{p.get('descricao', '')}</td>
                    <td>{p.get('fabricante', '')} {p.get('modelo', '')} ({p.get('ano', '')})</td>
                    <td style="color:#2ecc71; font-weight:bold;">R$ {float(p.get('preco_venda', 0) or 0):.2f}</td>
                    <td>
                        <form action="/admin/vender/{p.get('id')}" method="post" style="display:inline;">
                            <button type="submit" class="btn-sell">Dar Baixa</button>
                        </form>
                        <form action="/admin/excluir/{p.get('id')}" method="post" style="display:inline;" onsubmit="return confirm('Remover?');">
                            <button type="submit" class="btn-danger">Excluir</button>
                        </form>
                    </td>
                </tr>
            """
    else:
        linhas_estoque = '<tr><td colspan="6" style="text-align:center; color:#777;">Nenhum item em estoque.</td></tr>'

    linhas_vendas = ""
    if pecas_vendidas:
        for p in pecas_vendidas:
            foto_tag = f'<img src="{p.get("foto")}" class="img-thumb">' if p.get("foto") else '<span style="color:#777;">Sem foto</span>'
            linhas_vendas += f"""
                <tr>
                    <td>{foto_tag}</td>
                    <td><strong>{p.get('codigo', '')}</strong></td>
                    <td>{p.get('descricao', '')}</td>
                    <td>{p.get('fabricante', '')} {p.get('modelo', '')} ({p.get('ano', '')})</td>
                    <td style="color:#2ecc71; font-weight:bold;">R$ {float(p.get('preco_venda', 0) or 0):.2f}</td>
                    <td>
                        <form action="/admin/excluir/{p.get('id')}" method="post" style="display:inline;" onsubmit="return confirm('Remover registo de venda?');">
                            <button type="submit" class="btn-danger">Excluir</button>
                        </form>
                    </td>
                </tr>
            """
    else:
        linhas_vendas = '<tr><td colspan="6" style="text-align:center; color:#777;">Nenhuma venda registada.</td></tr>'

    from jinja2 import Template
    template = Template(HTML_ADMIN)
    rendered = template.render(
        total_pecas=total_pecas,
        valor_estoque=valor_estoque,
        total_vendas=total_vendas,
        tojson=lambda x: json.dumps(x)
    )
    return HTMLResponse(content=rendered.replace("__TABELA_ESTOQUE__", linhas_estoque).replace("__TABELA_VENDAS__", linhas_vendas))

@app.post("/login")
async def admin_login(senha: str = Form(...)):
    if senha == SENHA_ADMIN:
        response = RedirectResponse(url="/", status_code=303)
        response.set_cookie(key="admin_auth", value="ativo")
        return response
    
    from jinja2 import Template
    return HTMLResponse(content=Template(HTML_LOGIN).render(erro=True))

@app.get("/logout")
async def admin_logout():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie(key="admin_auth")
    return response

@app.post("/admin/cadastrar")
async def admin_cadastrar(
    codigo: str = Form(...),
    detran: str = Form(None),
    fabricante: str = Form(...),
    modelo: str = Form(...),
    ano: int = Form(...),
    cor: str = Form(None),
    descricao: str = Form(...),
    custo_inicial: float = Form(...),
    preco_venda: float = Form(...),
    foto_file: UploadFile = File(None)
):
    foto_b64 = None
    try:
        if foto_file and foto_file.filename:
            content = await foto_file.read()
            if content:
                encoded = base64.b64encode(content).decode("utf-8")
                foto_b64 = f"data:{foto_file.content_type};base64,{encoded}"
    except Exception:
        pass

    payload = {
        "codigo": codigo,
        "detran": detran,
        "fabricante": fabricante,
        "modelo": modelo,
        "ano": ano,
        "cor": cor,
        "descricao": descricao,
        "custo_inicial": custo_inicial,
        "preco_venda": preco_venda,
        "status": "disponivel"
    }
    if foto_b64:
        payload["foto"] = foto_b64

    if supabase:
        supabase.table("pecas").insert(payload).execute()
    return RedirectResponse(url="/", status_code=303)

@app.post("/admin/cadastrar_venda")
async def admin_cadastrar_venda(
    codigo: str = Form(...),
    fabricante: str = Form(...),
    modelo: str = Form(...),
    ano: int = Form(...),
    descricao: str = Form(...),
    preco_venda: float = Form(...),
    foto_file: UploadFile = File(None)
):
    foto_b64 = None
    try:
        if foto_file and foto_file.filename:
            content = await foto_file.read()
            if content:
                encoded = base64.b64encode(content).decode("utf-8")
                foto_b64 = f"data:{foto_file.content_type};base64,{encoded}"
    except Exception:
        pass

    payload = {
        "codigo": codigo,
        "fabricante": fabricante,
        "modelo": modelo,
        "ano": ano,
        "descricao": descricao,
        "preco_venda": preco_venda,
        "status": "vendido"
    }
    if foto_b64:
        payload["foto"] = foto_b64

    if supabase:
        supabase.table("pecas").insert(payload).execute()
    return RedirectResponse(url="/", status_code=303)

@app.post("/admin/vender/{peca_id}")
async def admin_vender(peca_id: int):
    if supabase:
        supabase.table("pecas").update({"status": "vendido"}).eq("id", peca_id).execute()
    return RedirectResponse(url="/", status_code=303)

@app.post("/admin/excluir/{peca_id}")
async def admin_excluir(peca_id: int):
    if supabase:
        supabase.table("pecas").delete().eq("id", peca_id).execute()
    return RedirectResponse(url="/", status_code=303)
