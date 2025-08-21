#!/usr/bin/env python3
"""
Script para migrar dados do SQLite para MySQL
"""

import sqlite3
import pymysql
from datetime import datetime, timezone, timedelta

def get_current_time_gmt3():
    """Retorna data/hora atual no fuso GMT-3"""
    return datetime.now(timezone(timedelta(hours=-3)))

def conectar_sqlite():
    """Conecta ao banco SQLite"""
    return sqlite3.connect('instance/placas.db')

def conectar_mysql():
    """Conecta ao banco MySQL"""
    return pymysql.connect(
        host='localhost',
        user='plate',
        password='Plate()123',
        database='plate',
        charset='utf8mb4'
    )

def criar_tabelas_mysql(cursor):
    """Cria as tabelas no MySQL"""
    
    # Tabela placa
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS placa (
            id INT AUTO_INCREMENT PRIMARY KEY,
            placa VARCHAR(7) NOT NULL UNIQUE,
            marca VARCHAR(100),
            generico VARCHAR(100),
            modelo VARCHAR(100),
            importado VARCHAR(10),
            ano VARCHAR(10),
            ano_modelo VARCHAR(10),
            cor VARCHAR(50),
            cilindrada VARCHAR(50),
            combustivel VARCHAR(50),
            chassi VARCHAR(50),
            motor VARCHAR(50),
            passageiros VARCHAR(10),
            uf VARCHAR(10),
            municipio VARCHAR(100),
            data_scraping DATETIME DEFAULT CURRENT_TIMESTAMP,
            status VARCHAR(20) DEFAULT 'pendente'
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """)
    
    # Tabela historico_scraping
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historico_scraping (
            id INT AUTO_INCREMENT PRIMARY KEY,
            data_inicio DATETIME DEFAULT CURRENT_TIMESTAMP,
            data_fim DATETIME NULL,
            total_placas INT DEFAULT 0,
            placas_processadas INT DEFAULT 0,
            status VARCHAR(20) DEFAULT 'em_andamento'
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """)
    
    print("✅ Tabelas criadas no MySQL")

def migrar_dados():
    """Migra os dados do SQLite para MySQL"""
    
    print("🔄 Iniciando migração de dados...")
    
    try:
        # Conectar aos bancos
        sqlite_conn = conectar_sqlite()
        mysql_conn = conectar_mysql()
        
        sqlite_cursor = sqlite_conn.cursor()
        mysql_cursor = mysql_conn.cursor()
        
        # Criar tabelas no MySQL
        criar_tabelas_mysql(mysql_cursor)
        
        # Migrar dados da tabela placa
        print("📋 Migrando dados da tabela placa...")
        sqlite_cursor.execute("SELECT * FROM placa")
        placas = sqlite_cursor.fetchall()
        
        for placa in placas:
            # Converter data para GMT+3 se existir
            data_scraping = None
            if placa[16]:  # data_scraping é o campo 16
                try:
                    # Converter string para datetime e ajustar para GMT-3
                    dt = datetime.fromisoformat(placa[16].replace('Z', '+00:00'))
                    data_scraping = dt.replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=-3)))
                except:
                    data_scraping = get_current_time_gmt3()
            else:
                data_scraping = get_current_time_gmt3()
            
            # Inserir no MySQL
            mysql_cursor.execute("""
                INSERT INTO placa (
                    placa, marca, generico, modelo, importado, ano, ano_modelo,
                    cor, cilindrada, combustivel, chassi, motor, passageiros,
                    uf, municipio, data_scraping, status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    marca=VALUES(marca), generico=VALUES(generico), modelo=VALUES(modelo),
                    importado=VALUES(importado), ano=VALUES(ano), ano_modelo=VALUES(ano_modelo),
                    cor=VALUES(cor), cilindrada=VALUES(cilindrada), combustivel=VALUES(combustivel),
                    chassi=VALUES(chassi), motor=VALUES(motor), passageiros=VALUES(passageiros),
                    uf=VALUES(uf), municipio=VALUES(municipio), data_scraping=VALUES(data_scraping),
                    status=VALUES(status)
            """, (placa[1], placa[2], placa[3], placa[4], placa[5], placa[6], placa[7], 
                  placa[8], placa[9], placa[10], placa[11], placa[12], placa[13], 
                  placa[14], placa[15], data_scraping, placa[17]))
        
        # Migrar dados da tabela historico_scraping
        print("📊 Migrando dados da tabela historico_scraping...")
        sqlite_cursor.execute("SELECT * FROM historico_scraping")
        historicos = sqlite_cursor.fetchall()
        
        for historico in historicos:
            # Converter datas para GMT+3
            data_inicio = None
            data_fim = None
            
            if historico[1]:  # data_inicio
                try:
                    dt = datetime.fromisoformat(historico[1].replace('Z', '+00:00'))
                    data_inicio = dt.replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=-3)))
                except:
                    data_inicio = get_current_time_gmt3()
            else:
                data_inicio = get_current_time_gmt3()
                
            if historico[2]:  # data_fim
                try:
                    dt = datetime.fromisoformat(historico[2].replace('Z', '+00:00'))
                    data_fim = dt.replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=-3)))
                except:
                    data_fim = None
            
            mysql_cursor.execute("""
                INSERT INTO historico_scraping (
                    data_inicio, data_fim, total_placas, placas_processadas, status
                ) VALUES (%s, %s, %s, %s, %s)
            """, (data_inicio, data_fim, historico[3], historico[4], historico[5]))
        
        # Commit das alterações
        mysql_conn.commit()
        
        print(f"✅ Migração concluída!")
        print(f"   - {len(placas)} placas migradas")
        print(f"   - {len(historicos)} históricos migrados")
        
        # Verificar dados no MySQL
        mysql_cursor.execute("SELECT COUNT(*) FROM placa")
        total_placas = mysql_cursor.fetchone()[0]
        print(f"   - Total de placas no MySQL: {total_placas}")
        
    except Exception as e:
        print(f"❌ Erro durante a migração: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        # Fechar conexões
        if 'sqlite_conn' in locals():
            sqlite_conn.close()
        if 'mysql_conn' in locals():
            mysql_conn.close()

if __name__ == "__main__":
    migrar_dados()
