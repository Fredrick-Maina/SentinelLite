import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON, Boolean
from sqlalchemy.orm import relationship
from app.database import Base


class AIAnalysis(Base):
    __tablename__ = "ai_analyses"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    alert_id = Column(String(36), ForeignKey("alerts.id", ondelete="CASCADE"), nullable=False, index=True)
    provider = Column(String(50), default="mock", nullable=False)
    model_name = Column(String(100), default="sentinellite-analyst-v1", nullable=False)

    summary = Column(Text, nullable=False)
    explanation = Column(Text, nullable=False)
    recommended_actions = Column(JSON, nullable=True)
    is_mock = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    alert = relationship("Alert", back_populates="ai_analyses")
