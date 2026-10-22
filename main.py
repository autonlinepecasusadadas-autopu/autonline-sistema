from fastapi import FastAPI, Request, Form
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

HTML_ADMIN = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>AUTON-LINE - Gestão de Pátio e Vendas</title>
    <style>
        * { box-sizing: border-box; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        body { margin: 0; padding: 0; background-color: #f4f6f9; color: #333; }
        header { background: #1a252f; color: white; padding: 15px 20px; display: flex; justify-content: space-between; align-items: center; border-bottom: 3px solid #f1c40f; }
        header h1 { margin: 0; font-size: 18px; color: #f1c40f; }
        nav { display: flex; gap: 8px; align-items: center; }
        nav button { background: #34495e; color: white; border: none; padding: 8px 15px; border-radius: 4px; cursor: pointer; font-size: 14px; }
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
        input, select, button { width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 4px; font-size: 14px; outline: none; }
        button.btn-primary { background: #27ae60; color: white; border: none; font-weight: bold; cursor: pointer; }
        button.btn-danger { background: #e74c3c; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; width: auto; }
        button.btn-sell { background: #2980b9; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; width: auto; }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        th, td { padding: 10px 12px; text-align: left; border-bottom: 1px solid #ddd; font-size: 14px; }
        th { background: #f8f9fa; font-size: 12px; color: #555; }
        .img-thumb { width: 40px; height: 40px; object-fit: cover; border-radius: 4px; }
    </style>
</head>
<body>

<header>
    <h1>AUTON-LINE — Gestão de Pátio e Vendas</h1>
    <nav>
        <button id="btn-tab-estoque" class="active" onclick="switchTab('estoque')">Estoque Pátio</button>
        <button id="btn-tab-vendas" onclick="switchTab('vendas')">Vendas Realizadas</button>
    </nav>
</header>

<div class="container">
    <div class="top-info">
        <div>WhatsApp Comercial Configurado: <strong>(31) 98290-0087</strong></div>
        <div style="color: #27ae60; font-weight: bold;">Painel Administrativo Interno</div>
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
                <input type="number" step="0.01" id="preco_venda" name="preco_venda" readonly style="background:#eef2f5;">
            </div>
            <div class="full-width">
                <label>Anexar Foto da Peça</label>
                <input type="file" name="foto_file" accept="image/*">
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
                __TABELA_ESTOQUE__
            </tbody>
        </table>
    </div>

    <!-- ABA VENDAS -->
    <div id="tab-vendas" class="section">
        <h2>Registar Nova Venda Diretamente</h2>
        
        <form action="/admin/cadastrar_venda" method="post" enctype="multipart/form-data" style="margin-bottom: 30px; background: #fff; padding: 15px; border-radius: 6px; border: 1px solid #ddd;">
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
async def admin_get():
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
            foto_tag = f'<img src="{p.get("foto")}" class="img-thumb">' if p.get("foto") else '<span style="color:#aaa;">Sem foto</span>'
            linhas_estoque += f"""
                <tr>
                    <td>{foto_tag}</td>
                    <td><strong>{p.get('codigo', '')}</strong></td>
                    <td>{p.get('descricao', '')}</td>
                    <td>{p.get('fabricante', '')} {p.get('modelo', '')} ({p.get('ano', '')})</td>
                    <td>R$ {float(p.get('preco_venda', 0) or 0):.2f}</td>
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
        linhas_estoque = '<tr><td colspan="6" style="text-align:center;">Nenhum item em estoque.</td></tr>'

    linhas_vendas = ""
    if pecas_vendidas:
        for p in pecas_vendidas:
            foto_tag = f'<img src="{p.get("foto")}" class="img-thumb">' if p.get("foto") else '<span style="color:#aaa;">Sem foto</span>'
            linhas_vendas += f"""
                <tr>
                    <td>{foto_tag}</td>
                    <td><strong>{p.get('codigo', '')}</strong></td>
                    <td>{p.get('descricao', '')}</td>
                    <td>{p.get('fabricante', '')} {p.get('modelo', '')} ({p.get('ano', '')})</td>
                    <td>R$ {float(p.get('preco_venda', 0) or 0):.2f}</td>
                    <td>
                        <form action="/admin/excluir/{p.get('id')}" method="post" style="display:inline;" onsubmit="return confirm('Remover registo de venda?');">
                            <button type="submit" class="btn-danger">Excluir</button>
                        </form>
                    </td>
                </tr>
            """
    else:
        linhas_vendas = '<tr><td colspan="6" style="text-align:center;">Nenhuma venda registada.</td></tr>'

    html_final = HTML_ADMIN \
        .replace("__TOTAL_PECAS__", str(total_pecas)) \
        .replace("__VALOR_ESTOQUE__", f"{valor_estoque:.2f}") \
        .replace("__TOTAL_VENDAS__", f"{total_vendas:.2f}") \
        .replace("__TABELA_ESTOQUE__", linhas_estoque) \
        .replace("__TABELA_VENDAS__", linhas_vendas)

    return HTMLResponse(content=html_final)

@app.post("/admin/cadastrar")
async def admin_cadastrar(
    request: Request,
    codigo: str = Form(...),
    detran: str = Form(None),
    fabricante: str = Form(...),
    modelo: str = Form(...),
    ano: int = Form(...),
    cor: str = Form(None),
    descricao: str = Form(...),
    custo_inicial: float = Form(...),
    preco_venda: float = Form(...)
):
    foto_b64 = None
    try:
        form_data = await request.form()
        uploaded_file = form_data.get("foto_file")
        if uploaded_file and hasattr(uploaded_file, "filename") and uploaded_file.filename:
            content = await uploaded_file.read()
            if content:
                encoded = base64.b64encode(content).decode("utf-8")
                foto_b64 = f"data:{uploaded_file.content_type};base64,{encoded}"
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
    request: Request,
    codigo: str = Form(...),
    fabricante: str = Form(...),
    modelo: str = Form(...),
    ano: int = Form(...),
    descricao: str = Form(...),
    preco_venda: float = Form(...)
):
    foto_b64 = None
    try:
        form_data = await request.form()
        uploaded_file = form_data.get("foto_file")
        if uploaded_file and hasattr(uploaded_file, "filename") and uploaded_file.filename:
            content = await uploaded_file.read()
            if content:
                encoded = base64.b64encode(content).decode("utf-8")
                foto_b64 = f"data:{uploaded_file.content_type};base64,{encoded}"
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
