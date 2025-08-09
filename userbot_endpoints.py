"""
Endpoints do UserBot para integração com o backend
"""
import requests
import json
from flask import jsonify

USERBOT_API_URL = "http://localhost:5003"

def start_userbot_session(uuid, phone_number):
    """Inicia sessão do userbot com telefone"""
    try:
        response = requests.post(f"{USERBOT_API_URL}/api/userbot/start-session", 
                               json={
                                   "uuid": uuid,
                                   "phone_number": phone_number
                               }, 
                               timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "success": False,
                "error": f"Erro na API do userbot: {response.status_code}"
            }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"Erro de conexão com userbot: {str(e)}"
        }

def verify_userbot_code(uuid, phone_number, code):
    """Verifica código de autorização do userbot"""
    try:
        response = requests.post(f"{USERBOT_API_URL}/api/userbot/verify-code", 
                               json={
                                   "uuid": uuid,
                                   "phone_number": phone_number,
                                   "code": code
                               }, 
                               timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "success": False,
                "error": f"Erro na verificação: {response.status_code}"
            }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"Erro de conexão: {str(e)}"
        }

def get_userbot_groups(uuid):
    """Obtém grupos do usuário via userbot"""
    try:
        response = requests.get(f"{USERBOT_API_URL}/api/userbot/user-groups/{uuid}", 
                              timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "success": False,
                "error": f"Erro ao obter grupos: {response.status_code}"
            }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"Erro de conexão: {str(e)}"
        }

