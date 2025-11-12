"""
Rate Limiting Middleware für API-Endpunkte
"""
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Dict
import logging

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, list] = defaultdict(list)
    
    def _get_client_ip(self, request: Request) -> str:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0]
        return request.client.host if request.client else "unknown"
    
    def _clean_old_requests(self, client_ip: str):
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=1)
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if req_time > cutoff
        ]
    
    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith(("/static", "/pics", "/health")):
            return await call_next(request)
        
        client_ip = self._get_client_ip(request)
        self._clean_old_requests(client_ip)
        
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            logger.warning(f"Rate limit exceeded for {client_ip}")
            raise HTTPException(
                status_code=429,
                detail="Zu viele Anfragen. Bitte versuchen Sie es später erneut."
            )
        
        self.requests[client_ip].append(datetime.now(timezone.utc))
        response = await call_next(request)
        return response
