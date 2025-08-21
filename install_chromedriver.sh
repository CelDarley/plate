#!/bin/bash

echo "🚀 Instalando ChromeDriver para o Sistema de Scraping"
echo "=================================================="

# Verificar se o Chrome está instalado
if ! command -v google-chrome &> /dev/null; then
    echo "❌ Google Chrome não encontrado!"
    echo "💡 Instale o Google Chrome primeiro:"
    echo "   sudo apt update && sudo apt install google-chrome-stable"
    exit 1
fi

echo "✅ Google Chrome encontrado"

# Remover instalações anteriores corrompidas
echo "🧹 Limpando instalações anteriores..."
rm -rf ~/.wdm/
rm -rf ~/.cache/selenium/

# Instalar dependências Python
echo "📦 Atualizando dependências Python..."
pip install --upgrade webdriver-manager selenium

# Verificar se o chromedriver está no sistema
if command -v chromedriver &> /dev/null; then
    echo "✅ ChromeDriver encontrado no sistema"
    CHROMEDRIVER_PATH=$(which chromedriver)
    echo "📍 Localização: $CHROMEDRIVER_PATH"
else
    echo "📥 ChromeDriver não encontrado, baixando..."
    
    # Baixar ChromeDriver
    CHROME_VERSION=$(google-chrome --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
    echo "🔍 Versão do Chrome: $CHROME_VERSION"
    
    # Extrair versão principal
    MAJOR_VERSION=$(echo $CHROME_VERSION | cut -d. -f1)
    echo "📋 Versão principal: $MAJOR_VERSION"
    
    # Baixar ChromeDriver compatível
    CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$MAJOR_VERSION")
    echo "📥 Versão do ChromeDriver: $CHROMEDRIVER_VERSION"
    
    # Baixar e instalar
    wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip"
    unzip -o /tmp/chromedriver.zip -d /tmp/
    sudo mv /tmp/chromedriver /usr/local/bin/
    sudo chmod +x /usr/local/bin/chromedriver
    
    echo "✅ ChromeDriver instalado em /usr/local/bin/chromedriver"
fi

# Testar instalação
echo "🧪 Testando instalação..."
python3 -c "
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

try:
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    service = Service('chromedriver')
    driver = webdriver.Chrome(service=service, options=options)
    print('✅ ChromeDriver funcionando corretamente!')
    driver.quit()
except Exception as e:
    print(f'❌ Erro no teste: {e}')
"

echo ""
echo "🎯 Instalação concluída!"
echo "💡 Agora você pode executar: python3 app.py"
