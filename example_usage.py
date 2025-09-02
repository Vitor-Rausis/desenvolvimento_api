#!/usr/bin/env python3
"""
Exemplo de uso da API Segura
Demonstra como usar todos os endpoints da API
"""

import requests
import json
from typing import Dict, Any

class APIClient:
    """Cliente para interagir com a API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.token = None
        self.headers = {"Content-Type": "application/json"}
    
    def login(self, username: str, password: str) -> bool:
        """Faz login e obtém token"""
        try:
            response = requests.post(
                f"{self.base_url}/login",
                json={"username": username, "password": password}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data["access_token"]
                self.headers["Authorization"] = f"Bearer {self.token}"
                print(f"✅ Login realizado com sucesso para {username}")
                return True
            else:
                print(f"❌ Erro no login: {response.json()}")
                return False
                
        except Exception as e:
            print(f"❌ Erro de conexão: {e}")
            return False
    
    def register(self, username: str, email: str, password: str, user_type: str = "user") -> bool:
        """Registra um novo usuário"""
        try:
            response = requests.post(
                f"{self.base_url}/register",
                json={
                    "username": username,
                    "email": email,
                    "password": password,
                    "user_type": user_type
                }
            )
            
            if response.status_code == 200:
                print(f"✅ Usuário {username} registrado com sucesso")
                return True
            else:
                print(f"❌ Erro no registro: {response.json()}")
                return False
                
        except Exception as e:
            print(f"❌ Erro de conexão: {e}")
            return False
    
    def create_data(self, title: str, content: str) -> Dict[str, Any]:
        """Cria um novo item de dados"""
        if not self.token:
            print("❌ Não autenticado. Faça login primeiro.")
            return {}
        
        try:
            response = requests.post(
                f"{self.base_url}/data",
                headers=self.headers,
                json={"title": title, "content": content}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Item criado: {data['title']} (ID: {data['id']})")
                return data
            else:
                print(f"❌ Erro ao criar item: {response.json()}")
                return {}
                
        except Exception as e:
            print(f"❌ Erro de conexão: {e}")
            return {}
    
    def get_data(self) -> list:
        """Lista todos os dados do usuário"""
        if not self.token:
            print("❌ Não autenticado. Faça login primeiro.")
            return []
        
        try:
            response = requests.get(f"{self.base_url}/data", headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Encontrados {len(data)} itens de dados")
                return data
            else:
                print(f"❌ Erro ao listar dados: {response.json()}")
                return []
                
        except Exception as e:
            print(f"❌ Erro de conexão: {e}")
            return []
    
    def get_data_by_id(self, item_id: int) -> Dict[str, Any]:
        """Obtém um item específico por ID"""
        if not self.token:
            print("❌ Não autenticado. Faça login primeiro.")
            return {}
        
        try:
            response = requests.get(f"{self.base_url}/data/{item_id}", headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Item encontrado: {data['title']}")
                return data
            else:
                print(f"❌ Erro ao obter item: {response.json()}")
                return {}
                
        except Exception as e:
            print(f"❌ Erro de conexão: {e}")
            return {}
    
    def update_data(self, item_id: int, title: str = None, content: str = None) -> Dict[str, Any]:
        """Atualiza um item de dados"""
        if not self.token:
            print("❌ Não autenticado. Faça login primeiro.")
            return {}
        
        update_data = {}
        if title:
            update_data["title"] = title
        if content:
            update_data["content"] = content
        
        try:
            response = requests.put(
                f"{self.base_url}/data/{item_id}",
                headers=self.headers,
                json=update_data
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Item atualizado: {data['title']}")
                return data
            else:
                print(f"❌ Erro ao atualizar item: {response.json()}")
                return {}
                
        except Exception as e:
            print(f"❌ Erro de conexão: {e}")
            return {}
    
    def delete_data(self, item_id: int) -> bool:
        """Deleta um item de dados"""
        if not self.token:
            print("❌ Não autenticado. Faça login primeiro.")
            return False
        
        try:
            response = requests.delete(f"{self.base_url}/data/{item_id}", headers=self.headers)
            
            if response.status_code == 200:
                print(f"✅ Item {item_id} deletado com sucesso")
                return True
            else:
                print(f"❌ Erro ao deletar item: {response.json()}")
                return False
                
        except Exception as e:
            print(f"❌ Erro de conexão: {e}")
            return False
    
    def get_users(self) -> list:
        """Lista todos os usuários (apenas para admins)"""
        if not self.token:
            print("❌ Não autenticado. Faça login primeiro.")
            return []
        
        try:
            response = requests.get(f"{self.base_url}/users", headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Encontrados {len(data)} usuários")
                return data
            else:
                print(f"❌ Erro ao listar usuários: {response.json()}")
                return []
                
        except Exception as e:
            print(f"❌ Erro de conexão: {e}")
            return []
    
    def get_me(self) -> Dict[str, Any]:
        """Obtém informações do usuário atual"""
        if not self.token:
            print("❌ Não autenticado. Faça login primeiro.")
            return {}
        
        try:
            response = requests.get(f"{self.base_url}/me", headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Informações do usuário: {data['username']} ({data['user_type']})")
                return data
            else:
                print(f"❌ Erro ao obter informações: {response.json()}")
                return {}
                
        except Exception as e:
            print(f"❌ Erro de conexão: {e}")
            return {}

def main():
    """Função principal com exemplos de uso"""
    print("🚀 Exemplo de uso da API Segura")
    print("=" * 50)
    
    # Cria cliente da API
    api = APIClient()
    
    # Testa conexão
    try:
        response = requests.get(f"{api.base_url}/health")
        if response.status_code == 200:
            print("✅ API está funcionando")
        else:
            print("❌ API não está respondendo")
            return
    except:
        print("❌ Não foi possível conectar à API")
        print("Certifique-se de que a API está rodando em http://localhost:8000")
        return
    
    print("\n📝 Exemplo 1: Usuário Normal")
    print("-" * 30)
    
    # Login como usuário normal
    if api.login("user1", "user123"):
        # Obtém informações do usuário
        api.get_me()
        
        # Lista dados (vazios inicialmente)
        print("\n📋 Listando dados do usuário:")
        data = api.get_data()
        
        # Cria alguns itens de dados
        print("\n➕ Criando itens de dados:")
        item1 = api.create_data("Minha primeira nota", "Esta é uma nota pessoal")
        item2 = api.create_data("Tarefa importante", "Lembrar de fazer backup")
        
        # Lista novamente
        print("\n📋 Listando dados após criação:")
        data = api.get_data()
        
        # Atualiza um item
        if item1:
            print(f"\n✏️ Atualizando item {item1['id']}:")
            api.update_data(item1['id'], title="Nota atualizada", content="Conteúdo modificado")
        
        # Obtém item específico
        if item2:
            print(f"\n🔍 Obtendo item {item2['id']}:")
            api.get_data_by_id(item2['id'])
        
        # Tenta acessar endpoint de admin (deve falhar)
        print("\n🚫 Tentando acessar endpoint de admin (deve falhar):")
        api.get_users()
    
    print("\n👑 Exemplo 2: Administrador")
    print("-" * 30)
    
    # Login como admin
    if api.login("admin", "admin123"):
        # Obtém informações do admin
        api.get_me()
        
        # Lista todos os usuários (apenas admin pode)
        print("\n👥 Listando todos os usuários:")
        users = api.get_users()
        
        # Lista todos os dados (admin vê todos)
        print("\n📋 Listando todos os dados:")
        all_data = api.get_data()
        
        # Cria um item como admin
        print("\n➕ Criando item como admin:")
        admin_item = api.create_data("Item do Admin", "Este item foi criado pelo administrador")
        
        # Lista novamente
        print("\n📋 Listando dados após criação do admin:")
        all_data = api.get_data()
    
    print("\n🧪 Exemplo 3: Testes de Segurança")
    print("-" * 30)
    
    # Tenta acessar dados sem autenticação
    print("\n🚫 Tentando acessar dados sem autenticação:")
    api.token = None
    api.headers.pop("Authorization", None)
    api.get_data()
    
    # Tenta fazer login com credenciais inválidas
    print("\n🚫 Tentando login com credenciais inválidas:")
    api.login("usuario_inexistente", "senha_errada")
    
    print("\n✅ Demonstração concluída!")
    print("\n💡 Dicas:")
    print("- Acesse http://localhost:8000/docs para documentação interativa")
    print("- Use os tokens JWT retornados para autenticar requisições")
    print("- Admins podem ver todos os dados, usuários normais veem apenas os próprios")
    print("- A API implementa rate limiting e headers de segurança")

if __name__ == "__main__":
    main()