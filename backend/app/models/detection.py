import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum, Text, Boolean, JSON, Integer
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.event import EventSeverity


class DetectionRule(Base):
    __tablename__ = "detection_rules"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True)
    code = Column(String(100), unique=True, index=True, nullable=False)  # e.g., SSH_BRUTE_FORCE
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    severity = Column(Enum(EventSeverity), default=EventSeverity.HIGH, nullable=False)
    is_enabled = Column(Boolean, default=True, nullable=False)
    time_window_seconds = Column(Integer, default=300, nullable=False)
    threshold_count = Column(Integer, default=10, nullable=False)
    rule_config = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    organization = relationship("Organization", back_populates="detection_rules")
    alerts = relationship("Alert", back_populates="detection_rule")
