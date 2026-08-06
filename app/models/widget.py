from sqlalchemy import Boolean, Column, ForeignKey, Integer, String

from app.database import Base


class Widget(Base):
    __tablename__ = "widgets"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    title = Column(String)

    description = Column(String)

    widget_type = Column(String)

    button_text = Column(String)

    is_active = Column(Boolean, default=True)