from sqlalchemy import Column, String, DateTime, Boolean
from datetime import datetime, timezone
import uuid

from ..database import Base
from .guid import GUID

class ApiKey(Base):
    __tablename__ = "api_keys"

    id = Column(GUID(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    key_hash = Column(String, nullable=False)
    label = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
