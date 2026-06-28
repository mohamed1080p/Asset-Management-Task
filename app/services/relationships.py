from sqlalchemy.orm import Session
from sqlalchemy import or_
from uuid import UUID
from typing import List, Optional

from ..models import Asset, Relationship
from ..schemas import RelationshipCreate
from .assets import get_asset, _asset_exists


def create_relationship(db: Session, data: RelationshipCreate) -> Relationship:
    """Create a relationship between two assets."""
    # Validate asset IDs are different
    if data.from_asset_id == data.to_asset_id:
        raise ValueError("Asset cannot have a relationship to itself")

    # Validate both assets exist
    if not _asset_exists(db, data.from_asset_id):
        raise ValueError(f"Source asset {data.from_asset_id} not found")
    if not _asset_exists(db, data.to_asset_id):
        raise ValueError(f"Target asset {data.to_asset_id} not found")

    # Check for duplicate relationship
    existing = db.query(Relationship).filter(
        Relationship.from_asset_id == data.from_asset_id,
        Relationship.to_asset_id == data.to_asset_id,
        Relationship.relation_type == data.relation_type
    ).first()

    if existing:
        raise ValueError("This relationship already exists")

    rel = Relationship(
        from_asset_id=data.from_asset_id,
        to_asset_id=data.to_asset_id,
        relation_type=data.relation_type,
    )
    db.add(rel)
    db.commit()
    db.refresh(rel)
    return rel


def get_relationships(db: Session, asset_id: UUID) -> List[Relationship]:
    """Get all relationships for an asset (both incoming and outgoing)."""
    return db.query(Relationship).filter(
        or_(
            Relationship.from_asset_id == asset_id,
            Relationship.to_asset_id == asset_id,
        )
    ).all()


def get_asset_graph(db: Session, asset_id: UUID) -> Optional[dict]:
    """Get an asset with all its related assets (the graph around it)."""
    asset = get_asset(db, asset_id)
    if not asset:
        return None

    relationships = get_relationships(db, asset_id)
    
    # Collect all related asset IDs
    related_ids = set()
    for rel in relationships:
        if rel.from_asset_id == asset_id:
            related_ids.add(rel.to_asset_id)
        else:
            related_ids.add(rel.from_asset_id)

    # Fetch related assets
    related_assets = []
    if related_ids:
        related_assets = db.query(Asset).filter(Asset.id.in_(related_ids)).all()

    return {
        "asset": asset,
        "relationships": relationships,
        "related_assets": related_assets,
        "relation_count": len(relationships)
    }
