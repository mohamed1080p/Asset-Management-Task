from sqlalchemy.orm import Session
from typing import Tuple, Optional
import hashlib
import secrets

from ..config import settings
from ..models import ApiKey


def hash_api_key(key: str) -> str:
    """Hash an API key using SHA256."""
    return hashlib.sha256(key.encode()).hexdigest()


def verify_api_key(db: Session, api_key: str) -> bool:
    """Verify if an API key is valid and active."""
    if api_key == settings.API_KEY:
        return True

    key_hash = hash_api_key(api_key)
    db_key = db.query(ApiKey).filter(
        ApiKey.key_hash == key_hash,
        ApiKey.is_active == True
    ).first()
    return db_key is not None


def create_api_key(db: Session, label: Optional[str] = None) -> Tuple[str, str]:
    """Create a new API key. Returns (raw_key, hashed_key)."""
    raw_key = secrets.token_urlsafe(32)
    hashed_key = hash_api_key(raw_key)
    
    api_key = ApiKey(
        key_hash=hashed_key,
        label=label,
        is_active=True
    )
    db.add(api_key)
    db.commit()
    
    return raw_key, hashed_key
