from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
import uuid

from ..database import Base
from .guid import GUID

class AssetTag(Base):
    __tablename__ = "asset_tags"

    id = Column(GUID(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    asset_id = Column(GUID(36), ForeignKey("assets.id"), nullable=False)
    tag = Column(String, nullable=False)

    asset = relationship("Asset", back_populates="tags")
