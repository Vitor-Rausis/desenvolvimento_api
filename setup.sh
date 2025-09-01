#!/bin/bash

echo "🚀 Configurando ambiente para API Python..."

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Por favor, instale o Python 3.8 ou superior."
    exit 1
fi

echo "✅ Python encontrado: $(python3 --version)"

# Criar ambiente virtual
echo "📦 Criando ambiente virtual..."
python3 -m venv venv

# Ativar ambiente virtual
echo "🔧 Ativando ambiente virtual..."
source venv/bin/activate

# Atualizar pip
echo "⬆️ Atualizando pip..."
pip install --upgrade pip

# Instalar dependências
echo "📚 Instalando dependências..."
pip install -r requirements.txt

# Criar arquivo .env
if [ ! -f .env ]; then
    echo "⚙️ Criando arquivo .env..."
    cp env.example .env
    echo "✅ Arquivo .env criado. Edite-o conforme necessário."
else
    echo "✅ Arquivo .env já existe."
fi

echo ""
echo "🎉 Ambiente configurado com sucesso!"
echo ""
echo "📋 Próximos passos:"
echo "1. Ative o ambiente virtual: source venv/bin/activate"
echo "2. Execute a API: python main.py"
echo "3. Acesse a documentação: http://localhost:8000/docs"
echo ""
echo "🔧 Para ativar o ambiente virtual novamente:"
echo "   source venv/bin/activate"
