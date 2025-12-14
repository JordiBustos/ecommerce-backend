"""
Honeypot Fields
Trap bots and automated attacks by including hidden fields
"""

from fastapi import HTTPException, status, Request
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timedelta
from collections import defaultdict
from app.core.logging_config import security_logger


class HoneypotTracker:
    """Track honeypot triggers to identify bots"""

    def __init__(self):
        self.triggered_ips = defaultdict(list)
        self.banned_ips = set()

    def record_trigger(self, ip: str, field: str):
        """Record a honeypot trigger"""
        now = datetime.utcnow()

        # Clean old triggers
        self.triggered_ips[ip] = [
            t for t in self.triggered_ips[ip] if now - t < timedelta(hours=24)
        ]

        self.triggered_ips[ip].append(now)

        security_logger.warning(f"Honeypot triggered by IP {ip} on field: {field}")

        # Ban IP after 3 triggers in 24 hours
        if len(self.triggered_ips[ip]) >= 3:
            self.banned_ips.add(ip)
            security_logger.critical(
                f"IP banned due to repeated honeypot triggers: {ip}"
            )

    def is_banned(self, ip: str) -> bool:
        """Check if IP is banned"""
        return ip in self.banned_ips


# Global tracker
honeypot_tracker = HoneypotTracker()


class HoneypotMixin(BaseModel):
    """Mixin to add honeypot fields to forms"""

    # Honeypot fields (should remain empty)
    website: Optional[str] = Field(None, description="Leave blank")
    company_name: Optional[str] = Field(None, description="Leave blank")

    def validate_honeypot(self, request: Request):
        """Validate honeypot fields"""
        ip = request.client.host if request.client else "unknown"

        if self.website or self.company_name:
            honeypot_tracker.record_trigger(ip, "website/company_name")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid form submission",
            )

        if honeypot_tracker.is_banned(ip):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
            )


class TimingHoneypot:
    """Detect bots based on form submission timing"""

    def __init__(self):
        self.form_starts = {}

    def start_timer(self, session_id: str):
        """Start timing for a form"""
        self.form_starts[session_id] = datetime.utcnow()

    def validate_timing(self, session_id: str, min_seconds: int = 3) -> bool:
        """Validate form wasn't submitted too quickly"""
        if session_id not in self.form_starts:
            return True  # No timing data, allow

        elapsed = (datetime.utcnow() - self.form_starts[session_id]).total_seconds()

        if elapsed < min_seconds:
            security_logger.warning(
                f"Form submitted too quickly: {session_id} ({elapsed}s)"
            )
            return False

        # Clean up
        del self.form_starts[session_id]
        return True


timing_honeypot = TimingHoneypot()
