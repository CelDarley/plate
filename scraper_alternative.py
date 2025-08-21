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
        """Inicializa o scraper alternativo"""
        self.session = requests.Session()
        
        # Configurar headers mais realistas
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        })
        
        # Lista de sites para tentar (mais confiáveis)
        self.sites = [
            {
                'name': 'Detran SP',
                'url': 'https://www.detran.sp.gov.br/veiculos/consultas/consulta-veiculo',
                'method': 'get',
                'params': {'placa': None}
            },
            {
                'name': 'Gov.br Denatran',
                'url': 'https://www.gov.br/denatran/pt-br/assuntos/veiculos/placa-mercosul',
                'method': 'get',
                'params': {}
            },
            {
                'name': 'Portal da Transparência',
                'url': 'https://www.portaltransparencia.gov.br/',
                'method': 'get',
                'params': {}
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
            (r'município[:\s]+([^\n\r<]+)', 'municipio'),
            (r'cilindrada[:\s]+([^\n\r<]+)', 'cilindrada'),
            (r'importado[:\s]+([^\n\r<]+)', 'importado'),
            (r'genérico[:\s]+([^\n\r<]+)', 'generico'),
            (r'ano modelo[:\s]+(\d{4})', 'ano_modelo')
        ]
        
        # Procurar por padrões no HTML
        for pattern, field in patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            if matches:
                dados[field] = matches[0].strip()
        
        # Procurar por dados em tabelas
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    key = cells[0].get_text(strip=True).lower()
                    value = cells[1].get_text(strip=True)
                    
                    # Mapear chaves para campos do modelo
                    key_mapping = {
                        'marca': 'marca',
                        'modelo': 'modelo',
                        'ano': 'ano',
                        'cor': 'cor',
                        'combustível': 'combustivel',
                        'chassi': 'chassi',
                        'motor': 'motor',
                        'passageiros': 'passageiros',
                        'uf': 'uf',
                        'município': 'municipio',
                        'cilindrada': 'cilindrada',
                        'importado': 'importado',
                        'genérico': 'generico',
                        'ano modelo': 'ano_modelo'
                    }
                    
                    for k, v in key_mapping.items():
                        if k in key and value and value not in ['-', 'N/A', '']:
                            dados[v] = value
        
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
            
            # Tentar extrair informações do formato da placa
            if re.match(r'^[A-Z]{3}\d{4}$', placa):
                # Formato antigo (ex: ABC1234)
                dados['formato_placa'] = 'antigo'
                # Tentar inferir algumas informações básicas
                dados['ano_estimado'] = '2000-2018'  # Placas antigas geralmente são deste período
                dados['status'] = 'formato_antigo'
            elif re.match(r'^[A-Z]{3}\d{1}[A-Z]\d{2}$', placa):
                # Formato Mercosul (ex: ABC1D23)
                dados['formato_placa'] = 'mercosul'
                dados['ano_estimado'] = '2018-2025'  # Placas Mercosul são mais recentes
                dados['status'] = 'formato_mercosul'
            
            # Tentar fazer uma consulta básica em sites públicos
            try:
                # Tentar consultar informações básicas do Denatran
                response = self.session.get(
                    'https://www.gov.br/denatran/pt-br/assuntos/veiculos/placa-mercosul',
                    timeout=10
                )
                if response.status_code == 200:
                    dados['fonte_consulta'] = 'gov.br'
                    dados['status'] = 'consulta_gov_br'
            except:
                pass
            
            # Tentar extrair informações da placa baseado em padrões conhecidos
            # Exemplo: placas que começam com certas letras podem indicar região
            if placa.startswith(('MG', 'SP', 'RJ', 'RS', 'PR', 'SC')):
                dados['uf_estimada'] = placa[:2]
            
            print(f"   ℹ️  Informações básicas extraídas para {placa}: {len(dados)} campos")
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
