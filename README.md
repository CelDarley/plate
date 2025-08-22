# 🚗 Placa FIPE Scraper API

API REST para consulta de dados de veículos por placa, com suporte a servidores headless (sem interface gráfica).

## 🌟 Características

- **API REST** completa para consulta de placas
- **Suporte a servidor headless** com Chrome em modo headless
- **Fallback automático** para scraper baseado em requests
- **Banco MySQL** para persistência de dados
- **Deploy automatizado** com Docker e scripts de instalação
- **Timezone GMT-3** configurado automaticamente

## 🚀 Deploy Rápido

### Opção 1: Deploy Local com Docker Compose
```bash
# Clonar repositório
git clone https://github.com/CelDarley/plate.git
cd plate

# Executar deploy local
./deploy.sh local
```

### Opção 2: Deploy em Servidor Headless
```bash
# Clonar repositório
git clone https://github.com/CelDarley/plate.git
cd plate

# Executar deploy em servidor
./deploy.sh server
```

### Opção 3: Deploy Apenas com Docker
```bash
# Clonar repositório
git clone https://github.com/CelDarley/plate.git
cd plate

# Executar deploy Docker
./deploy.sh docker
```

## 📋 Pré-requisitos

### Para Deploy Local
- Docker
- Docker Compose

### Para Deploy em Servidor
- Ubuntu/Debian (recomendado)
- Python 3.8+
- MySQL 8.0+
- Acesso sudo

## 🔧 Configuração

### Variáveis de Ambiente

Copie o arquivo de exemplo e configure:
```bash
cp config.env.example .env
```

**Configurações principais:**
```env
# Método de scraping
SCRAPER_METHOD=auto          # 'selenium', 'requests', 'auto'

# Chrome headless para servidor
CHROME_HEADLESS=true
CHROME_NO_SANDBOX=true
CHROME_DISABLE_GPU=true

# Banco de dados
DB_HOST=localhost
DB_USER=plate
DB_PASSWORD=Plate()123
DB_NAME=plate
```

### Configurações de Scraping

- **`SCRAPER_METHOD=selenium`**: Força uso do Selenium (Chrome)
- **`SCRAPER_METHOD=requests`**: Força uso do scraper baseado em requests
- **`SCRAPER_METHOD=auto`**: Tenta Selenium primeiro, fallback para requests

## 🐳 Deploy com Docker

### Docker Compose (Recomendado)
```bash
# Construir e iniciar todos os serviços
docker-compose up -d --build

# Ver status
docker-compose ps

# Ver logs
docker-compose logs -f plate-api
```

### Docker Apenas
```bash
# Construir imagem
docker build -t plate-api .

# Executar container
docker run -d \
  --name plate-api \
  -p 5000:5000 \
  -e CHROME_HEADLESS=true \
  plate-api
```

## 🖥️ Deploy em Servidor Headless

### Instalação Automática
```bash
# Executar script de instalação
./install_server.sh
```

O script irá:
- ✅ Instalar Python, MySQL, Chrome e ChromeDriver
- ✅ Configurar Chrome para modo headless
- ✅ Criar ambiente virtual Python
- ✅ Instalar dependências
- ✅ Configurar serviço systemd
- ✅ Testar Chrome headless

### Instalação Manual

#### 1. Instalar Dependências
```bash
# Atualizar sistema
sudo apt update

# Instalar Python e pip
sudo apt install -y python3 python3-pip python3-venv

# Instalar MySQL
sudo apt install -y mysql-server mysql-client

# Instalar Chrome
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt update
sudo apt install -y google-chrome-stable

# Instalar ChromeDriver
CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | awk -F'.' '{print $1}')
CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION")
wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip"
unzip /tmp/chromedriver.zip -d /tmp/
sudo mv /tmp/chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver
```

#### 2. Configurar Banco MySQL
```sql
-- Conectar como root
mysql -u root -p

-- Criar banco e usuário
CREATE DATABASE plate CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'plate'@'%' IDENTIFIED BY 'Plate()123';
GRANT ALL PRIVILEGES ON plate.* TO 'plate'@'%';
FLUSH PRIVILEGES;
```

#### 3. Configurar Aplicação
```bash
# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp config.env.example .env
# Editar .env com suas configurações
```

#### 4. Configurar Serviço Systemd
```bash
# Criar arquivo de serviço
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

# Habilitar e iniciar serviço
sudo systemctl daemon-reload
sudo systemctl enable plate-api.service
sudo systemctl start plate-api.service
```

## 🔍 Endpoints da API

### Consulta de Placa
```http
GET /api/placa/{placa}
```

**Exemplo:**
```bash
curl http://localhost:5000/api/placa/ABC1234
```

**Resposta:**
```json
{
  "placa": "ABC1234",
  "dados": {
    "marca": "FIAT",
    "modelo": "ARGO DRIVE 1.0",
    "ano": "2021",
    "uf": "SP",
    "municipio": "São Paulo"
  },
  "fonte": "scraping_novo",
  "timestamp": "2025-08-21T10:30:00-03:00"
}
```

### Listar Todas as Placas
```http
GET /api/placas?page=1&per_page=20&search=termo
```

### Histórico de Placa
```http
GET /api/placa/{placa}/historico
```

## 🧪 Testando a API

### Script de Teste
```bash
# Executar testes
python test_api.py
```

### Teste Manual
```bash
# Testar endpoint raiz
curl http://localhost:5000/

# Testar consulta de placa
curl http://localhost:5000/api/placa/ABC1234

# Testar listagem
curl http://localhost:5000/api/placas?page=1&per_page=5
```

## 🔧 Solução de Problemas

### Chrome Headless não Funciona
```bash
# Verificar se Chrome está instalado
google-chrome --version

# Testar Chrome headless
google-chrome --headless --no-sandbox --disable-gpu --dump-dom https://www.google.com

# Verificar logs do serviço
sudo journalctl -u plate-api -f
```

### Problemas de Permissão
```bash
# Verificar permissões do ChromeDriver
ls -la /usr/local/bin/chromedriver

# Corrigir permissões se necessário
sudo chmod +x /usr/local/bin/chromedriver
```

### Problemas de Banco
```bash
# Verificar status do MySQL
sudo systemctl status mysql

# Conectar ao banco
mysql -u plate -p plate

# Verificar tabelas
SHOW TABLES;
```

## 📊 Monitoramento

### Logs da Aplicação
```bash
# Logs em tempo real
sudo journalctl -u plate-api -f

# Logs do Docker
docker-compose logs -f plate-api
```

### Status dos Serviços
```bash
# Status do serviço
sudo systemctl status plate-api

# Status dos containers
docker-compose ps
```

## 🔄 Atualizações

### Atualizar Código
```bash
# Puxar alterações
git pull origin main

# Reiniciar serviço
sudo systemctl restart plate-api

# Ou reiniciar containers
docker-compose restart plate-api
```

### Atualizar Dependências
```bash
# Ativar ambiente virtual
source venv/bin/activate

# Atualizar dependências
pip install -r requirements.txt --upgrade

# Reiniciar serviço
sudo systemctl restart plate-api
```

## 📁 Estrutura do Projeto

```
plate/
├── app.py                 # Aplicação principal Flask
├── scraper.py            # Scraper com Selenium
├── scraper_requests.py   # Scraper baseado em requests
├── requirements.txt      # Dependências Python
├── config.env.example    # Configurações de exemplo
├── install_server.sh     # Script de instalação para servidor
├── deploy.sh            # Script de deploy
├── Dockerfile           # Imagem Docker
├── docker-compose.yml   # Orquestração Docker
├── docker-entrypoint.sh # Script de entrada Docker
├── test_api.py          # Testes da API
└── README.md            # Este arquivo
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🆘 Suporte

Se encontrar problemas:

1. Verifique os logs: `sudo journalctl -u plate-api -f`
2. Teste o Chrome headless: `google-chrome --headless --no-sandbox --disable-gpu --dump-dom https://www.google.com`
3. Verifique as variáveis de ambiente no arquivo `.env`
4. Abra uma issue no GitHub

---

**🚀 API pronta para produção em servidor headless!**
