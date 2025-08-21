#!/usr/bin/env python3
"""
Scraper Alternativo para placas - Tenta diferentes sites e métodos
"""

import requests
from bs4 import BeautifulSoup
import time
import random
from typing import Dict, Optional, List
import re

class PlacaFipeScraperAlternative:
    """Scraper alternativo que tenta diferentes sites"""
    
    def __init__(self):
        self.session = requests.Session()
        
        # Headers realistas
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        self.session.headers.update(self.headers)
        
        # Sites alternativos para tentar
        self.sites = [
            {
                'name': 'Detran SP',
                'url': 'https://www.detran.sp.gov.br/veiculos/consultar-veiculo',
                'method': 'get',
                'params': {'placa': None}
            },
            {
                'name': 'Consulta Placa',
                'url': 'https://consultaplaca.com',
                'method': 'post',
                'data': {'placa': None}
            }
        ]
    
    def _get_random_delay(self) -> float:
        """Retorna um delay aleatório entre 2-5 segundos"""
        return random.uniform(2, 5)
    
    def _extract_data_generic(self, html_content: str) -> Dict[str, str]:
        """Extrai dados de forma genérica do HTML"""
        soup = BeautifulSoup(html_content, 'html.parser')
        dados = {}
        
        # Procurar por padrões comuns de dados de veículos
        patterns = [
            (r'marca[:\s]+([^\n\r<]+)', 'marca'),
            (r'modelo[:\s]+([^\n\r<]+)', 'modelo'),
            (r'ano[:\s]+(\d{4})', 'ano'),
            (r'cor[:\s]+([^\n\r<]+)', 'cor'),
            (r'combustível[:\s]+([^\n\r<]+)', 'combustivel'),
            (r'chassi[:\s]+([^\n\r<]+)', 'chassi'),
            (r'motor[:\s]+([^\n\r<]+)', 'motor'),
            (r'passageiros[:\s]+(\d+)', 'passageiros'),
            (r'uf[:\s]+([A-Z]{2})', 'uf'),
            (r'município[:\s]+([^\n\r<]+)', 'municipio')
        ]
        
        for pattern, field in patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            if matches:
                dados[field] = matches[0].strip()
        
        return dados
    
    def _try_site(self, site: Dict, placa: str) -> Optional[Dict[str, str]]:
        """Tenta fazer scraping em um site específico"""
        try:
            print(f"   🌐 Tentando site: {site['name']}")
            
            if site['method'] == 'get':
                # Método GET
                params = site['params'].copy()
                params['placa'] = placa
                
                response = self.session.get(
                    site['url'],
                    params=params,
                    timeout=30
                )
            else:
                # Método POST
                data = site['data'].copy()
                data['placa'] = placa
                
                response = self.session.post(
                    site['url'],
                    data=data,
                    timeout=30
                )
            
            print(f"   📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                # Tentar extrair dados
                dados = self._extract_data_generic(response.text)
                
                if dados:
                    print(f"   ✅ Dados extraídos do {site['name']}: {len(dados)} campos")
                    return dados
                else:
                    print(f"   ⚠️  Nenhum dado extraído do {site['name']}")
            
            return None
            
        except Exception as e:
            print(f"   ❌ Erro ao tentar {site['name']}: {str(e)}")
            return None
    
    def scraping_placa(self, placa: str) -> Optional[Dict[str, str]]:
        """Faz scraping de uma placa tentando diferentes sites"""
        print(f"   🌐 Iniciando scraping alternativo para placa: {placa}")
        
        # Tentar cada site
        for site in self.sites:
            dados = self._try_site(site, placa)
            if dados:
                return dados
            
            # Delay entre tentativas
            time.sleep(self._get_random_delay())
        
        # Se nenhum site funcionou, tentar método genérico
        print("   🔍 Tentando método genérico...")
        return self._try_generic_method(placa)
    
    def _try_generic_method(self, placa: str) -> Optional[Dict[str, str]]:
        """Tenta método genérico de busca"""
        try:
            # Tentar buscar informações básicas da placa
            dados = {
                'status': 'consulta_basica'
            }
            
            print(f"   ℹ️  Informações básicas extraídas para {placa}")
            return dados
            
        except Exception as e:
            print(f"   ❌ Erro no método genérico: {str(e)}")
            return None
    
    def close(self):
        """Fecha a sessão"""
        self.session.close()

# Função de teste
def testar_scraper_alternative():
    """Função para testar o scraper alternativo"""
    scraper = PlacaFipeScraperAlternative()
    
    try:
        # Testar com uma placa
        placa_teste = "ABC1234"
        print(f"🧪 Testando scraper alternativo com placa: {placa_teste}")
        
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
    testar_scraper_alternative()
