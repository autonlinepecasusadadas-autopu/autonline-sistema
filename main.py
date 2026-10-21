import os
import shutil
from typing import Optional, List
from fastapi import FastAPI, HTTPException, status, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from supabase import create_client, Client

# CONFIGURAÇÃO DO SUPABASE (BANCO DE DADOS NA NUVEM)
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://ijirrzrallxuqqagwviq.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "sb_publishable_oq13Ilt9dcMFxXSu862Rw_9Q4wa12-")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI(
    title="AUTONLINE - Sistema de Gestão de CDV",
    version="5.0.0"
)

# Diretório para upload local de fotos
UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def home():
    # Busca peças cadastradas no Supabase
    try:
        res = supabase.table("pecas").select("*").order("created_at", desc=True).execute()
        pecas = res.data if res.data else []
    except Exception:
        pecas = []

    # Cálculo dos totais
    total_pecas = len(pecas)
    valor_estoque = sum(float(p.get("valor", 0) or 0) for p in pecas)
    
    # Montagem da tabela de peças
    linhas_tabela = ""
    for p in pecas:
        foto_html = f'<img src="{p.get("foto_url")}" style="height: 50px; border-radius: 4px;">' if p.get("foto_url") else '<span style="color:#aaa;">Sem foto</span>'
        linhas_tabela += f"""
        <tr>
            <td><strong>{p.get("codigo", "-")}</strong></td>
            <td>{p.get("nome", "-")}</td>
            <td>{p.get("modelo", "-")} ({p.get("ano", "-")})</td>
            <td>R$ {float(p.get("valor", 0)):,.2f}</td>
            <td>{foto_html}</td>
            <td><span style="background-color: #e2e3e5; padding: 4px 8px; border-radius: 4px; font-size: 12px;">Em Pátio</span></td>
        </tr>
        """

    if not linhas_tabela:
        linhas_tabela = '<tr><td colspan="6" style="text-align: center; color: #777;">Nenhuma peça cadastrada no estoque.</td></tr>'

    html_content = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AUTONLINE - Gestão de Peças</title>
        <!-- Biblioteca para leitura de QR Code via câmara -->
        <script src="https://unpkg.com/html5-qrcode"></script>
        <style>
            * {{ box-sizing: border-box; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }}
            body {{ background-color: #f4f6f9; margin: 0; padding: 20px; }}
            .container {{ max-width: 1200px; margin: auto; }}
            
            /* Indicadores Superiores */
            .cards-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 15px; margin-bottom: 25px; }}
            .card {{ background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); text-align: center; }}
            .card-title {{ font-size: 13px; color: #6c757d; font-weight: bold; text-transform: uppercase; }}
            .card-value {{ font-size: 24px; font-weight: bold; margin-top: 5px; color: #333; }}
            
            .card-blue {{ border-top: 4px solid #007bff; }}
            .card-yellow {{ border-top: 4px solid #ffc107; }}
            .card-info {{ border-top: 4px solid #17a2b8; }}
            .card-green {{ border-top: 4px solid #28a745; }}

            /* Abas de Navegação */
            .tabs {{ display: flex; gap: 10px; margin-bottom: 20px; }}
            .tab-btn {{ background: #e9ecef; border: none; padding: 10px 20px; border-radius: 6px; font-weight: bold; cursor: pointer; color: #495057; }}
            .tab-btn.active {{ background: #fff; color: #007bff; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }}

            /* Painel do Formulário */
            .panel {{ background: #fff; padding: 25px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 25px; }}
            .panel-title {{ font-size: 18px; font-weight: bold; margin-bottom: 20px; color: #333; }}
            
            .form-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 15px; }}
            .form-group {{ display: flex; flex-direction: column; }}
            .form-group label {{ font-size: 13px; font-weight: bold; margin-bottom: 5px; color: #495057; }}
            .form-group input, .form-group select {{ padding: 10px; border: 1px solid #ced4da; border-radius: 4px; font-size: 14px; width: 100%; }}
            
            .btn-qr {{ background-color: #17a2b8; color: white; border: none; padding: 8px; margin-top: 5px; border-radius: 4px; cursor: pointer; font-size: 12px; font-weight: bold; }}
            .btn-submit {{ background-color: #007bff; color: white; border: none; padding: 12px 25px; font-size: 15px; font-weight: bold; border-radius: 4px; cursor: pointer; float: right; margin-top: 15px; }}
            
            #reader {{ width: 100%; max-width: 320px; margin: 10px 0; display: none; }}

            /* Tabela de Estoque */
            table {{ width: 100%; border-collapse: collapse; background: #fff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }}
            th, td {{ padding: 12px 15px; text-align: left; border-bottom: 1px solid #dee2e6; font-size: 14px; }}
            th {{ background-color: #f8f9fa; color: #495057; font-weight: bold; }}
        </style>
    </head>
    <body>

        <div class="container">
            <!-- Indicadores -->
            <div class="cards-grid">
                <div class="card card-blue">
                    <div class="card-title">Total de Peças</div>
                    <div class="card-value">{total_pecas}</div>
                </div>
                <div class="card card-yellow">
                    <div class="card-title">Valor em Estoque</div>
                    <div class="card-value">R$ {valor_estoque:,.2f}</div>
                </div>
                <div class="card card-info">
                    <div class="card-title">Entradas do Mês</div>
                    <div class="card-value">{total_pecas}</div>
                </div>
                <div class="card card-green">
                    <div class="card-title">Vendas Realizadas</div>
                    <div class="card-value">R$ 0.00</div>
                </div>
            </div>

            <!-- Navegação -->
            <div class="tabs">
                <button class="tab-btn active">📦 Estoque em Pátio</button>
                <button class="tab-btn">💰 VENDAS (AUTONLINE)</button>
            </div>

            <!-- Formulário -->
            <div class="panel">
                <div class="panel-title">Cadastrar Peça no Pátio</div>
                <form action="/cadastrar" method="post" enctype="multipart/form-data">
                    <div class="form-grid">
                        
                        <div class="form-group">
                            <label for="codigo">QR Code / Tag</label>
                            <input type="text" id="codigo" name="codigo" placeholder="Ex: QR-001" required>
                            <button type="button" class="btn-qr" onclick="iniciarLeitor()">📷 Escanear QR Code</button>
                        </div>

                        <div class="form-group">
                            <label for="baixa_detran">Nº Baixa DETRAN</label>
                            <input type="text" id="baixa_detran" name="baixa_detran" placeholder="Ex: BX-1234">
                        </div>

                        <div class="form-group">
                            <label for="fabricante">Fabricante</label>
                            <select id="fabricante" name="fabricante">
                                <option value="FIAT">FIAT</option>
                                <option value="VW">VOLKSWAGEN</option>
                                <option value="GM">CHEVROLET</option>
                                <option value="FORD">FORD</option>
                            </select>
                        </div>

                        <div class="form-group">
                            <label for="modelo">Carro / Modelo Brasileiro</label>
                            <input type="text" id="modelo" name="modelo" placeholder="Ex: Uno" required>
                        </div>

                        <div class="form-group">
                            <label for="ano">Ano</label>
                            <input type="number" id="ano" name="ano" value="2020">
                        </div>

                        <div class="form-group">
                            <label for="cor">Cor do Veículo</label>
                            <select id="cor" name="cor">
                                <option value="Branco">Branco</option>
                                <option value="Preto">Preto</option>
                                <option value="Prata">Prata</option>
                                <option value="Cinza">Cinza</option>
                                <option value="Vermelho">Vermelho</option>
                            </select>
                        </div>

                        <div class="form-group">
                            <label for="valor">Custo Inicial (R$)</label>
                            <input type="number" step="0.01" id="valor" name="valor" placeholder="Ex: 1999.00" required>
                        </div>

                        <div class="form-group" style="grid-column: span 2;">
                            <label for="nome">Descrição da Peça</label>
                            <input type="text" id="nome" name="nome" placeholder="Ex: Alternador 75A" required>
                        </div>

                        <div class="form-group" style="grid-column: span 2;">
                            <label for="foto">Anexar Fotos do Computador/Telemóvel</label>
                            <input type="file" id="foto" name="foto" accept="image/*">
                        </div>

                    </div>

                    <!-- Visualizador da Câmara -->
                    <div id="reader"></div>

                    <button type="submit" class="btn-submit">+ Cadastrar Peça</button>
                    <div style="clear: both;"></div>
                </form>
            </div>

            <!-- Tabela -->
            <div class="panel">
                <div class="panel-title">Peças no Estoque</div>
                <table>
                    <thead>
                        <tr>
                            <th>Código / QR</th>
                            <th>Descrição</th>
                            <th>Modelo / Ano</th>
                            <th>Valor (R$)</th>
                            <th>Foto</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {linhas_tabela}
                    </tbody>
                </table>
            </div>
        </div>

        <script>
            let html5QrCode = null;

            function iniciarLeitor() {{
                const readerDiv = document.getElementById('reader');
                readerDiv.style.display = 'block';

                if (!html5QrCode) {{
                    html5QrCode = new Html5Qrcode("reader");
                }}

                html5QrCode.start(
                    {{ facingMode: "environment" }},
                    {{ fps: 10, qrbox: 250 }},
                    (decodedText) => {{
                        document.getElementById('codigo').value = decodedText;
                        html5QrCode.stop();
                        readerDiv.style.display = 'none';
                    }},
                    (errorMessage) => {{}}
                ).catch((err) => {{
                    alert("Erro ao aceder à câmara: " + err);
                }});
            }}
        </script>

    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/cadastrar")
async def cadastrar(
    codigo: str = Form(...),
    nome: str = Form(...),
    valor: float = Form(...),
    modelo: Optional[str] = Form(None),
    ano: Optional[int] = Form(None),
    foto: Optional[UploadFile] = File(None)
):
    foto_url = None
    
    # Processamento do arquivo de imagem enviado
    if foto and foto.filename:
        caminho_arquivo = os.path.join(UPLOAD_DIR, foto.filename)
        with open(caminho_arquivo, "wb") as buffer:
            shutil.copyfileobj(foto.file, buffer)
        foto_url = f"/{caminho_arquivo}"

    try:
        dados = {
            "codigo": codigo,
            "nome": nome,
            "valor": valor,
            "modelo": modelo,
            "ano": ano,
            "foto_url": foto_url
        }
        supabase.table("pecas").insert(dados).execute()
        return HTMLResponse(content="<h3>Peça cadastrada com sucesso!</h3><script>setTimeout(() => { window.location.href='/'; }, 1000);</script>")
    except Exception as e:
        return HTMLResponse(content=f"<h3>Erro ao cadastrar: {str(e)}</h3><a href='/'>Voltar</a>")