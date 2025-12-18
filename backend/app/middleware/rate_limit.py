"""
Optional: Rate limiting middleware for live detection
Only needed if you want to prevent API abuse
"""
from fastapi import HTTPException, Request
from collections import defaultdict
import time

# Simple in-memory rate limiter
class RateLimiter:
    def __init__(self, max_requests=30, window_seconds=60):
        """
        Args:
            max_requests: Maximum requests allowed per window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)
    
    def check_rate_limit(self, client_id: str) -> bool:
        """Check if client has exceeded rate limit"""
        now = time.time()
        window_start = now - self.window_seconds
        
        # Clean old requests
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if req_time > window_start
        ]
        
        # Check if limit exceeded
        if len(self.requests[client_id]) >= self.max_requests:
            return False
        
        # Add current request
        self.requests[client_id].append(now)
        return True

# Global rate limiter instance
rate_limiter = RateLimiter(max_requests=30, window_seconds=60)  # 30 requests per minute

async def check_rate_limit(request: Request):
    """Middleware to check rate limits"""
    # Use IP address as client identifier
    client_id = request.client.host
    
    if not rate_limiter.check_rate_limit(client_id):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please slow down your requests."
        )