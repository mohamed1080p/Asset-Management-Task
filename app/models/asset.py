from sqlalchemy import Column, String, DateTime, Enum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid
import enum

from ..database import Base
from .guid import GUID

class AssetType(str, enum.Enum):
    domain = "domain"
    subdomain = "subdomain"
    ip_address = "ip_address"
    service = "service"
    certificate = "certificate"
    technology = "technology"

class AssetStatus(str, enum.Enum):
    active = "active"
    stale = "stale"
    archived = "archived"


class Asset(Base):
    __tablename__ = "assets"

    id = Column(GUID(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    type = Column(Enum(AssetType), nullable=False)
    value = Column(String, nullable=False)
    status = Column(Enum(AssetStatus), default=AssetStatus.active)
    first_seen = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_seen = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    source = Column(String)
    metadata_ = Column("metadata", JSON)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    tags = relationship("AssetTag", back_populates="asset", cascade="all, delete")

    @property
    def tag_names(self):
        return [tag.tag for tag in self.tags] if self.tags else []

    relationships_from = relationship(
        "Relationship",
        foreign_keys="Relationship.from_asset_id",
        back_populates="from_asset",
        cascade="all, delete-orphan"
    )
    relationships_to = relationship(
        "Relationship",
        foreign_keys="Relationship.to_asset_id",
        back_populates="to_asset",
        cascade="all, delete-orphan"
    )
