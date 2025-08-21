#!/usr/bin/env python3
"""
Script para inserir placas no banco de dados
"""

from app import app, db, Placa
from datetime import datetime

def insert_placas():
    """Insere as placas fornecidas no banco de dados"""
    
    # Dados das placas com data/hora
    placas_data = [
        ("2025-08-19 12:55:34", "TCF5006"),
        ("2025-08-19 12:55:35", "IEN4074"),
        ("2025-08-19 12:57:42", "SHH0G95"),
        ("2025-08-19 12:58:01", "TAR1J00"),
        ("2025-08-19 13:00:33", "RNH4114"),
        ("2025-08-19 13:01:04", "ONY7017"),
        ("2025-08-19 13:02:05", "RZW2G87"),
        ("2025-08-19 13:03:08", "RUU7697"),
        ("2025-08-19 13:03:12", "RZH2G87"),
        ("2025-08-19 13:06:35", "TCF5C16"),
        ("2025-08-19 13:06:52", "TUJ2J64"),
        ("2025-08-19 13:07:15", "RFR0F50"),
        ("2025-08-19 13:07:32", "QOK5914"),
        ("2025-08-19 13:07:45", "PXU0N01"),
        ("2025-08-19 13:07:54", "PYV3131"),
        ("2025-08-19 13:08:21", "PZB0857"),
        ("2025-08-19 13:09:04", "QXA4346"),
        ("2025-08-19 13:10:10", "HIL5838"),
        ("2025-08-19 13:10:20", "QRW9195"),
        ("2025-08-19 13:11:35", "PYE8057"),
        ("2025-08-19 13:13:58", "TEJ6E10"),
        ("2025-08-19 13:13:59", "TEJ0E15"),
        ("2025-08-19 13:16:31", "TOZ7F01"),
        ("2025-08-19 13:16:33", "RTT1G05"),
        ("2025-08-19 13:21:29", "PHU5E40")
    ]
    
    with app.app_context():
        # Criar tabelas se não existirem
        db.create_all()
        
        print("🚀 Inserindo placas no banco de dados...")
        print("=" * 50)
        
        placas_inseridas = 0
        placas_existentes = 0
        
        for data_str, placa in placas_data:
            try:
                # Converter string de data para datetime
                data_scraping = datetime.strptime(data_str, "%Y-%m-%d %H:%M:%S")
                
                # Verificar se a placa já existe
                placa_existente = Placa.query.filter_by(placa=placa).first()
                
                if placa_existente:
                    # Atualizar data de scraping se for mais recente
                    if not placa_existente.data_scraping or data_scraping > placa_existente.data_scraping:
                        placa_existente.data_scraping = data_scraping
                        placa_existente.status = 'atualizado'
                        db.session.commit()
                        print(f"   ✅ {placa} - Data atualizada: {data_str}")
                    else:
                        print(f"   ⚠️  {placa} - Já existe com data mais recente")
                    placas_existentes += 1
                else:
                    # Criar nova entrada
                    nova_placa = Placa(
                        placa=placa,
                        data_scraping=data_scraping,
                        status='pendente'
                    )
                    db.session.add(nova_placa)
                    db.session.commit()
                    print(f"   ➕ {placa} - Inserida: {data_str}")
                    placas_inseridas += 1
                    
            except Exception as e:
                print(f"   ❌ Erro ao processar placa {placa}: {str(e)}")
                continue
        
        print("=" * 50)
        print(f"📊 Resumo:")
        print(f"   ➕ Placas inseridas: {placas_inseridas}")
        print(f"   ⚠️  Placas existentes: {placas_existentes}")
        print(f"   📅 Total processadas: {placas_inseridas + placas_existentes}")
        
        # Verificar total no banco
        total_banco = Placa.query.count()
        print(f"   🗄️  Total no banco: {total_banco}")
        
        print("\n🎯 Inserção concluída!")
        print("💡 Acesse http://localhost:5000/gestao para visualizar os dados")

if __name__ == "__main__":
    insert_placas()
