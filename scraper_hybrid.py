#!/usr/bin/env python3
"""
Scraper Híbrido para placas - Alterna automaticamente entre Selenium e Requests
"""

import time
import random
from typing import Dict, Optional, List, Union
import logging

# Importar ambos os scrapers
try:
    from scraper import PlacaFipeScraper
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("⚠️  Selenium não disponível")

try:
    from scraper_requests import PlacaFipeScraperRequests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("⚠️  Requests não disponível")

try:
    from scraper_alternative import PlacaFipeScraperAlternative
    ALTERNATIVE_AVAILABLE = True
except ImportError:
    ALTERNATIVE_AVAILABLE = False
    print("⚠️  Scraper alternativo não disponível")

class PlacaFipeScraperHybrid:
    """Scraper híbrido que alterna entre métodos automaticamente"""
    
    def __init__(self, preferencia: str = "auto"):
        """
        Inicializa o scraper híbrido
        
        Args:
            preferencia: "auto", "requests", "selenium", "alternative"
        """
        self.preferencia = preferencia
        self.scraper_selenium = None
        self.scraper_requests = None
        self.scraper_alternative = None
        self.metodo_atual = None
        
        # Inicializar scrapers disponíveis
        if SELENIUM_AVAILABLE:
            try:
                self.scraper_selenium = PlacaFipeScraper()
                print("✅ Scraper Selenium inicializado")
            except Exception as e:
                print(f"⚠️  Erro ao inicializar Selenium: {e}")
        
        if REQUESTS_AVAILABLE:
            try:
                self.scraper_requests = PlacaFipeScraperRequests()
                print("✅ Scraper Requests inicializado")
            except Exception as e:
                print(f"⚠️  Erro ao inicializar Requests: {e}")
        
        if ALTERNATIVE_AVAILABLE:
            try:
                self.scraper_alternative = PlacaFipeScraperAlternative()
                print("✅ Scraper Alternativo inicializado")
            except Exception as e:
                print(f"⚠️  Erro ao inicializar Alternativo: {e}")
        
        # Verificar disponibilidade
        if not any([self.scraper_selenium, self.scraper_requests, self.scraper_alternative]):
            raise Exception("❌ Nenhum scraper disponível!")
        
        print(f"🚀 Scraper Híbrido inicializado - Preferência: {preferencia}")
    
    def _escolher_metodo(self) -> str:
        """Escolhe o melhor método baseado na preferência e disponibilidade"""
        if self.preferencia == "requests" and self.scraper_requests:
            return "requests"
        elif self.preferencia == "selenium" and self.scraper_selenium:
            return "selenium"
        elif self.preferencia == "alternative" and self.scraper_alternative:
            return "alternative"
        elif self.preferencia == "auto":
            # Auto: preferir requests (mais rápido), depois alternativo, depois selenium
            if self.scraper_requests:
                return "requests"
            elif self.scraper_alternative:
                return "alternative"
            elif self.scraper_selenium:
                return "selenium"
        
        # Fallback: usar o que estiver disponível
        if self.scraper_requests:
            return "requests"
        elif self.scraper_alternative:
            return "alternative"
        elif self.scraper_selenium:
            return "selenium"
        
        raise Exception("❌ Nenhum método disponível!")
    
    def scraping_placa(self, placa: str) -> Optional[Dict[str, str]]:
        """Faz scraping de uma placa usando o melhor método disponível"""
        metodo = self._escolher_metodo()
        self.metodo_atual = metodo
        
        print(f"🔧 Usando método: {metodo.upper()}")
        
        # Tentar o método escolhido
        dados = None
        try:
            if metodo == "requests":
                dados = self.scraper_requests.scraping_placa(placa)
            elif metodo == "selenium":
                dados = self.scraper_selenium.scraping_placa(placa)
            elif metodo == "alternative":
                dados = self.scraper_alternative.scraping_placa(placa)
        except Exception as e:
            print(f"❌ Erro com método {metodo}: {str(e)}")
        
        # Se o método escolhido falhou, tentar fallback
        if not dados:
            print("🔄 Método principal falhou, tentando fallback...")
            dados = self._tentar_fallback(placa, metodo)
        
        return dados
    
    def _tentar_fallback(self, placa: str, metodo_falhou: str) -> Optional[Dict[str, str]]:
        """Tenta métodos alternativos quando o principal falha"""
        fallback_methods = []
        
        # Definir ordem de fallback baseada no método que falhou
        if metodo_falhou == "requests":
            if self.scraper_alternative:
                fallback_methods.append(("alternative", self.scraper_alternative))
            if self.scraper_selenium:
                fallback_methods.append(("selenium", self.scraper_selenium))
        elif metodo_falhou == "alternative":
            if self.scraper_requests:
                fallback_methods.append(("requests", self.scraper_requests))
            if self.scraper_selenium:
                fallback_methods.append(("selenium", self.scraper_selenium))
        elif metodo_falhou == "selenium":
            if self.scraper_requests:
                fallback_methods.append(("requests", self.scraper_requests))
            if self.scraper_alternative:
                fallback_methods.append(("alternative", self.scraper_alternative))
        
        # Tentar cada método de fallback
        for nome_metodo, scraper in fallback_methods:
            try:
                print(f"🔄 Tentando fallback para {nome_metodo.upper()}...")
                self.metodo_atual = nome_metodo
                
                if nome_metodo == "requests":
                    dados = scraper.scraping_placa(placa)
                elif nome_metodo == "selenium":
                    dados = scraper.scraping_placa(placa)
                elif nome_metodo == "alternative":
                    dados = scraper.scraping_placa(placa)
                
                if dados:
                    print(f"✅ Fallback para {nome_metodo.upper()} funcionou!")
                    return dados
                    
            except Exception as e:
                print(f"❌ Fallback para {nome_metodo.upper()} falhou: {str(e)}")
                continue
        
        print("❌ Todos os métodos de fallback falharam")
        return None
    
    def scraping_multiplas_placas(self, placas: List[str], delay_entre_placas: float = 2.0) -> List[Dict[str, str]]:
        """Faz scraping de múltiplas placas"""
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
    
    def get_status(self) -> Dict[str, Union[str, bool]]:
        """Retorna o status dos scrapers"""
        return {
            "metodo_atual": self.metodo_atual,
            "selenium_disponivel": bool(self.scraper_selenium),
            "requests_disponivel": bool(self.scraper_requests),
            "alternative_disponivel": bool(self.scraper_alternative),
            "preferencia": self.preferencia
        }
    
    def close(self):
        """Fecha todos os scrapers"""
        if self.scraper_selenium:
            try:
                self.scraper_selenium.close()
                print("✅ Scraper Selenium fechado")
            except:
                pass
        
        if self.scraper_requests:
            try:
                self.scraper_requests.close()
                print("✅ Scraper Requests fechado")
            except:
                pass
        
        if self.scraper_alternative:
            try:
                self.scraper_alternative.close()
                print("✅ Scraper Alternativo fechado")
            except:
                pass

# Função de teste
def testar_scraper_hybrid():
    """Função para testar o scraper híbrido"""
    try:
        scraper = PlacaFipeScraperHybrid(preferencia="auto")
        
        # Mostrar status
        status = scraper.get_status()
        print(f"📊 Status: {status}")
        
        # Testar com uma placa
        placa_teste = "ABC1234"
        print(f"🧪 Testando com placa: {placa_teste}")
        
        dados = scraper.scraping_placa(placa_teste)
        
        if dados:
            print(f"✅ Sucesso! Dados obtidos: {dados}")
        else:
            print("❌ Falha ao obter dados")
            
    except Exception as e:
        print(f"❌ Erro no teste: {str(e)}")
    finally:
        if 'scraper' in locals():
            scraper.close()

if __name__ == "__main__":
    testar_scraper_hybrid()
