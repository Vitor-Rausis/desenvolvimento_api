"""
Modelos de dados para a API Segura
Inclui modelos SQLAlchemy para banco de dados e Pydantic para validação da API
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pydantic import BaseModel, EmailStr, ConfigDict, Field, validator
from typing import Optional, List
from datetime import datetime
import re

# Base declarativa para SQLAlchemy
Base = declarative_base()

class User(Base):
    """
    Modelo de usuário no banco de dados
    Armazena informações de autenticação e perfil do usuário
    """
    __tablename__ = "users"
    
    # Campos principais
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # Status e tipo
    is_active = Column(Boolean, default=True, nullable=False)
    user_type = Column(String(20), default="user", nullable=False)  # user, admin, moderator
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    data_items = relationship("DataItem", back_populates="user", cascade="all, delete-orphan")
    
    # Índices para performance
    __table_args__ = (
        Index('idx_user_username', 'username'),
        Index('idx_user_email', 'email'),
        Index('idx_user_type', 'user_type'),
        Index('idx_user_active', 'is_active'),
    )
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', type='{self.user_type}')>"

class DataItem(Base):
    """
    Modelo de item de dados no banco de dados
    Representa dados criados pelos usuários
    """
    __tablename__ = "data_items"
    
    # Campos principais
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    
    # Relacionamento com usuário
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    user = relationship("User", back_populates="data_items")
    
    # Índices para performance
    __table_args__ = (
        Index('idx_data_user_id', 'user_id'),
        Index('idx_data_created_at', 'created_at'),
        Index('idx_data_title', 'title'),
    )
    
    def __repr__(self):
        return f"<DataItem(id={self.id}, title='{self.title}', user_id={self.user_id})>"


class UserBase(BaseModel):
    """
    Modelo base para usuários
    Contém campos comuns para criação e resposta
    """
    username: str = Field(..., min_length=3, max_length=50, description="Nome de usuário único")
    email: EmailStr = Field(..., description="Email válido do usuário")
    user_type: str = Field(default="user", description="Tipo de usuário: user, admin, moderator")
    
    @validator('username')
    def validate_username(cls, v):
        """Valida formato do username"""
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username deve conter apenas letras, números e underscore')
        return v.lower()
    
    @validator('user_type')
    def validate_user_type(cls, v):
        """Valida tipo de usuário"""
        allowed_types = ['user', 'admin', 'moderator']
        if v not in allowed_types:
            raise ValueError(f'Tipo de usuário deve ser um dos: {allowed_types}')
        return v

class UserCreate(UserBase):
    """
    Modelo para criação de usuário
    Inclui senha que será hasheada
    """
    password: str = Field(..., min_length=8, max_length=128, description="Senha do usuário")
    
    @validator('password')
    def validate_password(cls, v):
        """Valida força da senha"""
        if len(v) < 8:
            raise ValueError('Senha deve ter pelo menos 8 caracteres')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Senha deve conter pelo menos uma letra maiúscula')
        if not re.search(r'[a-z]', v):
            raise ValueError('Senha deve conter pelo menos uma letra minúscula')
        if not re.search(r'\d', v):
            raise ValueError('Senha deve conter pelo menos um número')
        return v

class UserUpdate(BaseModel):
    """
    Modelo para atualização de usuário
    Todos os campos são opcionais
    """
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    user_type: Optional[str] = None
    is_active: Optional[bool] = None
    
    @validator('username')
    def validate_username(cls, v):
        if v is not None:
            if not re.match(r'^[a-zA-Z0-9_]+$', v):
                raise ValueError('Username deve conter apenas letras, números e underscore')
            return v.lower()
        return v
    
    @validator('user_type')
    def validate_user_type(cls, v):
        if v is not None:
            allowed_types = ['user', 'admin', 'moderator']
            if v not in allowed_types:
                raise ValueError(f'Tipo de usuário deve ser um dos: {allowed_types}')
        return v

class UserResponse(UserBase):
    """
    Modelo para resposta de usuário
    Não inclui senha e adiciona campos do banco
    """
    id: int = Field(..., description="ID único do usuário")
    is_active: bool = Field(..., description="Status ativo do usuário")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: Optional[datetime] = Field(None, description="Data da última atualização")
    
    model_config = ConfigDict(from_attributes=True)

class UserLogin(BaseModel):
    """
    Modelo para login de usuário
    """
    username: str = Field(..., description="Nome de usuário")
    password: str = Field(..., description="Senha do usuário")

class Token(BaseModel):
    """
    Modelo para resposta de token JWT
    """
    access_token: str = Field(..., description="Token JWT de acesso")
    token_type: str = Field(default="bearer", description="Tipo do token")
    expires_in: int = Field(..., description="Tempo de expiração em segundos")
    user_info: Optional[UserResponse] = Field(None, description="Informações do usuário")

class TokenData(BaseModel):
    """
    Modelo para dados do token JWT decodificado
    """
    username: Optional[str] = None
    user_id: Optional[int] = None
    user_type: Optional[str] = None
    exp: Optional[int] = None

class DataItemBase(BaseModel):
    """
    Modelo base para itens de dados
    """
    title: str = Field(..., min_length=1, max_length=200, description="Título do item")
    content: str = Field(..., min_length=1, description="Conteúdo do item")
    
    @validator('title')
    def validate_title(cls, v):
        """Valida título não vazio"""
        if not v.strip():
            raise ValueError('Título não pode estar vazio')
        return v.strip()
    
    @validator('content')
    def validate_content(cls, v):
        """Valida conteúdo não vazio"""
        if not v.strip():
            raise ValueError('Conteúdo não pode estar vazio')
        return v.strip()

class DataItemCreate(DataItemBase):
    """
    Modelo para criação de item de dados
    """
    pass

class DataItemUpdate(BaseModel):
    """
    Modelo para atualização de item de dados
    Todos os campos são opcionais
    """
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    
    @validator('title')
    def validate_title(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError('Título não pode estar vazio')
            return v.strip()
        return v
    
    @validator('content')
    def validate_content(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError('Conteúdo não pode estar vazio')
            return v.strip()
        return v

class DataItemResponse(DataItemBase):
    """
    Modelo para resposta de item de dados
    Inclui campos do banco de dados
    """
    id: int = Field(..., description="ID único do item")
    user_id: int = Field(..., description="ID do usuário proprietário")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: Optional[datetime] = Field(None, description="Data da última atualização")
    
    model_config = ConfigDict(from_attributes=True)


class PaginationParams(BaseModel):
    """
    Parâmetros para paginação
    """
    skip: int = Field(default=0, ge=0, description="Número de itens para pular")
    limit: int = Field(default=100, ge=1, le=1000, description="Número máximo de itens")

class DataItemFilters(BaseModel):
    """
    Filtros para busca de itens de dados
    """
    title_contains: Optional[str] = Field(None, description="Título contém")
    user_id: Optional[int] = Field(None, description="ID do usuário")
    created_after: Optional[datetime] = Field(None, description="Criado após")
    created_before: Optional[datetime] = Field(None, description="Criado antes")

class PaginatedResponse(BaseModel):
    """
    Resposta paginada genérica
    """
    items: List[DataItemResponse] = Field(..., description="Lista de itens")
    total: int = Field(..., description="Total de itens")
    skip: int = Field(..., description="Itens pulados")
    limit: int = Field(..., description="Limite de itens")
    has_next: bool = Field(..., description="Tem próxima página")
    has_prev: bool = Field(..., description="Tem página anterior")

class ErrorResponse(BaseModel):
    """
    Modelo para respostas de erro
    """
    error: str = Field(..., description="Tipo do erro")
    message: str = Field(..., description="Mensagem de erro")
    details: Optional[dict] = Field(None, description="Detalhes adicionais")

class ValidationErrorResponse(BaseModel):
    """
    Modelo para erros de validação
    """
    error: str = Field(default="validation_error", description="Tipo do erro")
    message: str = Field(default="Erro de validação", description="Mensagem de erro")
    field_errors: List[dict] = Field(..., description="Erros por campo")


class UserStats(BaseModel):
    """
    Estatísticas do usuário
    """
    total_items: int = Field(..., description="Total de itens criados")
    last_activity: Optional[datetime] = Field(None, description="Última atividade")
    items_this_month: int = Field(..., description="Itens criados este mês")

class SystemStats(BaseModel):
    """
    Estatísticas do sistema (apenas para admins)
    """
    total_users: int = Field(..., description="Total de usuários")
    total_items: int = Field(..., description="Total de itens")
    active_users_today: int = Field(..., description="Usuários ativos hoje")
    items_created_today: int = Field(..., description="Itens criados hoje")