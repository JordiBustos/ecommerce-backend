"""
Security Configuration
Centralized security settings - uses main app settings
"""

from app.core.config import settings

# Export main settings for use in security modules
security_settings = settings

# Additional constants not in environment
ALLOWED_FILE_TYPES = [".csv", ".jpg", ".jpeg", ".png", ".pdf"]
MAX_STRING_LENGTH = 10000
CSP_POLICY = "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; img-src 'self' data: https://cdn.jsdelivr.net; font-src 'self' data:;"
