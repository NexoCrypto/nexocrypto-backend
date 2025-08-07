from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Configuração para produção
if os.environ.get('FLASK_ENV') == 'production':
    app.config['DEBUG'] = False
else:
    app.config['DEBUG'] = True

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
    # Dados mock dos sinais
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
            'analysis': 'BTC testando resistência em $115K com volume institucional forte.'
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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

