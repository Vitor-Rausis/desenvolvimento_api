from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uvicorn

from config import settings
from database import get_db, create_tables
from models import (
    UserCreate, UserResponse, UserLogin, Token, 
    DataItemCreate, DataItemUpdate, DataItemResponse
)
from auth import (
    authenticate_user, create_access_token, 
    get_current_active_user, require_admin
)
from crud import (
    create_user, get_user_by_username, get_data_item,
    create_data_item, get_data_items_by_user, get_all_data_items,
    update_data_item, delete_data_item, can_access_data_item
)
from middleware import RateLimitMiddleware, LoggingMiddleware, SecurityMiddleware

# Configuração da aplicação
app = FastAPI(
    title="API Segura com Autenticação",
    description="API com camada de segurança, autenticação JWT e CRUD completo",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Adiciona middlewares
app.add_middleware(SecurityMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimitMiddleware, requests_per_minute=60)

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Evento de inicialização
@app.on_event("startup")
async def startup_event():
    """Cria as tabelas do banco de dados na inicialização"""
    create_tables()

# Rotas básicas
@app.get("/")
async def root():
    """Rota raiz da API"""
    return {
        "message": "API Segura funcionando!",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "auth": "/login",
            "data": "/data",
            "users": "/users"
        }
    }

@app.get("/health")
async def health_check():
    """Verificação de saúde da API"""
    return {
        "status": "healthy",
        "message": "API pronta para uso",
        "security": "JWT Authentication ativo"
    }

# Rotas de autenticação
@app.post("/login", response_model=Token, tags=["Autenticação"])
async def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Endpoint de login que autentica o usuário e retorna um token JWT
    """
    user = authenticate_user(db, user_credentials.username, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário inativo"
        )
    
    # Cria o token de acesso
    access_token = create_access_token(
        data={
            "sub": user.username,
            "user_id": user.id,
            "user_type": user.user_type
        }
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@app.post("/register", response_model=UserResponse, tags=["Autenticação"])
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    Endpoint para registro de novos usuários
    """
    # Verifica se o usuário já existe
    db_user = get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username já registrado"
        )
    
    try:
        return create_user(db=db, user=user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# Rotas de dados (protegidas)
@app.post("/data", response_model=DataItemResponse, tags=["Dados"])
async def create_data(
    data_item: DataItemCreate,
    current_user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Cria um novo item de dados (requer autenticação)
    """
    return create_data_item(db=db, data_item=data_item, user_id=current_user.id)

@app.get("/data", response_model=list[DataItemResponse], tags=["Dados"])
async def get_data(
    skip: int = 0,
    limit: int = 100,
    current_user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Lista os dados do usuário autenticado
    """
    if current_user.user_type == "admin":
        # Admins podem ver todos os dados
        return get_all_data_items(db, skip=skip, limit=limit)
    else:
        # Usuários normais veem apenas seus próprios dados
        return get_data_items_by_user(db, user_id=current_user.id, skip=skip, limit=limit)

@app.get("/data/{item_id}", response_model=DataItemResponse, tags=["Dados"])
async def get_data_item_by_id(
    item_id: int,
    current_user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtém um item de dados específico por ID (requer autenticação)
    """
    # Verifica permissão de acesso
    if not can_access_data_item(db, item_id, current_user.id, current_user.user_type):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado a este item de dados"
        )
    
    data_item = get_data_item(db, item_id=item_id)
    if data_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item de dados não encontrado"
        )
    
    return data_item

@app.put("/data/{item_id}", response_model=DataItemResponse, tags=["Dados"])
async def update_data_item_by_id(
    item_id: int,
    data_item_update: DataItemUpdate,
    current_user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Atualiza um item de dados específico (requer autenticação)
    """
    # Verifica permissão de acesso
    if not can_access_data_item(db, item_id, current_user.id, current_user.user_type):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado a este item de dados"
        )
    
    updated_item = update_data_item(db, item_id=item_id, data_item_update=data_item_update)
    if updated_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item de dados não encontrado"
        )
    
    return updated_item

@app.delete("/data/{item_id}", tags=["Dados"])
async def delete_data_item_by_id(
    item_id: int,
    current_user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Deleta um item de dados específico (requer autenticação)
    """
    # Verifica permissão de acesso
    if not can_access_data_item(db, item_id, current_user.id, current_user.user_type):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado a este item de dados"
        )
    
    success = delete_data_item(db, item_id=item_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item de dados não encontrado"
        )
    
    return {"message": "Item de dados deletado com sucesso"}

# Rotas de usuários (apenas para admins)
@app.get("/users", response_model=list[UserResponse], tags=["Usuários"])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    current_user: UserResponse = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Lista todos os usuários (apenas para administradores)
    """
    from crud import get_users as get_all_users
    return get_all_users(db, skip=skip, limit=limit)

@app.get("/me", response_model=UserResponse, tags=["Usuários"])
async def get_current_user_info(
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Obtém informações do usuário autenticado
    """
    return current_user

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
        log_level=settings.LOG_LEVEL.lower()
    )