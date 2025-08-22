#!/bin/bash

# Script de deploy para API Placa FIPE Scraper
# Suporta deploy local e em servidor

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para mostrar ajuda
show_help() {
    echo -e "${BLUE}🚀 Script de Deploy - API Placa FIPE Scraper${NC}"
    echo ""
    echo "Uso: $0 [OPÇÃO]"
    echo ""
    echo "Opções:"
    echo "  local     - Deploy local com Docker Compose"
    echo "  server    - Deploy em servidor com script de instalação"
    echo "  docker    - Deploy apenas com Docker (sem compose)"
    echo "  help      - Mostra esta ajuda"
    echo ""
    echo "Exemplos:"
    echo "  $0 local     # Deploy local com Docker Compose"
    echo "  $0 server    # Deploy em servidor headless"
    echo "  $0 docker    # Deploy com Docker apenas"
}

# Função para deploy local
deploy_local() {
    echo -e "${GREEN}🏠 Deploy local com Docker Compose...${NC}"
    
    # Verificar se Docker está instalado
    if ! command -v docker > /dev/null 2>&1; then
        echo -e "${RED}❌ Docker não encontrado. Instale o Docker primeiro.${NC}"
        exit 1
    fi
    
    if ! command -v docker-compose > /dev/null 2>&1; then
        echo -e "${RED}❌ Docker Compose não encontrado. Instale o Docker Compose primeiro.${NC}"
        exit 1
    fi
    
    # Criar diretórios necessários
    mkdir -p logs data mysql/init nginx/ssl
    
    # Criar arquivo de configuração do Nginx
    if [ ! -f "nginx/nginx.conf" ]; then
        cat > nginx/nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    upstream plate_api {
        server plate-api:5000;
    }
    
    server {
        listen 80;
        server_name localhost;
        
        location / {
            proxy_pass http://plate_api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
EOF
        echo -e "${GREEN}✅ Configuração do Nginx criada${NC}"
    fi
    
    # Construir e iniciar serviços
    echo -e "${YELLOW}🔨 Construindo e iniciando serviços...${NC}"
    docker-compose up -d --build
    
    echo -e "${GREEN}✅ Deploy local concluído!${NC}"
    echo -e "${BLUE}🌐 API disponível em: http://localhost:5000${NC}"
    echo -e "${BLUE}🗄️ MySQL disponível em: localhost:3306${NC}"
    echo -e "${BLUE}📊 Status: docker-compose ps${NC}"
    echo -e "${BLUE}📋 Logs: docker-compose logs -f${NC}"
}

# Função para deploy em servidor
deploy_server() {
    echo -e "${GREEN}🖥️ Deploy em servidor headless...${NC}"
    
    # Verificar se o script de instalação existe
    if [ ! -f "install_server.sh" ]; then
        echo -e "${RED}❌ Script de instalação não encontrado${NC}"
        exit 1
    fi
    
    # Executar script de instalação
    echo -e "${YELLOW}🚀 Executando script de instalação...${NC}"
    ./install_server.sh
    
    echo -e "${GREEN}✅ Deploy em servidor concluído!${NC}"
}

# Função para deploy apenas com Docker
deploy_docker() {
    echo -e "${GREEN}🐳 Deploy apenas com Docker...${NC}"
    
    # Verificar se Docker está instalado
    if ! command -v docker > /dev/null 2>&1; then
        echo -e "${RED}❌ Docker não encontrado. Instale o Docker primeiro.${NC}"
        exit 1
    fi
    
    # Construir imagem
    echo -e "${YELLOW}🔨 Construindo imagem Docker...${NC}"
    docker build -t plate-api .
    
    # Criar rede se não existir
    docker network create plate-network 2>/dev/null || true
    
    # Executar container
    echo -e "${YELLOW}🚀 Iniciando container...${NC}"
    docker run -d \
        --name plate-api \
        --network plate-network \
        -p 5000:5000 \
        -e CHROME_HEADLESS=true \
        -e CHROME_NO_SANDBOX=true \
        -e CHROME_DISABLE_GPU=true \
        -e SCRAPER_METHOD=auto \
        plate-api
    
    echo -e "${GREEN}✅ Deploy com Docker concluído!${NC}"
    echo -e "${BLUE}🌐 API disponível em: http://localhost:5000${NC}"
    echo -e "${BLUE}📊 Status: docker ps${NC}"
    echo -e "${BLUE}📋 Logs: docker logs -f plate-api${NC}"
}

# Função principal
main() {
    case "${1:-help}" in
        "local")
            deploy_local
            ;;
        "server")
            deploy_server
            ;;
        "docker")
            deploy_docker
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# Executar função principal
main "$@"
