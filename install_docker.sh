#!/bin/bash

# Script de instalação do Docker e Docker Compose
# Para Ubuntu/Debian

echo "🐳 Instalando Docker e Docker Compose..."

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

echo -e "${YELLOW}📋 Verificando sistema...${NC}"

# Verificar distribuição
if ! command_exists lsb_release; then
    echo -e "${RED}❌ lsb_release não encontrado. Instalando...${NC}"
    sudo apt update
    sudo apt install -y lsb-release
fi

DISTRO=$(lsb_release -is)
VERSION=$(lsb_release -rs)

echo -e "${GREEN}✅ Distribuição: $DISTRO $VERSION${NC}"

# Verificar se Docker já está instalado
if command_exists docker; then
    echo -e "${GREEN}✅ Docker já está instalado${NC}"
    DOCKER_VERSION=$(docker --version)
    echo -e "${BLUE}📋 Versão: $DOCKER_VERSION${NC}"
else
    echo -e "${YELLOW}📥 Instalando Docker...${NC}"
    
    # Remover versões antigas se existirem
    sudo apt remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true
    
    # Atualizar sistema
    sudo apt update
    
    # Instalar dependências
    sudo apt install -y \
        apt-transport-https \
        ca-certificates \
        curl \
        gnupg \
        lsb-release
    
    # Adicionar chave GPG oficial do Docker
    echo -e "${YELLOW}🔑 Adicionando chave GPG do Docker...${NC}"
    curl -fsSL https://download.docker.com/linux/$DISTRO/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    
    # Adicionar repositório do Docker
    echo -e "${YELLOW}📦 Adicionando repositório do Docker...${NC}"
    echo \
        "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/$DISTRO \
        $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Atualizar e instalar Docker
    sudo apt update
    sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    
    echo -e "${GREEN}✅ Docker instalado com sucesso${NC}"
fi

# Verificar se Docker Compose está instalado
if command_exists docker-compose; then
    echo -e "${GREEN}✅ Docker Compose já está instalado${NC}"
    COMPOSE_VERSION=$(docker-compose --version)
    echo -e "${BLUE}📋 Versão: $COMPOSE_VERSION${NC}"
else
    echo -e "${YELLOW}📥 Instalando Docker Compose...${NC}"
    
    # Instalar Docker Compose standalone (versão mais recente)
    COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d\" -f4)
    
    echo -e "${YELLOW}📥 Baixando Docker Compose $COMPOSE_VERSION...${NC}"
    sudo curl -L "https://github.com/docker/compose/releases/download/$COMPOSE_VERSION/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    
    # Tornar executável
    sudo chmod +x /usr/local/bin/docker-compose
    
    echo -e "${GREEN}✅ Docker Compose instalado com sucesso${NC}"
fi

# Adicionar usuário ao grupo docker
if ! groups $USER | grep -q docker; then
    echo -e "${YELLOW}👤 Adicionando usuário ao grupo docker...${NC}"
    sudo usermod -aG docker $USER
    echo -e "${GREEN}✅ Usuário adicionado ao grupo docker${NC}"
    echo -e "${YELLOW}⚠️ IMPORTANTE: Faça logout e login novamente para aplicar as permissões${NC}"
else
    echo -e "${GREEN}✅ Usuário já está no grupo docker${NC}"
fi

# Iniciar e habilitar serviço Docker
echo -e "${YELLOW}🚀 Iniciando serviço Docker...${NC}"
sudo systemctl start docker
sudo systemctl enable docker

# Verificar status
if sudo systemctl is-active --quiet docker; then
    echo -e "${GREEN}✅ Serviço Docker está rodando${NC}"
else
    echo -e "${RED}❌ Erro ao iniciar serviço Docker${NC}"
    sudo systemctl status docker
    exit 1
fi

# Testar Docker
echo -e "${YELLOW}🧪 Testando Docker...${NC}"
if sudo docker run --rm hello-world > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Docker funcionando perfeitamente${NC}"
else
    echo -e "${RED}❌ Erro no teste do Docker${NC}"
    exit 1
fi

# Testar Docker Compose
echo -e "${YELLOW}🧪 Testando Docker Compose...${NC}"
if docker-compose --version > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Docker Compose funcionando${NC}"
else
    echo -e "${RED}❌ Erro no teste do Docker Compose${NC}"
    exit 1
fi

echo -e "${GREEN}🎉 Docker e Docker Compose instalados com sucesso!${NC}"
echo -e "${BLUE}📋 Informações:${NC}"
echo -e "   Docker: $(docker --version)"
echo -e "   Docker Compose: $(docker-compose --version)"
echo -e "   Status: $(sudo systemctl is-active docker)"

echo -e "${YELLOW}📋 Próximos passos:${NC}"
echo -e "1. Faça logout e login novamente (para aplicar permissões do grupo docker)"
echo -e "2. Teste: docker run hello-world"
echo -e "3. Execute: ./deploy.sh local"

echo -e "${GREEN}🚀 Agora você pode usar o script de deploy!${NC}"
