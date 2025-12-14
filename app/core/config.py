from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    PROJECT_NAME: str = "E-Commerce API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Database
    DATABASE_URL: str

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    # Security Settings
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    RATE_LIMIT_LOGIN_PER_MINUTE: int = 5
    RATE_LIMIT_LOGIN_PER_HOUR: int = 20
    MAX_LOGIN_ATTEMPTS: int = 5
    ACCOUNT_LOCKOUT_DURATION: int = 900
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_REQUIRE_UPPERCASE: bool = True
    PASSWORD_REQUIRE_LOWERCASE: bool = True
    PASSWORD_REQUIRE_DIGITS: bool = True
    PASSWORD_REQUIRE_SPECIAL: bool = True
    MAX_REQUEST_SIZE: int = 10485760
    MAX_FILE_SIZE: int = 5242880
    ENABLE_HSTS: bool = True
    HSTS_MAX_AGE: int = 31536000
    ENABLE_CSP: bool = True
    HONEYPOT_BAN_THRESHOLD: int = 3
    HONEYPOT_BAN_DURATION: int = 86400
    MIN_FORM_SUBMIT_TIME: int = 3
    SANITIZE_HTML: bool = True
    CSRF_ENABLED: bool = False
    AUTO_BLOCK_ENABLED: bool = False

    # Stripe
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""

    # Email
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAILS_FROM_EMAIL: str = ""

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""
    CACHE_TTL: int = 300  # Cache TTL in seconds (5 minutes)

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
