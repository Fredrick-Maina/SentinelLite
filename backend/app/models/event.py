import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum, Text, JSON, Integer
from sqlalchemy.orm import relationship
from app.database import Base


class EventSeverity(str, enum.Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class LogEvent(Base):
    __tablename__ = "log_events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    device_id = Column(String(36), ForeignKey("devices.id", ondelete="SET NULL"), nullable=True, index=True)

    hostname = Column(String(255), nullable=True, index=True)
    source_type = Column(String(50), nullable=False, index=True)  # ssh, syslog, nginx, windows, json
    event_type = Column(String(100), nullable=False, index=True)  # auth_failure, auth_success, path_scan, etc.
    severity = Column(Enum(EventSeverity), default=EventSeverity.INFO, nullable=False, index=True)

    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    received_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

    username = Column(String(255), nullable=True, index=True)
    source_ip = Column(String(45), nullable=True, index=True)
    destination_ip = Column(String(45), nullable=True)
    destination_port = Column(Integer, nullable=True)

    message = Column(Text, nullable=True)
    raw_message = Column(Text, nullable=False)
    extra_metadata = Column(JSON, nullable=True)
    detection_processed = Column(String(20), default="PENDING", nullable=False)  # PENDING, PROCESSED

    organization = relationship("Organization", back_populates="events")
    device = relationship("Device", back_populates="events")
