#!/usr/bin/env python3
"""
Script para comparar performance entre diferentes métodos de scraping
"""

import time
import statistics
from typing import List, Dict
import sys

def benchmark_scraper(scraper_class, placas: List[str], nome: str) -> Dict:
    """Executa benchmark de um scraper específico"""
    print(f"\n🚀 Benchmark: {nome}")
    print("=" * 50)
    
    tempos = []
    sucessos = 0
    erros = 0
    
    try:
        scraper = scraper_class()
        
        for i, placa in enumerate(placas):
            print(f"   📊 Testando placa {i+1}/{len(placas)}: {placa}")
            
            inicio = time.time()
            try:
                dados = scraper.scraping_placa(placa)
                fim = time.time()
                tempo = fim - inicio
                tempos.append(tempo)
                
                if dados:
                    sucessos += 1
                    print(f"      ✅ Sucesso em {tempo:.2f}s - {len(dados)} campos")
                else:
                    erros += 1
                    print(f"      ⚠️  Sem dados em {tempo:.2f}s")
                    
            except Exception as e:
                fim = time.time()
                tempo = fim - inicio
                tempos.append(tempo)
                erros += 1
                print(f"      ❌ Erro em {tempo:.2f}s: {str(e)}")
            
            # Delay entre testes
            if i < len(placas) - 1:
                time.sleep(1)
        
        scraper.close()
        
    except Exception as e:
        print(f"   ❌ Erro ao inicializar scraper: {str(e)}")
        return {
            "nome": nome,
            "status": "erro",
            "erro": str(e)
        }
    
    # Calcular estatísticas
    if tempos:
        stats = {
            "nome": nome,
            "status": "sucesso",
            "total_placas": len(placas),
            "sucessos": sucessos,
            "erros": erros,
            "taxa_sucesso": (sucessos / len(placas)) * 100,
            "tempo_total": sum(tempos),
            "tempo_medio": statistics.mean(tempos),
            "tempo_mediana": statistics.median(tempos),
            "tempo_min": min(tempos),
            "tempo_max": max(tempos),
            "tempos": tempos
        }
    else:
        stats = {
            "nome": nome,
            "status": "sem_dados",
            "total_placas": len(placas),
            "sucessos": 0,
            "erros": len(placas)
        }
    
    return stats

def exibir_resultados(resultados: List[Dict]):
    """Exibe os resultados do benchmark de forma organizada"""
    print("\n" + "="*80)
    print("📊 RESULTADOS DO BENCHMARK")
    print("="*80)
    
    for resultado in resultados:
        print(f"\n🏆 {resultado['nome'].upper()}")
        print("-" * 40)
        
        if resultado['status'] == 'erro':
            print(f"❌ Status: {resultado['status']}")
            print(f"❌ Erro: {resultado['erro']}")
            continue
            
        if resultado['status'] == 'sem_dados':
            print(f"⚠️  Status: {resultado['status']}")
            print(f"📊 Total de placas: {resultado['total_placas']}")
            print(f"❌ Erros: {resultado['erros']}")
            continue
        
        print(f"📊 Total de placas: {resultado['total_placas']}")
        print(f"✅ Sucessos: {resultado['sucessos']}")
        print(f"❌ Erros: {resultado['erros']}")
        print(f"📈 Taxa de sucesso: {resultado['taxa_sucesso']:.1f}%")
        print(f"⏱️  Tempo total: {resultado['tempo_total']:.2f}s")
        print(f"⏱️  Tempo médio: {resultado['tempo_medio']:.2f}s")
        print(f"⏱️  Tempo mediana: {resultado['tempo_mediana']:.2f}s")
        print(f"⏱️  Tempo mínimo: {resultado['tempo_min']:.2f}s")
        print(f"⏱️  Tempo máximo: {resultado['tempo_max']:.2f}s")
    
    # Comparação entre métodos
    metodos_sucesso = [r for r in resultados if r['status'] == 'sucesso']
    if len(metodos_sucesso) > 1:
        print("\n" + "="*80)
        print("🏁 COMPARAÇÃO DE PERFORMANCE")
        print("="*80)
        
        # Ordenar por tempo médio
        metodos_sucesso.sort(key=lambda x: x['tempo_medio'])
        
        print(f"\n🥇 1º Lugar: {metodos_sucesso[0]['nome']}")
        print(f"   ⏱️  Tempo médio: {metodos_sucesso[0]['tempo_medio']:.2f}s")
        print(f"   📈 Taxa de sucesso: {metodos_sucesso[0]['taxa_sucesso']:.1f}%")
        
        if len(metodos_sucesso) > 1:
            print(f"\n🥈 2º Lugar: {metodos_sucesso[1]['nome']}")
            print(f"   ⏱️  Tempo médio: {metodos_sucesso[1]['tempo_medio']:.2f}s")
            print(f"   📈 Taxa de sucesso: {metodos_sucesso[1]['taxa_sucesso']:.1f}%")
            
            # Calcular diferença
            diff = metodos_sucesso[1]['tempo_medio'] - metodos_sucesso[0]['tempo_medio']
            percentual = (diff / metodos_sucesso[0]['tempo_medio']) * 100
            print(f"   📊 Diferença: +{diff:.2f}s ({percentual:.1f}% mais lento)")

def main():
    """Função principal do benchmark"""
    print("🧪 BENCHMARK DE SCRAPERS")
    print("=" * 50)
    
    # Placas de teste
    placas_teste = ["ABC1234", "DEF5678", "GHI9012"]
    
    print(f"📋 Placas de teste: {placas_teste}")
    print(f"🔍 Total de testes: {len(placas_teste)}")
    
    resultados = []
    
    # Testar scraper Requests (se disponível)
    try:
        from scraper_requests import PlacaFipeScraperRequests
        resultado = benchmark_scraper(PlacaFipeScraperRequests, placas_teste, "Requests + BeautifulSoup")
        resultados.append(resultado)
    except ImportError:
        print("⚠️  Scraper Requests não disponível")
    
    # Testar scraper Selenium (se disponível)
    try:
        from scraper import PlacaFipeScraper
        resultado = benchmark_scraper(PlacaFipeScraper, placas_teste, "Selenium WebDriver")
        resultados.append(resultado)
    except ImportError:
        print("⚠️  Scraper Selenium não disponível")
    
    # Testar scraper Alternativo (se disponível)
    try:
        from scraper_alternative import PlacaFipeScraperAlternative
        resultado = benchmark_scraper(PlacaFipeScraperAlternative, placas_teste, "Alternativo (Múltiplos Sites)")
        resultados.append(resultado)
    except ImportError:
        print("⚠️  Scraper Alternativo não disponível")
    
    # Testar scraper Híbrido (se disponível)
    try:
        from scraper_hybrid import PlacaFipeScraperHybrid
        resultado = benchmark_scraper(PlacaFipeScraperHybrid, placas_teste, "Híbrido (Auto)")
        resultados.append(resultado)
    except ImportError:
        print("⚠️  Scraper Híbrido não disponível")
    
    if not resultados:
        print("❌ Nenhum scraper disponível para teste!")
        return
    
    # Exibir resultados
    exibir_resultados(resultados)
    
    print(f"\n✅ Benchmark concluído com {len(resultados)} métodos testados!")

if __name__ == "__main__":
    main()
