from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone, timedelta
import os
from dotenv import load_dotenv
from scraper import PlacaFipeScraper
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

@app.route('/')
def index():
    """Endpoint raiz com informações da API"""
    return jsonify({
        'api': 'Placa FIPE Scraper API',
        'version': '1.0.0',
        'description': 'API para consulta de dados de veículos por placa',
        'endpoints': {
            '/': 'Informações da API',
            '/api/placa/<placa>': 'Consulta dados de uma placa específica',
            '/api/placas': 'Lista todas as placas consultadas',
            '/api/placa/<placa>/historico': 'Histórico de consultas de uma placa'
        },
        'usage': {
            'method': 'GET',
            'example': '/api/placa/ABC1234'
        }
    })

@app.route('/api/placa/<placa>', methods=['GET'])
def consultar_placa(placa):
    """
    Endpoint principal: consulta uma placa e retorna os dados
    
    Args:
        placa (str): Número da placa (formato: ABC1234 ou ABC1D23)
    
    Returns:
        JSON com os dados da placa ou erro
    """
    try:
        # Validar formato da placa
        if not validar_formato_placa(placa):
            return jsonify({
                'erro': 'Formato de placa inválido',
                'placa': placa,
                'formatos_aceitos': ['ABC1234', 'ABC1D23'],
                'exemplo': 'ABC1234 ou ABC1D23'
            }), 400
        
        # Verificar se a placa já existe no banco
        placa_existente = Placa.query.filter_by(placa=placa).first()
        
        if placa_existente:
            logger.info(f"Placa {placa} encontrada no banco")
            return jsonify({
                'placa': placa,
                'dados': {
                    'id': placa_existente.id,
                    'marca': placa_existente.marca,
                    'generico': placa_existente.generico,
                    'modelo': placa_existente.modelo,
                    'importado': placa_existente.importado,
                    'ano': placa_existente.ano,
                    'ano_modelo': placa_existente.ano_modelo,
                    'cor': placa_existente.cor,
                    'cilindrada': placa_existente.cilindrada,
                    'combustivel': placa_existente.combustivel,
                    'chassi': placa_existente.chassi,
                    'motor': placa_existente.motor,
                    'passageiros': placa_existente.passageiros,
                    'uf': placa_existente.uf,
                    'municipio': placa_existente.municipio,
                    'status': placa_existente.status,
                    'data_scraping': placa_existente.data_scraping.isoformat() if placa_existente.data_scraping else None
                },
                'fonte': 'banco_local',
                'timestamp': get_current_time_gmt3().isoformat()
            })
        
        # Placa não existe, fazer scraping
        logger.info(f"Iniciando scraping para placa {placa}")
        
        try:
            scraper = PlacaFipeScraper()
            dados = scraper.scraping_placa(placa)
            
            if dados:
                # Salvar no banco
                nova_placa = Placa(placa=placa, **dados)
                db.session.add(nova_placa)
                db.session.commit()
                
                logger.info(f"Placa {placa} processada com sucesso")
                
                return jsonify({
                    'placa': placa,
                    'dados': {
                        'id': nova_placa.id,
                        'marca': nova_placa.marca,
                        'generico': nova_placa.generico,
                        'modelo': nova_placa.modelo,
                        'importado': nova_placa.importado,
                        'ano': nova_placa.ano,
                        'ano_modelo': nova_placa.ano_modelo,
                        'cor': nova_placa.cor,
                        'cilindrada': nova_placa.cilindrada,
                        'combustivel': nova_placa.combustivel,
                        'chassi': nova_placa.chassi,
                        'motor': nova_placa.motor,
                        'passageiros': nova_placa.passageiros,
                        'uf': nova_placa.uf,
                        'municipio': nova_placa.municipio,
                        'status': nova_placa.status,
                        'data_scraping': nova_placa.data_scraping.isoformat() if nova_placa.data_scraping else None
                    },
                    'fonte': 'scraping_novo',
                    'timestamp': get_current_time_gmt3().isoformat()
                })
            else:
                logger.error(f"Falha no scraping para placa {placa}")
                return jsonify({
                    'erro': 'Falha ao obter dados da placa',
                    'placa': placa,
                    'mensagem': 'Não foi possível extrair dados do site',
                    'timestamp': get_current_time_gmt3().isoformat()
                }), 500
                
        except Exception as e:
            logger.error(f"Erro durante scraping da placa {placa}: {str(e)}")
            return jsonify({
                'erro': 'Erro interno durante scraping',
                'placa': placa,
                'mensagem': str(e),
                'timestamp': get_current_time_gmt3().isoformat()
            }), 500
            
    except Exception as e:
        logger.error(f"Erro geral na consulta da placa {placa}: {str(e)}")
        return jsonify({
            'erro': 'Erro interno da API',
            'placa': placa,
            'mensagem': str(e),
            'timestamp': get_current_time_gmt3().isoformat()
        }), 500

@app.route('/api/placas', methods=['GET'])
def listar_placas():
    """
    Lista todas as placas consultadas com paginação
    
    Query params:
        page (int): Página (padrão: 1)
        per_page (int): Itens por página (padrão: 20, máximo: 100)
        search (str): Termo de busca opcional
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
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
                'uf': p.uf,
                'municipio': p.municipio,
                'data_scraping': p.data_scraping.isoformat() if p.data_scraping else None
            } for p in placas.items],
            'paginacao': {
                'pagina_atual': page,
                'total_paginas': placas.pages,
                'total_placas': placas.total,
                'por_pagina': per_page
            },
            'timestamp': get_current_time_gmt3().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Erro ao listar placas: {str(e)}")
        return jsonify({
            'erro': 'Erro ao listar placas',
            'mensagem': str(e),
            'timestamp': get_current_time_gmt3().isoformat()
        }), 500

@app.route('/api/placa/<placa>/historico', methods=['GET'])
def historico_placa(placa):
    """
    Retorna o histórico de consultas de uma placa específica
    """
    try:
        placa_obj = Placa.query.filter_by(placa=placa).first()
        
        if not placa_obj:
            return jsonify({
                'erro': 'Placa não encontrada',
                'placa': placa,
                'timestamp': get_current_time_gmt3().isoformat()
            }), 404
        
        return jsonify({
            'placa': placa,
            'historico': {
                'id': placa_obj.id,
                'marca': placa_obj.marca,
                'generico': placa_obj.generico,
                'modelo': placa_obj.modelo,
                'importado': placa_obj.importado,
                'ano': placa_obj.ano,
                'ano_modelo': placa_obj.ano_modelo,
                'cor': placa_obj.cor,
                'cilindrada': placa_obj.cilindrada,
                'combustivel': placa_obj.combustivel,
                'chassi': placa_obj.chassi,
                'motor': placa_obj.motor,
                'passageiros': placa_obj.passageiros,
                'uf': placa_obj.uf,
                'municipio': placa_obj.municipio,
                'status': placa_obj.status,
                'data_scraping': placa_obj.data_scraping.isoformat() if placa_obj.data_scraping else None
            },
            'timestamp': get_current_time_gmt3().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Erro ao consultar histórico da placa {placa}: {str(e)}")
        return jsonify({
            'erro': 'Erro ao consultar histórico',
            'placa': placa,
            'mensagem': str(e),
            'timestamp': get_current_time_gmt3().isoformat()
        }), 500

def validar_formato_placa(placa):
    """
    Valida se o formato da placa é válido
    
    Formatos aceitos:
    - Antigo: ABC1234 (3 letras + 4 números)
    - Mercosul: ABC1D23 (3 letras + 1 número + 1 letra + 2 números)
    """
    import re
    
    # Formato antigo: ABC1234
    formato_antigo = re.match(r'^[A-Z]{3}\d{4}$', placa)
    
    # Formato Mercosul: ABC1D23
    formato_mercosul = re.match(r'^[A-Z]{3}\d[A-Z]\d{2}$', placa)
    
    return bool(formato_antigo or formato_mercosul)

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'erro': 'Endpoint não encontrado',
        'mensagem': 'Verifique a URL e tente novamente',
        'endpoints_disponiveis': [
            '/',
            '/api/placa/<placa>',
            '/api/placas',
            '/api/placa/<placa>/historico'
        ],
        'timestamp': get_current_time_gmt3().isoformat()
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'erro': 'Erro interno do servidor',
        'mensagem': 'Tente novamente mais tarde',
        'timestamp': get_current_time_gmt3().isoformat()
    }), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    logger.info("🚀 Iniciando Placa FIPE Scraper API...")
    logger.info("📡 API disponível em: http://localhost:5000")
    logger.info("🔍 Endpoint principal: /api/placa/<placa>")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
