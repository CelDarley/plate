#!/bin/bash

# Script de entrada para Docker
# Configura Chrome headless e inicia a aplicação

set -e

echo "🚀 Iniciando API Placa FIPE Scraper..."

# Função para configurar Chrome headless
setup_chrome_headless() {
    echo "🔧 Configurando Chrome headless..."
    
    # Iniciar Xvfb (display virtual)
    if [ "$CHROME_HEADLESS" = "true" ]; then
        echo "📺 Iniciando display virtual Xvfb..."
        Xvfb :99 -screen 0 1920x1080x24 > /dev/null 2>&1 &
        export DISPLAY=:99
        
        # Aguardar Xvfb inicializar
        sleep 2
        
        # Testar Chrome headless
        echo "🧪 Testando Chrome headless..."
        timeout 10s google-chrome --headless --no-sandbox --disable-gpu --dump-dom https://www.google.com > /dev/null 2>&1
        if [ $? -eq 0 ]; then
            echo "✅ Chrome headless funcionando"
        else
            echo "⚠️ Chrome headless pode ter problemas"
        fi
    fi
}

# Função para verificar dependências
check_dependencies() {
    echo "🔍 Verificando dependências..."
    
    # Verificar Python
    if ! command -v python > /dev/null 2>&1; then
        echo "❌ Python não encontrado"
        exit 1
    fi
    
    # Verificar Chrome
    if ! command -v google-chrome > /dev/null 2>&1; then
        echo "❌ Google Chrome não encontrado"
        exit 1
    fi
    
    # Verificar ChromeDriver
    if ! command -v chromedriver > /dev/null 2>&1; then
        echo "❌ ChromeDriver não encontrado"
        exit 1
    fi
    
    echo "✅ Todas as dependências encontradas"
}

# Função para aguardar banco de dados
wait_for_database() {
    if [ -n "$DB_HOST" ] && [ -n "$DB_PORT" ]; then
        echo "🗄️ Aguardando banco de dados..."
        while ! nc -z "$DB_HOST" "$DB_PORT"; do
            echo "⏳ Aguardando banco de dados em $DB_HOST:$DB_PORT..."
            sleep 2
        done
        echo "✅ Banco de dados disponível"
    fi
}

# Função para aplicar migrações
run_migrations() {
    echo "🔄 Verificando migrações..."
    if [ -f "migrate_to_mysql.py" ]; then
        echo "📊 Executando migração se necessário..."
        python migrate_to_mysql.py
    fi
}

# Função principal
main() {
    echo "🔧 Configurando ambiente..."
    
    # Verificar dependências
    check_dependencies
    
    # Configurar Chrome headless
    setup_chrome_headless
    
    # Aguardar banco se configurado
    wait_for_database
    
    # Executar migrações se necessário
    run_migrations
    
    echo "🚀 Iniciando aplicação..."
    
    # Executar comando passado
    exec "$@"
}

# Executar função principal
main "$@"
