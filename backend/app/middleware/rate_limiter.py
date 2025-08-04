from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict, Tuple, Optional, Callable
import time
import redis
import logging

from app.core.config import settings
from app.core.security import log_security_violation

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
        
        # Define rate limits for different endpoints (requests per minute)
        self.endpoint_limits = {
            "/api/v1/auth/login": 10,  # More strict for login attempts
            "/api/v1/auth/register": 5,  # Very strict for registration
            "/api/v1/auth/2fa/verify": 15,  # Moderate for 2FA verification
            "/api/v1/auth/refresh": 20,  # Token refresh
            "/api/v1/auth/reset-password": 5,  # Password reset requests
            "/api/v1/auth/reset-password/confirm": 5,  # Password reset confirmation
            "/api/v1/auth/verify-email": 10,  # Email verification
            "default": settings.RATE_LIMIT_PER_MINUTE  # Default limit
        }
        
        # Progressive lockout periods (in seconds)
        # Each subsequent violation increases the lockout period
        self.lockout_periods = [
            60,     # 1 minute for first violation
            300,    # 5 minutes for second violation
            900,    # 15 minutes for third violation
            3600,   # 1 hour for fourth violation
            86400   # 24 hours for fifth and subsequent violations
        ]
        
        # Notification thresholds for suspicious activity
        self.notification_thresholds = {
            "violations": 3,  # Number of violations before notification
            "lockout_period": 900  # Notify on lockouts >= 15 minutes
        }
    
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
        path_key = f"rate_limit:{client_ip}:{request.url.path}"
        
        # Create lockout key
        lockout_key = f"lockout:{client_ip}"
        
        # Check if client is in lockout period
        if self.limiter.redis:
            try:
                lockout_ttl = self.limiter.redis.ttl(lockout_key)
                if lockout_ttl > 0:
                    logger.warning(f"Client {client_ip} is in lockout period for {lockout_ttl} more seconds")
                    
                    # Log security violation
                    log_security_violation(
                        "lockout_period_active",
                        {
                            "ip": client_ip,
                            "path": request.url.path,
                            "method": request.method,
                            "remaining_seconds": lockout_ttl
                        },
                        request
                    )
                    
                    # Instead of raising an exception, return a response
                    return JSONResponse(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        content={"detail": f"Too many requests. Please try again in {lockout_ttl} seconds."}
                    )
            except redis.RedisError:
                # If Redis fails, continue without lockout check
                pass
        
        # Get rate limit for this endpoint
        rate_limit = self.endpoint_limits.get(request.url.path, self.endpoint_limits["default"])
        
        # Check if rate limited
        if self.limiter.is_rate_limited(path_key, rate_limit, 60):
            logger.warning(f"Rate limit exceeded for {client_ip} on {request.url.path}")
            
            # Log rate limit exceeded
            log_security_violation(
                "rate_limit_exceeded",
                {
                    "ip": client_ip,
                    "path": request.url.path,
                    "method": request.method,
                    "limit": rate_limit
                },
                request
            )
            
            # Apply progressive lockout
            if self.limiter.redis:
                try:
                    # Get violation count
                    violation_key = f"violations:{client_ip}"
                    violations = self.limiter.redis.incr(violation_key)
                    self.limiter.redis.expire(violation_key, 86400)  # Expire after 24 hours
                    
                    # Determine lockout period based on violation count
                    lockout_index = min(violations - 1, len(self.lockout_periods) - 1)
                    lockout_period = self.lockout_periods[lockout_index]
                    
                    # Set lockout
                    self.limiter.redis.set(lockout_key, 1, ex=lockout_period)
                    
                    logger.warning(f"Client {client_ip} locked out for {lockout_period} seconds after {violations} violations")
                    
                    # Log lockout
                    log_security_violation(
                        "progressive_lockout_applied",
                        {
                            "ip": client_ip,
                            "path": request.url.path,
                            "method": request.method,
                            "violations": violations,
                            "lockout_period": lockout_period
                        },
                        request
                    )
                    
                    # Check if notification threshold is reached
                    if violations >= self.notification_thresholds["violations"] or \
                       lockout_period >= self.notification_thresholds["lockout_period"]:
                        # Log suspicious activity for notification
                        log_security_violation(
                            "suspicious_login_activity",
                            {
                                "ip": client_ip,
                                "path": request.url.path,
                                "method": request.method,
                                "violations": violations,
                                "lockout_period": lockout_period,
                                "requires_notification": True
                            },
                            request
                        )
                        
                        # TODO: Implement notification system (email, SMS, etc.)
                        # This would typically call a notification service
                    
                    # Instead of raising an exception, return a response
                    return JSONResponse(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        content={"detail": f"Too many requests. Please try again in {lockout_period} seconds."}
                    )
                except redis.RedisError:
                    # If Redis fails, use standard rate limit response
                    pass
            
            # Instead of raising an exception, return a response
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Rate limit exceeded. Please try again later."}
            )
        
        # Process request
        return await call_next(request)