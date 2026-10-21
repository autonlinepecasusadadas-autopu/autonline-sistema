from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from supabase import create_client, Client
import os

app = FastAPI()

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://ijirrzrallxuqqagwviq.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "sb_publishable_oq13Ilt9dcMFxXSu862Rw_9Q4wa12-")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Autonline - Gestão de Peças</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f9; color: #333; }
        .container { max-width: 600px; margin: auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
        h1, h2 { text-align: center; color: #0056b3; }
        form { display: flex; flex-direction: column; gap: 12px; margin-bottom: 20px; }
        input, button { padding: 10px; font-size: 16px; border: 1px solid #ccc; border-radius: 4px; }
        button { background-color: #0056b3; color: white; border: none; cursor: pointer; font-weight: bold; }
        button:hover { background-color: #004494; }
        .btn-danger { background-color: #dc3545; }
        .btn-danger:hover { background-color: #c82333; }
        ul { list-style: none; padding: 0; }
        li { background: #fff; margin-bottom: 8px; padding: 12px; border-radius: 4px; border: 1px solid #ddd; display: flex; justify-content: space-between; align-items: center; }
    </style>
</head>
<body>

<div class="container">
    <h1>Autonline - Sistema</h1>

    <h2>Cadastrar Peça</h2>
    <form action="/adicionar" method="post">
        <input type="text" name="codigo" placeholder="Código / QR Code da Peça" required>
        <input type="text" name="nome" placeholder="Nome da Peça" required>
        <input type="text" name="veiculo" placeholder="Veículo Compatível">
        <input type="number" step="0.01" name="preco" placeholder="Preço" required>
        <input type="number" name="quantidade" placeholder="Quantidade em Stock" required>
        <button type="submit">Salvar Peça</button>
    </form>

    <h2>Inventário em Stock</h2>
    <ul>
        {% for peca in pecas %}
        <li>
            <span><strong>{{ peca.nome }}</strong> (Qtd: {{ peca.quantidade }}) - R$ {{ peca.preco }}</span>
            <form action="/apagar/{{ peca.id }}" method="post" style="display:inline;" onsubmit="return confirm('Deseja realmente apagar esta peça?');">
                <button type="submit" class="btn-danger" style="padding: 5px 10px; font-size: 12px;">Apagar</button>
            </form>
        </li>
        {% endfor %}
    </ul>
</div>

</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    response = supabase.table("pecas").select("*").execute()
    pecas = response.data if response.data else []
    
    from jinja2 import Template
    template = Template(HTML_TEMPLATE)
    html_renderizado = template.render(pecas=pecas)
    return HTMLResponse(content=html_renderizado)

@app.post("/adicionar")
async def adicionar_peca(
    codigo: str = Form(...),
    nome: str = Form(...),
    veiculo: str = Form(None),
    preco: float = Form(...),
    quantidade: int = Form(...)
):
    supabase.table("pecas").insert({
        "codigo": codigo,
        "nome": nome,
        "veiculo": veiculo,
        "preco": preco,
        "quantidade": quantidade
    }).execute()
    return RedirectResponse(url="/", status_code=303)

@app.post("/apagar/{peca_id}")
async def apagar_peca(peca_id: int):
    supabase.table("pecas").delete().eq("id", peca_id).execute()
    return RedirectResponse(url="/", status_code=303)
