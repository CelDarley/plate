from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone, timedelta
import os
from dotenv import load_dotenv
from scraper import PlacaFipeScraper
import threading
import time

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://plate:Plate()123@localhost/plate?charset=utf8mb4'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

db = SQLAlchemy(app)

# Função para obter data/hora atual no fuso GMT-3
def get_current_time_gmt3():
    return datetime.now(timezone(timedelta(hours=-3)))

# Modelo para armazenar os dados das placas
class Placa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    placa = db.Column(db.String(7), nullable=False, unique=True)
    marca = db.Column(db.String(100))
    generico = db.Column(db.String(100))
    modelo = db.Column(db.String(100))
    importado = db.Column(db.String(10))
    ano = db.Column(db.String(10))
    ano_modelo = db.Column(db.String(10))
    cor = db.Column(db.String(50))
    cilindrada = db.Column(db.String(50))
    combustivel = db.Column(db.String(50))
    chassi = db.Column(db.String(50))
    motor = db.Column(db.String(50))
    passageiros = db.Column(db.String(10))
    uf = db.Column(db.String(10))
    municipio = db.Column(db.String(100))
    data_scraping = db.Column(db.DateTime, default=get_current_time_gmt3)
    status = db.Column(db.String(20), default='pendente')

# Modelo para armazenar o histórico de scraping
class HistoricoScraping(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_inicio = db.Column(db.DateTime, default=get_current_time_gmt3)
    data_fim = db.Column(db.DateTime)
    total_placas = db.Column(db.Integer, default=0)
    placas_processadas = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='em_andamento')

# Variável global para controlar o scraping
scraping_ativo = False
scraper_thread = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/gestao')
def gestao():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    search = request.args.get('search', '')
    
    if search:
        placas = Placa.query.filter(
            Placa.placa.contains(search) | 
            Placa.marca.contains(search) | 
            Placa.modelo.contains(search)
        ).paginate(page=page, per_page=per_page, error_out=False)
    else:
        placas = Placa.query.paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('gestao.html', placas=placas, search=search)

@app.route('/api/iniciar-scraping', methods=['POST'])
def iniciar_scraping():
    global scraping_ativo, scraper_thread
    
    print(f"🚀 Iniciando scraping... Status atual: {scraping_ativo}")
    
    if scraping_ativo:
        print("❌ Scraping já está em andamento")
        return jsonify({'status': 'erro', 'mensagem': 'Scraping já está em andamento'})
    
    # Obter lista de placas do request
    data = request.get_json()
    placas = data.get('placas', [])
    
    print(f"📋 Placas recebidas: {placas}")
    
    if not placas:
        print("❌ Nenhuma placa fornecida")
        return jsonify({'status': 'erro', 'mensagem': 'Nenhuma placa fornecida'})
    
    try:
        # Criar registro de histórico
        historico = HistoricoScraping(total_placas=len(placas))
        db.session.add(historico)
        db.session.commit()
        print(f"📊 Histórico criado com ID: {historico.id}")
        
        # Iniciar scraping em thread separada
        scraping_ativo = True
        print("🔄 Status alterado para ATIVO")
        
        scraper_thread = threading.Thread(
            target=executar_scraping, 
            args=(placas, historico.id),
            daemon=True  # Thread será encerrada quando o programa principal terminar
        )
        scraper_thread.start()
        print("🧵 Thread de scraping iniciada")
        
        return jsonify({'status': 'sucesso', 'mensagem': 'Scraping iniciado com sucesso'})
        
    except Exception as e:
        print(f"❌ Erro ao iniciar scraping: {str(e)}")
        scraping_ativo = False
        return jsonify({'status': 'erro', 'mensagem': f'Erro interno: {str(e)}'})

@app.route('/api/parar-scraping', methods=['POST'])
def parar_scraping():
    global scraping_ativo
    print("🛑 Parando scraping...")
    scraping_ativo = False
    return jsonify({'status': 'sucesso', 'mensagem': 'Scraping parado com sucesso'})

@app.route('/api/status-scraping')
def status_scraping():
    global scraping_ativo
    print(f"📊 Status consultado: {scraping_ativo}")
    return jsonify({'ativo': scraping_ativo})

def executar_scraping(placas, historico_id):
    global scraping_ativo
    
    print(f"🎯 Iniciando execução do scraping para {len(placas)} placas")
    print(f"📅 Histórico ID: {historico_id}")
    
    # Criar contexto de aplicação para esta thread
    with app.app_context():
        try:
            print("🔧 Inicializando scraper...")
            scraper = PlacaFipeScraper()
            print("✅ Scraper inicializado com sucesso")
            
            tempos = [30, 45, 65, 48]  # Sequência de tempos
            tempo_index = 0
            
            for i, placa in enumerate(placas):
                if not scraping_ativo:
                    print("⏹️  Scraping interrompido pelo usuário")
                    break
                    
                print(f"\n🚗 Processando placa {i+1}/{len(placas)}: {placa}")
                
                try:
                    # Fazer scraping da placa
                    print(f"   🔍 Fazendo scraping de {placa}...")
                    dados = scraper.scraping_placa(placa)
                    
                    if dados:
                        print(f"   ✅ Dados obtidos para {placa}: {len(dados)} campos")
                        
                        # Verificar se a placa já existe
                        placa_existente = Placa.query.filter_by(placa=placa).first()
                        if placa_existente:
                            print(f"   🔄 Atualizando placa existente: {placa}")
                            # Atualizar dados existentes
                            for key, value in dados.items():
                                if hasattr(placa_existente, key):
                                    setattr(placa_existente, key, value)
                            placa_existente.status = 'atualizado'
                        else:
                            print(f"   ➕ Criando nova entrada para: {placa}")
                            # Criar nova entrada
                            nova_placa = Placa(placa=placa, **dados)
                            db.session.add(nova_placa)
                        
                        db.session.commit()
                        print(f"   💾 Dados salvos no banco para {placa}")
                        
                        # Atualizar histórico
                        historico = db.session.get(HistoricoScraping, historico_id)
                        if historico:
                            historico.placas_processadas += 1
                            db.session.commit()
                            print(f"   📊 Histórico atualizado: {historico.placas_processadas}/{historico.total_placas}")
                    else:
                        print(f"   ⚠️  Nenhum dado obtido para {placa}")
                    
                    # Aguardar tempo especificado
                    if i < len(placas) - 1:  # Não aguardar após a última placa
                        tempo_espera = tempos[tempo_index % len(tempos)]
                        print(f"   ⏰ Aguardando {tempo_espera} segundos...")
                        time.sleep(tempo_espera)
                        tempo_index += 1
                        
                except Exception as e:
                    print(f"   ❌ Erro ao processar placa {placa}: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    continue
                    
        except Exception as e:
            print(f"❌ Erro geral no scraping: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            print("🏁 Finalizando scraping...")
            # Finalizar histórico
            try:
                historico = db.session.get(HistoricoScraping, historico_id)
                if historico:
                    historico.data_fim = get_current_time_gmt3()
                    historico.status = 'concluido'
                    db.session.commit()
                    print(f"📊 Histórico finalizado: {historico.placas_processadas}/{historico.total_placas} placas processadas")
            except Exception as e:
                print(f"❌ Erro ao finalizar histórico: {str(e)}")
            
            scraping_ativo = False
            print("✅ Scraping finalizado")

@app.route('/api/placas')
def api_placas():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')
    
    if search:
        placas = Placa.query.filter(
            Placa.placa.contains(search) | 
            Placa.marca.contains(search) | 
            Placa.modelo.contains(search)
        ).paginate(page=page, per_page=per_page, error_out=False)
    else:
        placas = Placa.query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'placas': [{
            'id': p.id,
            'placa': p.placa,
            'marca': p.marca,
            'modelo': p.modelo,
            'ano': p.ano,
            'municipio': p.municipio,
            'uf': p.uf,
            'data_scraping': p.data_scraping.isoformat() if p.data_scraping else None
        } for p in placas.items],
        'total': placas.total,
        'pages': placas.pages,
        'current_page': page
    })

@app.route('/api/placa/<int:placa_id>')
def api_placa_detalhes(placa_id):
    """Retorna todos os dados de uma placa específica"""
    placa = Placa.query.get_or_404(placa_id)
    return jsonify({
        'id': placa.id,
        'placa': placa.placa,
        'marca': placa.marca,
        'generico': placa.generico,
        'modelo': placa.modelo,
        'importado': placa.importado,
        'ano': placa.ano,
        'ano_modelo': placa.ano_modelo,
        'cor': placa.cor,
        'cilindrada': placa.cilindrada,
        'combustivel': placa.combustivel,
        'chassi': placa.chassi,
        'motor': placa.motor,
        'passageiros': placa.passageiros,
        'uf': placa.uf,
        'municipio': placa.municipio,
        'data_scraping': placa.data_scraping.isoformat() if placa.data_scraping else None,
        'status': placa.status
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
