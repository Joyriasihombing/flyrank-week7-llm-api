from sqlalchemy import Column, ForeignKey, Integer, String

from app.database import Base


class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)

    widget_id = Column(Integer, ForeignKey("widgets.id"))

    name = Column(String)

    email = Column(String)

    message = Column(String)

    country = Column(String)

    city = Column(String)

    ip_address = Column(String)