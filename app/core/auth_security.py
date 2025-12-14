"""
Authentication Security
Implements account lockout, failed login tracking, and session management
"""

from datetime import datetime, timedelta
from typing import Optional, Dict
from collections import defaultdict
from app.core.security_config import security_settings
from app.core.logging_config import security_logger


class LoginAttemptTracker:
    """Track failed login attempts and enforce account lockout"""

    def __init__(self):
        self.failed_attempts: Dict[str, list] = defaultdict(list)
        self.locked_accounts: Dict[str, datetime] = {}

    def record_failed_attempt(self, identifier: str, ip: str):
        """Record a failed login attempt"""
        now = datetime.utcnow()

        # Clean old attempts (older than 1 hour)
        self.failed_attempts[identifier] = [
            attempt
            for attempt in self.failed_attempts[identifier]
            if now - attempt < timedelta(hours=1)
        ]

        self.failed_attempts[identifier].append(now)

        # Check if account should be locked
        if (
            len(self.failed_attempts[identifier])
            >= security_settings.MAX_LOGIN_ATTEMPTS
        ):
            self.locked_accounts[identifier] = now
            security_logger.warning(
                f"Account locked due to multiple failed attempts: {identifier} from IP: {ip}"
            )

    def record_successful_login(self, identifier: str):
        """Clear failed attempts on successful login"""
        if identifier in self.failed_attempts:
            del self.failed_attempts[identifier]
        if identifier in self.locked_accounts:
            del self.locked_accounts[identifier]

    def is_locked(self, identifier: str) -> bool:
        """Check if account is locked"""
        if identifier not in self.locked_accounts:
            return False

        locked_time = self.locked_accounts[identifier]
        now = datetime.utcnow()

        # Check if lockout duration has passed
        if now - locked_time > timedelta(
            seconds=security_settings.ACCOUNT_LOCKOUT_DURATION
        ):
            del self.locked_accounts[identifier]
            if identifier in self.failed_attempts:
                del self.failed_attempts[identifier]
            return False

        return True

    def get_remaining_lockout_time(self, identifier: str) -> Optional[int]:
        """Get remaining lockout time in seconds"""
        if identifier not in self.locked_accounts:
            return None

        locked_time = self.locked_accounts[identifier]
        elapsed = (datetime.utcnow() - locked_time).total_seconds()
        remaining = security_settings.ACCOUNT_LOCKOUT_DURATION - elapsed

        return max(0, int(remaining))


# Global instance
login_tracker = LoginAttemptTracker()
