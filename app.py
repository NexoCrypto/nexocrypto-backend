from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import requests
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Configuração para produção
if os.environ.get('FLASK_ENV') == 'production':
    app.config['DEBUG'] = False
else:
    app.config['DEBUG'] = True

# URL da API Telegram
TELEGRAM_API_URL = "https://5002-iqrmmohoou2pzfnpp8zc0-6721939a.manusvm.computer/api"

def format_brazilian_date(date_str):
    """Converte data para formato brasileiro"""
    try:
        if not date_str:
            return datetime.now().strftime('%d/%m/%Y - %H:%M')
        
        # Tenta converter diferentes formatos de data
        for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S.%f']:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime('%d/%m/%Y - %H:%M')
            except ValueError:
                continue
        
        return datetime.now().strftime('%d/%m/%Y - %H:%M')
    except:
        return datetime.now().strftime('%d/%m/%Y - %H:%M')

@app.route('/')
def home():
    return jsonify({
        'message': 'NexoCrypto Backend API',
        'version': '1.0.0',
        'status': 'online',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'nexocrypto-backend',
        'timestamp': datetime.now().isoformat(),
        'uptime': 'active'
    })

@app.route('/api/signals')
def get_signals():
    try:
        # Tenta buscar sinais reais da API Telegram
        response = requests.get(f"{TELEGRAM_API_URL}/signals/CRP-DEFAULT", timeout=5)
        if response.status_code == 200:
            telegram_signals = response.json().get('signals', [])
            
            # Converte sinais do Telegram para formato do frontend
            converted_signals = []
            for signal in telegram_signals:
                converted_signals.append({
                    'id': len(converted_signals) + 1,
                    'pair': signal.get('symbol', 'UNKNOWN'),
                    'direction': signal.get('direction', 'UNKNOWN'),
                    'entry': signal.get('entry_price', 0),
                    'currentPrice': signal.get('entry_price', 0) * 1.001,  # Simula pequena variação
                    'targets': [
                        signal.get('take_profit_1', 0),
                        signal.get('take_profit_2', 0),
                        signal.get('take_profit_3', 0)
                    ],
                    'stopLoss': signal.get('stop_loss', 0),
                    'confidence': int(signal.get('confidence_score', 0.75) * 100),
                    'timeframe': '4H',
                    'status': 'active',
                    'created': format_brazilian_date(signal.get('processed_at', '')),
                    'analysis': f'Sinal capturado do grupo {signal.get("source", "Telegram")}',
                    'source': signal.get('source', 'Telegram Bot')
                })
            
            # Se há sinais do Telegram, usa eles
            if converted_signals:
                return jsonify(converted_signals)
    except Exception as e:
        print(f"Erro ao buscar sinais do Telegram: {e}")
    
    # Fallback para dados mock se API Telegram não estiver disponível
    signals = [
        {
            'id': 1,
            'pair': 'BTCUSDT',
            'direction': 'LONG',
            'entry': 115000,
            'currentPrice': 115045,
            'targets': [118500, 122000, 128000],
            'stopLoss': 110500,
            'confidence': 89,
            'timeframe': '1D',
            'status': 'active',
            'created': '07/08/2025 - 22:30',
            'analysis': 'BTC testando resistência em $115K com volume institucional forte.',
            'source': 'NexoCrypto IA'
        },
        {
            'id': 2,
            'pair': 'ETHUSDT',
            'direction': 'LONG',
            'entry': 3675,
            'currentPrice': 3674,
            'targets': [3850, 4100, 4400],
            'stopLoss': 3450,
            'confidence': 82,
            'timeframe': '4H',
            'status': 'active',
            'created': '07/08/2025 - 22:15',
            'analysis': 'ETH rompeu $3700 com força. Empresas públicas acumulando ETH.'
        }
    ]
    return jsonify(signals)

@app.route('/api/gems')
def get_gems():
    # Dados mock das gems
    gems = [
        {
            'id': 1,
            'name': 'Bitcoin Hyper',
            'symbol': 'BTHYP',
            'rating': 5,
            'potential': '1000%+',
            'category': 'Layer-2',
            'description': 'Layer-2 em presale com backing institucional'
        },
        {
            'id': 2,
            'name': 'Biconomy',
            'symbol': 'BICO',
            'rating': 4,
            'potential': '500%+',
            'category': 'Web3',
            'description': 'Web3 com backing Coinbase - Target $5+'
        }
    ]
    return jsonify(gems)

@app.route('/api/news')
def get_news():
    # Dados mock das notícias
    news = [
        {
            'id': 1,
            'title': 'SEC aprova resgates in-kind para ETFs',
            'impact': 8.5,
            'sentiment': 'BULLISH',
            'timestamp': '07/08/2025 - 22:45',
            'description': 'Decisão histórica facilita operações institucionais'
        },
        {
            'id': 2,
            'title': 'Empresas públicas acumulam ETH',
            'impact': 7.8,
            'sentiment': 'BULLISH',
            'timestamp': '07/08/2025 - 22:30',
            'description': 'Movimento massivo de adoção corporativa'
        }
    ]
    return jsonify(news)

@app.route('/api/telegram/generate-uuid', methods=['POST'])
def generate_telegram_uuid():
    """Gera UUID para validação Telegram"""
    try:
        response = requests.post(f"{TELEGRAM_API_URL}/generate-uuid", timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            return jsonify({'success': False, 'error': 'Erro ao gerar UUID'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/telegram/check-validation/<uuid_code>', methods=['GET'])
def check_telegram_validation(uuid_code):
    """Verifica se UUID foi validado"""
    try:
        response = requests.get(f"{TELEGRAM_API_URL}/check-validation/{uuid_code}", timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            return jsonify({'success': False, 'error': 'UUID não encontrado'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/telegram/user-groups/<uuid_code>', methods=['GET'])
def get_telegram_groups(uuid_code):
    """Retorna grupos conectados do usuário"""
    try:
        response = requests.get(f"{TELEGRAM_API_URL}/user-groups/{uuid_code}", timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            return jsonify({'success': False, 'groups': []}), 200
    except Exception as e:
        return jsonify({'success': False, 'groups': []}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

