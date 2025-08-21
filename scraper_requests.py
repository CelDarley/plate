#!/usr/bin/env python3
"""
Scraper para placas usando Requests + BeautifulSoup (sem navegador)
Muito mais rápido e eficiente que Selenium
"""

import requests
from bs4 import BeautifulSoup
import time
import random
from typing import Dict, Optional, List
import re

class PlacaFipeScraperRequests:
    """Scraper de placas usando requisições HTTP diretas"""
    
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://placafipe.com"
        self.search_url = "https://placafipe.com/consulta"
        
        # Headers mais realistas para simular um navegador real
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
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
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"'
        }
        
        # Configurar session
        self.session.headers.update(self.headers)
        
        # Adicionar referer e outras configurações
        self.session.verify = True
        self.session.allow_redirects = True
        
    def _get_random_delay(self) -> float:
        """Retorna um delay aleatório entre 1-3 segundos"""
        return random.uniform(1, 3)
    
    def _extract_data_from_html(self, html_content: str) -> Dict[str, str]:
        """Extrai dados do HTML usando BeautifulSoup"""
        soup = BeautifulSoup(html_content, 'html.parser')
        dados = {}
        
        try:
            # Procurar pela tabela de resultados
            tabela = soup.find('table', class_='table') or soup.find('table')
            
            if not tabela:
                print("   ⚠️  Tabela de resultados não encontrada")
                return {}
            
            # Extrair linhas da tabela
            linhas = tabela.find_all('tr')
            print(f"   📊 Encontradas {len(linhas)} linhas na tabela")
            
            for i, linha in enumerate(linhas):
                # Procurar por células com label e valor
                celulas = linha.find_all(['td', 'th'])
                if len(celulas) >= 2:
                    # Tentar extrair label e valor
                    label = celulas[0].get_text(strip=True)
                    valor = celulas[1].get_text(strip=True)
                    
                    if label and valor:
                        # Mapear labels para campos do banco
                        campo = self._mapear_campo(label)
                        if campo:
                            dados[campo] = valor
                            print(f"   📝 {campo}: {valor}")
            
            print(f"   ✅ Dados extraídos: {len(dados)} campos")
            return dados
            
        except Exception as e:
            print(f"   ❌ Erro ao extrair dados: {str(e)}")
            return {}
    
    def _mapear_campo(self, label: str) -> Optional[str]:
        """Mapeia labels da tabela para campos do banco"""
        label_lower = label.lower()
        
        mapeamento = {
            'marca': 'marca',
            'marcaplacas mercosul': 'marca',
            'genérico': 'generico',
            'modelo': 'modelo',
            'importado': 'importado',
            'ano': 'ano',
            'ano modelo': 'ano_modelo',
            'cor': 'cor',
            'cilindrada': 'cilindrada',
            'combustível': 'combustivel',
            'chassi': 'chassi',
            'motor': 'motor',
            'passageiros': 'passageiros',
            'uf': 'uf',
            'município': 'municipio'
        }
        
        for key, value in mapeamento.items():
            if key in label_lower:
                return value
        
        return None
    
    def scraping_placa(self, placa: str) -> Optional[Dict[str, str]]:
        """Faz scraping de uma placa específica"""
        print(f"   🌐 Iniciando scraping para placa: {placa}")
        
        try:
            # Primeira requisição para obter cookies e simular navegação
            print("   🔍 Obtendo página inicial...")
            response = self.session.get(self.base_url, timeout=30)
            print(f"   📊 Status da página inicial: {response.status_code}")
            
            if response.status_code != 200:
                print(f"   ⚠️  Página inicial retornou status {response.status_code}")
                print(f"   📄 Conteúdo: {response.text[:200]}...")
                return None
            
            # Aguardar um pouco para simular comportamento humano
            time.sleep(self._get_random_delay())
            
            # Tentar diferentes URLs de consulta
            urls_consulta = [
                f"{self.base_url}/consulta",
                f"{self.base_url}/buscar",
                f"{self.base_url}/",
                f"{self.base_url}/index.php"
            ]
            
            dados = None
            for url in urls_consulta:
                try:
                    print(f"   🔍 Tentando URL: {url}")
                    
                    # Preparar dados para a consulta
                    data = {
                        'placa': placa,
                        'submit': 'Consultar',
                        'buscar': 'Consultar',
                        'search': placa
                    }
                    
                    # Fazer a consulta
                    print(f"   🔍 Consultando placa: {placa}")
                    response = self.session.post(
                        url,
                        data=data,
                        timeout=30,
                        allow_redirects=True
                    )
                    
                    print(f"   📊 Status da consulta: {response.status_code}")
                    print(f"   📄 Tamanho da resposta: {len(response.text)} bytes")
                    
                    if response.status_code == 200:
                        # Verificar se a consulta foi bem-sucedida
                        if 'erro' in response.text.lower() or 'não encontrada' in response.text.lower():
                            print(f"   ⚠️  Placa {placa} não encontrada ou erro na consulta")
                            continue
                        
                        # Extrair dados do HTML retornado
                        dados = self._extract_data_from_html(response.text)
                        
                        if dados:
                            print(f"   ✅ Dados extraídos com sucesso para {placa}")
                            break
                        else:
                            print(f"   ⚠️  Nenhum dado extraído da URL {url}")
                    else:
                        print(f"   ⚠️  URL {url} retornou status {response.status_code}")
                        
                except Exception as e:
                    print(f"   ⚠️  Erro ao tentar URL {url}: {str(e)}")
                    continue
            
            return dados
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Erro de requisição para {placa}: {str(e)}")
            return None
        except Exception as e:
            print(f"   ❌ Erro geral para {placa}: {str(e)}")
            return None
    
    def scraping_multiplas_placas(self, placas: List[str], delay_entre_placas: float = 2.0) -> List[Dict[str, str]]:
        """Faz scraping de múltiplas placas com delay entre elas"""
        resultados = []
        
        for i, placa in enumerate(placas):
            print(f"\n🚗 Processando placa {i+1}/{len(placas)}: {placa}")
            
            dados = self.scraping_placa(placa)
            if dados:
                dados['placa'] = placa
                resultados.append(dados)
            
            # Delay entre placas (exceto na última)
            if i < len(placas) - 1:
                print(f"   ⏰ Aguardando {delay_entre_placas} segundos...")
                time.sleep(delay_entre_placas)
        
        return resultados
    
    def close(self):
        """Fecha a sessão"""
        self.session.close()

# Função de teste
def testar_scraper():
    """Função para testar o scraper"""
    scraper = PlacaFipeScraperRequests()
    
    try:
        # Testar com uma placa
        placa_teste = "ABC1234"
        print(f"🧪 Testando scraper com placa: {placa_teste}")
        
        dados = scraper.scraping_placa(placa_teste)
        
        if dados:
            print(f"✅ Sucesso! Dados obtidos: {dados}")
        else:
            print("❌ Falha ao obter dados")
            
    except Exception as e:
        print(f"❌ Erro no teste: {str(e)}")
    finally:
        scraper.close()

if __name__ == "__main__":
    testar_scraper()
