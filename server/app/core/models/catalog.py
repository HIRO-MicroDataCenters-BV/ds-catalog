from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Uuid

from ..database import Base


class CatalogItemModel(Base):
    __tablename__ = "catalog_items"

    id = Column(Uuid, primary_key=True, index=True)
    is_local = Column(Boolean, index=True)
    is_shared = Column(Boolean, default=False, index=True)
    created = Column(DateTime(timezone=True), default=datetime.now, index=True)
