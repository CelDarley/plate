import requests
from bs4 import BeautifulSoup
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

class PlacaFipeScraper:
    def __init__(self):
        self.base_url = "https://placafipe.com/"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def scraping_placa(self, placa):
        """
        Faz o scraping de uma placa específica
        """
        print(f"      🌐 Iniciando scraping para placa: {placa}")
        
        try:
            # Usar Selenium para melhor compatibilidade
            print(f"      🔧 Tentando com Selenium...")
            dados = self._scraping_selenium(placa)
            if dados:
                print(f"      ✅ Selenium funcionou para {placa}")
                return dados
                
            # Fallback para requests se Selenium falhar
            print(f"      🔄 Selenium falhou, tentando com requests...")
            dados = self._scraping_requests(placa)
            if dados:
                print(f"      ✅ Requests funcionou para {placa}")
                return dados
            else:
                print(f"      ❌ Ambos os métodos falharam para {placa}")
                return None
                
        except Exception as e:
            print(f"      ❌ Erro no scraping da placa {placa}: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def _scraping_selenium(self, placa):
        """
        Scraping usando Selenium
        """
        driver = None
        try:
            print(f"        🚗 Configurando Chrome...")
            
            # Configurar Chrome
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            print(f"        🔧 Instalando ChromeDriver...")
            try:
                service = Service(ChromeDriverManager().install())
                print(f"        ✅ ChromeDriver instalado")
            except Exception as e:
                print(f"        ❌ Erro ao instalar ChromeDriver: {e}")
                print(f"        🔄 Tentando método alternativo...")
                # Tentar usar chromedriver do sistema
                import subprocess
                try:
                    result = subprocess.run(['which', 'chromedriver'], capture_output=True, text=True)
                    if result.returncode == 0:
                        chromedriver_path = result.stdout.strip()
                        print(f"        📍 ChromeDriver encontrado em: {chromedriver_path}")
                        service = Service(chromedriver_path)
                    else:
                        print(f"        ❌ ChromeDriver não encontrado no sistema")
                        return None
                except Exception as e2:
                    print(f"        ❌ Erro ao procurar ChromeDriver: {e2}")
                    return None
            
            print(f"        🚀 Iniciando Chrome...")
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Executar script para evitar detecção
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            print(f"        🌐 Acessando site...")
            driver.get(self.base_url)
            
            # Aguardar carregamento da página
            wait = WebDriverWait(driver, 15)
            
            print(f"        🔍 Procurando campo de placa...")
            # Encontrar campo de placa
            campo_placa = wait.until(
                EC.presence_of_element_located((By.ID, "sPlaca"))
            )
            
            print(f"        ✏️  Inserindo placa: {placa}")
            # Limpar e inserir placa
            campo_placa.clear()
            campo_placa.send_keys(placa)
            
            print(f"        🔘 Procurando botão de pesquisa...")
            # Encontrar e clicar no botão de pesquisa
            botao_pesquisa = driver.find_element(By.XPATH, "//button[@type='submit']")
            botao_pesquisa.click()
            
            print(f"        ⏳ Aguardando resultados...")
            # Aguardar carregamento dos resultados
            time.sleep(5)
            
            # Verificar se há resultados
            try:
                print(f"        📊 Procurando tabela de resultados...")
                tabela_resultado = wait.until(
                    EC.presence_of_element_located((By.CLASS_NAME, "fipeTablePriceDetail"))
                )
                
                print(f"        ✅ Tabela encontrada, extraindo dados...")
                # Extrair dados da tabela
                dados = self._extrair_dados_tabela(tabela_resultado)
                return dados
                
            except Exception as e:
                print(f"        ⚠️  Nenhum resultado encontrado para a placa {placa}: {e}")
                return None
                
        except Exception as e:
            print(f"        ❌ Erro no Selenium para placa {placa}: {str(e)}")
            return None
            
        finally:
            if driver:
                try:
                    driver.quit()
                    print(f"        🚪 Chrome fechado")
                except:
                    pass
    
    def _scraping_requests(self, placa):
        """
        Scraping usando requests (fallback)
        """
        try:
            print(f"        🌐 Tentando com requests...")
            
            # Configurar headers mais realistas
            headers = {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0',
                'Referer': 'https://www.google.com/'
            }
            
            # Primeiro, acessar a página inicial para obter cookies
            print(f"        🍪 Obtendo cookies da página inicial...")
            session = requests.Session()
            session.headers.update(headers)
            
            # Tentar acessar com diferentes URLs
            urls_teste = [
                self.base_url,
                'https://www.placafipe.com/',
                'https://placafipe.com.br/'
            ]
            
            response_inicial = None
            for url in urls_teste:
                try:
                    print(f"        🔗 Tentando URL: {url}")
                    response_inicial = session.get(url, timeout=30)
                    if response_inicial.status_code == 200:
                        print(f"        ✅ URL funcionou: {url}")
                        break
                    else:
                        print(f"        ⚠️  URL retornou {response_inicial.status_code}: {url}")
                except Exception as e:
                    print(f"        ❌ Erro ao acessar {url}: {e}")
                    continue
            
            if not response_inicial or response_inicial.status_code != 200:
                print(f"        ❌ Nenhuma URL funcionou")
                return None
            
            print(f"        ✅ Página inicial acessada, cookies obtidos")
            print(f"        📊 Tamanho da resposta: {len(response_inicial.content)} bytes")
            
            # Aguardar um pouco para simular comportamento humano
            time.sleep(3)
            
            # Fazer POST para o formulário
            data = {
                'sPlaca': placa
            }
            
            print(f"        📤 Enviando requisição POST para placa {placa}...")
            response = session.post(self.base_url, data=data, headers=headers, timeout=30)
            
            print(f"        📥 Resposta recebida: {response.status_code}")
            print(f"        📊 Tamanho da resposta: {len(response.content)} bytes")
            
            if response.status_code == 403:
                print(f"        🚫 Acesso bloqueado (403) - site pode estar detectando automação")
                print(f"        📄 Headers da resposta:")
                for key, value in response.headers.items():
                    print(f"           {key}: {value}")
                return None
            elif response.status_code != 200:
                print(f"        ❌ Erro HTTP: {response.status_code}")
                print(f"        📄 Conteúdo da resposta: {response.text[:500]}...")
                return None
            
            # Parsear HTML
            print(f"        🔍 Parseando HTML...")
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Procurar pela tabela de resultados
            tabela = soup.find('table', class_='fipeTablePriceDetail')
            
            if tabela:
                print(f"        ✅ Tabela encontrada no HTML")
                return self._extrair_dados_tabela(tabela)
            else:
                print(f"        ⚠️  Tabela não encontrada no HTML")
                # Salvar HTML para debug
                debug_file = f"debug_{placa}.html"
                with open(debug_file, "w", encoding="utf-8") as f:
                    f.write(response.text)
                print(f"        📄 HTML salvo em {debug_file} para análise")
                
                # Procurar por outras estruturas que possam conter os dados
                print(f"        🔍 Procurando por outras estruturas...")
                todas_tabelas = soup.find_all('table')
                print(f"        📊 Total de tabelas encontradas: {len(todas_tabelas)}")
                
                for i, tab in enumerate(todas_tabelas):
                    print(f"        📋 Tabela {i+1}: classes='{tab.get('class', [])}'")
                
                return None
                
        except Exception as e:
            print(f"        ❌ Erro no requests para placa {placa}: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def _extrair_dados_tabela(self, tabela):
        """
        Extrai os dados da tabela HTML
        """
        dados = {}
        
        try:
            print(f"        🔍 Extraindo dados da tabela...")
            
            # Se for um WebElement do Selenium, converter para HTML
            if hasattr(tabela, 'get_attribute'):
                html_content = tabela.get_attribute('outerHTML')
                print(f"        📄 Convertendo WebElement para HTML...")
            else:
                html_content = str(tabela)
                print(f"        📄 Usando HTML diretamente...")
            
            # Parsear HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            print(f"        🔍 HTML parseado, procurando linhas...")
            
            # Encontrar todas as linhas da tabela
            linhas = soup.find_all('tr')
            print(f"        📊 Encontradas {len(linhas)} linhas na tabela")
            
            for i, linha in enumerate(linhas):
                colunas = linha.find_all('td')
                if len(colunas) >= 2:
                    chave = colunas[0].get_text(strip=True).replace(':', '')
                    valor = colunas[1].get_text(strip=True)
                    
                    print(f"        📝 Linha {i+1}: {chave} = {valor}")
                    
                    # Mapear chaves para os campos do modelo
                    if chave == 'Marca':
                        dados['marca'] = valor
                    elif chave == 'Genérico':
                        dados['generico'] = valor
                    elif chave == 'Modelo':
                        dados['modelo'] = valor
                    elif chave == 'Importado':
                        dados['importado'] = valor
                    elif chave == 'Ano':
                        dados['ano'] = valor
                    elif chave == 'Ano Modelo':
                        dados['ano_modelo'] = valor
                    elif chave == 'Cor':
                        dados['cor'] = valor
                    elif chave == 'Cilindrada':
                        dados['cilindrada'] = valor
                    elif chave == 'Combustível':
                        dados['combustivel'] = valor
                    elif chave == 'Chassi':
                        dados['chassi'] = valor
                    elif chave == 'Motor':
                        dados['motor'] = valor
                    elif chave == 'Passageiros':
                        dados['passageiros'] = valor
                    elif chave == 'UF':
                        dados['uf'] = valor
                    elif chave == 'Município':
                        dados['municipio'] = valor
            
            print(f"        ✅ Dados extraídos: {len(dados)} campos")
            return dados
            
        except Exception as e:
            print(f"        ❌ Erro ao extrair dados da tabela: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def validar_placa(self, placa):
        """
        Valida o formato da placa
        """
        import re
        
        # Padrões de placas brasileiras
        padrao_mercosul = r'^[A-Za-z]{3}[0-9][A-Za-z][0-9]{2}$'
        padrao_antigo = r'^[A-Za-z]{3}[0-9]{4}$'
        
        if re.match(padrao_mercosul, placa) or re.match(padrao_antigo, placa):
            return True
        return False
    
    def gerar_placas_teste(self, quantidade=10):
        """
        Gera placas de teste para desenvolvimento
        """
        placas = []
        letras = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        numeros = '0123456789'
        
        for _ in range(quantidade):
            # Gerar placa no formato antigo (ABC1234)
            placa = ''.join(random.choices(letras, k=3)) + ''.join(random.choices(numeros, k=4))
            placas.append(placa)
        
        return placas
