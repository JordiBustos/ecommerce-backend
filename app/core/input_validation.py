"""Input Validation and Sanitization
Protects against injection attacks, XSS, and malicious inputs
"""

import re
import html
from typing import Any, Optional, Set
from pathlib import Path
from fastapi import HTTPException, status
from app.core.security_config import security_settings, MAX_STRING_LENGTH
from app.core.logging_config import security_logger

# Load common passwords from file (lazy loading)
_common_passwords: Optional[Set[str]] = None


def _load_common_passwords() -> Set[str]:
    """Load common passwords from file"""
    global _common_passwords
    if _common_passwords is None:
        passwords_file = Path(__file__).parent / "assets" / "10k-most-common.txt"
        if passwords_file.exists():
            with open(passwords_file, "r", encoding="utf-8") as f:
                _common_passwords = {line.strip().lower() for line in f if line.strip()}
        else:
            _common_passwords = set()
    return _common_passwords


class InputSanitizer:
    """
    Sanitizes and validates user inputs to prevent security vulnerabilities
    """

    @staticmethod
    def sanitize_string(value: str, max_length: Optional[int] = None) -> str:
        """Sanitize string input"""
        if not isinstance(value, str):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid input type"
            )

        # Remove null bytes
        value = value.replace("\x00", "")

        # Limit length
        max_len = max_length or MAX_STRING_LENGTH
        if len(value) > max_len:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Input too long. Maximum {max_len} characters allowed",
            )

        # Sanitize HTML if enabled
        if security_settings.SANITIZE_HTML:
            value = html.escape(value)

        return value.strip()

    @staticmethod
    def sanitize_email(email: str) -> str:
        """Validate and sanitize email"""
        email = email.strip().lower()

        # Basic email regex
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email format"
            )

        if len(email) > 254:  # RFC 5321
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Email too long"
            )

        return email

    @staticmethod
    def sanitize_phone(phone: str) -> str:
        """Validate and sanitize phone number"""
        # Remove all non-numeric characters except +
        phone = re.sub(r"[^\d+]", "", phone)

        # Basic phone validation (international format)
        if not re.match(r"^\+?\d{7,15}$", phone):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid phone format"
            )

        return phone

    @staticmethod
    def sanitize_slug(slug: str) -> str:
        """Validate URL slug"""
        slug = slug.lower().strip()

        # Only allow alphanumeric, hyphens, underscores
        if not re.match(r"^[a-z0-9-_]+$", slug):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid slug format. Only lowercase letters, numbers, hyphens and underscores allowed",
            )

        if len(slug) > 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Slug too long"
            )

        return slug

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Validate and sanitize filename"""
        # Remove directory traversal attempts
        filename = filename.replace("../", "").replace("..\\", "")

        # Only allow safe characters
        filename = re.sub(r"[^a-zA-Z0-9._-]", "_", filename)

        # Check file extension
        if "." in filename:
            ext = "." + filename.rsplit(".", 1)[1].lower()
            if ext not in security_settings.ALLOWED_FILE_TYPES:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File type not allowed. Allowed types: {', '.join(security_settings.ALLOWED_FILE_TYPES)}",
                )

        if len(filename) > 255:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Filename too long"
            )

        return filename

    @staticmethod
    def detect_sql_injection(value: str) -> bool:
        """Detect SQL injection patterns"""
        dangerous_patterns = [
            r"(\bunion\b.*\bselect\b)",
            r"(\bdrop\b.*\btable\b)",
            r"(\binsert\b.*\binto\b)",
            r"(\bdelete\b.*\bfrom\b)",
            r"(\bexec\b.*\()",
            r"(--)",
            r"(;.*drop)",
            r"('.*or.*'.*=.*')",
            r"(admin'--)",
            r"(1=1|2=2)",
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                security_logger.critical(f"SQL injection detected: {value}")
                return True
        return False

    @staticmethod
    def detect_xss(value: str) -> bool:
        """Detect XSS patterns"""
        xss_patterns = [
            r"<script.*?>.*?</script>",
            r"javascript:",
            r"on\w+\s*=\s*['\"]",
            r"<iframe",
            r"<object",
            r"<embed",
            r"<img.*?onerror",
            r"eval\(",
        ]

        for pattern in xss_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                security_logger.critical(f"XSS attempt detected: {value}")
                return True
        return False

    @staticmethod
    def validate_and_sanitize(value: Any, field_type: str = "string") -> Any:
        """Main validation dispatcher"""
        if value is None:
            return None

        if isinstance(value, str):
            # Check for attacks
            if InputSanitizer.detect_sql_injection(value):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid input detected",
                )

            if InputSanitizer.detect_xss(value):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid input detected",
                )

            # Type-specific sanitization
            if field_type == "email":
                return InputSanitizer.sanitize_email(value)
            elif field_type == "phone":
                return InputSanitizer.sanitize_phone(value)
            elif field_type == "slug":
                return InputSanitizer.sanitize_slug(value)
            elif field_type == "filename":
                return InputSanitizer.sanitize_filename(value)
            else:
                return InputSanitizer.sanitize_string(value)

        return value


def validate_password_strength(password: str) -> bool:
    """Validate password complexity requirements"""
    if len(password) < security_settings.PASSWORD_MIN_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Password must be at least {security_settings.PASSWORD_MIN_LENGTH} characters long",
        )

    if security_settings.PASSWORD_REQUIRE_UPPERCASE and not re.search(
        r"[A-Z]", password
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must contain at least one uppercase letter",
        )

    if security_settings.PASSWORD_REQUIRE_LOWERCASE and not re.search(
        r"[a-z]", password
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must contain at least one lowercase letter",
        )

    if security_settings.PASSWORD_REQUIRE_DIGITS and not re.search(r"\d", password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must contain at least one digit",
        )

    if security_settings.PASSWORD_REQUIRE_SPECIAL and not re.search(
        r'[!@#$%^&*(),.?":{}|<>]', password
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must contain at least one special character",
        )

    # Check for common passwords from file
    common_passwords = _load_common_passwords()
    if password.lower() in common_passwords:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password is too common. Please choose a stronger password",
        )

    return True
