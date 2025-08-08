from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import requests
import hashlib
import secrets
import re
from datetime import datetime, timedelta
from telegram_mock import get_mock_validation, generate_mock_uuid

app = Flask(__name__)
CORS(app)

# Configuração para produção
if os.environ.get('FLASK_ENV') == 'production':
    app.config['DEBUG'] = False
else:
    app.config['DEBUG'] = True

# Banco de dados simples em memória para usuários
users_db = {}
verification_codes = {}
password_reset_tokens = {}

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

def hash_password(password):
    """Hash da senha usando SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def generate_verification_code():
    """Gera código de verificação de 6 dígitos"""
    return str(secrets.randbelow(900000) + 100000)

def validate_email(email):
    """Valida formato de e-mail"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Valida formato de telefone brasileiro"""
    # Remove caracteres não numéricos
    phone_clean = re.sub(r'[^\d]', '', phone)
    # Verifica se tem 10 ou 11 dígitos (com DDD)
    return len(phone_clean) in [10, 11] and phone_clean.startswith(('11', '12', '13', '14', '15', '16', '17', '18', '19', '21', '22', '24', '27', '28', '31', '32', '33', '34', '35', '37', '38', '41', '42', '43', '44', '45', '46', '47', '48', '49', '51', '53', '54', '55', '61', '62', '63', '64', '65', '66', '67', '68', '69', '71', '73', '74', '75', '77', '79', '81', '82', '83', '84', '85', '86', '87', '88', '89', '91', '92', '93', '94', '95', '96', '97', '98', '99'))

def send_sms_code(phone, code):
    """Simula envio de SMS (em produção, usar serviço real como Twilio)"""
    print(f"SMS enviado para {phone}: Código {code}")
    return True

def send_email_code(email, code):
    """Simula envio de e-mail (em produção, usar serviço real como SendGrid)"""
    print(f"E-mail enviado para {email}: Código {code}")
    return True

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
            return jsonify(response.json())
        else:
            # Fallback para dados mock
            return jsonify(generate_mock_uuid())
    except Exception as e:
        # Fallback para dados mock em caso de erro
        return jsonify(generate_mock_uuid())

@app.route('/api/telegram/check-validation/<uuid_code>', methods=['GET'])
def check_telegram_validation(uuid_code):
    """Verifica validação do UUID Telegram"""
    try:
        response = requests.get(f"{TELEGRAM_API_URL}/check-validation/{uuid_code}", timeout=5)
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            # Fallback para dados mock
            return jsonify(get_mock_validation(uuid_code))
    except Exception as e:
        # Fallback para dados mock em caso de erro
        return jsonify(get_mock_validation(uuid_code))

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

# Endpoints de Autenticação

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Endpoint para cadastro de usuário"""
    try:
        data = request.get_json()
        
        # Validação dos dados
        required_fields = ['name', 'email', 'phone', 'password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Campo {field} é obrigatório'}), 400
        
        email = data['email'].lower().strip()
        phone = re.sub(r'[^\d]', '', data['phone'])
        
        # Validações
        if not validate_email(email):
            return jsonify({'error': 'E-mail inválido'}), 400
        
        if not validate_phone(phone):
            return jsonify({'error': 'Telefone inválido'}), 400
        
        if len(data['password']) < 8:
            return jsonify({'error': 'Senha deve ter pelo menos 8 caracteres'}), 400
        
        # Verifica se usuário já existe
        if email in users_db:
            return jsonify({'error': 'E-mail já cadastrado'}), 400
        
        # Gera códigos de verificação
        email_code = generate_verification_code()
        sms_code = generate_verification_code()
        
        # Armazena dados temporários
        temp_user_id = secrets.token_urlsafe(16)
        verification_codes[temp_user_id] = {
            'user_data': {
                'name': data['name'].strip(),
                'email': email,
                'phone': phone,
                'password_hash': hash_password(data['password'])
            },
            'email_code': email_code,
            'sms_code': sms_code,
            'created_at': datetime.now(),
            'verified_email': False,
            'verified_sms': False
        }
        
        # Simula envio dos códigos
        send_email_code(email, email_code)
        send_sms_code(phone, sms_code)
        
        return jsonify({
            'success': True,
            'message': 'Códigos de verificação enviados',
            'temp_user_id': temp_user_id,
            'email_code': email_code,  # Para teste
            'sms_code': sms_code       # Para teste
        })
        
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

@app.route('/api/auth/verify', methods=['POST'])
def verify_codes():
    """Endpoint para verificar códigos de validação"""
    try:
        data = request.get_json()
        
        temp_user_id = data.get('temp_user_id')
        email_code = data.get('email_code')
        sms_code = data.get('sms_code')
        
        if not all([temp_user_id, email_code, sms_code]):
            return jsonify({'error': 'Dados incompletos'}), 400
        
        # Verifica se existe
        if temp_user_id not in verification_codes:
            return jsonify({'error': 'Sessão inválida ou expirada'}), 400
        
        verification_data = verification_codes[temp_user_id]
        
        # Verifica se não expirou (30 minutos)
        if datetime.now() - verification_data['created_at'] > timedelta(minutes=30):
            del verification_codes[temp_user_id]
            return jsonify({'error': 'Códigos expirados'}), 400
        
        # Verifica códigos
        if (email_code == verification_data['email_code'] and 
            sms_code == verification_data['sms_code']):
            
            # Cria usuário definitivo
            user_data = verification_data['user_data']
            user_id = secrets.token_urlsafe(16)
            
            users_db[user_data['email']] = {
                'id': user_id,
                'name': user_data['name'],
                'email': user_data['email'],
                'phone': user_data['phone'],
                'password_hash': user_data['password_hash'],
                'created_at': datetime.now(),
                'verified': True,
                'plan': 'free'  # Plano inicial
            }
            
            # Remove dados temporários
            del verification_codes[temp_user_id]
            
            return jsonify({
                'success': True,
                'message': 'Conta criada com sucesso',
                'user_id': user_id
            })
        else:
            return jsonify({'error': 'Códigos inválidos'}), 400
            
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Endpoint para login"""
    try:
        data = request.get_json()
        
        email = data.get('email', '').lower().strip()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'error': 'E-mail e senha são obrigatórios'}), 400
        
        # Verifica credenciais admin (mantém para testes)
        admin_credentials = [
            {'email': 'admin@nexocrypto.app', 'password': 'NexoCrypto2025!@#'},
            {'email': 'nexoadmin', 'password': 'Crypto@Admin123'}
        ]
        
        for admin in admin_credentials:
            if (email == admin['email'] or email == admin['email'].lower()) and password == admin['password']:
                return jsonify({
                    'success': True,
                    'message': 'Login realizado com sucesso',
                    'user': {
                        'id': 'admin',
                        'name': 'Administrador',
                        'email': admin['email'],
                        'plan': 'admin'
                    },
                    'token': 'admin_token'
                })
        
        # Verifica usuários cadastrados
        if email in users_db:
            user = users_db[email]
            if user['password_hash'] == hash_password(password):
                return jsonify({
                    'success': True,
                    'message': 'Login realizado com sucesso',
                    'user': {
                        'id': user['id'],
                        'name': user['name'],
                        'email': user['email'],
                        'plan': user['plan']
                    },
                    'token': secrets.token_urlsafe(32)
                })
        
        return jsonify({'error': 'Credenciais inválidas'}), 401
        
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

@app.route('/api/auth/forgot-password', methods=['POST'])
def forgot_password():
    """Endpoint para recuperação de senha"""
    try:
        data = request.get_json()
        email = data.get('email', '').lower().strip()
        
        if not email or not validate_email(email):
            return jsonify({'error': 'E-mail inválido'}), 400
        
        # Verifica se usuário existe
        if email in users_db:
            # Gera token de reset
            reset_token = secrets.token_urlsafe(32)
            password_reset_tokens[reset_token] = {
                'email': email,
                'created_at': datetime.now()
            }
            
            # Simula envio de e-mail
            print(f"E-mail de recuperação enviado para {email} com token: {reset_token}")
            
            return jsonify({
                'success': True,
                'message': 'E-mail de recuperação enviado',
                'reset_token': reset_token  # Para teste
            })
        else:
            # Por segurança, sempre retorna sucesso
            return jsonify({
                'success': True,
                'message': 'Se o e-mail existir, você receberá instruções de recuperação'
            })
            
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

@app.route('/api/auth/reset-password', methods=['POST'])
def reset_password():
    """Endpoint para redefinir senha"""
    try:
        data = request.get_json()
        
        reset_token = data.get('reset_token')
        new_password = data.get('new_password')
        
        if not reset_token or not new_password:
            return jsonify({'error': 'Token e nova senha são obrigatórios'}), 400
        
        if len(new_password) < 8:
            return jsonify({'error': 'Senha deve ter pelo menos 8 caracteres'}), 400
        
        # Verifica token
        if reset_token not in password_reset_tokens:
            return jsonify({'error': 'Token inválido'}), 400
        
        token_data = password_reset_tokens[reset_token]
        
        # Verifica se não expirou (1 hora)
        if datetime.now() - token_data['created_at'] > timedelta(hours=1):
            del password_reset_tokens[reset_token]
            return jsonify({'error': 'Token expirado'}), 400
        
        # Atualiza senha
        email = token_data['email']
        if email in users_db:
            users_db[email]['password_hash'] = hash_password(new_password)
            del password_reset_tokens[reset_token]
            
            return jsonify({
                'success': True,
                'message': 'Senha redefinida com sucesso'
            })
        else:
            return jsonify({'error': 'Usuário não encontrado'}), 404
            
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

