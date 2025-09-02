"""
Configuração do banco de dados para a API Segura
Inclui engine, sessões, migrações e utilitários de banco
"""

import logging
from contextlib import contextmanager
from typing import Generator, Optional
from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from config import settings

# Configuração de logging
logger = logging.getLogger(__name__)



def create_database_engine() -> Engine:
    """
    Cria o engine do banco de dados com configurações otimizadas
    """
    # Configurações específicas por tipo de banco
    if "sqlite" in settings.DATABASE_URL:
        # SQLite para desenvolvimento
        engine = create_engine(
            settings.DATABASE_URL,
            connect_args={
                "check_same_thread": False,
                "timeout": 20,
                "isolation_level": None  # Auto-commit mode
            },
            poolclass=QueuePool,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=settings.DEBUG
        )
        
        # Habilita foreign keys no SQLite
        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.execute("PRAGMA cache_size=10000")
            cursor.execute("PRAGMA temp_store=MEMORY")
            cursor.close()
            
    elif "postgresql" in settings.DATABASE_URL:
        # PostgreSQL para produção
        engine = create_engine(
            settings.DATABASE_URL,
            poolclass=QueuePool,
            pool_size=20,
            max_overflow=30,
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=settings.DEBUG,
            # Configurações específicas do PostgreSQL
            connect_args={
                "connect_timeout": 10,
                "application_name": "api_segura"
            }
        )
        
    else:
        # Configuração genérica para outros bancos
        engine = create_engine(
            settings.DATABASE_URL,
            poolclass=QueuePool,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=settings.DEBUG
        )
    
    return engine

# Criação do engine
engine = create_database_engine()


# Criação da sessão com configurações otimizadas
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False  # Mantém objetos válidos após commit
)

def get_db() -> Generator[Session, None, None]:
    """
    Dependency para obter a sessão do banco de dados
    Usado pelo FastAPI para injetar a sessão nos endpoints
    """
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        logger.error(f"Erro no banco de dados: {e}")
        db.rollback()
        raise
    except Exception as e:
        logger.error(f"Erro inesperado: {e}")
        db.rollback()
        raise
    finally:
        db.close()

@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    Context manager para sessões de banco de dados
    Útil para operações fora dos endpoints da API
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        logger.error(f"Erro na sessão: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def create_tables() -> bool:
    """
    Cria todas as tabelas no banco de dados
    Retorna True se bem-sucedido, False caso contrário
    """
    try:
        # Importa os modelos para garantir que estão registrados
        from models import Base
        
        # Cria as tabelas
        Base.metadata.create_all(bind=engine)
        logger.info("Tabelas criadas com sucesso")
        return True
        
    except Exception as e:
        logger.error(f"Erro ao criar tabelas: {e}")
        return False

def drop_tables() -> bool:
    """
    Remove todas as tabelas do banco de dados
    CUIDADO: Isso apaga todos os dados!
    """
    try:
        from models import Base
        Base.metadata.drop_all(bind=engine)
        logger.info("Tabelas removidas com sucesso")
        return True
        
    except Exception as e:
        logger.error(f"Erro ao remover tabelas: {e}")
        return False

def check_database_connection() -> bool:
    """
    Verifica se a conexão com o banco está funcionando
    """
    try:
        with get_db_session() as db:
            # Executa uma query simples
            result = db.execute(text("SELECT 1"))
            result.fetchone()
            logger.info("Conexão com banco de dados OK")
            return True
            
    except Exception as e:
        logger.error(f"Erro na conexão com banco: {e}")
        return False

def get_database_info() -> dict:
    """
    Retorna informações sobre o banco de dados
    """
    try:
        with get_db_session() as db:
            # Detecta o tipo de banco
            if "sqlite" in settings.DATABASE_URL:
                result = db.execute(text("SELECT sqlite_version()"))
                version = result.fetchone()[0]
                db_type = "SQLite"
            elif "postgresql" in settings.DATABASE_URL:
                result = db.execute(text("SELECT version()"))
                version = result.fetchone()[0]
                db_type = "PostgreSQL"
            else:
                version = "Desconhecido"
                db_type = "Desconhecido"
            
            return {
                "type": db_type,
                "version": version,
                "url": settings.DATABASE_URL.replace(
                    settings.DATABASE_URL.split("@")[-1], 
                    "***" if "@" in settings.DATABASE_URL else "***"
                ),
                "pool_size": engine.pool.size(),
                "checked_in": engine.pool.checkedin(),
                "checked_out": engine.pool.checkedout(),
                "overflow": engine.pool.overflow()
            }
            
    except Exception as e:
        logger.error(f"Erro ao obter informações do banco: {e}")
        return {"error": str(e)}


def run_migration(migration_name: str) -> bool:
    """
    Executa uma migração específica
    """
    try:
        with get_db_session() as db:
            # Aqui você pode adicionar lógica de migração específica
            logger.info(f"Migração '{migration_name}' executada com sucesso")
            return True
            
    except Exception as e:
        logger.error(f"Erro na migração '{migration_name}': {e}")
        return False

def backup_database(backup_path: str) -> bool:
    """
    Cria backup do banco de dados (apenas SQLite)
    """
    if "sqlite" not in settings.DATABASE_URL:
        logger.warning("Backup automático apenas disponível para SQLite")
        return False
    
    try:
        import shutil
        import os
        
        # Extrai o caminho do banco SQLite
        db_path = settings.DATABASE_URL.replace("sqlite:///", "")
        if not os.path.exists(db_path):
            logger.error(f"Arquivo de banco não encontrado: {db_path}")
            return False
        
        # Cria o backup
        shutil.copy2(db_path, backup_path)
        logger.info(f"Backup criado: {backup_path}")
        return True
        
    except Exception as e:
        logger.error(f"Erro ao criar backup: {e}")
        return False


def vacuum_database() -> bool:
    """
    Executa VACUUM no banco (apenas SQLite)
    """
    if "sqlite" not in settings.DATABASE_URL:
        return False
    
    try:
        with get_db_session() as db:
            db.execute(text("VACUUM"))
            logger.info("VACUUM executado com sucesso")
            return True
            
    except Exception as e:
        logger.error(f"Erro ao executar VACUUM: {e}")
        return False

def analyze_database() -> bool:
    """
    Executa ANALYZE no banco (PostgreSQL)
    """
    if "postgresql" not in settings.DATABASE_URL:
        return False
    
    try:
        with get_db_session() as db:
            db.execute(text("ANALYZE"))
            logger.info("ANALYZE executado com sucesso")
            return True
            
    except Exception as e:
        logger.error(f"Erro ao executar ANALYZE: {e}")
        return False


@event.listens_for(engine, "connect")
def receive_connect(dbapi_connection, connection_record):
    """Log quando uma nova conexão é criada"""
    logger.debug("Nova conexão com banco de dados criada")

@event.listens_for(engine, "checkout")
def receive_checkout(dbapi_connection, connection_record, connection_proxy):
    """Log quando uma conexão é emprestada do pool"""
    logger.debug("Conexão emprestada do pool")

@event.listens_for(engine, "checkin")
def receive_checkin(dbapi_connection, connection_record):
    """Log quando uma conexão é devolvida ao pool"""
    logger.debug("Conexão devolvida ao pool")


def initialize_database() -> bool:
    """
    Inicializa o banco de dados
    Verifica conexão, cria tabelas se necessário
    """
    logger.info("Inicializando banco de dados...")
    
    # Verifica conexão
    if not check_database_connection():
        logger.error("Falha na conexão com banco de dados")
        return False
    
    # Cria tabelas se não existirem
    if not create_tables():
        logger.error("Falha ao criar tabelas")
        return False
    
    logger.info("Banco de dados inicializado com sucesso")
    return True

# Executa inicialização se este módulo for executado diretamente
if __name__ == "__main__":
    initialize_database()