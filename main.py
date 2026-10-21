from fastapi import FastAPI, HTTPException, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from supabase import create_client, Client
import os
import json
import base64

app = FastAPI()

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://ijirrzrallxuqqagwviq.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "sb_publishable_oq13Ilt9dcMFxXSu862Rw_9Q4wa12-")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Autonline - Gestão e Catálogo de Peças</title>
    <script src="https://unpkg.com/html5-qrcode"></script>
    <style>
        * { box-sizing: border-box; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        body { margin: 0; padding: 0; background-color: #f4f6f9; color: #333; }
        header { background: #1a252f; color: white; padding: 15px 20px; display: flex; justify-content: space-between; align-items: center; }
        header h1 { margin: 0; font-size: 20px; }
        nav button { background: #34495e; color: white; border: none; padding: 8px 15px; margin-left: 5px; border-radius: 4px; cursor: pointer; }
        nav button.active { background: #27ae60; }
        .container { max-width: 1100px; margin: 20px auto; padding: 0 15px; }
        .cards-summary { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 20px; }
        .card { background: white; padding: 15px; border-radius: 6px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); text-align: center; }
        .card h3 { margin: 0 0 10px 0; font-size: 14px; color: #7f8c8d; text-transform: uppercase; }
        .card p { margin: 0; font-size: 22px; font-weight: bold; color: #2c3e50; }
        .section { display: none; background: white; padding: 20px; border-radius: 6px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
        .section.active { display: block; }
        form { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; }
        .full-width { grid-column: 1 / -1; }
        label { font-size: 12px; font-weight: bold; color: #555; margin-bottom: 4px; display: block; }
        input, select, button { width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 4px; font-size: 14px; }
        button.btn-primary { background: #27ae60; color: white; border: none; font-weight: bold; cursor: pointer; }
        button.btn-danger { background: #e74c3c; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; width: auto; }
        button.btn-sell { background: #2980b9; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; width: auto; }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #f8f9fa; font-size: 13px; color: #555; }
        tr.clickable { cursor: pointer; }
        tr.clickable:hover { background: #f1f4f8; }
        .img-thumb { width: 45px; height: 45px; object-fit: cover; border-radius: 4px; }
        #reader { width: 100%; max-width: 320px; margin: 10px auto; display: none; }
        
        .modal { display: none; position: fixed; z-index: 2000; left: 0; top: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.6); justify-content: center; align-items: center; }
        .modal-content { background: white; padding: 25px; border-radius: 8px; width: 90%; max-width: 550px; position: relative; max-height: 90vh; overflow-y: auto; }
        .close-modal { position: absolute; right: 15px; top: 10px; font-size: 24px; cursor: pointer; color: #888; }
        .modal-img { width: 100%; max-height: 250px; object-fit: contain; border-radius: 6px; margin-bottom: 15px; background: #eee; }
        .modal-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 10px; }
        .modal-item { background: #f8f9fa; padding: 8px 12px; border-radius: 4px; }
        .modal-item span { display: block; font-size: 11px; color: #7f8c8d; text-transform: uppercase; }
        .modal-item strong { font-size: 14px; color: #2c3e50; }
    </style>
</head>
<body>

<header>
    <h1>AUTONLINE - Gestão de Peças</h1>
    <nav>
        <button id="btn-tab-estoque" class="active" onclick="switchTab('estoque')">Estoque Pátio</button>
        <button id="btn-tab-vendas" onclick="switchTab('vendas')">Vendas</button>
        <button id="btn-tab-publico" onclick="switchTab('publico')">Catálogo Público</button>
    </nav>
</header>

<div class="container">
    <div class="cards-summary">
        <div class="card"><h3>Total em Estoque</h3><p>{{ total_pecas }}</p></div>
        <div class="card"><h3>Valor Estoque (Venda)</h3><p>R$ {{ "%.2f"|format(valor_estoque) }}</p></div>
        <div class="card"><h3>Vendas Realizadas</h3><p>R$ {{ "%.2f"|format(total_vendas) }}</p></div>
    </div>

    <!-- ABA ESTOQUE -->
    <div id="tab-estoque" class="section active">
        <h2>Cadastrar / Reutilizar Peça</h2>
        
        <div style="margin-bottom: 15px;">
            <label>Reutilizar Peça Existente</label>
            <select onchange="preencherCamposExistentes(this.value)">
                <option value="">-- Selecione uma peça já cadastrada para copiar dados --</option>
                {% for p in pecas_unicas %}
                <option value='{{ p | tojson | safe }}'>{{ p.descricao }} - {{ p.fabricante }} {{ p.modelo }} ({{ p.ano }})</option>
                {% endfor %}
            </select>
        </div>

        <form action="/cadastrar" method="post" enctype="multipart/form-data">
            <div>
                <label>QR Code / Tag</label>
                <input type="text" id="codigo" name="codigo" placeholder="Ex: QR-001" required>
                <button type="button" onclick="toggleCamera()" style="margin-top:5px; background:#e67e22; color:white; border:none; padding:5px;">📷 Escanear QR</button>
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
                <label>Carro / Modelo</label>
                <input type="text" id="modelo" name="modelo" placeholder="Ex: Uno" required>
            </div>
            <div>
                <label>Ano</label>
                <input type="number" id="ano" name="ano" placeholder="Ex: 2020" required>
            </div>
            <div>
                <label>Cor do Veículo</label>
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
                <label>Valor de Venda (250% Lucro)</label>
                <input type="number" step="0.01" id="preco_venda" name="preco_venda" placeholder="Calculado automaticamente" readonly style="background:#eef2f5;">
            </div>
            <div class="full-width">
                <label>Anexar Foto da Peça</label>
                <input type="file" name="foto_file" accept="image/*">
            </div>
            <div class="full-width">
                <div id="reader"></div>
            </div>
            <div class="full-width">
                <button type="submit" class="btn-primary">+ Cadastrar Peça no Pátio</button>
            </div>
        </form>

        <h2 style="margin-top: 30px;">Peças no Estoque</h2>
        <table>
            <thead>
                <tr>
                    <th>Foto</th>
                    <th>Código</th>
                    <th>Descrição</th>
                    <th>Modelo / Ano</th>
                    <th>Valor Venda</th>
                    <th>Ações</th>
                </tr>
            </thead>
            <tbody>
                {% for p in pecas_estoque %}
                <tr class="clickable" onclick='abrirModal({{ p | tojson | safe }})'>
                    <td>
                        {% if p.foto %}
                        <img src="{{ p.foto }}" class="img-thumb">
                        {% else %}
                        <span style="font-size:10px; color:#aaa;">Sem foto</span>
                        {% endif %}
                    </td>
                    <td><strong>{{ p.codigo }}</strong></td>
                    <td>{{ p.descricao }}</td>
                    <td>{{ p.fabricante }} {{ p.modelo }} ({{ p.ano }})</td>
                    <td>R$ {{ "%.2f"|format(p.preco_venda or 0) }}</td>
                    <td onclick="event.stopPropagation();">
                        <form action="/vender/{{ p.id }}" method="post" style="display:inline;">
                            <button type="submit" class="btn-sell">Vender</button>
                        </form>
                        <form action="/excluir/{{ p.id }}" method="post" style="display:inline;" onsubmit="return confirm('Confirmar exclusão permanente?');">
                            <button type="submit" class="btn-danger">Excluir</button>
                        </form>
                    </td>
                </tr>
                {% else %}
                <tr><td colspan="6" style="text-align:center;">Nenhuma peça no estoque.</td></tr>
                {% endfor %}
            </tbody>
        </table>
    </div>

    <!-- ABA VENDAS -->
    <div id="tab-vendas" class="section">
        <h2>Histórico de Vendas Realizadas</h2>
        <table>
            <thead>
                <tr>
                    <th>Foto</th>
                    <th>Código</th>
                    <th>Descrição</th>
                    <th>Modelo / Ano</th>
                    <th>Valor Vendido</th>
                </tr>
            </thead>
            <tbody>
                {% for p in pecas_vendidas %}
                <tr class="clickable" onclick='abrirModal({{ p | tojson | safe }})'>
                    <td>
                        {% if p.foto %}
                        <img src="{{ p.foto }}" class="img-thumb">
                        {% else %}
                        <span style="font-size:10px; color:#aaa;">Sem foto</span>
                        {% endif %}
                    </td>
                    <td><strong>{{ p.codigo }}</strong></td>
                    <td>{{ p.descricao }}</td>
                    <td>{{ p.fabricante }} {{ p.modelo }} ({{ p.ano }})</td>
                    <td>R$ {{ "%.2f"|format(p.preco_venda or 0) }}</td>
                </tr>
                {% else %}
                <tr><td colspan="5" style="text-align:center;">Nenhuma venda registrada ainda.</td></tr>
                {% endfor %}
            </tbody>
        </table>
    </div>

    <!-- ABA CATÁLOGO PÚBLICO -->
    <div id="tab-publico" class="section">
        <h2>Catálogo de Consulta Pública</h2>
        <div style="margin-bottom: 15px;">
            <input type="text" id="searchPublic" onkeyup="filtrarPublico()" placeholder="Buscar por modelo, fabricante ou peça (Ex: Uno, Alternador)...">
        </div>
        <table>
            <thead>
                <tr>
                    <th>Foto</th>
                    <th>Descrição</th>
                    <th>Modelo / Ano</th>
                    <th>Cor</th>
                    <th>Valor</th>
                </tr>
            </thead>
            <tbody id="publicTableBody">
                {% for p in pecas_estoque %}
                <tr class="clickable public-row" onclick='abrirModal({{ p | tojson | safe }}, true)'>
                    <td>
                        {% if p.foto %}
                        <img src="{{ p.foto }}" class="img-thumb">
                        {% else %}
                        <span style="font-size:10px; color:#aaa;">Sem foto</span>
                        {% endif %}
                    </td>
                    <td>{{ p.descricao }}</td>
                    <td>{{ p.fabricante }} {{ p.modelo }} ({{ p.ano }})</td>
                    <td>{{ p.cor or '-' }}</td>
                    <td>R$ {{ "%.2f"|format(p.preco_venda or 0) }}</td>
                </tr>
                {% else %}
                <tr><td colspan="5" style="text-align:center;">Nenhuma peça disponível para consulta pública.</td></tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>

<!-- MODAL MÉDIO DE DETALHES -->
<div id="modalDetalhes" class="modal">
    <div class="modal-content">
        <span class="close-modal" onclick="fecharModal()">&times;</span>
        <h3 id="modal-titulo" style="margin-top:0; color:#1a252f;">Detalhes do Item</h3>
        <img id="modal-img" src="" class="modal-img" style="display:none;">
        <div class="modal-grid">
            <div class="modal-item" id="box-codigo"><span>Código Tag / QR</span><strong id="m-codigo"></strong></div>
            <div class="modal-item" id="box-detran"><span>Nº Baixa DETRAN</span><strong id="m-detran"></strong></div>
            <div class="modal-item"><span>Descrição</span><strong id="m-descricao"></strong></div>
            <div class="modal-item"><span>Veículo / Modelo</span><strong id="m-modelo"></strong></div>
            <div class="modal-item"><span>Ano</span><strong id="m-ano"></strong></div>
            <div class="modal-item"><span>Cor</span><strong id="m-cor"></strong></div>
            <div class="modal-item"><span>Preço de Venda</span><strong id="m-preco" style="color:#27ae60;"></strong></div>
            <div class="modal-item"><span>Status</span><strong id="m-status"></strong></div>
        </div>
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
            const venda = val * 3.5;
            document.getElementById('preco_venda').value = venda.toFixed(2);
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

    function abrirModal(p, isPublic = false) {
        document.getElementById('modal-titulo').innerText = (p.descricao || '') + " - " + (p.fabricante || '') + " " + (p.modelo || '');
        document.getElementById('m-descricao').innerText = p.descricao || '-';
        document.getElementById('m-modelo').innerText = (p.fabricante || '') + ' ' + (p.modelo || '');
        document.getElementById('m-ano').innerText = p.ano || '-';
        document.getElementById('m-cor').innerText = p.cor || '-';
        document.getElementById('m-preco').innerText = 'R$ ' + parseFloat(p.preco_venda || 0).toFixed(2);
        document.getElementById('m-status').innerText = (p.status === 'vendido') ? 'Vendido' : 'Disponível em Estoque';

        if (isPublic) {
            document.getElementById('box-codigo').style.display = 'none';
            document.getElementById('box-detran').style.display = 'none';
        } else {
            document.getElementById('box-codigo').style.display = 'block';
            document.getElementById('box-detran').style.display = 'block';
            document.getElementById('m-codigo').innerText = p.codigo || '-';
            document.getElementById('m-detran').innerText = p.detran || '-';
        }

        const imgEl = document.getElementById('modal-img');
        if (p.foto) {
            imgEl.src = p.foto;
            imgEl.style.display = 'block';
        } else {
            imgEl.style.display = 'none';
        }

        document.getElementById('modalDetalhes').style.display = 'flex';
    }

    function fecharModal() {
        document.getElementById('modalDetalhes').style.display = 'none';
    }

    function filtrarPublico() {
        const input = document.getElementById('searchPublic').value.toLowerCase();
        const rows = document.querySelectorAll('.public-row');
        rows.forEach(row => {
            const text = row.innerText.toLowerCase();
            row.style.display = text.includes(input) ? '' : 'none';
        });
    }

    window.onclick = function(e) {
        if (e.target == document.getElementById('modalDetalhes')) fecharModal();
    }
</script>

</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
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
    template = Template(HTML_TEMPLATE)
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

@app.post("/cadastrar")
async def cadastrar(
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

    supabase.table("pecas").insert(payload).execute()
    return RedirectResponse(url="/", status_code=303)

@app.post("/vender/{peca_id}")
async def vender(peca_id: int):
    supabase.table("pecas").update({"status": "vendido"}).eq("id", peca_id).execute()
    return RedirectResponse(url="/", status_code=303)

@app.post("/excluir/{peca_id}")
async def excluir(peca_id: int):
    supabase.table("pecas").delete().eq("id", peca_id).execute()
    return RedirectResponse(url="/", status_code=303)
