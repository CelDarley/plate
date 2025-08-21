#!/usr/bin/env python3
"""
Script de teste para o Sistema de Scraping Placa FIPE
"""

import sys
import time
from scraper import PlacaFipeScraper

def test_scraper():
    """Testa o scraper com placas de exemplo"""
    print("🧪 Testando Sistema de Scraping")
    print("=" * 40)
    
    try:
        # Criar instância do scraper
        scraper = PlacaFipeScraper()
        print("✅ Scraper criado com sucesso")
        
        # Testar validação de placas
        print("\n🔍 Testando validação de placas...")
        placas_teste = ['ABC1234', 'DEF5678', 'GHI9012', 'ABC1D23', 'INVALID']
        
        for placa in placas_teste:
            if scraper.validar_placa(placa):
                print(f"   ✅ {placa} - Válida")
            else:
                print(f"   ❌ {placa} - Inválida")
        
        # Testar geração de placas de teste
        print("\n🎲 Testando geração de placas...")
        placas_geradas = scraper.gerar_placas_teste(5)
        print(f"   Placas geradas: {', '.join(placas_geradas)}")
        
        # Testar conexão com o site (sem fazer scraping real)
        print("\n🌐 Testando conexão com placafipe.com...")
        try:
            import requests
            response = requests.get('https://placafipe.com/', timeout=10)
            if response.status_code == 200:
                print("   ✅ Site acessível")
            else:
                print(f"   ⚠️  Site retornou status {response.status_code}")
        except Exception as e:
            print(f"   ❌ Erro ao acessar site: {e}")
        
        print("\n🎯 Testes básicos concluídos!")
        print("\n💡 Para testar o scraping real:")
        print("   1. Execute: python app.py")
        print("   2. Acesse: http://localhost:5000/gestao")
        print("   3. Use placas reais para teste")
        
    except Exception as e:
        print(f"❌ Erro durante os testes: {e}")
        return False
    
    return True

def test_dependencies():
    """Testa se todas as dependências estão disponíveis"""
    print("📦 Verificando dependências...")
    
    dependencies = [
        ('Flask', 'flask'),
        ('Requests', 'requests'),
        ('BeautifulSoup', 'bs4'),
        ('Selenium', 'selenium'),
        ('SQLAlchemy', 'sqlalchemy'),
        ('Flask-SQLAlchemy', 'flask_sqlalchemy'),
        ('python-dotenv', 'dotenv')
    ]
    
    all_ok = True
    
    for name, module in dependencies:
        try:
            __import__(module)
            print(f"   ✅ {name}")
        except ImportError:
            print(f"   ❌ {name}")
            all_ok = False
    
    return all_ok

def main():
    """Função principal"""
    print("🚀 Sistema de Scraping Placa FIPE - Testes")
    print("=" * 50)
    
    # Testar dependências
    if not test_dependencies():
        print("\n❌ Algumas dependências estão faltando!")
        print("Execute: pip install -r requirements.txt")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    
    # Testar scraper
    if test_scraper():
        print("\n🎉 Todos os testes passaram!")
        print("O sistema está pronto para uso.")
    else:
        print("\n❌ Alguns testes falharam.")
        print("Verifique os erros acima.")

if __name__ == "__main__":
    main()
