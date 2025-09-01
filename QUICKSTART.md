# 🚀 Guia de Início Rápido

## Configuração Inicial (Primeira vez)

```bash
# 1. Execute o script de setup
./setup.sh

# 2. Ative o ambiente virtual
source venv/bin/activate
```

## Executando a API

```bash
# Desenvolvimento (com reload automático)
python main.py

# Ou usando uvicorn diretamente
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Acessando a API

- **API Base:** http://localhost:8000
- **Documentação Swagger:** http://localhost:8000/docs
- **Documentação ReDoc:** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/health

## Testando a API

```bash
# Executar todos os testes
pytest test_api.py -v

# Testar endpoints manualmente
curl http://localhost:8000/
curl http://localhost:8000/health
```

## 🎯 Ambiente Limpo e Pronto

Este ambiente está **100% limpo** e pronto para você criar qualquer API. Apenas:

1. **Execute:** `python main.py`
2. **Acesse:** http://localhost:8000/docs
3. **Comece a desenvolver** sua API específica!

## 📝 Para Criar Sua API

### 1. Defina seus modelos Pydantic
```python
from pydantic import BaseModel

class SeuModelo(BaseModel):
    campo1: str
    campo2: int
    campo3: Optional[str] = None
```

### 2. Crie seus endpoints
```python
@app.get("/seu-endpoint")
async def seu_endpoint():
    return {"message": "Seu endpoint funcionando!"}

@app.post("/seu-endpoint")
async def criar_algo(item: SeuModelo):
    # Sua lógica aqui
    return item
```

### 3. Adicione testes
```python
def test_seu_endpoint():
    response = client.get("/seu-endpoint")
    assert response.status_code == 200
```

## Comandos Úteis

```bash
# Ativar ambiente virtual
source venv/bin/activate

# Desativar ambiente virtual
deactivate

# Instalar nova dependência
pip install nome-do-pacote

# Ver dependências instaladas
pip list

# Atualizar requirements.txt
pip freeze > requirements.txt
```

## Estrutura do Projeto

```
teste_multiplike/
├── main.py              # API principal (limpa)
├── config.py            # Configurações
├── test_api.py          # Testes básicos
├── requirements.txt     # Dependências
├── setup.sh            # Script de setup
├── README.md           # Documentação completa
├── QUICKSTART.md       # Este arquivo
├── env.example         # Exemplo de variáveis
├── .gitignore          # Arquivos ignorados
└── venv/               # Ambiente virtual
```

## 🚀 Próximos Passos

1. **Defina o tema** - Escolha o domínio da sua API
2. **Crie modelos** - Defina estruturas de dados com Pydantic
3. **Implemente endpoints** - Crie as rotas da API
4. **Adicione testes** - Teste cada funcionalidade
5. **Configure banco** - Adicione persistência de dados
6. **Implemente auth** - Adicione autenticação se necessário
