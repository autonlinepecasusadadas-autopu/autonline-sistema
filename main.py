from fastapi import FastAPI, Request, Form
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
    <title>Autonline - Gestão de Peças</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f6f9; color: #333; }
        .container { max-width: 800px; margin: auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1, h2 { text-align: center; color: #1a252f; }
        form { display: flex; flex-direction: column; gap: 10px; margin-bottom: 20px; }
        input, button { padding: 10px; font-size: 14px; border: 1px solid #ccc; border-radius: 4px; }
        button { background-color: #27ae60; color: white; border: none; font-weight: bold; cursor: pointer; }
        button:hover { background-color: #219150; }
        .btn-danger { background-color: #e74c3c; width: auto; padding: 5px 10px; font-size: 12px; }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; font-size: 14px; }
        th { background: #f8f9fa; }
    </style>
</head>
<body>
<div class="container">
    <h1>AUTONLINE - Gestão de Peças</h1>
    
    <h2>Cadastrar Peça</h2>
    <form action="/cadastrar" method="post">
        <input type="text" name="codigo" placeholder="Código / QR Code" required>
        <input type="text" name="descricao" placeholder="Descrição da Peça (Ex: Alternador)" required>
        <input type="text" name="modelo" placeholder="Modelo do Veículo (Ex: Uno)" required>
        <input type="number" step="0.01" name="custo_inicial" placeholder="Custo Inicial (R$)" required>
        <button type="submit">Salvar Peça (Cálculo Automático +250% Lucro)</button>
    </form>

    <h2>Estoque Atual</h2>
    <table>
        <thead>
            <tr>
                <th>Código</th>
                <th>Descrição</th>
                <th>Modelo</th>
                <th>Preço de Venda</th>
                <th>Ações</th>
            </tr>
        </thead>
        <tbody>
            {% for p in pecas %}
            <tr>
                <td>{{ p.codigo }}</td>
                <td>{{ p.descricao }}</td>
                <td>{{ p.modelo }}</td>
                <td>R$ {{ "%.2f"|format(p.preco_venda or 0) }}</td>
                <td>
                    <form action="/excluir/{{ p.id }}" method="post" style="display:inline;" onsubmit="return confirm('Deseja apagar esta peça?');">
                        <button type="submit" class="btn-danger">Excluir</button>
                    </form>
                </td>
            </tr>
            {% else %}
            <tr><td colspan="5" style="text-align:center;">Nenhuma peça cadastrada.</td></tr>
            {% endfor %}
        </tbody>
    </table>
</div>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    pecas = []
    try:
        response = supabase.table("pecas").select("*").execute()
        if response and response.data:
            pecas = response.data
    except Exception as e:
        print("Erro ao buscar no Supabase:", e)

    from jinja2 import Template
    template = Template(HTML_TEMPLATE)
    rendered = template.render(pecas=pecas)
    return HTMLResponse(content=rendered)

@app.post("/cadastrar")
async def cadastrar(
    codigo: str = Form(...),
    descricao: str = Form(...),
    modelo: str = Form(...),
    custo_inicial: float = Form(...)
):
    try:
        preco_venda = custo_inicial * 3.5  # Custo + 250% de lucro
        supabase.table("pecas").insert({
            "codigo": codigo,
            "descricao": descricao,
            "modelo": modelo,
            "custo_inicial": custo_inicial,
            "preco_venda": preco_venda,
            "status": "disponivel"
        }).execute()
    except Exception as e:
        print("Erro ao inserir:", e)
    
    return RedirectResponse(url="/", status_code=303)

@app.post("/excluir/{peca_id}")
async def excluir(peca_id: int):
    try:
        supabase.table("pecas").delete().eq("id", peca_id).execute()
    except Exception as e:
        print("Erro ao excluir:", e)
    
    return RedirectResponse(url="/", status_code=303)
