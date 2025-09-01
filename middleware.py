import time
from collections import defaultdict
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware para controle de taxa de requisições"""
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(list)
    
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        
        current_time = time.time()
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if current_time - req_time < 60
        ]
        
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Máximo de {self.requests_per_minute} requisições por minuto excedido"
                }
            )
        
        self.requests[client_ip].append(current_time)
        
        response = await call_next(request)
        return response

class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware para logging de requisições"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        logger.info(f"Requisição {request.method} {request.url.path} de {request.client.host}")
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        
        logger.info(
            f"Resposta {response.status_code} para {request.method} {request.url.path} "
            f"em {process_time:.3f}s"
        )
        
        response.headers["X-Process-Time"] = str(process_time)
        
        return response

class SecurityMiddleware(BaseHTTPMiddleware):
    """Middleware para headers de segurança"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response