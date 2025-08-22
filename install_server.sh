#!/bin/bash

# Script de instalação para servidor headless
# API Placa FIPE Scraper

echo "🚀 Instalando API Placa FIPE Scraper no servidor..."

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para verificar se o comando existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Verificar se é root
if [[ $EUID -eq 0 ]]; then
   echo -e "${RED}❌ Este script não deve ser executado como root${NC}"
   exit 1
fi

echo -e "${YELLOW}📋 Verificando dependências do sistema...${NC}"

# Verificar Python
if ! command_exists python3; then
    echo -e "${RED}❌ Python3 não encontrado. Instalando...${NC}"
    sudo apt update
    sudo apt install -y python3 python3-pip python3-venv
else
    echo -e "${GREEN}✅ Python3 encontrado${NC}"
fi

# Verificar pip
if ! command_exists pip3; then
    echo -e "${RED}❌ pip3 não encontrado. Instalando...${NC}"
    sudo apt install -y python3-pip
else
    echo -e "${GREEN}✅ pip3 encontrado${NC}"
fi

# Verificar MySQL
if ! command_exists mysql; then
    echo -e "${YELLOW}⚠️ MySQL não encontrado. Instalando...${NC}"
    sudo apt install -y mysql-server mysql-client
    sudo systemctl start mysql
    sudo systemctl enable mysql
else
    echo -e "${GREEN}✅ MySQL encontrado${NC}"
fi

echo -e "${YELLOW}🔧 Instalando Chrome e ChromeDriver para servidor headless...${NC}"

# Instalar Chrome
if ! command_exists google-chrome; then
    echo -e "${YELLOW}📥 Baixando e instalando Google Chrome...${NC}"
    wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
    sudo apt update
    sudo apt install -y google-chrome-stable
else
    echo -e "${GREEN}✅ Google Chrome encontrado${NC}"
fi

# Instalar ChromeDriver
if ! command_exists chromedriver; then
    echo -e "${YELLOW}📥 Baixando ChromeDriver...${NC}"
    CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | awk -F'.' '{print $1}')
    CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION")
    
    wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip"
    unzip /tmp/chromedriver.zip -d /tmp/
    sudo mv /tmp/chromedriver /usr/local/bin/
    sudo chmod +x /usr/local/bin/chromedriver
    rm /tmp/chromedriver.zip
    
    echo -e "${GREEN}✅ ChromeDriver instalado${NC}"
else
    echo -e "${GREEN}✅ ChromeDriver encontrado${NC}"
fi

echo -e "${YELLOW}🐍 Criando ambiente virtual Python...${NC}"

# Criar ambiente virtual
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✅ Ambiente virtual criado${NC}"
else
    echo -e "${GREEN}✅ Ambiente virtual já existe${NC}"
fi

# Ativar ambiente virtual
source venv/bin/activate

echo -e "${YELLOW}📦 Instalando dependências Python...${NC}"

# Instalar dependências
pip install --upgrade pip
pip install -r requirements.txt

echo -e "${YELLOW}⚙️ Configurando variáveis de ambiente...${NC}"

# Criar arquivo .env se não existir
if [ ! -f ".env" ]; then
    cp config.env.example .env
    echo -e "${GREEN}✅ Arquivo .env criado${NC}"
    echo -e "${YELLOW}⚠️ Edite o arquivo .env com suas configurações${NC}"
else
    echo -e "${GREEN}✅ Arquivo .env já existe${NC}"
fi

echo -e "${YELLOW}🔧 Configurando Chrome para servidor headless...${NC}"

# Verificar se o Chrome funciona em modo headless
if command_exists google-chrome; then
    echo -e "${YELLOW}🧪 Testando Chrome headless...${NC}"
    timeout 10s google-chrome --headless --no-sandbox --disable-gpu --dump-dom https://www.google.com > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Chrome headless funcionando${NC}"
    else
        echo -e "${YELLOW}⚠️ Chrome headless pode ter problemas${NC}"
    fi
fi

echo -e "${YELLOW}📝 Criando arquivo de serviço systemd...${NC}"

# Criar arquivo de serviço systemd
sudo tee /etc/systemd/system/plate-api.service > /dev/null <<EOF
[Unit]
Description=Placa FIPE Scraper API
After=network.target mysql.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin
ExecStart=$(pwd)/venv/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}✅ Serviço systemd criado${NC}"

echo -e "${YELLOW}🚀 Configurando e iniciando serviço...${NC}"

# Recarregar systemd e habilitar serviço
sudo systemctl daemon-reload
sudo systemctl enable plate-api.service

echo -e "${GREEN}✅ Instalação concluída!${NC}"
echo -e "${YELLOW}📋 Próximos passos:${NC}"
echo -e "1. Edite o arquivo .env com suas configurações"
echo -e "2. Configure o banco MySQL"
echo -e "3. Inicie o serviço: sudo systemctl start plate-api"
echo -e "4. Verifique o status: sudo systemctl status plate-api"
echo -e "5. Veja os logs: sudo journalctl -u plate-api -f"
echo -e ""
echo -e "${GREEN}🌐 A API estará disponível em: http://$(hostname -I | awk '{print $1}'):5000${NC}"
