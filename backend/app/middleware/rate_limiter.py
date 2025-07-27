from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict, Tuple, Optional, Callable
import time
import redis
import logging

from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RateLimiter:
    """Rate limiter using Redis"""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        """
        Initialize the rate limiter.
        
        Args:
            redis_client: Optional Redis client, will create one if not provided
        """
        if redis_client:
            self.redis = redis_client
        else:
            try:
                self.redis = redis.Redis(
                    host=settings.REDIS_HOST,
                    port=settings.REDIS_PORT,
                    db=settings.REDIS_DB
                )
                # Test connection
                self.redis.ping()
                logger.info("Connected to Redis for rate limiting")
            except redis.ConnectionError:
                logger.warning("Redis connection failed, using in-memory rate limiting")
                self.redis = None
        
        # In-memory fallback
        self.in_memory_store: Dict[str, Tuple[int, float]] = {}
    
    def is_rate_limited(self, key: str, limit: int, window: int) -> bool:
        """
        Check if a key is rate limited.
        
        Args:
            key: The key to check (usually IP address or user ID)
            limit: Maximum number of requests allowed in the window
            window: Time window in seconds
            
        Returns:
            bool: True if rate limited, False otherwise
        """
        current_time = time.time()
        
        if self.redis:
            # Use Redis for distributed rate limiting
            try:
                pipe = self.redis.pipeline()
                pipe.incr(key)
                pipe.expire(key, window)
                result = pipe.execute()
                
                request_count = result[0]
                
                return request_count > limit
            except redis.RedisError as e:
                logger.error(f"Redis error in rate limiter: {str(e)}")
                # Fall back to in-memory rate limiting
                return self._in_memory_is_rate_limited(key, limit, window, current_time)
        else:
            # Use in-memory rate limiting
            return self._in_memory_is_rate_limited(key, limit, window, current_time)
    
    def _in_memory_is_rate_limited(self, key: str, limit: int, window: int, current_time: float) -> bool:
        """
        In-memory implementation of rate limiting.
        
        Args:
            key: The key to check
            limit: Maximum number of requests allowed in the window
            window: Time window in seconds
            current_time: Current time
            
        Returns:
            bool: True if rate limited, False otherwise
        """
        # Clean up expired entries
        self._cleanup_expired(current_time, window)
        
        if key in self.in_memory_store:
            count, _ = self.in_memory_store[key]
            self.in_memory_store[key] = (count + 1, current_time)
            return count + 1 > limit
        else:
            self.in_memory_store[key] = (1, current_time)
            return False
    
    def _cleanup_expired(self, current_time: float, window: int) -> None:
        """
        Clean up expired entries from in-memory store.
        
        Args:
            current_time: Current time
            window: Time window in seconds
        """
        keys_to_delete = []
        for key, (_, timestamp) in self.in_memory_store.items():
            if current_time - timestamp > window:
                keys_to_delete.append(key)
        
        for key in keys_to_delete:
            del self.in_memory_store[key]


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting"""
    
    def __init__(self, app, redis_client: Optional[redis.Redis] = None):
        """
        Initialize the middleware.
        
        Args:
            app: FastAPI application
            redis_client: Optional Redis client
        """
        super().__init__(app)
        self.limiter = RateLimiter(redis_client)
        self.rate_limit_per_minute = settings.RATE_LIMIT_PER_MINUTE
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request and apply rate limiting.
        
        Args:
            request: FastAPI request
            call_next: Next middleware or endpoint
            
        Returns:
            Response: FastAPI response
        """
        # Skip rate limiting for non-auth endpoints
        if not request.url.path.startswith("/api/v1/auth"):
            return await call_next(request)
        
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Create rate limit key
        key = f"rate_limit:{client_ip}:{request.url.path}"
        
        # Check if rate limited
        if self.limiter.is_rate_limited(key, self.rate_limit_per_minute, 60):
            logger.warning(f"Rate limit exceeded for {client_ip} on {request.url.path}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later."
            )
        
        # Process request
        return await call_next(request)