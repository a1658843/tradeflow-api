from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime

from app.core.database import Base


class Shipment(Base):
    __tablename__ = "shipments"

    id = Column(Integer, primary_key=True, index=True)

    order_id = Column(Integer, ForeignKey("trade_orders.id"), nullable=False)

    carrier = Column(String, nullable=False)
    tracking_number = Column(String, unique=True, index=True, nullable=False)

    shipment_status = Column(String, default="pending")

    shipped_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)