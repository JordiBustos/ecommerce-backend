"""
Security Middleware
Implements various security measures including rate limiting,
request validation, and security headers
"""

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from typing import Callable, Dict, List
from datetime import datetime, timedelta
from collections import defaultdict
import re
from app.core.security_config import security_settings, CSP_POLICY
from app.core.logging_config import security_logger
from app.db.base import SessionLocal


class RateLimitEntry:
    """Track rate limit for an IP address"""

    def __init__(self):
        self.minute_requests: List[datetime] = []
        self.hour_requests: List[datetime] = []
        self.login_minute_requests: List[datetime] = []
        self.login_hour_requests: List[datetime] = []


class SecurityMiddleware(BaseHTTPMiddleware):
    """
    Comprehensive security middleware implementing:
    - Rate limiting
    - IP blocking/whitelisting
    - Request size limits
    - Security headers
    - Suspicious activity detection
    """

    def __init__(self, app):
        super().__init__(app)
        self.rate_limits: Dict[str, RateLimitEntry] = defaultdict(RateLimitEntry)
        self.suspicious_ips: Dict[str, int] = defaultdict(int)

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request"""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    def _is_ip_blocked(self, ip: str) -> bool:
        """Check if IP is blocked in database"""
        from app.services.ip_block import IPBlockService

        # Check database
        db = SessionLocal()
        try:
            if IPBlockService.is_ip_blocked(db, ip):
                return True

            # Auto-block IPs with too many violations (only if enabled)
            if security_settings.AUTO_BLOCK_ENABLED and self.suspicious_ips.get(ip, 0) >= 10:
                # Add to database with 24-hour block
                IPBlockService.block_ip(
                    db,
                    ip,
                    reason="Auto-blocked: 10+ security violations",
                    duration_seconds=86400,  # 24 hours
                    blocked_by="auto",
                    violation_count=self.suspicious_ips[ip],
                )
                security_logger.warning(f"Auto-blocked suspicious IP: {ip}")
                return True
        finally:
            db.close()

        return False

    def _is_ip_whitelisted(self, ip: str) -> bool:
        """Check if IP is in whitelist (database) or localhost"""
        from app.services.ip_block import IPBlockService

        # Always allow localhost/127.0.0.1
        if ip in ["127.0.0.1", "localhost", "::1"]:
            return True

        db = SessionLocal()
        try:
            return IPBlockService.is_ip_whitelisted(db, ip)
        finally:
            db.close()

    def _check_rate_limit(self, ip: str, path: str) -> bool:
        """Check if request exceeds rate limits"""
        if not security_settings.RATE_LIMIT_ENABLED:
            return True

        now = datetime.utcnow()
        entry = self.rate_limits[ip]

        # Clean old entries
        entry.minute_requests = [
            t for t in entry.minute_requests if now - t < timedelta(minutes=1)
        ]
        entry.hour_requests = [
            t for t in entry.hour_requests if now - t < timedelta(hours=1)
        ]

        # Check login endpoints separately
        is_login = "/auth/login" in path or "/auth/register" in path

        if is_login:
            entry.login_minute_requests = [
                t for t in entry.login_minute_requests if now - t < timedelta(minutes=1)
            ]
            entry.login_hour_requests = [
                t for t in entry.login_hour_requests if now - t < timedelta(hours=1)
            ]

            if (
                len(entry.login_minute_requests)
                >= security_settings.RATE_LIMIT_LOGIN_PER_MINUTE
            ):
                return False
            if (
                len(entry.login_hour_requests)
                >= security_settings.RATE_LIMIT_LOGIN_PER_HOUR
            ):
                return False

            entry.login_minute_requests.append(now)
            entry.login_hour_requests.append(now)

        # Check general rate limits
        if len(entry.minute_requests) >= security_settings.RATE_LIMIT_PER_MINUTE:
            return False
        if len(entry.hour_requests) >= security_settings.RATE_LIMIT_PER_HOUR:
            return False

        entry.minute_requests.append(now)
        entry.hour_requests.append(now)

        return True

    def _validate_request_size(self, request: Request) -> bool:
        """Validate request content length"""
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > security_settings.MAX_REQUEST_SIZE:
            return False
        return True

    def _detect_sql_injection(self, value: str) -> bool:
        """Detect potential SQL injection patterns"""
        sql_patterns = [
            r"(\bUNION\b.*\bSELECT\b)",
            r"(\bDROP\b.*\bTABLE\b)",
            r"(\bINSERT\b.*\bINTO\b)",
            r"(\bDELETE\b.*\bFROM\b)",
            r"(\bEXEC\b.*\()",
            r"(--\s*$)",
            r"(;\s*DROP\s+)",
            r"('.*OR.*'.*=.*')",
            r"(1=1)",
            r"(\bOR\b.*\d+\s*=\s*\d+)",
        ]

        for pattern in sql_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                return True
        return False

    def _detect_xss(self, value: str) -> bool:
        """Detect potential XSS patterns"""
        xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",
            r"<iframe",
            r"<object",
            r"<embed",
        ]

        for pattern in xss_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                return True
        return False

    def _add_security_headers(self, response: Response) -> Response:
        """Add security headers to response"""
        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Enable XSS protection
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        # HSTS (HTTP Strict Transport Security)
        if security_settings.ENABLE_HSTS:
            response.headers["Strict-Transport-Security"] = (
                f"max-age={security_settings.HSTS_MAX_AGE}; includeSubDomains"
            )

        # Content Security Policy
        if security_settings.ENABLE_CSP:
            response.headers["Content-Security-Policy"] = CSP_POLICY

        # Referrer Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Permissions Policy
        response.headers["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=()"
        )

        return response

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request through security checks"""
        client_ip = self._get_client_ip(request)
        path = request.url.path

        # Check IP blocking
        if self._is_ip_blocked(client_ip):
            security_logger.warning(f"Blocked request from IP: {client_ip}")
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": "Access denied"},
            )

        # Check IP whitelist for admin endpoints only (not all DELETE/PUT)
        if "/admin" in path:
            if not self._is_ip_whitelisted(client_ip):
                security_logger.warning(
                    f"Unauthorized IP for admin action: {client_ip}"
                )
                self.suspicious_ips[client_ip] += 1
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={"detail": "Access denied"},
                )

        # Rate limiting
        if not self._check_rate_limit(client_ip, path):
            security_logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            self.suspicious_ips[client_ip] += 1
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Too many requests. Please try again later."},
            )

        # Request size validation
        if not self._validate_request_size(request):
            security_logger.warning(f"Request too large from IP: {client_ip}")
            return JSONResponse(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                content={"detail": "Request entity too large"},
            )

        # Check query parameters for malicious patterns
        query_params = str(request.query_params)
        if self._detect_sql_injection(query_params):
            security_logger.error(
                f"SQL injection attempt from IP: {client_ip} - Query: {query_params}"
            )
            self.suspicious_ips[client_ip] += 3
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": "Invalid request"},
            )

        if self._detect_xss(query_params):
            security_logger.error(
                f"XSS attempt from IP: {client_ip} - Query: {query_params}"
            )
            self.suspicious_ips[client_ip] += 3
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": "Invalid request"},
            )

        # Process request
        try:
            response = await call_next(request)
            response = self._add_security_headers(response)
            return response
        except Exception as e:
            security_logger.error(
                f"Error processing request from {client_ip}: {str(e)}"
            )
            raise


def setup_cors(app):
    """Configure CORS middleware"""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=security_settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
        max_age=3600,
    )
