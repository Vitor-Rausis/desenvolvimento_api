import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

class Settings:
    """Configurações da aplicação"""
    
    # Configurações básicas
    APP_NAME: str = "Minha API Python"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # Configurações do servidor
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Configurações de banco de dados
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "sqlite:///./app.db"
    )
    
    # Configurações de segurança
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY", 
        "sua-chave-secreta-aqui-mude-em-producao"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    )
    
    # Configurações de CORS
    CORS_ORIGINS: list = os.getenv(
        "CORS_ORIGINS", 
        "*"
    ).split(",")
    
    # Configurações de logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

# Instância global das configurações
settings = Settings()
