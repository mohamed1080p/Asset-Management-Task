from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

from ..database import Base
from .guid import GUID

class Relationship(Base):
    __tablename__ = "relationships"

    id = Column(GUID(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    from_asset_id = Column(GUID(36), ForeignKey("assets.id"), nullable=False)
    to_asset_id = Column(GUID(36), ForeignKey("assets.id"), nullable=False)
    relation_type = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    from_asset = relationship("Asset", foreign_keys=[from_asset_id], back_populates="relationships_from")
    to_asset = relationship("Asset", foreign_keys=[to_asset_id], back_populates="relationships_to")
