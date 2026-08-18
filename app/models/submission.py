from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Submission(Base):
    __tablename__ = "submission"

    id = Column(Integer, primary_key=True, index=True)

    widget_id = Column(Integer, ForeignKey("widgets.id"))

    name = Column(String)
    email = Column(String)
    message = Column(String)

    # AI Triage Result
    category = Column(String, default="other")
    urgency = Column(String, default="normal")
    confidence = Column(Float, default=0.0)
    reason = Column(String, nullable=True)

    widget = relationship("Widget")