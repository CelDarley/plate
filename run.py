#!/usr/bin/env python3
"""
Script de inicialização do Sistema de Scraping Placa FIPE
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Verifica se a versão do Python é compatível"""
    if sys.version_info < (3, 8):
        print("❌ Erro: Python 3.8+ é necessário")
        print(f"Versão atual: {sys.version}")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detectado")
    return True

def check_dependencies():
    """Verifica se as dependências estão instaladas"""
    try:
        import flask
        import requests
        import bs4
        import selenium
        print("✅ Todas as dependências estão instaladas")
        return True
    except ImportError as e:
        print(f"❌ Dependência não encontrada: {e}")
        print("Execute: pip install -r requirements.txt")
        return False

def create_directories():
    """Cria diretórios necessários"""
    Path("templates").mkdir(exist_ok=True)
    print("✅ Diretórios criados/verificados")

def setup_database():
    """Configura o banco de dados"""
    try:
        from app import app, db
        with app.app_context():
            db.create_all()
        print("✅ Banco de dados configurado")
        return True
    except Exception as e:
        print(f"❌ Erro ao configurar banco: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 Iniciando Sistema de Scraping Placa FIPE")
    print("=" * 50)
    
    # Verificações
    if not check_python_version():
        sys.exit(1)
    
    if not check_dependencies():
        print("\n💡 Para instalar as dependências:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    
    create_directories()
    
    if not setup_database():
        print("⚠️  Continuando sem configuração do banco...")
    
    print("\n🎯 Sistema pronto para execução!")
    print("\n📋 Próximos passos:")
    print("   1. Acesse: http://localhost:5000")
    print("   2. Vá para a página de Gestão")
    print("   3. Insira as placas e inicie o scraping")
    
    print("\n🚀 Iniciando servidor...")
    print("=" * 50)
    
    # Inicia o servidor Flask
    try:
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n\n👋 Servidor parado pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro ao iniciar servidor: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
