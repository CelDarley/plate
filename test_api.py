#!/usr/bin/env python3
"""
Script de teste para a API Placa FIPE Scraper
"""

import requests
import json
import time

# Configurações
BASE_URL = "http://localhost:5000"
PLACAS_TESTE = ["ABC1234", "DEF5678", "GHI9012"]

def testar_endpoint_raiz():
    """Testa o endpoint raiz da API"""
    print("🔍 Testando endpoint raiz...")
    
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            data = response.json()
            print("✅ Endpoint raiz funcionando!")
            print(f"   API: {data['api']}")
            print(f"   Versão: {data['version']}")
            print(f"   Descrição: {data['description']}")
            print("   Endpoints disponíveis:")
            for endpoint, desc in data['endpoints'].items():
                print(f"     {endpoint}: {desc}")
        else:
            print(f"❌ Erro no endpoint raiz: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao testar endpoint raiz: {str(e)}")

def testar_consulta_placa(placa):
    """Testa a consulta de uma placa específica"""
    print(f"\n🚗 Testando consulta da placa {placa}...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/placa/{placa}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Placa {placa} consultada com sucesso!")
            print(f"   Fonte: {data['fonte']}")
            print(f"   Marca: {data['dados']['marca']}")
            print(f"   Modelo: {data['dados']['modelo']}")
            print(f"   Ano: {data['dados']['ano']}")
            print(f"   UF: {data['dados']['uf']}")
            print(f"   Município: {data['dados']['municipio']}")
            print(f"   Timestamp: {data['timestamp']}")
            
        elif response.status_code == 400:
            data = response.json()
            print(f"⚠️  Erro de validação: {data['erro']}")
            print(f"   Mensagem: {data['mensagem']}")
            
        else:
            print(f"❌ Erro na consulta: {response.status_code}")
            try:
                data = response.json()
                print(f"   Mensagem: {data.get('mensagem', 'Erro desconhecido')}")
            except:
                print(f"   Resposta: {response.text}")
                
    except Exception as e:
        print(f"❌ Erro ao consultar placa {placa}: {str(e)}")

def testar_listagem_placas():
    """Testa a listagem de todas as placas"""
    print(f"\n📋 Testando listagem de placas...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/placas?page=1&per_page=5")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Listagem de placas funcionando!")
            print(f"   Total de placas: {data['paginacao']['total_placas']}")
            print(f"   Página atual: {data['paginacao']['pagina_atual']}")
            print(f"   Total de páginas: {data['paginacao']['total_paginas']}")
            
            if data['placas']:
                print("   Primeiras placas:")
                for placa in data['placas'][:3]:
                    print(f"     {placa['placa']} - {placa['marca']} {placa['modelo']}")
            else:
                print("   Nenhuma placa encontrada")
                
        else:
            print(f"❌ Erro na listagem: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro ao listar placas: {str(e)}")

def testar_historico_placa(placa):
    """Testa o histórico de uma placa específica"""
    print(f"\n📊 Testando histórico da placa {placa}...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/placa/{placa}/historico")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Histórico da placa {placa} obtido!")
            print(f"   Marca: {data['historico']['marca']}")
            print(f"   Modelo: {data['historico']['modelo']}")
            print(f"   Status: {data['historico']['status']}")
            print(f"   Data scraping: {data['historico']['data_scraping']}")
            
        elif response.status_code == 404:
            print(f"⚠️  Placa {placa} não encontrada no histórico")
            
        else:
            print(f"❌ Erro no histórico: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro ao consultar histórico: {str(e)}")

def testar_placas_invalidas():
    """Testa placas com formato inválido"""
    print(f"\n🚫 Testando placas com formato inválido...")
    
    placas_invalidas = ["123ABC", "ABCD123", "ABC123", "ABC12345"]
    
    for placa in placas_invalidas:
        try:
            response = requests.get(f"{BASE_URL}/api/placa/{placa}")
            
            if response.status_code == 400:
                data = response.json()
                print(f"✅ Validação funcionando para {placa}: {data['erro']}")
            else:
                print(f"❌ Validação falhou para {placa}: status {response.status_code}")
                
        except Exception as e:
            print(f"❌ Erro ao testar placa inválida {placa}: {str(e)}")

def main():
    """Função principal de teste"""
    print("🚀 Iniciando testes da API Placa FIPE Scraper")
    print("=" * 50)
    
    # Testar endpoint raiz
    testar_endpoint_raiz()
    
    # Testar consulta de placas válidas
    for placa in PLACAS_TESTE:
        testar_consulta_placa(placa)
        time.sleep(2)  # Aguardar entre consultas
    
    # Testar listagem de placas
    testar_listagem_placas()
    
    # Testar histórico de uma placa
    if PLACAS_TESTE:
        testar_historico_placa(PLACAS_TESTE[0])
    
    # Testar placas inválidas
    testar_placas_invalidas()
    
    print("\n" + "=" * 50)
    print("🏁 Testes concluídos!")
    print("\n💡 Dicas de uso:")
    print("   - Para consultar uma placa: GET /api/placa/ABC1234")
    print("   - Para listar placas: GET /api/placas?page=1&per_page=20")
    print("   - Para histórico: GET /api/placa/ABC1234/historico")
    print("   - Formato aceito: ABC1234 (antigo) ou ABC1D23 (Mercosul)")

if __name__ == "__main__":
    main()
