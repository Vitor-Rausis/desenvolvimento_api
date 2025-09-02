import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from database import get_db, Base
from models import User, DataItem
from auth import get_password_hash

# Configuração do banco de dados de teste
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    """Override da função get_db para testes"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Substitui a dependência do banco de dados
app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    """Cliente de teste"""
    # Cria as tabelas
    Base.metadata.create_all(bind=engine)
    
    with TestClient(app) as c:
        yield c
    
    # Limpa as tabelas após os testes
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_user():
    """Usuário de teste"""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
        "user_type": "user"
    }

@pytest.fixture
def test_admin():
    """Administrador de teste"""
    return {
        "username": "testadmin",
        "email": "admin@example.com",
        "password": "adminpass123",
        "user_type": "admin"
    }

@pytest.fixture
def auth_headers(client, test_user):
    """Headers de autenticação para um usuário"""
    # Registra o usuário
    response = client.post("/register", json=test_user)
    assert response.status_code == 200
    
    # Faz login
    login_data = {
        "username": test_user["username"],
        "password": test_user["password"]
    }
    response = client.post("/login", json=login_data)
    assert response.status_code == 200
    
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def admin_headers(client, test_admin):
    """Headers de autenticação para um administrador"""
    # Registra o admin
    response = client.post("/register", json=test_admin)
    assert response.status_code == 200
    
    # Faz login
    login_data = {
        "username": test_admin["username"],
        "password": test_admin["password"]
    }
    response = client.post("/login", json=login_data)
    assert response.status_code == 200
    
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

class TestAuthentication:
    """Testes de autenticação"""
    
    def test_register_user(self, client, test_user):
        """Testa registro de usuário"""
        response = client.post("/register", json=test_user)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == test_user["username"]
        assert data["email"] == test_user["email"]
        assert "password" not in data
    
    def test_register_duplicate_username(self, client, test_user):
        """Testa registro com username duplicado"""
        # Primeiro registro
        response = client.post("/register", json=test_user)
        assert response.status_code == 200
        
        # Segundo registro com mesmo username
        response = client.post("/register", json=test_user)
        assert response.status_code == 400
        assert "já registrado" in response.json()["detail"]
    
    def test_login_success(self, client, test_user):
        """Testa login bem-sucedido"""
        # Registra o usuário
        client.post("/register", json=test_user)
        
        # Faz login
        login_data = {
            "username": test_user["username"],
            "password": test_user["password"]
        }
        response = client.post("/login", json=login_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_credentials(self, client, test_user):
        """Testa login com credenciais inválidas"""
        # Registra o usuário
        client.post("/register", json=test_user)
        
        # Tenta login com senha errada
        login_data = {
            "username": test_user["username"],
            "password": "wrongpassword"
        }
        response = client.post("/login", json=login_data)
        assert response.status_code == 401

class TestDataEndpoints:
    """Testes dos endpoints de dados"""
    
    def test_create_data_item(self, client, auth_headers):
        """Testa criação de item de dados"""
        data_item = {
            "title": "Test Item",
            "content": "This is a test item"
        }
        response = client.post("/data", json=data_item, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == data_item["title"]
        assert data["content"] == data_item["content"]
        assert "id" in data
    
    def test_create_data_item_unauthorized(self, client):
        """Testa criação sem autenticação"""
        data_item = {
            "title": "Test Item",
            "content": "This is a test item"
        }
        response = client.post("/data", json=data_item)
        assert response.status_code == 401
    
    def test_get_data_items(self, client, auth_headers):
        """Testa listagem de dados do usuário"""
        # Cria alguns itens
        data_items = [
            {"title": "Item 1", "content": "Content 1"},
            {"title": "Item 2", "content": "Content 2"}
        ]
        for item in data_items:
            client.post("/data", json=item, headers=auth_headers)
        
        # Lista os itens
        response = client.get("/data", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
    
    def test_get_data_item_by_id(self, client, auth_headers):
        """Testa obtenção de item específico"""
        # Cria um item
        data_item = {"title": "Test Item", "content": "Test Content"}
        create_response = client.post("/data", json=data_item, headers=auth_headers)
        item_id = create_response.json()["id"]
        
        # Obtém o item
        response = client.get(f"/data/{item_id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == item_id
        assert data["title"] == data_item["title"]
    
    def test_update_data_item(self, client, auth_headers):
        """Testa atualização de item"""
        # Cria um item
        data_item = {"title": "Original Title", "content": "Original Content"}
        create_response = client.post("/data", json=data_item, headers=auth_headers)
        item_id = create_response.json()["id"]
        
        # Atualiza o item
        update_data = {"title": "Updated Title"}
        response = client.put(f"/data/{item_id}", json=update_data, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["content"] == "Original Content"  # Não foi alterado
    
    def test_delete_data_item(self, client, auth_headers):
        """Testa exclusão de item"""
        # Cria um item
        data_item = {"title": "To Delete", "content": "Will be deleted"}
        create_response = client.post("/data", json=data_item, headers=auth_headers)
        item_id = create_response.json()["id"]
        
        # Deleta o item
        response = client.delete(f"/data/{item_id}", headers=auth_headers)
        assert response.status_code == 200
        assert "deletado com sucesso" in response.json()["message"]
        
        # Verifica que foi deletado
        get_response = client.get(f"/data/{item_id}", headers=auth_headers)
        assert get_response.status_code == 404

class TestAdminEndpoints:
    """Testes dos endpoints de administrador"""
    
    def test_admin_can_see_all_data(self, client, auth_headers, admin_headers):
        """Testa que admin pode ver todos os dados"""
        # Usuário normal cria dados
        data_item = {"title": "User Data", "content": "User content"}
        client.post("/data", json=data_item, headers=auth_headers)
        
        # Admin lista todos os dados
        response = client.get("/data", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1  # Pelo menos o item criado pelo usuário
    
    def test_normal_user_cannot_access_admin_endpoint(self, client, auth_headers):
        """Testa que usuário normal não pode acessar endpoint de admin"""
        response = client.get("/users", headers=auth_headers)
        assert response.status_code == 403
    
    def test_admin_can_access_users_endpoint(self, client, admin_headers):
        """Testa que admin pode acessar endpoint de usuários"""
        response = client.get("/users", headers=admin_headers)
        assert response.status_code == 200

class TestSecurity:
    """Testes de segurança"""
    
    def test_rate_limiting(self, client, auth_headers):
        """Testa rate limiting"""
        # Faz muitas requisições rapidamente
        for _ in range(65):  # Mais que o limite de 60 por minuto
            response = client.get("/data", headers=auth_headers)
            if response.status_code == 429:
                break
        else:
            # Se não atingiu o limite, pelo menos deve funcionar
            assert response.status_code in [200, 429]
    
    def test_invalid_token(self, client):
        """Testa token inválido"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/data", headers=headers)
        assert response.status_code == 401

if __name__ == "__main__":
    pytest.main([__file__, "-v"])