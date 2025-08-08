# Mock data para testes de Telegram
TELEGRAM_MOCK_DATA = {
    "CRP-KTT5GM69-120S-9C19": {
        "validated": True,
        "username": "usuario_teste",
        "telegram_id": 123456789
    },
    "CRP-HN6952FJ-N0FJ-P4DB": {
        "validated": True,
        "username": "nexocrypto_user",
        "telegram_id": 987654321
    }
}

def get_mock_validation(uuid_code):
    """Retorna dados mock para validação"""
    if uuid_code in TELEGRAM_MOCK_DATA:
        data = TELEGRAM_MOCK_DATA[uuid_code]
        return {
            'success': True,
            'validated': data['validated'],
            'username': data['username'],
            'telegram_id': data['telegram_id']
        }
    return {'success': False, 'error': 'UUID não encontrado'}

def generate_mock_uuid():
    """Gera UUID mock"""
    import random
    import string
    
    def random_string(length):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
    
    uuid = f"CRP-{random_string(8)}-{random_string(4)}-{random_string(4)}"
    return {
        'success': True,
        'uuid': uuid,
        'bot_username': '@nexocrypto_trading_bot',
        'validation_command': f'/validate {uuid}'
    }

