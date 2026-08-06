from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Submission(Base):
    __tablename__ = "submission"

    id = Column(Integer, primary_key=True, index=True)

    widget_id = Column(Integer, ForeignKey("widgets.id"))

    name = Column(String)
    email = Column(String)
    message = Column(String)

    widget = relationship("Widget")