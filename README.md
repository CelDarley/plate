# �� Placa FIPE Scraper API

API REST para consulta de informações de veículos através de placas, com armazenamento em banco MySQL e fuso horário GMT-3 (Brasil).

## ✨ Funcionalidades

- **🔍 API REST**: Endpoint simples para consulta de placas
- **📊 Cache Inteligente**: Dados salvos no banco para consultas futuras
- **🌐 Scraping Automatizado**: Consulta automática quando placa não existe no banco
- **✅ Validação**: Verifica formato de placa (antigo e Mercosul)
- **📈 Histórico**: Rastreamento de todas as consultas realizadas
- **💾 Banco MySQL**: Armazenamento robusto com fuso horário GMT-3
- **🔧 Logs**: Sistema de logging para monitoramento

## 🚀 Tecnologias Utilizadas

- **Backend**: Flask (Python)
- **Banco de Dados**: MySQL com SQLAlchemy
- **Web Scraping**: Selenium WebDriver
- **Validação**: Regex para formatos de placa
- **Logging**: Sistema de logs estruturado
- **Fuso Horário**: GMT-3 (Horário de Brasília)

## 📋 Dados Coletados

Para cada placa, a API retorna:

| Campo | Descrição |
|-------|-----------|
| **ID** | Identificador único |
| **Placa** | Número da placa do veículo |
| **Marca** | Fabricante do veículo |
| **Genérico** | Código genérico do modelo |
| **Modelo** | Nome/modelo específico |
| **Importado** | Se é veículo importado |
| **Ano** | Ano de fabricação |
| **Ano Modelo** | Ano do modelo |
| **Cor** | Cor do veículo |
| **Cilindrada** | Capacidade do motor |
| **Combustível** | Tipo de combustível |
| **Chassi** | Número do chassi |
| **Motor** | Número do motor |
| **Passageiros** | Capacidade de passageiros |
| **UF** | Estado de registro |
| **Município** | Cidade de registro |
| **Status** | Status do processamento |
| **Data Scraping** | Data/hora da consulta |

## 🛠️ Instalação

### Pré-requisitos

- Python 3.8+
- MySQL 5.7+
- Chrome/Chromium browser
- Git

### 1. Clone o repositório

```bash
git clone https://github.com/CelDarley/plate.git
cd plate
```

### 2. Instale as dependências

```bash
pip install -r requirements.txt
```

### 3. Configure o banco MySQL

```sql
-- Conectar como root
mysql -u root -p

-- Criar banco e usuário
CREATE DATABASE plate;
CREATE USER 'plate'@'%' IDENTIFIED BY 'Plate()123';
GRANT ALL PRIVILEGES ON plate.* TO 'plate'@'%';
FLUSH PRIVILEGES;

-- Configurar fuso horário
SET GLOBAL time_zone = '-03:00';
SET time_zone = '-03:00';
```

### 4. Configure as variáveis de ambiente

```bash
cp config.example .env
# Edite o arquivo .env com suas configurações
```

### 5. Execute a migração (se necessário)

```bash
python3 migrate_to_mysql.py
```

### 6. Inicie a API

```bash
python3 app.py
```

A API estará disponível em: http://localhost:5000

## 📖 Como Usar

### 🔍 Endpoints Disponíveis

#### 1. **Informações da API**
```http
GET /
```
**Resposta:**
```json
{
  "api": "Placa FIPE Scraper API",
  "version": "1.0.0",
  "description": "API para consulta de dados de veículos por placa",
  "endpoints": {
    "/": "Informações da API",
    "/api/placa/<placa>": "Consulta dados de uma placa específica",
    "/api/placas": "Lista todas as placas consultadas",
    "/api/placa/<placa>/historico": "Histórico de consultas de uma placa"
  }
}
```

#### 2. **Consulta de Placa** (Principal)
```http
GET /api/placa/{placa}
```

**Exemplos:**
- `GET /api/placa/ABC1234` (formato antigo)
- `GET /api/placa/ABC1D23` (formato Mercosul)

**Resposta de Sucesso:**
```json
{
  "placa": "ABC1234",
  "dados": {
    "id": 1,
    "marca": "VOLKSWAGEN",
    "generico": "POLO",
    "modelo": "POLO CL AB",
    "importado": "Não",
    "ano": "2024",
    "ano_modelo": "2025",
    "cor": "CINZA",
    "cilindrada": "1000 cc",
    "combustivel": "Gasolina",
    "chassi": "*******12345",
    "motor": "*****67890",
    "passageiros": "5",
    "uf": "MG",
    "municipio": "Belo Horizonte",
    "status": "pendente",
    "data_scraping": "2025-08-21T10:30:00"
  },
  "fonte": "scraping_novo",
  "timestamp": "2025-08-21T10:30:00"
}
```

**Resposta de Erro (formato inválido):**
```json
{
  "erro": "Formato de placa inválido",
  "placa": "123ABC",
  "formatos_aceitos": ["ABC1234", "ABC1D23"],
  "exemplo": "ABC1234 ou ABC1D23"
}
```

#### 3. **Listar Todas as Placas**
```http
GET /api/placas?page=1&per_page=20&search=termo
```

**Parâmetros:**
- `page` (opcional): Número da página (padrão: 1)
- `per_page` (opcional): Itens por página (padrão: 20, máximo: 100)
- `search` (opcional): Termo de busca

**Resposta:**
```json
{
  "placas": [
    {
      "id": 1,
      "placa": "ABC1234",
      "marca": "VOLKSWAGEN",
      "modelo": "POLO CL AB",
      "ano": "2024",
      "uf": "MG",
      "municipio": "Belo Horizonte",
      "data_scraping": "2025-08-21T10:30:00"
    }
  ],
  "paginacao": {
    "pagina_atual": 1,
    "total_paginas": 1,
    "total_placas": 1,
    "por_pagina": 20
  },
  "timestamp": "2025-08-21T10:30:00"
}
```

#### 4. **Histórico de uma Placa**
```http
GET /api/placa/{placa}/historico
```

**Resposta:**
```json
{
  "placa": "ABC1234",
  "historico": {
    "id": 1,
    "marca": "VOLKSWAGEN",
    "generico": "POLO",
    "modelo": "POLO CL AB",
    "importado": "Não",
    "ano": "2024",
    "ano_modelo": "2025",
    "cor": "CINZA",
    "cilindrada": "1000 cc",
    "combustivel": "Gasolina",
    "chassi": "*******12345",
    "motor": "*****67890",
    "passageiros": "5",
    "uf": "MG",
    "municipio": "Belo Horizonte",
    "status": "pendente",
    "data_scraping": "2025-08-21T10:30:00"
  },
  "timestamp": "2025-08-21T10:30:00"
}
```

### 📱 Exemplos de Uso

#### cURL
```bash
# Consultar uma placa
curl "http://localhost:5000/api/placa/ABC1234"

# Listar placas
curl "http://localhost:5000/api/placas?page=1&per_page=10"

# Histórico de uma placa
curl "http://localhost:5000/api/placa/ABC1234/historico"
```

#### Python
```python
import requests

# Consultar uma placa
response = requests.get("http://localhost:5000/api/placa/ABC1234")
if response.status_code == 200:
    dados = response.json()
    print(f"Marca: {dados['dados']['marca']}")
    print(f"Modelo: {dados['dados']['modelo']}")
```

#### JavaScript
```javascript
// Consultar uma placa
fetch('http://localhost:5000/api/placa/ABC1234')
  .then(response => response.json())
  .then(data => {
    console.log(`Marca: ${data.dados.marca}`);
    console.log(`Modelo: ${data.dados.modelo}`);
  });
```

### 🔧 Formatos de Placa Aceitos

1. **Formato Antigo**: `ABC1234` (3 letras + 4 números)
2. **Formato Mercosul**: `ABC1D23` (3 letras + 1 número + 1 letra + 2 números)

## 🔧 Configuração

### Variáveis de Ambiente (.env)

```bash
SECRET_KEY=sua-chave-secreta-aqui
MYSQL_HOST=localhost
MYSQL_USER=plate
MYSQL_PASSWORD=Plate()123
MYSQL_DATABASE=plate
```

### Configuração do Banco

```python
# app.py
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://plate:Plate()123@localhost/plate?charset=utf8mb4'
```

## 📊 Estrutura do Projeto

```
plate/
├── app.py                 # API principal Flask
├── scraper.py            # Módulo de scraping
├── migrate_to_mysql.py   # Script de migração SQLite → MySQL
├── test_api.py           # Script de teste da API
├── requirements.txt      # Dependências Python
├── .gitignore          # Arquivos ignorados pelo Git
└── README.md           # Este arquivo
```

## 🧪 Testando a API

Execute o script de teste para verificar se tudo está funcionando:

```bash
python3 test_api.py
```

Este script testa:
- ✅ Endpoint raiz
- ✅ Consulta de placas válidas
- ✅ Listagem de placas
- ✅ Histórico de placas
- ✅ Validação de placas inválidas

## 🚨 Troubleshooting

### Erro de Conexão MySQL
```bash
# Verificar se o MySQL está rodando
sudo systemctl status mysql

# Verificar permissões do usuário
mysql -u root -p -e "SHOW GRANTS FOR 'plate'@'%';"
```

### Erro de ChromeDriver
```bash
# Instalar ChromeDriver automaticamente
chmod +x install_chromedriver.sh
./install_chromedriver.sh
```

### Fuso Horário Incorreto
```sql
-- Verificar configuração atual
SELECT @@global.time_zone, @@session.time_zone;

-- Configurar para GMT-3
SET GLOBAL time_zone = '-03:00';
SET time_zone = '-03:00';
```

## 🔒 Segurança e Boas Práticas

- **Rate Limiting**: Considere implementar limitação de requisições
- **Autenticação**: Para uso em produção, adicione autenticação
- **HTTPS**: Use HTTPS em ambiente de produção
- **Validação**: Sempre valide o formato da placa antes de processar
- **Logs**: Monitore os logs para detectar problemas

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 👨‍💻 Autor

**CelDarley** - [GitHub](https://github.com/CelDarley)

## 🙏 Agradecimentos

- Flask Framework
- Selenium WebDriver
- MySQL Community Edition
- Comunidade Python

---

⭐ **Se esta API foi útil para você, considere dar uma estrela no repositório!**
