O campo de preço de venda foi ajustado para permitir **edição manual direta**, mantendo o cálculo automático inicial de 250% sobre o custo como uma sugestão base que pode ser alterada a qualquer momento.

Abaixo está o arquivo **`main.py`** completo e atualizado com essa correção:

```python
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
    <script src="https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js"></script>
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
        input:focus, select:focus { border-color: #f1c40f; }
        button.btn-primary { background: #27ae60; color: white; border: none; font-weight: bold; cursor: pointer; transition: background 0.2s; }
        button.btn-primary:hover { background: #219653; }
        button.btn-danger { background: #c0392b; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; width: auto; font-weight: 600; }
        button.btn-danger:hover { background: #a93226; }
        button.btn-sell { background: #2980b9; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; width: auto; font-weight: 600; }
        button.btn-sell:hover { background: #2471a3; }
        button.btn-print { background: #d35400; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; width: auto; font-weight: 600; }
        button.btn-print:hover { background: #ba4a00; }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #333; font-size: 14px; }
        th { background: #161616; font-size: 12px; color: #f1c40f; text-transform: uppercase; }
        tr:hover { background: #252525; }
        .img-thumb { width: 45px; height: 45px; object-fit: cover; border-radius: 4px; border: 1px solid #444; }
        .tag-local { background: #f39c12; color: #000; padding: 2px 6px; border-radius: 3px; font-size: 11px; font-weight: bold; }
    </style>
    <script>
        const modelosPorFabricante = {
            "Audi": ["80", "100", "A1", "A3 Sedan", "A3 Sportback", "A4", "A4 Avant", "A5 Coupé", "A5 Cabriolet", "A5 Sedan", "A5 Sportback", "A5 Avant", "A6", "A6 Avant", "A6 e-tron", "A7 Sportback", "A8", "e-tron SUV", "e-tron Sportback", "e-tron GT", "RS e-tron GT", "Q2", "Q3", "Q3 Sportback", "Q4 e-tron", "Q5", "Q5 Sportback", "Q6 e-tron", "Q7", "Q8", "R8", "R8 Spyder", "RS 3 Sedan", "RS 3 Sportback", "RS 4 Avant", "RS 6 Avant", "RS Q3", "RS Q8", "S3", "S4", "S6", "TT", "TTS", "TT RS"],
            "BMW": ["i3", "i4", "i7", "i8", "iX", "iX1", "iX2", "iX3", "iX5", "M2", "M3 Sedan", "M3 Touring", "M4", "M5", "M6", "M8", "M135i", "M140i", "Série 1", "Série 2 Coupé", "Série 2 Gran Coupé", "Série 3", "Série 3 Touring", "Série 4 Coupé", "Série 4 Cabrio", "Série 4 Gran Coupé", "Série 5", "Série 5 Touring", "Série 6", "Série 7", "Série 8", "X1", "X2", "X3", "X4", "X5", "X6", "X7", "XM", "Z3", "Z4"],
            "BYD": ["Atto 2", "Atto 8", "Dolphin", "Dolphin Mini", "Dolphin Plus", "Dolphin SE", "Han", "King", "Seal", "Sealion 7", "Song Plus", "Song Pro", "Tan", "Yuan Plus", "Yuan Pro"],
            "Caoa Chery": ["Arrizo 5", "Arrizo 6", "Celer Hatch", "Celer Sedan", "Cielo Sedan", "Face", "QQ", "Tiggo (original)", "Tiggo 2", "Tiggo 3X", "Tiggo 5X", "Tiggo 7", "Tiggo 8", "Tiggo 9"],
            "Chevrolet": ["Agile", "Astra", "Astra Sedan", "Blazer", "Blazer EV", "Bolt EV", "Bolt EUV", "Calibra", "Camaro Cupê", "Camaro Conversível", "Captiva", "Celta", "Chevette", "Chevette Hatch", "Corsa", "Corsa Sedan", "Corsa Wagon", "Classic", "Cruze", "Cruze Sport6", "Equinox", "Equinox EV", "Grand Vitara", "Kadett", "Malibu", "Marajó", "Meriva", "Monza", "Omega", "Onix", "Onix Plus", "Opala", "Opala Cupê", "Prisma", "Cobalt", "Sonic", "Sonic Sedan", "Spin", "Tracker", "Trailblazer", "Vectra", "Vectra GT", "Zafira"],
            "Citroën": ["AirCross", "AX", "C3", "C3 Aircross", "C3 X-Air", "C4 Cactus", "C4 Lounge", "C4 Pallas", "C4 Picasso", "Grand C4 Picasso", "C5", "C5 Break", "C5 Aircross", "C5 X", "C6", "DS3", "DS4", "DS5", "Xantia", "Xantia Break", "XM", "Xsara", "Xsara Picasso", "ZX", "Saxo"],
            "Fiat": ["147", "500 (Cinquecento)", "500C", "500e", "Argo", "Barchetta", "Brava", "Bravo", "Coupé", "Cronos", "Elba", "Fastback", "Freemont", "Grand Siena", "Linea", "Marea", "Marea Weekend", "Mobi", "Oggi", "Palio", "Palio Weekend", "Prêmio", "Pulse", "Punto", "Stilo", "Tempra", "Tipo", "Uno"],
            "Honda": ["Accord", "City", "City Hatchback", "Civic", "Civic Hatch", "Civic VTi", "Civic si", "Civic Type R", "CR-V", "Fit", "HR-V", "WR-V", "ZR-V"],
            "Hyundai": ["Accent", "Atos Prime", "Azera", "Creta", "Elantra", "Equus", "Genesis", "HB20", "HB20S", "i30", "i30 CW", "Ioniq", "ix35", "Kona", "Palisade", "Santa Fe", "Sonata", "Terracan", "Tucson", "Veloster", "Veracruz"],
            "Mitsubishi": ["ASX", "Colt", "Eclipse Cross", "Galant", "Lancer", "Outlander", "Pajero Full", "Pajero IO", "Pajero TR4", "Pajero Dakar", "Pajero Sport"],
            "Nissan": [], "Peugeot": [], "Ram": [], "Renault": [], "Suzuki": [], "Toyota": [], "Volkswagen": []
        };

        function atualizarModelos(prefixo) {
            const fabSelect = document.getElementById(prefixo + '_fabricante');
            const modSelect = document.getElementById(prefixo + '_modelo');
            const fab = fabSelect.value;
            
            modSelect.innerHTML = '<option value="">Selecione o Modelo</option>';
            if (modelosPorFabricante[fab]) {
                modelosPorFabricante[fab].forEach(mod => {
                    const opt = document.createElement('option');
                    opt.value = mod;
                    opt.textContent = mod;
                    modSelect.appendChild(opt);
                });
            }
        }

        function calcularPrecoSugerido(custo) {
            const campoPreco = document.getElementById('preco_venda');
            if (custo && !isNaN(custo)) {
                campoPreco.value = (parseFloat(custo) * 3.5).toFixed(2);
            }
        }

        function imprimirEtiqueta(codigo, descricao, localizacao, veiculo) {
            var win = window.open('', '', 'height=400,width=400');
            win.document.write('<html><head><title>Etiqueta ' + codigo + '</title>');
            win.document.write('<style>');
            win.document.write('body { font-family: Arial, sans-serif; text-align: center; margin: 0; padding: 5px; }');
            win.document.write('h4 { margin: 2px 0; font-size: 14px; }');
            win.document.write('.qr-box { margin: 5px auto; display: flex; justify-content: center; }');
            win.document.write('p { font-size: 11px; margin: 2px 0; }');
            win.document.write('</style>');
            win.document.write('</head><body>');
            win.document.write('<h4>AUTON-LINE</h4>');
            win.document.write('<div id="qrcode" class="qr-box"></div>');
            win.document.write('<p><strong>Cód: ' + codigo + '</strong></p>');
            win.document.write('<p>' + descricao + '</p>');
            win.document.write('<p>Veículo: ' + veiculo + '</p>');
            win.document.write('<p><strong>Local: ' + (localizacao ? localizacao : 'Não definido') + '</strong></p>');
            win.document.write('<script src="https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js"><\/script>');
            win.document.write('<script>');
            win.document.write('new QRCode(document.getElementById("qrcode"), { text: "' + codigo + '", width: 90, height: 90 });');
            win.document.write('setTimeout(function(){ window.print(); window.close(); }, 600);');
            win.document.write('<\/script>');
            win.document.write('</body></html>');
            win.document.close();
        }
    </script>
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
                <label>Local / Prateleira no Pátio</label>
                <input type="text" name="localizacao" placeholder="Ex: Prateleira B3 / Setor 2">
            </div>
            <div>
                <label>Nº Baixa DETRAN</label>
                <input type="text" name="detran" placeholder="Ex: BX-1234">
            </div>
            <div>
                <label>Fabricante</label>
                <select name="fabricante" id="cad_fabricante" onchange="atualizarModelos('cad')" required>
                    <option value="">Selecione a Marca</option>
                    <option value="Audi">Audi</option>
                    <option value="BMW">BMW</option>
                    <option value="BYD">BYD</option>
                    <option value="Caoa Chery">Caoa Chery</option>
                    <option value="Chevrolet">Chevrolet</option>
                    <option value="Citroën">Citroën</option>
                    <option value="Fiat">Fiat</option>
                    <option value="Honda">Honda</option>
                    <option value="Hyundai">Hyundai</option>
                    <option value="Mitsubishi">Mitsubishi</option>
                    <option value="Nissan">Nissan</option>
                    <option value="Peugeot">Peugeot</option>
                    <option value="Ram">Ram</option>
                    <option value="Renault">Renault</option>
                    <option value="Suzuki">Suzuki</option>
                    <option value="Toyota">Toyota</option>
                    <option value="Volkswagen">Volkswagen</option>
                </select>
            </div>
            <div>
                <label>Modelo</label>
                <select name="modelo" id="cad_modelo" required>
                    <option value="">Selecione o Modelo</option>
                </select>
            </div>
            <div>
                <label>Ano</label>
                <input type="number" name="ano" placeholder="Ex: 2020" required>
            </div>
            <div>
                <label>Cor</label>
                <select name="cor" required>
                    <option value="">Selecione a Cor</option>
                    <option value="Azul">Azul</option>
                    <option value="Bege">Bege</option>
                    <option value="Branco">Branco</option>
                    <option value="Cinza">Cinza</option>
                    <option value="Marrom">Marrom</option>
                    <option value="Prata">Prata</option>
                    <option value="Preto">Preto</option>
                    <option value="Vermelho">Vermelho</option>
                </select>
            </div>
            <div>
                <label>Descrição da Peça</label>
                <input type="text" name="descricao" placeholder="Ex: Alternador 75A" required>
            </div>
            <div>
                <label>Custo Inicial (R$)</label>
                <input type="number" step="0.01" name="custo_inicial" placeholder="Ex: 100.00" oninput="calcularPrecoSugerido(this.value)" required>
            </div>
            <div>
                <label>Preço Venda (Editável)</label>
                <input type="number" step="0.01" id="preco_venda" name="preco_venda" placeholder="Ex: 350.00" required style="background:#1a1a1a; color:#f1c40f; font-weight:bold; border-color:#f1c40f;">
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
                    <th>Local</th>
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
                <select name="fabricante" id="venda_fabricante" onchange="atualizarModelos('venda')" required>
                    <option value="">Selecione a Marca</option>
                    <option value="Audi">Audi</option>
                    <option value="BMW">BMW</option>
                    <option value="BYD">BYD</option>
                    <option value="Caoa Chery">Caoa Chery</option>
                    <option value="Chevrolet">Chevrolet</option>
                    <option value="Citroën">Citroën</option>
                    <option value="Fiat">Fiat</option>
                    <option value="Honda">Honda</option>
                    <option value="Hyundai">Hyundai</option>
                    <option value="Mitsubishi">Mitsubishi</option>
                    <option value="Nissan">Nissan</option>
                    <option value="Peugeot">Peugeot</option>
                    <option value="Ram">Ram</option>
                    <option value="Renault">Renault</option>
                    <option value="Suzuki">Suzuki</option>
                    <option value="Toyota">Toyota</option>
                    <option value="Volkswagen">Volkswagen</option>
                </select>
            </div>
            <div>
                <label>Modelo</label>
                <select name="modelo" id="venda_modelo" required>
                    <option value="">Selecione o Modelo</option>
                </select>
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
                <input type="number" step="0.01" name="preco_venda" placeholder="Ex: 250.00" required style="background:#1a1a1a; color:#2ecc71; font-weight:bold;">
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
            local_tag = f'<span class="tag-local">{p.get("localizacao")}</span>' if p.get("localizacao") else '<span style="color:#555;">-</span>'
            
            codigo_js = str(p.get('codigo', '')).replace("'", "\\'")
            desc_js = str(p.get('descricao', '')).replace("'", "\\'")
            local_js = str(p.get('localizacao', '')).replace("'", "\\'")
            veiculo_js = f"{p.get('fabricante', '')} {p.get('modelo', '')} ({p.get('ano', '')})".replace("'", "\\'")

            linhas_estoque += f"""
                <tr>
                    <td>{foto_tag}</td>
                    <td><strong>{p.get('codigo', '')}</strong></td>
                    <td>{local_tag}</td>
                    <td>{p.get('descricao', '')}</td>
                    <td>{p.get('fabricante', '')} {p.get('modelo', '')} ({p.get('ano', '')})</td>
                    <td style="color:#2ecc71; font-weight:bold;">R$ {float(p.get('preco_venda', 0) or 0):.2f}</td>
                    <td>
                        <button type="button" class="btn-print" onclick="imprimirEtiqueta('{codigo_js}', '{desc_js}', '{local_js}', '{veiculo_js}')">Imprimir QR</button>
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
        linhas_estoque = '<tr><td colspan="7" style="text-align:center; color:#777;">Nenhum item em estoque.</td></tr>'

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
async def admin_cadastrar(request: Request):
    try:
        form_data = await request.form()
        codigo = form_data.get("codigo", "")
        localizacao = form_data.get("localizacao", "")
        detran = form_data.get("detran", "")
        fabricante = form_data.get("fabricante", "")
        modelo = form_data.get("modelo", "")
        
        ano_str = form_data.get("ano", "0")
        ano = int(ano_str) if ano_str and str(ano_str).isdigit() else 0
        
        cor = form_data.get("cor", "")
        descricao = form_data.get("descricao", "")
        
        custo_str = form_data.get("custo_inicial", "0")
        custo_inicial = float(custo_str) if custo_str else 0.0
        
        preco_str = form_data.get("preco_venda", "0")
        preco_venda = float(preco_str) if preco_str else 0.0

        foto_b64 = None
        uploaded_file = form_data.get("foto_file")
        if uploaded_file and hasattr(uploaded_file, "filename") and uploaded_file.filename:
            content = await uploaded_file.read()
            if content:
                encoded = base64.b64encode(content).decode("utf-8")
                foto_b64 = f"data:{uploaded_file.content_type};base64,{encoded}"

        payload = {
            "codigo": codigo,
            "localizacao": localizacao,
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
    except Exception as e:
        print(f"Erro: {e}")
        
    return RedirectResponse(url="/", status_code=303)

@app.post("/admin/cadastrar_venda")
async def admin_cadastrar_venda(request: Request):
    try:
        form_data = await request.form()
        codigo = form_data.get("codigo", "")
        fabricante = form_data.get("fabricante", "")
        modelo = form_data.get("modelo", "")
        
        ano_str = form_data.get("ano", "0")
        ano = int(ano_str) if ano_str and str(ano_str).isdigit() else 0
        
        descricao = form_data.get("descricao", "")
        
        preco_str = form_data.get("preco_venda", "0")
        preco_venda = float(preco_str) if preco_str else 0.0

        foto_b64 = None
        uploaded_file = form_data.get("foto_file")
        if uploaded_file and hasattr(uploaded_file, "filename") and uploaded_file.filename:
            content = await uploaded_file.read()
            if content:
                encoded = base64.b64encode(content).decode("utf-8")
                foto_b64 = f"data:{uploaded_file.content_type};base64,{encoded}"

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
    except Exception as e:
        print(f"Erro: {e}")
        
    return RedirectResponse(url="/", status_code=303)

@app.post("/admin/vender/{peca_id}")
async def admin_vender(peca_id: int):
    if supabase:
        try:
            supabase.table("pecas").update({"status": "vendido"}).eq("id", peca_id).execute()
        except Exception:
            pass
    return RedirectResponse(url="/", status_code=303)

@app.post("/admin/excluir/{peca_id}")
async def admin_excluir(peca_id: int):
    if supabase:
        try:
            supabase.table("pecas").delete().eq("id", peca_id).execute()
        except Exception:
            pass
    return RedirectResponse(url="/", status_code=303)

```
