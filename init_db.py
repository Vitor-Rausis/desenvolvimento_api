#!/usr/bin/env python3

from database import SessionLocal, create_tables
from models import User, DataItem
from auth import get_password_hash
from crud import create_user
from models import UserCreate

def init_database():
    """Inicializa o banco de dados com dados de exemplo"""
    print("Inicializando banco de dados...")
    
    # Cria as tabelas
    create_tables()
    print("✓ Tabelas criadas")
    
    # Cria sessão do banco
    db = SessionLocal()
    
    try:
        # Verifica se já existem usuários
        existing_users = db.query(User).count()
        if existing_users > 0:
            print("✓ Banco de dados já possui dados")
            return
        
        # Cria usuários de exemplo
        users_data = [
            {
                "username": "admin",
                "email": "admin@example.com",
                "password": "admin123",
                "user_type": "admin"
            },
            {
                "username": "user1",
                "email": "user1@example.com",
                "password": "user123",
                "user_type": "user"
            },
            {
                "username": "user2",
                "email": "user2@example.com",
                "password": "user123",
                "user_type": "user"
            }
        ]
        
        created_users = []
        for user_data in users_data:
            try:
                user = UserCreate(**user_data)
                created_user = create_user(db, user)
                created_users.append(created_user)
                print(f"✓ Usuário criado: {created_user.username}")
            except Exception as e:
                print(f"✗ Erro ao criar usuário {user_data['username']}: {e}")
        
        # Cria dados de exemplo
        sample_data = [
            {
                "title": "Primeiro item",
                "content": "Este é o primeiro item de dados criado pelo admin",
                "user_id": created_users[0].id  # admin
            },
            {
                "title": "Nota pessoal",
                "content": "Esta é uma nota pessoal do usuário 1",
                "user_id": created_users[1].id  # user1
            },
            {
                "title": "Tarefa importante",
                "content": "Lembrar de fazer backup dos dados",
                "user_id": created_users[1].id  # user1
            },
            {
                "title": "Projeto futuro",
                "content": "Ideias para melhorias na API",
                "user_id": created_users[2].id  # user2
            }
        ]
        
        for data_item in sample_data:
            db_data_item = DataItem(**data_item)
            db.add(db_data_item)
            print(f"✓ Item de dados criado: {data_item['title']}")
        
        db.commit()
        print("✓ Banco de dados inicializado com sucesso!")
        print("\nUsuários criados:")
        print("- admin/admin123 (tipo: admin)")
        print("- user1/user123 (tipo: user)")
        print("- user2/user123 (tipo: user)")
        
    except Exception as e:
        print(f"✗ Erro ao inicializar banco de dados: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_database()