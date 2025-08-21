#!/usr/bin/env python3
"""
Teste simples do scraper
"""

from scraper import PlacaFipeScraper
import time

def test_simple():
    """Teste simples de uma placa"""
    print("🧪 Teste Simples do Scraper")
    print("=" * 40)
    
    try:
        scraper = PlacaFipeScraper()
        print("✅ Scraper criado")
        
        # Testar com uma placa
        placa_teste = "ABC1234"
        print(f"\n🔍 Testando placa: {placa_teste}")
        
        print("⏳ Iniciando scraping...")
        dados = scraper.scraping_placa(placa_teste)
        
        if dados:
            print("✅ Scraping funcionou!")
            print(f"📊 Dados obtidos: {len(dados)} campos")
            for key, value in dados.items():
                print(f"   {key}: {value}")
        else:
            print("❌ Scraping falhou - nenhum dado retornado")
            
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple()
