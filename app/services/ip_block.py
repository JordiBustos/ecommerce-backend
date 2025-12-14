from typing import Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.blocked_ip import BlockedIP
from app.models.whitelisted_ip import WhitelistedIP
from app.core.logging_config import log_security_event


class IPBlockService:
    """Service for managing IP blocking and whitelisting in database"""
    
    @staticmethod
    def is_ip_blocked(db: Session, ip_address: str) -> bool:
        """Check if an IP is currently blocked"""
        now = datetime.utcnow()
        
        blocked = db.query(BlockedIP).filter(
            and_(
                BlockedIP.ip_address == ip_address,
                BlockedIP.is_active == True,
                # Check if block is permanent (blocked_until is NULL) or not expired
                (BlockedIP.blocked_until.is_(None) | (BlockedIP.blocked_until > now))
            )
        ).first()
        
        return blocked is not None
    
    @staticmethod
    def block_ip(
        db: Session, 
        ip_address: str, 
        reason: str,
        duration_seconds: Optional[int] = None,
        blocked_by: str = "system",
        notes: Optional[str] = None,
        violation_count: int = 1
    ) -> BlockedIP:
        """Block an IP address"""
        # Check if already blocked
        existing = db.query(BlockedIP).filter(
            BlockedIP.ip_address == ip_address
        ).first()
        
        if existing:
            # Update existing block
            existing.reason = reason
            existing.is_active = True
            existing.blocked_at = datetime.utcnow()
            existing.blocked_until = (
                datetime.utcnow() + timedelta(seconds=duration_seconds)
                if duration_seconds else None
            )
            existing.blocked_by = blocked_by
            existing.notes = notes
            existing.violation_count += violation_count
            db.commit()
            db.refresh(existing)
            
            log_security_event(
                "warning",
                "IP block updated",
                {
                    "ip": ip_address,
                    "reason": reason,
                    "duration": duration_seconds,
                    "total_violations": existing.violation_count
                }
            )
            
            return existing
        else:
            # Create new block
            blocked_ip = BlockedIP(
                ip_address=ip_address,
                reason=reason,
                blocked_until=(
                    datetime.utcnow() + timedelta(seconds=duration_seconds)
                    if duration_seconds else None
                ),
                blocked_by=blocked_by,
                notes=notes,
                violation_count=violation_count
            )
            db.add(blocked_ip)
            db.commit()
            db.refresh(blocked_ip)
            
            log_security_event(
                "warning",
                "IP blocked",
                {
                    "ip": ip_address,
                    "reason": reason,
                    "duration": duration_seconds,
                    "violations": violation_count
                }
            )
            
            return blocked_ip
    
    @staticmethod
    def unblock_ip(db: Session, ip_address: str) -> bool:
        """Unblock an IP address"""
        blocked = db.query(BlockedIP).filter(
            BlockedIP.ip_address == ip_address
        ).first()
        
        if blocked:
            blocked.is_active = False
            db.commit()
            
            log_security_event(
                "info",
                "IP unblocked",
                {"ip": ip_address}
            )
            return True
        
        return False
    
    @staticmethod
    def get_blocked_ips(db: Session, active_only: bool = True) -> List[BlockedIP]:
        """Get list of blocked IPs"""
        query = db.query(BlockedIP)
        
        if active_only:
            now = datetime.utcnow()
            query = query.filter(
                and_(
                    BlockedIP.is_active == True,
                    (BlockedIP.blocked_until.is_(None) | (BlockedIP.blocked_until > now))
                )
            )
        
        return query.all()
    
    @staticmethod
    def cleanup_expired_blocks(db: Session) -> int:
        """Remove expired temporary blocks"""
        now = datetime.utcnow()
        
        expired = db.query(BlockedIP).filter(
            and_(
                BlockedIP.is_active == True,
                BlockedIP.blocked_until.isnot(None),
                BlockedIP.blocked_until <= now
            )
        ).all()
        
        count = len(expired)
        for block in expired:
            block.is_active = False
        
        db.commit()
        
        if count > 0:
            log_security_event(
                "info",
                f"Cleaned up {count} expired IP blocks",
                {"count": count}
            )
        
        return count
    
    @staticmethod
    def is_ip_whitelisted(db: Session, ip_address: str) -> bool:
        """Check if an IP is whitelisted"""
        whitelisted = db.query(WhitelistedIP).filter(
            WhitelistedIP.ip_address == ip_address
        ).first()
        
        return whitelisted is not None
    
    @staticmethod
    def whitelist_ip(
        db: Session, 
        ip_address: str, 
        description: str,
        added_by: str = "admin",
        notes: Optional[str] = None
    ) -> WhitelistedIP:
        """Add an IP to whitelist"""
        # Check if already whitelisted
        existing = db.query(WhitelistedIP).filter(
            WhitelistedIP.ip_address == ip_address
        ).first()
        
        if existing:
            log_security_event(
                "info",
                "IP already whitelisted",
                {"ip": ip_address}
            )
            return existing
        
        # Add to whitelist
        whitelisted_ip = WhitelistedIP(
            ip_address=ip_address,
            description=description,
            added_by=added_by,
            notes=notes
        )
        db.add(whitelisted_ip)
        db.commit()
        db.refresh(whitelisted_ip)
        
        log_security_event(
            "info",
            "IP whitelisted",
            {"ip": ip_address, "description": description}
        )
        
        return whitelisted_ip
    
    @staticmethod
    def remove_from_whitelist(db: Session, ip_address: str) -> bool:
        """Remove an IP from whitelist"""
        whitelisted = db.query(WhitelistedIP).filter(
            WhitelistedIP.ip_address == ip_address
        ).first()
        
        if whitelisted:
            db.delete(whitelisted)
            db.commit()
            
            log_security_event(
                "info",
                "IP removed from whitelist",
                {"ip": ip_address}
            )
            return True
        
        return False
    
    @staticmethod
    def get_whitelisted_ips(db: Session) -> List[WhitelistedIP]:
        """Get list of whitelisted IPs"""
        return db.query(WhitelistedIP).all()
