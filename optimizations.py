"""
Otimizações de Performance para Backend NexoCrypto
Implementa cache, compressão e otimizações de banco de dados
"""

import os
import gzip
import json
import time
import sqlite3
import hashlib
from functools import wraps
from datetime import datetime, timedelta
from flask import request, jsonify, g
from flask_caching import Cache
import redis

class PerformanceOptimizer:
    def __init__(self, app=None):
        self.app = app
        self.cache = None
        self.redis_client = None
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Inicializa otimizações no app Flask"""
        self.app = app
        
        # Configuração de cache
        cache_config = {
            'CACHE_TYPE': 'simple',  # Usar Redis em produção
            'CACHE_DEFAULT_TIMEOUT': 300
        }
        
        self.cache = Cache(app, config=cache_config)
        
        # Middleware de compressão
        app.after_request(self.compress_response)
        
        # Middleware de cache de headers
        app.after_request(self.add_cache_headers)
        
        # Middleware de métricas
        app.before_request(self.start_timer)
        app.after_request(self.end_timer)
        
        # Pool de conexões do banco
        self.init_db_pool()
    
    def init_db_pool(self):
        """Inicializa pool de conexões do banco"""
        # Em produção, usar um pool real como SQLAlchemy
        pass
    
    def compress_response(self, response):
        """Comprime respostas grandes"""
        if (response.status_code == 200 and 
            'gzip' in request.headers.get('Accept-Encoding', '') and
            len(response.data) > 1000):  # Só comprime se > 1KB
            
            try:
                compressed_data = gzip.compress(response.data)
                response.data = compressed_data
                response.headers['Content-Encoding'] = 'gzip'
                response.headers['Content-Length'] = len(compressed_data)
            except:
                pass  # Se falhar, retorna sem compressão
        
        return response
    
    def add_cache_headers(self, response):
        """Adiciona headers de cache apropriados"""
        if request.endpoint:
            # Cache para recursos estáticos
            if request.endpoint in ['static']:
                response.headers['Cache-Control'] = 'public, max-age=31536000'  # 1 ano
            
            # Cache para API de dados
            elif request.endpoint.startswith('api.'):
                if 'health' in request.endpoint:
                    response.headers['Cache-Control'] = 'no-cache'
                else:
                    response.headers['Cache-Control'] = 'public, max-age=60'  # 1 minuto
            
            # Headers de segurança
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['X-Frame-Options'] = 'DENY'
            response.headers['X-XSS-Protection'] = '1; mode=block'
        
        return response
    
    def start_timer(self):
        """Inicia timer para métricas"""
        g.start_time = time.time()
    
    def end_timer(self, response):
        """Finaliza timer e adiciona métricas"""
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            response.headers['X-Response-Time'] = f"{duration:.3f}s"
        
        return response
    
    def cached(self, timeout=300, key_prefix=''):
        """Decorator para cache de funções"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                # Gera chave de cache
                cache_key = f"{key_prefix}:{f.__name__}:{hashlib.md5(str(args + tuple(kwargs.items())).encode()).hexdigest()}"
                
                # Tenta buscar no cache
                result = self.cache.get(cache_key)
                if result is not None:
                    return result
                
                # Executa função e salva no cache
                result = f(*args, **kwargs)
                self.cache.set(cache_key, result, timeout=timeout)
                
                return result
            
            return decorated_function
        return decorator
    
    def cache_api_response(self, timeout=60):
        """Decorator para cache de respostas da API"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                # Gera chave baseada na URL e parâmetros
                cache_key = f"api:{request.endpoint}:{hashlib.md5(request.url.encode()).hexdigest()}"
                
                # Verifica cache
                cached_response = self.cache.get(cache_key)
                if cached_response:
                    response = jsonify(cached_response)
                    response.headers['X-Cache'] = 'HIT'
                    return response
                
                # Executa função
                result = f(*args, **kwargs)
                
                # Salva no cache se for sucesso
                if hasattr(result, 'status_code') and result.status_code == 200:
                    try:
                        data = result.get_json()
                        self.cache.set(cache_key, data, timeout=timeout)
                        result.headers['X-Cache'] = 'MISS'
                    except:
                        pass
                
                return result
            
            return decorated_function
        return decorator

class DatabaseOptimizer:
    def __init__(self, db_path):
        self.db_path = db_path
        self.connection_pool = []
        self.max_connections = 10
    
    def get_connection(self):
        """Obtém conexão do pool"""
        if self.connection_pool:
            return self.connection_pool.pop()
        else:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row  # Permite acesso por nome
            return conn
    
    def return_connection(self, conn):
        """Retorna conexão ao pool"""
        if len(self.connection_pool) < self.max_connections:
            self.connection_pool.append(conn)
        else:
            conn.close()
    
    def execute_query(self, query, params=None, fetch=False):
        """Executa query com pool de conexões"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if fetch:
                if fetch == 'one':
                    result = cursor.fetchone()
                else:
                    result = cursor.fetchall()
            else:
                result = cursor.rowcount
                conn.commit()
            
            return result
            
        finally:
            self.return_connection(conn)
    
    def optimize_database(self):
        """Executa otimizações no banco"""
        optimizations = [
            "PRAGMA journal_mode = WAL",
            "PRAGMA synchronous = NORMAL", 
            "PRAGMA cache_size = 10000",
            "PRAGMA temp_store = MEMORY",
            "VACUUM",
            "ANALYZE"
        ]
        
        for optimization in optimizations:
            try:
                self.execute_query(optimization)
            except Exception as e:
                print(f"Erro na otimização {optimization}: {e}")

class APIRateLimiter:
    def __init__(self):
        self.requests = {}
        self.limits = {
            'default': {'requests': 100, 'window': 3600},  # 100 req/hora
            'auth': {'requests': 10, 'window': 300},       # 10 req/5min
            'data': {'requests': 1000, 'window': 3600}     # 1000 req/hora
        }
    
    def is_allowed(self, client_ip, endpoint_type='default'):
        """Verifica se requisição é permitida"""
        now = time.time()
        limit_config = self.limits.get(endpoint_type, self.limits['default'])
        
        # Limpa requisições antigas
        if client_ip in self.requests:
            self.requests[client_ip] = [
                req_time for req_time in self.requests[client_ip]
                if now - req_time < limit_config['window']
            ]
        else:
            self.requests[client_ip] = []
        
        # Verifica limite
        if len(self.requests[client_ip]) >= limit_config['requests']:
            return False
        
        # Adiciona requisição atual
        self.requests[client_ip].append(now)
        return True
    
    def rate_limit(self, endpoint_type='default'):
        """Decorator para rate limiting"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                client_ip = request.remote_addr
                
                if not self.is_allowed(client_ip, endpoint_type):
                    return jsonify({
                        'error': 'Rate limit exceeded',
                        'message': 'Muitas requisições. Tente novamente mais tarde.'
                    }), 429
                
                return f(*args, **kwargs)
            
            return decorated_function
        return decorator

class MetricsCollector:
    def __init__(self):
        self.metrics = {
            'requests_total': 0,
            'requests_by_endpoint': {},
            'response_times': [],
            'errors_total': 0,
            'cache_hits': 0,
            'cache_misses': 0
        }
    
    def record_request(self, endpoint, response_time, status_code):
        """Registra métricas de requisição"""
        self.metrics['requests_total'] += 1
        
        if endpoint not in self.metrics['requests_by_endpoint']:
            self.metrics['requests_by_endpoint'][endpoint] = 0
        self.metrics['requests_by_endpoint'][endpoint] += 1
        
        self.metrics['response_times'].append(response_time)
        
        # Mantém apenas últimas 1000 medições
        if len(self.metrics['response_times']) > 1000:
            self.metrics['response_times'] = self.metrics['response_times'][-1000:]
        
        if status_code >= 400:
            self.metrics['errors_total'] += 1
    
    def record_cache_hit(self):
        """Registra cache hit"""
        self.metrics['cache_hits'] += 1
    
    def record_cache_miss(self):
        """Registra cache miss"""
        self.metrics['cache_misses'] += 1
    
    def get_metrics(self):
        """Retorna métricas atuais"""
        avg_response_time = 0
        if self.metrics['response_times']:
            avg_response_time = sum(self.metrics['response_times']) / len(self.metrics['response_times'])
        
        cache_hit_rate = 0
        total_cache_requests = self.metrics['cache_hits'] + self.metrics['cache_misses']
        if total_cache_requests > 0:
            cache_hit_rate = self.metrics['cache_hits'] / total_cache_requests * 100
        
        return {
            'requests_total': self.metrics['requests_total'],
            'requests_by_endpoint': self.metrics['requests_by_endpoint'],
            'avg_response_time': round(avg_response_time, 3),
            'errors_total': self.metrics['errors_total'],
            'cache_hit_rate': round(cache_hit_rate, 2),
            'uptime': time.time() - getattr(self, 'start_time', time.time())
        }

# Instâncias globais
performance_optimizer = PerformanceOptimizer()
db_optimizer = DatabaseOptimizer('/home/ubuntu/nexocrypto-telegram/nexocrypto.db')
rate_limiter = APIRateLimiter()
metrics_collector = MetricsCollector()

# Funções de conveniência
def init_optimizations(app):
    """Inicializa todas as otimizações"""
    performance_optimizer.init_app(app)
    db_optimizer.optimize_database()
    metrics_collector.start_time = time.time()

def get_performance_metrics():
    """Retorna métricas de performance"""
    return metrics_collector.get_metrics()

