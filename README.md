# 🚗 Placa FIPE Scraper

Sistema automatizado de scraping para consulta de informações de veículos através de placas, com interface web moderna e banco de dados MySQL.

## ✨ Funcionalidades

- **🔍 Scraping Automatizado**: Consulta automática de dados de veículos por placa
- **🌐 Interface Web**: Dashboard moderno com Bootstrap 5 e Font Awesome
- **📊 Gestão de Dados**: Visualização e gerenciamento de todas as placas processadas
- **👁️ Modal de Detalhes**: Visualização completa de todos os dados de cada veículo
- **⏱️ Controle de Intervalos**: Sistema inteligente de pausas entre consultas
- **📈 Histórico**: Rastreamento completo de todas as operações de scraping
- **🔧 Multi-threading**: Processamento em background sem bloquear a interface
- **💾 Banco MySQL**: Armazenamento robusto com fuso horário GMT-3 (Brasil)

## 🚀 Tecnologias Utilizadas

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Banco de Dados**: MySQL com SQLAlchemy
- **Web Scraping**: 
  - **Selenium WebDriver** (com navegador)
  - **Requests + BeautifulSoup** (sem navegador - mais rápido)
  - **Sistema Híbrido** (alterna automaticamente)
- **Interface**: Font Awesome Icons
- **Fuso Horário**: GMT-3 (Horário de Brasília)

## 🔧 Métodos de Scraping

### 1. **Requests + BeautifulSoup** ⚡ (Recomendado)
- **Vantagens**: Muito mais rápido, menor uso de memória, sem dependência do Chrome
- **Desvantagens**: Pode não funcionar em sites com JavaScript complexo
- **Performance**: 3-5x mais rápido que Selenium

### 2. **Selenium WebDriver** 🌐
- **Vantagens**: Funciona com JavaScript, mais robusto
- **Desvantagens**: Mais lento, maior uso de memória, depende do Chrome
- **Performance**: Mais lento, mas mais confiável

### 3. **Scraper Alternativo** 🔄
- **Vantagens**: Tenta múltiplos sites, fallback automático, sem dependências externas
- **Desvantagens**: Dados podem ser limitados
- **Performance**: Rápido e confiável

### 4. **Sistema Híbrido** 🚀
- **Vantagens**: Melhor dos três mundos, fallback automático inteligente
- **Como funciona**: Tenta Requests → Alternativo → Selenium (em ordem de preferência)
- **Performance**: Otimizado automaticamente

## 📋 Dados Coletados

Para cada placa, o sistema coleta:

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

### 6. Inicie a aplicação

```bash
python3 app.py
```

A aplicação estará disponível em: http://localhost:5000

## 🔧 Configuração dos Métodos de Scraping

### Usar Apenas Requests (Mais Rápido)

```python
# Em app.py, altere a linha:
from scraper_requests import PlacaFipeScraperRequests

# E na função executar_scraping:
scraper = PlacaFipeScraperRequests()
```

### Usar Apenas Selenium (Mais Robusto)

```python
# Em app.py, altere a linha:
from scraper import PlacaFipeScraper

# E na função executar_scraping:
scraper = PlacaFipeScraper()
```

### Usar Apenas Alternativo (Múltiplos Sites)

```python
# Em app.py, altere a linha:
from scraper_alternative import PlacaFipeScraperAlternative

# E na função executar_scraping:
scraper = PlacaFipeScraperAlternative()
```

### Usar Sistema Híbrido (Recomendado)

```python
# Em app.py, altere a linha:
from scraper_hybrid import PlacaFipeScraperHybrid

# E na função executar_scraping:
scraper = PlacaFipeScraperHybrid(preferencia="auto")  # ou "requests", "selenium", "alternative"
```

## 🧪 Testando Performance

Execute o benchmark para comparar os métodos:

```bash
python3 benchmark_scrapers.py
```

Este script testa todos os métodos disponíveis e mostra:
- Tempo de execução
- Taxa de sucesso
- Comparação de performance
- Ranking dos métodos

## 🧪 Resultados do Benchmark

### 📊 Comparação de Performance

| Método | Tempo Médio | Taxa de Sucesso | Vantagens | Desvantagens |
|--------|-------------|-----------------|-----------|--------------|
| **Requests + BeautifulSoup** | ~0.3s | 0% | Muito rápido | Bloqueado pelo site |
| **Selenium WebDriver** | ~12.7s | 100% | Dados completos | Lento, usa Chrome |
| **Alternativo** | ~18.4s | 100% | Sem dependências | Dados limitados |
| **Híbrido (Auto)** | ~22.5s | 100% | Melhor dos mundos | Overhead de fallback |

### 🏆 Recomendações

1. **Para Produção**: Use o **Sistema Híbrido** com `preferencia="auto"`
2. **Para Desenvolvimento**: Use **Selenium** para dados completos
3. **Para Performance**: Use **Alternativo** se não precisar de todos os dados
4. **Evite**: **Requests** puro (bloqueado pelo site)

### 🔧 Configuração Recomendada

```python
# Em app.py
from scraper_hybrid import PlacaFipeScraperHybrid

# Na função executar_scraping:
scraper = PlacaFipeScraperHybrid(preferencia="auto")
```

O sistema híbrido automaticamente:
- Tenta Requests primeiro (mais rápido)
- Se falhar, tenta Alternativo (sem dependências)
- Se falhar, usa Selenium (mais robusto)
- Garante 100% de taxa de sucesso

## 📖 Como Usar

### 1. Acesso ao Sistema

- **Página Inicial**: http://localhost:5000
- **Painel de Gestão**: http://localhost:5000/gestao

### 2. Iniciar Scraping

1. Acesse o painel de gestão
2. Digite as placas (uma por linha) no campo de texto
3. Clique em "Iniciar Scraping"
4. Acompanhe o progresso em tempo real

### 3. Visualizar Resultados

- **Tabela Principal**: Mostra placa, marca, modelo, ano, município, UF e data
- **Modal de Detalhes**: Clique no ícone 👁️ para ver todos os dados
- **Pesquisa**: Use o campo de busca para filtrar resultados
- **Paginação**: Navegue entre as páginas de resultados

### 4. Controles de Scraping

- **Intervalos Inteligentes**: 30s → 45s → 65s → 48s (repetindo)
- **Parada Segura**: Pode interromper o processo a qualquer momento
- **Status em Tempo Real**: Monitoramento contínuo do progresso

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
├── app.py                    # Aplicação principal Flask
├── scraper.py               # Módulo de scraping com Selenium
├── scraper_requests.py      # Módulo de scraping sem navegador (Requests)
├── scraper_alternative.py   # Scraper alternativo (múltiplos sites)
├── scraper_hybrid.py        # Sistema híbrido (Selenium + Requests + Alternativo)
├── benchmark_scrapers.py    # Script de comparação de performance
├── migrate_to_mysql.py      # Script de migração SQLite → MySQL
├── requirements.txt         # Dependências Python
├── templates/               # Templates HTML
│   ├── index.html          # Página inicial
│   └── gestao.html         # Painel de gestão
├── instance/               # Banco SQLite (local)
├── .gitignore             # Arquivos ignorados pelo Git
└── README.md              # Este arquivo
```

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
- Bootstrap 5
- Font Awesome
- Selenium WebDriver
- MySQL Community Edition

---

⭐ **Se este projeto foi útil para você, considere dar uma estrela no repositório!**
