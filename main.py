import os
from typing import List, Optional
from dotenv import load_dotenv

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from supabase import create_client, Client

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# --- CONFIGURAÇÃO E CONEXÃO COM O SUPABASE ---
SUPABASE_URL = os.getenv("SUPABASE_URL") 
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    # Este erro será levantado se o .env estiver faltando ou for inválido
    raise ValueError("As variáveis SUPABASE_URL ou SUPABASE_KEY não foram definidas no arquivo .env.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- INICIALIZAÇÃO DO FASTAPI ---
app = FastAPI(
    title="GêneseHub API",
    version="1.0.0"
)

# Configuração para Templates HTML (Procura na pasta 'templates')
templates = Jinja2Templates(directory="./templates")

# Configuração para Arquivos Estáticos (Procura na pasta raiz '.' para o style.css)
# O CSS é acessado através do prefixo /static/
app.mount("/static", StaticFiles(directory="."), name="static") 

# --- MODELOS PYDANTIC ---

class ProjetoView(BaseModel):
    """Modelo simplificado para card de projeto na galeria do perfil."""
    id: int
    titulo: str
    tipo_midia: Optional[str] = "Geral"
    # Campos mockados ou derivados
    curtidas: int = 120
    visualizacoes: int = 500
    nota_media: float = 4.8 
    
    class Config:
        from_attributes = True

class PerfilDados(BaseModel):
    """Modelo para BUSCAR os dados do perfil."""
    id: str
    email: Optional[str] = None
    nome_completo: Optional[str] = None
    biografia: Optional[str] = None
    foto_url: Optional[str] = None
    telefone: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None

    class Config:
        from_attributes = True

class PerfilUpdate(BaseModel):
    """Modelo para ATUALIZAR os dados na tabela Perfis."""
    nome_completo: Optional[str] = None
    biografia: Optional[str] = None
    telefone: Optional[str] = None


# --- ROTAS DE AUTENTICAÇÃO (MOCKUP) ---

async def get_current_user_id():
    """
    Função mockada. Obtém o ID do MOCK_USER_ID do .env. 
    SE ESTA FUNÇÃO FALHAR, VERIFIQUE SE O MOCK_USER_ID ESTÁ CORRETO NO .ENV
    """
    MOCK_USER_ID = os.getenv("MOCK_USER_ID")
    
    if not MOCK_USER_ID or MOCK_USER_ID == "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11":
        raise HTTPException(
            status_code=401, 
            detail="Não autenticado. Defina MOCK_USER_ID no .env para testar."
        )
    return MOCK_USER_ID

# --- ROTAS DE DADOS DA API ---

@app.get("/perfil/me/dados", response_model=PerfilDados, summary="Obter Meus Dados de Perfil")
def get_me(current_user_id: str = Depends(get_current_user_id)):
    """Busca os dados do perfil (Perfis + Links_Sociais) do usuário logado."""
    try:
        # 1. Busca dados da tabela Perfis
        perfil_result = supabase.table('Perfis').select('*').eq('id', current_user_id).single().execute()
        perfil_data = perfil_result.data
        
        # 2. Busca links sociais da tabela Links_Sociais
        links_result = supabase.table('Links_Sociais').select('plataforma, url').eq('id_perfil', current_user_id).execute()
        links_data = links_result.data
        
        linkedin_url = next((link['url'] for link in links_data if link['plataforma'] == 'LinkedIn'), None)
        github_url = next((link['url'] for link in links_data if link['plataforma'] == 'GitHub'), None)
        
        return PerfilDados(
            id=perfil_data.get('id', current_user_id),
            email="mock.user@creathub.com", # Email mockado para o front-end
            nome_completo=perfil_data.get('nome_completo'),
            biografia=perfil_data.get('biografia'),
            foto_url=perfil_data.get('foto_url'),
            telefone=perfil_data.get('telefone'),
            linkedin_url=linkedin_url,
            github_url=github_url
        )
        
    except Exception as e:
        if "JSONDecodeError" in str(e) or "404" in str(e):
             # Retorna um perfil vazio se o usuário não existir no banco
             return PerfilDados(id=current_user_id) 
        raise HTTPException(status_code=500, detail=f"Erro ao buscar perfil: {e}")

@app.get("/perfil/me/projetos", response_model=List[ProjetoView], summary="Obter Projetos do Usuário Logado")
def get_my_projects(current_user_id: str = Depends(get_current_user_id)):
    """Busca todos os projetos criados pelo usuário logado."""
    try:
        result = supabase.table('Projetos').select('id, titulo, tipo_midia').eq('id_autor', current_user_id).execute()
        
        # Se você tiver uma view de estatísticas, usaria aqui
        
        return result.data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar projetos: {e}")

# --- ROTAS PARA RENDERIZAR HTML (Páginas) ---

# Rota Raiz
@app.get("/", response_class=HTMLResponse, summary="Página Inicial")
def show_home_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Rota para Cursos
@app.get("/courses", response_class=HTMLResponse, summary="Página de Cursos")
def show_courses_page(request: Request):
    return templates.TemplateResponse("courses.html", {"request": request})

# Rota para Portfólio (Galeria de Projetos)
@app.get("/portifolio", response_class=HTMLResponse, summary="Página de Portfólio")
def show_portifolio_page(request: Request):
    return templates.TemplateResponse("portifolio.html", {"request": request})

# Rota para Adicionar Projeto
@app.get("/add-project", response_class=HTMLResponse, summary="Página de Adicionar Projeto")
def show_add_project_page(request: Request):
    return templates.TemplateResponse("add-project.html", {"request": request})


# Rota para VISUALIZAÇÃO DE PERFIL (com abas)
@app.get("/profile", response_class=HTMLResponse, summary="Exibe a página de Visualização de Perfil")
def show_profile_page(request: Request, current_user_id: str = Depends(get_current_user_id)):
    """Busca dados e projetos e renderiza a página de perfil completa."""
    try:
        # 1. Carrega dados do Perfil
        perfil_data_response = get_me(current_user_id)
        perfil_data_dict = perfil_data_response.model_dump()

        # 2. Carrega Projetos do Usuário
        projetos_data_response = get_my_projects(current_user_id)
        
        # 3. Renderiza o template 'profile.html' (Visualização)
        return templates.TemplateResponse(
            "profile.html",
            {
                "request": request, 
                "perfil_data": perfil_data_dict,
                "projetos": projetos_data_response 
            }
        )
    except HTTPException as e:
        if e.status_code == 401:
            # Redireciona para o login se não estiver autenticado
            return RedirectResponse(url="/login", status_code=302) 
        raise e

# Rota para EDIÇÃO DE PERFIL (Formulário)
@app.get("/profile/edit", response_class=HTMLResponse, summary="Exibe o Formulário de Edição")
def show_profile_edit_page(request: Request, current_user_id: str = Depends(get_current_user_id)):
    """Busca dados e renderiza o formulário de edição (profile_edit.html)."""
    perfil_data_response = get_me(current_user_id)
    perfil_data_dict = perfil_data_response.model_dump()
    
    return templates.TemplateResponse(
        "profile_edit.html", # <--- Template do Formulário de Edição
        {"request": request, "perfil_data": perfil_data_dict}
    )

# Rota POST para ATUALIZAR o Perfil
@app.post("/perfil/me/update", summary="Atualizar Meu Perfil via Formulário HTML")
def update_profile_from_form(
    current_user_id: str = Depends(get_current_user_id),
    nome_completo: str = Form(None),
    biografia: str = Form(None),
    linkedin_url: Optional[str] = Form(None),
    github_url: Optional[str] = Form(None),
):
    try:
        # Atualiza a tabela Perfis
        perfil_update = PerfilUpdate(
            nome_completo=nome_completo,
            biografia=biografia
        ).model_dump(exclude_none=True)

        supabase.table('Perfis').update(perfil_update).eq('id', current_user_id).execute()

        # Atualiza a tabela Links_Sociais (usando upsert)
        links_data = []
        if linkedin_url:
            links_data.append({"id_perfil": current_user_id, "plataforma": "LinkedIn", "url": linkedin_url})
        if github_url:
            links_data.append({"id_perfil": current_user_id, "plataforma": "GitHub", "url": github_url})

        if links_data:
            # O 'on_conflict' garante que a linha é atualizada se já existir (upsert)
            supabase.table('Links_Sociais').upsert(links_data, on_conflict=['id_perfil', 'plataforma']).execute()
            
        # Redireciona para a página de visualização
        return RedirectResponse(url="/profile", status_code=303) 
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro interno ao salvar as alterações do perfil.")

# --- BLOCO DE EXECUÇÃO PRINCIPAL ---

if __name__ == "__main__":
    # Comando de execução quando rodamos python main.py
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)